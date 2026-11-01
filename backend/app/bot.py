"""Telegram bot (aiogram 3). Long polling locally, webhook in production."""
import asyncio
import html
import json
import logging
import os
import re
import shutil
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command, CommandObject
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton,
                           MenuButtonWebApp, Message, ReplyKeyboardMarkup, WebAppInfo)
from sqlalchemy.orm import selectinload

from . import botstate
from .config import get_settings
from .core import all_settings
from .db import SessionLocal
from .models import (STATUS_RU, STATUS_UZ, AdminAccount, Customer, MarketingVisit, Order, Product, ShopSession,
                     StoreEvent, now)

log = logging.getLogger("whitmore.bot")
router = Router()

T = {
    "uz": {
        "choose_lang": "Tilni tanlang / Выберите язык",
        "welcome": (
            "<b>WHITMORE — Sartorial Menswear</b>\n\n"
            "Xitoydan buyurtma asosida yetkaziladigan klassik erkaklar kiyimi.\n"
            "Do'konni (Mini App) ochish yoki bo'limlarni ko'rish uchun pastdagi tugmalardan foydalaning:"
        ),
        "share_phone": "📱 Telefon raqamini ulashish (ixtiyoriy)",
        "phone_saved": "Raqamingiz saqlandi. Rahmat!",
        "open": "🛍 Do'konni ochish (Mini App)",
        "catalog": "👔 Katalog",
        "cart": "🛒 Savatni ochish",
        "orders_btn": "📦 Buyurtmalarim",
        "faq_btn": "❓ Ko'p so'raladigan savollar",
        "contact_btn": "📞 Aloqa",
        "no_orders": "Sizda hali buyurtmalar yo'q.",
        "orders": "<b>Sizning buyurtmalaringiz:</b>",
        "contact": "Biz bilan bog'lanish:",
        "lang_set": "Til o'zgartirildi: O'zbekcha",
        "myid": "Sizning Telegram ID: ",
        "linked": "✅ <b>Telegram akkauntingiz admin panelga muvaffaqiyatli ulandi!</b>\nYangi buyurtma xabarnomalari shu yerga keladi.",
        "link_bad": "Havola eskirgan yoki noto'g'ri. Admin paneldan yangisini oling.",
        "need_https": "HTTPS tunnel ishga tushirilmoqda... Bir necha soniyadan so'ng /start bosing yoki quyidagi katalogdan foydalaning:",
        "faq": "Ko'p so'raladigan savollar",
        "catalog_header": "<b>WHITMORE — Tanlangan modellar:</b>\n\nTo'liq katalog, o'lchamlar jadvali va buyurtma berish uchun Mini App tugmasini bosing:",
    },
    "ru": {
        "choose_lang": "Tilni tanlang / Выберите язык",
        "welcome": (
            "<b>WHITMORE — Sartorial Menswear</b>\n\n"
            "Классическая мужская одежда под заказ из Китая.\n"
            "Используйте кнопки ниже, чтобы открыть магазин (Mini App) или разделы:"
        ),
        "share_phone": "📱 Поделиться номером (по желанию)",
        "phone_saved": "Номер сохранён. Спасибо!",
        "open": "🛍 Открыть магазин (Mini App)",
        "catalog": "👔 Каталог",
        "cart": "🛒 Открыть корзину",
        "orders_btn": "📦 Мои заказы",
        "faq_btn": "❓ Частые вопросы",
        "contact_btn": "📞 Контакты",
        "no_orders": "У вас пока нет заказов.",
        "orders": "<b>Ваши заказы:</b>",
        "contact": "Связаться с нами:",
        "lang_set": "Язык изменён: Русский",
        "myid": "Ваш Telegram ID: ",
        "linked": "✅ <b>Ваш Telegram успешно привязан к админ-панели!</b>\nУведомления о новых заказах будут приходить сюда.",
        "link_bad": "Ссылка устарела или неверна. Получите новую в админ-панели.",
        "need_https": "HTTPS-туннель запускается... Нажмите /start через несколько секунд или воспользуйтесь каталогом ниже:",
        "faq": "Частые вопросы",
        "catalog_header": "<b>WHITMORE — Избранные модели:</b>\n\nДля полного каталога, таблицы размеров и оформления заказа откройте Mini App:",
    },
}


def tr(lang: str, key: str) -> str:
    return T.get(lang, T["uz"])[key]


def effective_base_url() -> str:
    cfg_url = get_settings().APP_URL.rstrip("/")
    if cfg_url.startswith("https://"):
        return cfg_url
    if botstate.public_https_url.startswith("https://"):
        return botstate.public_https_url.rstrip("/")
    return cfg_url


def app_url(path: str = "") -> str:
    return effective_base_url() + "/miniapp" + path


def webapp_markup(lang: str, key: str = "open", path: str = ""):
    url = app_url(path)
    if not url.startswith("https://"):
        return None
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=tr(lang, key), web_app=WebAppInfo(url=url))]])


def main_menu_markup(
    lang: str,
    pending_admin: AdminAccount | None = None,
    utm_query: str = "",
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    url = app_url(utm_query)
    if url.startswith("https://"):
        rows.append([InlineKeyboardButton(text=tr(lang, "open"), web_app=WebAppInfo(url=url))])
    if pending_admin is not None:
        rows.append([InlineKeyboardButton(
            text=f"🔐 Admin panelga ulash ({pending_admin.login})",
            callback_data=f"link_admin:{pending_admin.id}"
        )])
    rows.append([
        InlineKeyboardButton(text=tr(lang, "catalog"), callback_data="menu:catalog"),
        InlineKeyboardButton(text=tr(lang, "orders_btn"), callback_data="menu:orders"),
    ])
    rows.append([
        InlineKeyboardButton(text=tr(lang, "faq_btn"), callback_data="menu:faq"),
        InlineKeyboardButton(text=tr(lang, "contact_btn"), callback_data="menu:contact"),
    ])
    rows.append([
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def _record_bot_utm(db, customer_id: int, source: str, medium: str, campaign: str) -> str:
    import secrets
    from .security import token_hash

    src = re.sub(r"[^\w.\-]", "", source or "")[:64] or "instagram"
    med = re.sub(r"[^\w.\-]", "", medium or "")[:64] or "bot"
    cmp = re.sub(r"[^\w.\-]", "", campaign or "")[:64]
    db.add(MarketingVisit(customer_id=customer_id, source=src, medium=med, campaign=cmp))
    sess = db.query(ShopSession).filter_by(customer_id=customer_id).first()
    if not sess:
        sess = ShopSession(
            customer_id=customer_id,
            token_hash=token_hash(secrets.token_urlsafe(32)),
            cart=[],
        )
        db.add(sess)
    sess.utm_source = src
    sess.utm_medium = med
    sess.utm_campaign = cmp
    sess.last_seen = now()
    db.commit()
    return f"?utm_source={src}&utm_medium={med}&utm_campaign={cmp}"


async def _send_product_deeplink(m: Message, db, c: Customer, pid: int, source: str = "instagram"):
    lang = c.language or "uz"
    p = (
        db.query(Product)
        .options(selectinload(Product.images), selectinload(Product.variants))
        .filter(
            Product.id == pid,
            Product.active.is_(True),
            Product.draft.is_(False),
            Product.deleted_at.is_(None),
        )
        .first()
    )
    if not p:
        return False

    utm_q = _record_bot_utm(db, c.id, source, "product", f"prod_{p.id}")
    db.add(StoreEvent(type="product_view", customer_id=c.id, product_id=p.id))
    db.commit()

    name = p.name_ru if lang == "ru" and p.name_ru else p.name_uz
    desc = (p.desc_ru if lang == "ru" and p.desc_ru else p.desc_uz) or ""
    price = f"{p.price_uzs:,}".replace(",", " ")
    badge = (
        ("Под заказ (14–25 дней)" if lang == "ru" else "Buyurtma asosida (14–25 kun)")
        if p.sale_type == "preorder"
        else ("В наличии" if lang == "ru" else "Omborda mavjud")
    )
    sizes = ", ".join(dict.fromkeys(v.size for v in p.variants if v.size)) or "—"
    colors = ", ".join(dict.fromkeys(v.color for v in p.variants if v.color)) or "—"

    caption_lines = [
        f"✨ <b>{html.escape(name)}</b>",
        f"💰 Narxi: <b>{price} so'm</b>",
        f"📦 Holati: <i>{badge}</i>",
        f"📏 O'lchamlar: <b>{html.escape(sizes)}</b>",
        f"🎨 Ranglar: <b>{html.escape(colors)}</b>",
    ]
    if p.material:
        caption_lines.append(f"🧵 Material: {html.escape(p.material)}")
    if desc.strip():
        short_desc = desc.strip()[:220] + ("..." if len(desc.strip()) > 220 else "")
        caption_lines.extend(["", html.escape(short_desc)])
    caption = "\n".join(caption_lines)

    prod_url = app_url(f"/product/{p.id}{utm_q}")
    cat_url = app_url(utm_q)
    kb_rows: list[list[InlineKeyboardButton]] = []
    if prod_url.startswith("https://"):
        btn_lbl = (
            "🛍 Открыть этот товар в Mini App"
            if lang == "ru"
            else "🛍 Shu mahsulotni ochish (Mini App)"
        )
        all_lbl = "👔 Весь каталог" if lang == "ru" else "👔 Barcha modellar"
        kb_rows.append([InlineKeyboardButton(text=btn_lbl, web_app=WebAppInfo(url=prod_url))])
        kb_rows.append([InlineKeyboardButton(text=all_lbl, web_app=WebAppInfo(url=cat_url))])
    kb_rows.append([
        InlineKeyboardButton(text=tr(lang, "orders_btn"), callback_data="menu:orders"),
        InlineKeyboardButton(text=tr(lang, "contact_btn"), callback_data="menu:contact"),
    ])
    markup = InlineKeyboardMarkup(inline_keyboard=kb_rows)

    if p.images:
        img_file = get_settings().upload_path / p.images[0].path
        if img_file.exists():
            try:
                await m.answer_photo(photo=FSInputFile(img_file), caption=caption, reply_markup=markup)
                return True
            except Exception:
                pass
    await m.answer(caption, reply_markup=markup)
    return True


def get_customer(db, u) -> Customer:
    c = db.query(Customer).filter_by(tg_id=u.id).first()
    if not c:
        c = Customer(tg_id=u.id, language="ru" if getattr(u, "language_code", "") == "ru" else "uz")
        db.add(c)
    c.first_name = (u.first_name or "")[:120]
    c.last_name = (u.last_name or "")[:120]
    c.username = (u.username or "")[:64]
    c.last_seen = now()
    db.commit()
    return c


def _link_admin_account(db, a: AdminAccount, chat_id: int, user) -> None:
    a.tg_chat_id = chat_id
    a.link_token = None
    a.link_token_expires = None
    if user and getattr(user, "username", None):
        a.tg_username = user.username[:64]
    db.commit()


@router.message(Command("start"))
async def start(m: Message, command: CommandObject):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        lang = c.language or "uz"
        arg = (command.args or "").strip()
        utm_query = ""

        # Refresh MenuButtonWebApp for this user so mobile Telegram always has current HTTPS URL
        base_url = app_url()
        if base_url.startswith("https://") and botstate.bot is not None:
            try:
                await botstate.bot.set_chat_menu_button(
                    chat_id=m.chat.id,
                    menu_button=MenuButtonWebApp(text="Do'kon", web_app=WebAppInfo(url=base_url)),
                )
            except Exception:
                pass

        # 1) Explicit /start link_<token>
        if arg.startswith("link_"):
            tok = arg[5:]
            a = db.query(AdminAccount).filter_by(link_token=tok).first()
            if not a:
                # Fallback if owner regenerated token right before clicking
                a = db.query(AdminAccount).filter(
                    AdminAccount.link_token.isnot(None),
                    AdminAccount.blocked == False  # noqa: E712
                ).first()
            if a and not a.blocked and (not a.link_token_expires or a.link_token_expires > now()):
                _link_admin_account(db, a, m.chat.id, m.from_user)
                await m.answer(tr(lang, "linked"))
            else:
                await m.answer(tr(lang, "link_bad"))

        # 2) Product deep-link from Instagram / Reels / Story: /start prod_<id> or /start prod_<id>_<source>
        elif arg.startswith("prod_"):
            parts = arg.split("_")
            pid = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
            src = parts[2] if len(parts) > 2 and parts[2] else "instagram"
            if pid > 0 and await _send_product_deeplink(m, db, c, pid, source=src):
                return

        # 3) Marketing / Instagram campaign deep-link: /start instagram-reels-kuz or /start instagram
        else:
            if arg:
                parts = arg.split("-")
                src = parts[0]
                med = parts[1] if len(parts) > 1 else "bio"
                cmp = "-".join(parts[2:]) if len(parts) > 2 else "profil"
                utm_query = _record_bot_utm(db, c.id, src, med, cmp)

            uname = (m.from_user.username or "").strip().lower()
            matched_admin = None
            if uname:
                matched_admin = db.query(AdminAccount).filter(
                    AdminAccount.tg_username.ilike(uname),
                    AdminAccount.blocked == False  # noqa: E712
                ).first()
            if not matched_admin:
                # If owner clicked "Telegramni ulash" in the Admin Panel, auto-link when they press Start
                pending = db.query(AdminAccount).filter(
                    AdminAccount.link_token.isnot(None),
                    AdminAccount.blocked == False  # noqa: E712
                ).all()
                if len(pending) == 1:
                    matched_admin = pending[0]
            if matched_admin and matched_admin.tg_chat_id != m.chat.id:
                _link_admin_account(db, matched_admin, m.chat.id, m.from_user)
                await m.answer(tr(lang, "linked"))

        pending_unlinked = db.query(AdminAccount).filter(
            AdminAccount.tg_chat_id.is_(None),
            AdminAccount.blocked == False  # noqa: E712
        ).first()

        await m.answer(tr(lang, "welcome"), reply_markup=main_menu_markup(lang, pending_unlinked, utm_query=utm_query))
    finally:
        db.close()


@router.callback_query(F.data.startswith("link_admin:"))
async def link_admin_cb(cb: CallbackQuery):
    aid = int(cb.data.split(":")[1])
    db = SessionLocal()
    try:
        c = get_customer(db, cb.from_user)
        a = db.get(AdminAccount, aid)
        if a and not a.blocked:
            _link_admin_account(db, a, cb.message.chat.id, cb.from_user)
            await cb.answer("Telegram admin panelga ulandi!", show_alert=True)
            await cb.message.answer(tr(c.language, "linked"), reply_markup=main_menu_markup(c.language))
        else:
            await cb.answer(tr(c.language, "link_bad"), show_alert=True)
    finally:
        db.close()


@router.callback_query(F.data.startswith("lang:"))
async def pick_lang(cb: CallbackQuery):
    lang = cb.data.split(":")[1]
    db = SessionLocal()
    try:
        c = get_customer(db, cb.from_user)
        c.language = lang
        db.commit()
    finally:
        db.close()
    await cb.answer(tr(lang, "lang_set"))
    phone_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=tr(lang, "share_phone"), request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await cb.message.answer(tr(lang, "welcome"), reply_markup=main_menu_markup(lang))
    await cb.message.answer(tr(lang, "share_phone"), reply_markup=phone_kb)


@router.message(F.contact)
async def got_contact(m: Message):
    if m.contact.user_id != m.from_user.id:
        return
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        c.phone = "+" + m.contact.phone_number.lstrip("+")
        db.commit()
        await m.answer(tr(c.language, "phone_saved"), reply_markup=main_menu_markup(c.language))
    finally:
        db.close()


async def _send_catalog_overview(target_msg: Message, lang: str):
    db = SessionLocal()
    try:
        prods = (
            db.query(Product)
            .filter(Product.active.is_(True), Product.draft.is_(False), Product.deleted_at.is_(None))
            .order_by(Product.featured.desc(), Product.id.desc())
            .limit(8)
            .all()
        )
        lines = [tr(lang, "catalog_header"), ""]
        for i, p in enumerate(prods, 1):
            name = (p.name_ru if lang == "ru" and p.name_ru else p.name_uz)
            badge = ("Под заказ" if lang == "ru" else "Buyurtmaga") if p.sale_type == "preorder" else ("В наличии" if lang == "ru" else "Omborda bor")
            price = f"{p.price_uzs:,}".replace(",", " ")
            lines.append(f"{i}. <b>{html.escape(name)}</b> — {price} so'm <i>({badge})</i>")
        rows: list[list[InlineKeyboardButton]] = []
        url = app_url("/catalog")
        if url.startswith("https://"):
            rows.append([InlineKeyboardButton(text=tr(lang, "open"), web_app=WebAppInfo(url=url))])
        rows.append([InlineKeyboardButton(text=tr(lang, "orders_btn"), callback_data="menu:orders"),
                     InlineKeyboardButton(text=tr(lang, "contact_btn"), callback_data="menu:contact")])
        await target_msg.answer("\n".join(lines), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    finally:
        db.close()


@router.callback_query(F.data.startswith("menu:"))
async def menu_cb(cb: CallbackQuery):
    action = cb.data.split(":")[1]
    await cb.answer()
    db = SessionLocal()
    try:
        c = get_customer(db, cb.from_user)
        lang = c.language or "uz"
        if action == "catalog":
            await _send_catalog_overview(cb.message, lang)
        elif action == "orders":
            rows = db.query(Order).filter_by(customer_id=c.id).order_by(Order.id.desc()).limit(5).all()
            if not rows:
                await cb.message.answer(tr(lang, "no_orders"), reply_markup=main_menu_markup(lang))
                return
            labels = STATUS_RU if lang == "ru" else STATUS_UZ
            lines = [tr(lang, "orders")] + [
                f"• <b>{o.code}</b> — {labels.get(o.status, o.status)} — {o.total:,} so'm".replace(",", " ")
                for o in rows
            ]
            await cb.message.answer("\n".join(lines), reply_markup=main_menu_markup(lang))
        elif action == "faq":
            s = all_settings(db)
            items = json.loads(s["faq"] or "[]")
            suf = "ru" if lang == "ru" else "uz"
            text = f"<b>{tr(lang, 'faq')}</b>\n\n" + "\n\n".join(
                f"<b>{html.escape(i['q_' + suf])}</b>\n{html.escape(i['a_' + suf])}" for i in items
            )
            await cb.message.answer(text, reply_markup=main_menu_markup(lang))
        elif action == "contact":
            u = all_settings(db)["contact_username"].lstrip("@")
            await cb.message.answer(f"{tr(lang, 'contact')} https://t.me/{html.escape(u)}", reply_markup=main_menu_markup(lang))
    finally:
        db.close()


@router.message(Command("catalog"))
async def catalog(m: Message):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        lang = c.language or "uz"
    finally:
        db.close()
    await _send_catalog_overview(m, lang)


@router.message(Command("cart"))
async def cart(m: Message):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        markup = webapp_markup(c.language, "cart", "/cart")
        if markup:
            await m.answer(tr(c.language, "cart"), reply_markup=markup)
        else:
            await _send_catalog_overview(m, c.language)
    finally:
        db.close()


@router.message(Command("orders"))
async def orders(m: Message):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        rows = db.query(Order).filter_by(customer_id=c.id).order_by(Order.id.desc()).limit(5).all()
        if not rows:
            await m.answer(tr(c.language, "no_orders"), reply_markup=main_menu_markup(c.language))
            return
        labels = STATUS_RU if c.language == "ru" else STATUS_UZ
        lines = [tr(c.language, "orders")] + [
            f"• <b>{o.code}</b> — {labels.get(o.status, o.status)} — {o.total:,} so'm".replace(",", " ")
            for o in rows
        ]
        await m.answer("\n".join(lines), reply_markup=main_menu_markup(c.language))
    finally:
        db.close()


@router.message(Command("faq"))
async def faq(m: Message):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        s = all_settings(db)
        items = json.loads(s["faq"] or "[]")
        suf = "ru" if c.language == "ru" else "uz"
        text = f"<b>{tr(c.language, 'faq')}</b>\n\n" + "\n\n".join(
            f"<b>{html.escape(i['q_' + suf])}</b>\n{html.escape(i['a_' + suf])}" for i in items)
        await m.answer(text, reply_markup=main_menu_markup(c.language))
    finally:
        db.close()


@router.message(Command("contact"))
async def contact(m: Message):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        u = all_settings(db)["contact_username"].lstrip("@")
        await m.answer(f"{tr(c.language, 'contact')} https://t.me/{html.escape(u)}", reply_markup=main_menu_markup(c.language))
    finally:
        db.close()


@router.message(Command("language"))
async def language(m: Message):
    LANG_KB = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")]])
    await m.answer(tr("uz", "choose_lang"), reply_markup=LANG_KB)


@router.message(Command("myid"))
async def myid(m: Message):
    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        await m.answer(tr(c.language, "myid") + f"<code>{m.from_user.id}</code>")
    finally:
        db.close()


@router.callback_query(F.data.startswith("pay_ok:"))
async def pay_ok_cb(cb: CallbackQuery):
    from .orders_service import set_status
    oid = int(cb.data.split(":")[1])
    db = SessionLocal()
    try:
        o = db.get(Order, oid)
        if not o:
            await cb.answer("Buyurtma topilmadi", show_alert=True)
            return
        admin = db.query(AdminAccount).filter_by(tg_chat_id=cb.from_user.id).first()
        admin_name = admin.full_name if admin else (cb.from_user.full_name or "admin")
        if o.status not in ("paid", "ordered_china", "china_warehouse", "in_transit", "in_uz", "delivered", "cancelled"):
            set_status(db, o, "paid", admin_name)
            db.commit()
        await cb.answer("✅ To'lov tasdiqlandi!", show_alert=True)
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await cb.message.answer(f"✅ <b>{html.escape(o.code)}</b> — To'lov tasdiqlandi ({html.escape(admin_name)}). Mijozga xabar yuborildi.")
    finally:
        db.close()


@router.callback_query(F.data.startswith("pay_no:"))
async def pay_no_cb(cb: CallbackQuery):
    from .models import OrderStatusHistory
    from .outbox import enqueue
    oid = int(cb.data.split(":")[1])
    db = SessionLocal()
    try:
        o = db.get(Order, oid)
        if not o:
            await cb.answer("Buyurtma topilmadi", show_alert=True)
            return
        admin = db.query(AdminAccount).filter_by(tg_chat_id=cb.from_user.id).first()
        admin_name = admin.full_name if admin else (cb.from_user.full_name or "admin")
        o.history.append(OrderStatusHistory(status=o.status, by=f"{admin_name} (chek rad etildi)"))
        if o.customer and o.customer.tg_id:
            msg = (
                f"❌ Заказ <b>{html.escape(o.code)}</b>: чек оплаты не подтверждён. Пожалуйста, проверьте и отправьте снова."
                if o.customer.language == "ru"
                else f"❌ Buyurtma <b>{html.escape(o.code)}</b> bo'yicha yuborilgan to'lov cheki tasdiqlanmadi. Iltimos, qayta tekshirib yuboring yoki adminga murojaat qiling."
            )
            enqueue(db, "status", o.customer.tg_id, msg)
        db.commit()
        await cb.answer("❌ Chek rad etildi", show_alert=True)
        try:
            await cb.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        await cb.message.answer(f"❌ <b>{html.escape(o.code)}</b> — To'lov cheki rad etildi. Mijoz ogohlantirildi.")
    finally:
        db.close()


@router.message(F.photo)
async def got_receipt_photo(m: Message):
    """If a customer sends a photo in bot chat, attach it as payment receipt for their latest unpaid order."""
    from io import BytesIO
    from .core import get_setting, process_image_bytes, set_setting
    from .models import OrderStatusHistory
    from .orders_service import fmt_money
    from .outbox import enqueue

    db = SessionLocal()
    try:
        c = get_customer(db, m.from_user)
        o = (
            db.query(Order)
            .filter(Order.customer_id == c.id, Order.status.in_(["new", "awaiting_payment"]))
            .order_by(Order.id.desc())
            .first()
        )
        if not o:
            return
        photo = m.photo[-1]
        buf = BytesIO()
        await m.bot.download(photo, destination=buf)
        up = process_image_bytes(buf.getvalue(), "tg_receipt.jpg", db, None, subdir="receipts", max_side=1400)
        set_setting(db, f"receipt:{o.code}", up.path)
        if o.status == "new":
            o.status = "awaiting_payment"
            o.history.append(OrderStatusHistory(status="awaiting_payment", by="mijoz (bot orqali chek)"))
        pct = float(get_setting(db, "advance_pct") or 30)
        adv = int(round(o.total * pct / 100))
        caption = (
            f"💳 <b>To'lov cheki (Bot orqali) — {html.escape(o.code)}</b>\n"
            f"Mijoz: {html.escape(o.name)} | {html.escape(o.phone or '-')}\n"
            f"Jami: <b>{fmt_money(o.total)}</b> | Avans ({int(pct)}%): <b>{fmt_money(adv)}</b>"
        )
        targets = []
        if o.meta and o.meta.assigned_admin and o.meta.assigned_admin.tg_chat_id:
            targets.append(o.meta.assigned_admin.tg_chat_id)
        else:
            targets = [
                a.tg_chat_id for a in db.query(AdminAccount).filter(
                    AdminAccount.tg_chat_id.isnot(None), AdminAccount.blocked.is_(False)
                ).all() if a.tg_chat_id
            ]
        for chat_id in dict.fromkeys(targets):
            enqueue(db, "receipt", chat_id, caption, photo=up.path, button_text="Tasdiqlash",
                    button_url=f"cb:approve_receipt:{o.id}", order_id=o.id)
        db.commit()
        reply = (
            f"✅ Чек по заказу <b>{html.escape(o.code)}</b> принят и отправлен администратору на проверку."
            if c.language == "ru"
            else f"✅ <b>{html.escape(o.code)}</b> buyurtmangiz uchun to'lov cheki qabul qilindi va adminga tasdiqlash uchun yuborildi!"
        )
        await m.answer(reply, reply_markup=main_menu_markup(c.language))
    finally:
        db.close()


@router.message(Command("backup"))
async def backup_cmd(m: Message):
    from aiogram.types import BufferedInputFile, FSInputFile
    from sqlalchemy import func
    from .routers.admin_stats import _build_orders_csv

    db = SessionLocal()
    try:
        admin = db.query(AdminAccount).filter_by(tg_chat_id=m.from_user.id, blocked=False).first()
        if not admin:
            await m.answer("Bu buyruq faqat ulangan adminlar uchun.")
            return
        csv_bytes = _build_orders_csv(db).encode("utf-8")
        n_orders = db.query(func.count(Order.id)).scalar() or 0
        n_cust = db.query(func.count(Customer.id)).scalar() or 0
        await m.answer_document(
            BufferedInputFile(csv_bytes, filename=f"whitmore-orders-{now().strftime('%Y%m%d')}.csv"),
            caption=f"💾 <b>WHITMORE Zaxira</b> — Buyurtmalar: {n_orders} ta, Mijozlar: {n_cust} ta",
        )
        st = get_settings()
        if st.DATABASE_URL.startswith("sqlite:///"):
            db_path = Path(st.DATABASE_URL.replace("sqlite:///", "", 1))
            if db_path.exists():
                await m.answer_document(
                    FSInputFile(db_path, filename=f"whitmore-backup-{now().strftime('%Y%m%d')}.db"),
                    caption="🗄 SQLite baza (.db)",
                )
    finally:
        db.close()


def build() -> tuple[Bot, Dispatcher] | None:
    token = (get_settings().BOT_TOKEN or "").strip()
    if not token or token.startswith("your_"):
        return None
    bot = Bot(token, default=DefaultBotProperties(parse_mode="HTML"))
    dp = Dispatcher()
    dp.include_router(router)
    return bot, dp


COMMANDS = [("start", "Do'konni ochish / Boshlash"), ("catalog", "Katalog"), ("cart", "Savat"),
            ("orders", "Buyurtmalarim"), ("faq", "Savollar"), ("contact", "Aloqa"), ("language", "Til"), ("myid", "ID")]


async def update_menu_button(bot: Bot, notify_admins: bool = False):
    url = app_url()
    if url.startswith("https://"):
        menu_btn = MenuButtonWebApp(text="Do'kon", web_app=WebAppInfo(url=url))
        try:
            await bot.set_chat_menu_button(menu_button=menu_btn)
            log.info("Telegram MenuButtonWebApp set to %s", url)
        except Exception as exc:
            log.warning("Could not set MenuButtonWebApp: %s", type(exc).__name__)
        # Also force-refresh menu button per chat so mobile Telegram (iOS/Android) updates immediately
        db = SessionLocal()
        try:
            chat_ids = set()
            for (cid,) in db.query(Customer.tg_id).filter(Customer.tg_id.isnot(None)).all():
                if cid:
                    chat_ids.add(int(cid))
            admin_ids = set()
            for (aid,) in db.query(AdminAccount.tg_chat_id).filter(
                AdminAccount.tg_chat_id.isnot(None), AdminAccount.blocked.is_(False)
            ).all():
                if aid:
                    chat_ids.add(int(aid))
                    admin_ids.add(int(aid))
            for cid in chat_ids:
                try:
                    await bot.set_chat_menu_button(chat_id=cid, menu_button=menu_btn)
                except Exception:
                    pass
            if notify_admins and admin_ids:
                kb = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text="🛍 Do'konni ochish (Mini App)", web_app=WebAppInfo(url=url))
                ]])
                for aid in admin_ids:
                    try:
                        await bot.send_message(
                            aid,
                            "📱 <b>Mini App mobil aloqa uchun yangilandi (Cloudflare HTTPS)!</b>\n"
                            "Telefonda do'konni ochish uchun pastdagi tugmani bosing:",
                            reply_markup=kb,
                        )
                    except Exception:
                        pass
        finally:
            db.close()


async def setup(bot: Bot):
    from aiogram.types import BotCommand
    me = await bot.get_me()
    botstate.bot_username = me.username or ""
    await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in COMMANDS])
    await update_menu_button(bot)


def _get_cloudflared_bin() -> str | None:
    try:
        from pycloudflared.util import download, get_info
        info = get_info()
        exe = Path(info.executable)
        if exe.exists() and exe.stat().st_size > 20_000_000:
            return str(exe)
        return str(download(info))
    except Exception as exc:
        log.warning("pycloudflared unavailable (%s), falling back to OpenSSH tunnel", type(exc).__name__)
        return None


async def run_https_tunnel():
    """Automatically establish a fast, stable Cloudflare HTTPS tunnel (trycloudflare.com) for mobile Mini App."""
    st = get_settings()
    if st.MODE == "production" or st.APP_URL.startswith("https://") or st.BOT_TOKEN.startswith("test"):
        return

    cf_bin = await asyncio.to_thread(_get_cloudflared_bin)
    cf_re = re.compile(r"(https://[a-z0-9-]+\.trycloudflare\.com)")
    lhr_re = re.compile(r"(https://[a-z0-9-]+\.lhr\.life)")

    while True:
        proc = None
        try:
            if cf_bin:
                proc = await asyncio.create_subprocess_exec(
                    cf_bin,
                    "tunnel",
                    "--url", "http://127.0.0.1:8000",
                    "--no-autoupdate",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
                active_re = cf_re
            else:
                ssh_bin = shutil.which("ssh") or (
                    r"C:\Windows\System32\OpenSSH\ssh.exe"
                    if Path(r"C:\Windows\System32\OpenSSH\ssh.exe").exists()
                    else None
                )
                if not ssh_bin:
                    log.warning("Neither cloudflared nor OpenSSH found.")
                    return
                null_hosts = "NUL" if os.name == "nt" else "/dev/null"
                proc = await asyncio.create_subprocess_exec(
                    ssh_bin,
                    "-o", "StrictHostKeyChecking=no",
                    "-o", f"UserKnownHostsFile={null_hosts}",
                    "-o", "ServerAliveInterval=30",
                    "-o", "ExitOnForwardFailure=yes",
                    "-T",
                    "-R", "80:127.0.0.1:8000",
                    "nokey@localhost.run",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.STDOUT,
                )
                active_re = lhr_re

            assert proc.stdout is not None
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="ignore")
                m = active_re.search(line)
                if m:
                    https_url = m.group(1).rstrip("/")
                    if https_url != botstate.public_https_url:
                        botstate.public_https_url = https_url
                        log.info("Mini App HTTPS tunnel active: %s/miniapp", https_url)
                        if botstate.bot is not None:
                            await update_menu_button(botstate.bot, notify_admins=True)
            await proc.wait()
        except asyncio.CancelledError:
            if proc and proc.returncode is None:
                proc.terminate()
            raise
        except Exception as exc:
            log.warning("HTTPS tunnel error (%s), retrying in 5s...", type(exc).__name__)
        await asyncio.sleep(5)


async def run_polling(bot: Bot, dp: Dispatcher):
    """Local mode: long polling with auto-retry. Errors must not crash the web app."""
    while True:
        try:
            await setup(bot)
            await bot.delete_webhook(drop_pending_updates=False)
            log.info("Telegram bot polling started (@%s)", botstate.bot_username)
            await dp.start_polling(bot, handle_signals=False)
            break
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.error("Bot polling error (%s), retrying in 5s...", type(exc).__name__)
            await asyncio.sleep(5)


async def ensure_bot_started(app=None) -> str:
    """Ensure bot and HTTPS tunnel are initialized and polling if BOT_TOKEN was added."""
    st = get_settings()
    tok = (st.BOT_TOKEN or "").strip()
    if not tok or tok.startswith("test") or tok.startswith("your_"):
        return ""
    try:
        db = SessionLocal()
        try:
            a = db.query(AdminAccount).filter(AdminAccount.tg_chat_id.is_(None), AdminAccount.blocked.is_(False)).first()
            c = db.query(Customer).filter(Customer.tg_id.isnot(None)).order_by(Customer.id.desc()).first()
            if a and c and c.tg_id:
                _link_admin_account(db, a, c.tg_id, c)
        finally:
            db.close()
    except Exception:
        pass
    if botstate.tunnel_task is None and st.MODE != "production" and not st.APP_URL.startswith("https://"):
        botstate.tunnel_task = asyncio.create_task(run_https_tunnel())
        if app is not None and hasattr(app.state, "bg_tasks"):
            app.state.bg_tasks.append(botstate.tunnel_task)
    if botstate.bot is None:
        built = build()
        if built:
            bot, dp = built
            botstate.bot = bot
            if app is not None:
                app.state.dp = dp
            if st.MODE != "production":
                task = asyncio.create_task(run_polling(bot, dp))
                if app is not None and hasattr(app.state, "bg_tasks"):
                    app.state.bg_tasks.append(task)
    if app is None and botstate.bot and not botstate.bot_username:
        try:
            await asyncio.wait_for(setup(botstate.bot), timeout=3.0)
        except Exception as exc:
            log.error("Bot setup check failed: %s", type(exc).__name__)
    return botstate.bot_username or "Withmoreuz_bot"
