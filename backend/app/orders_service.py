"""Order creation (idempotent, atomic stock reservation), status changes, round-robin assignment."""
import html
import secrets
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .config import get_settings
from .core import get_setting, set_setting
from .models import (STATUS_RU, STATUS_UZ, STATUSES, AdminAccount, Customer, Order, OrderItem, OrderMeta,
                     OrderStatusHistory, Product, ProductVariant, Promocode, now)
from .outbox import enqueue

CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def new_code(db: Session) -> str:
    while True:
        code = "WM" + "".join(secrets.choice(CODE_ALPHABET) for _ in range(10))
        if not db.query(Order.id).filter_by(code=code).first():
            return code


def fmt_money(n: int) -> str:
    return f"{n:,}".replace(",", " ") + " so'm"


def active_order_admins(db: Session) -> list[AdminAccount]:
    return db.query(AdminAccount).filter(AdminAccount.blocked.is_(False), AdminAccount.accepts_orders.is_(True)) \
        .order_by(AdminAccount.id).all()


def pick_round_robin(db: Session) -> AdminAccount | None:
    admins = active_order_admins(db)
    if not admins:
        return None
    last = int(get_setting(db, "rr_last") or 0)
    nxt = next((a for a in admins if a.id > last), admins[0])
    set_setting(db, "rr_last", str(nxt.id))
    return nxt


def check_promo(db: Session, code: str) -> Promocode | None:
    if not code:
        return None
    p = db.query(Promocode).filter(Promocode.code == code.strip().upper()).first()
    if (not p or not p.active or (p.expires_at and p.expires_at < now())
            or (p.usage_limit and p.used_count >= p.usage_limit)):
        raise HTTPException(422, "Promokod yaroqsiz")
    return p


def admin_order_text(order: Order) -> str:
    e = html.escape
    lines = [f"<b>Yangi buyurtma {order.code}</b>", f"{e(order.name)} | {e(order.phone or '-')}"]
    if order.tg_username:
        lines.append(f"@{e(order.tg_username)}")
    lines.append("")
    for it in order.items:
        lines.append(f"{e(it.name)} ({e(it.size)} {e(it.color)}) x{it.qty} - {fmt_money(it.price * it.qty)}")
    lines += ["", f"Jami: <b>{fmt_money(order.total)}</b>",
              "Yetkazish: 📮 Pochta orqali (BTS / EMU)"]
    if order.city or order.address:
        lines.append(f"📍 Manzil/Pochta: {e(order.city)}, {e(order.address)}")
    if order.comment:
        lines.append(f"Izoh: {e(order.comment)}")
    return "\n".join(lines)


def customer_summary_text(order: Order) -> str:
    """Plain-text message pre-filled when the customer contacts an admin."""
    lines = [f"Salom! Buyurtma {order.code}"]
    for it in order.items:
        lines.append(f"- {it.name} ({it.size} {it.color}) x{it.qty}")
    lines.append(f"Jami: {fmt_money(order.total)}")
    return "\n".join(lines)


def create_order(db: Session, *, customer: Customer, name: str, phone: str, tg_username: str = "",
                 city: str = "", address: str = "", comment: str = "", delivery: str = "courier",
                 items: list[dict], promo_code: str = "", idem_key: str, source: str = "",
                 medium: str = "", campaign: str = "", assign_admin_id: int | None = None) -> tuple[Order, bool]:
    """Returns (order, created). Same idempotency key -> same order, created=False."""
    existing = db.query(OrderMeta).filter_by(idempotency_key=idem_key).first()
    if existing:
        return existing.order, False
    if delivery in ("post", "pochta"):
        delivery = "courier"
    if delivery not in ("courier", "pickup"):
        raise HTTPException(422, "Yetkazish turi noto'g'ri")
    if not items:
        raise HTTPException(422, "Savat bo'sh")
    merged: dict[int, int] = {}
    for it in items:
        q = int(it["qty"])
        if q < 1 or q > 20:
            raise HTTPException(422, "Miqdor noto'g'ri")
        merged[int(it["variant_id"])] = merged.get(int(it["variant_id"]), 0) + q

    promo = check_promo(db, promo_code)
    order = Order(code=new_code(db), customer_id=customer.id, name=name.strip(), phone=phone.strip(),
                  tg_username=(tg_username or customer.username or "").lstrip("@"), city=city.strip(),
                  address=address.strip(), comment=comment.strip(), delivery=delivery, discount=0, paid_amount=0)
    meta = OrderMeta(idempotency_key=idem_key, source=source[:64], medium=medium[:64], campaign=campaign[:64])
    order.meta = meta
    low_alerts = []
    try:
        subtotal = 0
        for vid, qty in merged.items():
            v = db.get(ProductVariant, vid)
            p: Product | None = v.product if v else None
            if not v or not p or not p.active or p.draft or p.deleted_at:
                raise HTTPException(409, "Mahsulot mavjud emas")
            item = OrderItem(product_id=p.id, variant_id=v.id, name=p.name_uz, size=v.size, color=v.color,
                             price=p.price_uzs, qty=qty, sale_type=p.sale_type)
            if p.sale_type == "stock":
                res = db.execute(update(ProductVariant)
                                 .where(ProductVariant.id == vid, ProductVariant.stock >= qty)
                                 .values(stock=ProductVariant.stock - qty))
                if res.rowcount != 1:
                    raise HTTPException(409, f"Omborda yetarli emas: {p.name_uz} ({v.size})")
                item.reserved = True
                meta.stock_reserved = True
                db.refresh(v)
                low_alerts.append((p, v))
            order.items.append(item)
            subtotal += item.price * qty
        order.subtotal = subtotal
        if promo:
            if promo.usage_limit:
                res = db.execute(update(Promocode).where(Promocode.id == promo.id, Promocode.used_count < promo.usage_limit)
                                 .values(used_count=Promocode.used_count + 1))
                if res.rowcount != 1:
                    raise HTTPException(422, "Promokod limiti tugagan")
            else:
                promo.used_count += 1
            order.discount = subtotal * promo.percent // 100
            order.promo_code = promo.code
        order.total = subtotal - order.discount
        admin = db.get(AdminAccount, assign_admin_id) if assign_admin_id else pick_round_robin(db)
        meta.assigned_admin_id = admin.id if admin else None
        order.history.append(OrderStatusHistory(status="new", by="mijoz" if not assign_admin_id else "admin"))
        db.add(order)
        db.flush()
        _queue_admin_notifications(db, order, admin, low_alerts)
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.query(OrderMeta).filter_by(idempotency_key=idem_key).first()
        if existing:
            return existing.order, False
        raise
    except Exception:
        db.rollback()
        raise
    return order, True


def _queue_admin_notifications(db: Session, order: Order, admin: AdminAccount | None, low_alerts):
    meta = order.meta
    base = get_settings().APP_URL.rstrip("/")
    if get_setting(db, "notify_admin_order") != "1":
        meta.notification_status = "disabled"
    elif not admin or not admin.tg_chat_id:
        meta.notification_status = "no_telegram"
    else:
        enqueue(db, "admin_order", admin.tg_chat_id, admin_order_text(order), button_text="Buyurtmani ochish",
                button_url=f"{base}/admin/orders/{order.id}", order_id=order.id)
    if get_setting(db, "notify_admin_lowstock") == "1":
        threshold = int(float(get_setting(db, "low_stock") or 3))
        targets = [a for a in db.query(AdminAccount).filter(AdminAccount.blocked.is_(False)).all()
                   if a.tg_chat_id and (a.role == "owner" or "products" in (a.permissions or []))]
        for p, v in low_alerts:
            if v.stock <= threshold:
                text = f"<b>Kam qoldi:</b> {html.escape(p.name_uz)} ({html.escape(v.size)} {html.escape(v.color)}) - {v.stock} dona"
                for a in targets:
                    enqueue(db, "low_stock", a.tg_chat_id, text)


def release_stock(db: Session, order: Order):
    for it in order.items:
        if it.reserved and it.variant_id:
            db.execute(update(ProductVariant).where(ProductVariant.id == it.variant_id)
                       .values(stock=ProductVariant.stock + it.qty))
            it.reserved = False
    order.meta.stock_reserved = False


def status_text(customer: Customer, order: Order) -> str:
    lang = customer.language if customer else "uz"
    code = html.escape(order.code)
    tracking = html.escape(order.tracking) if order.tracking else ""
    name = html.escape(customer.display_name if customer else order.name)

    if lang == "ru":
        msgs = {
            "new": f"🆕 <b>Заказ принят!</b>\n\nЗдравствуйте, {name}. Ваш заказ <b>{code}</b> успешно зарегистрирован. Мы свяжемся с вами для подтверждения.",
            "awaiting_payment": f"💳 <b>Ожидание оплаты / Аванса</b>\n\nПо заказу <b>{code}</b> ожидается оплата аванса. Свяжитесь с администратором или отправьте чек.",
            "paid": f"✅ <b>Оплата подтверждена!</b>\n\nУважаемый(ая) {name}, оплата по заказу <b>{code}</b> успешно получена. Заказ отправлен на закупку поставщику.",
            "ordered_china": f"🇨🇳 <b>Выкуплен в Китае!</b>\n\nВаш заказ <b>{code}</b> успешно выкуплен и направлен на карго-склад в Китае.",
            "china_warehouse": f"📦 <b>Принят на складе в Китае!</b>\n\nТовары по заказу <b>{code}</b> проверены и упакованы для международной отправки.",
            "in_transit": f"✈️ <b>Заказ в пути!</b>\n\nВаш заказ <b>{code}</b> отправлен карго-рейсом в Узбекистан. Ожидаемый срок прибытия: 5-8 дней.",
            "in_uz": f"🏢 <b>Прибыл в Ташкент!</b>\n\nЗаказ <b>{code}</b> поступил на главный склад в Ташкенте и готовится к передаче в почтовую службу (BTS / EMU).",
            "delivered": f"📮 <b>Отправлен почтой!</b>\n\nУважаемый(ая) {name}, ваш заказ <b>{code}</b> передан в почтовую службу (BTS / EMU).\n" + (f"📦 Трек-номер: <code>{tracking}</code>\n" if tracking else "") + f"📍 Адрес выдачи: {html.escape(order.city)}, {html.escape(order.address)}\n\nСпасибо за выбор WHITMORE!",
            "cancelled": f"❌ <b>Заказ отменён</b>\n\nЗаказ <b>{code}</b> был отменён. Если у вас возникли вопросы, обратитесь к администратору.",
        }
        return msgs.get(order.status, f"Заказ <b>{code}</b>: статус - <b>{STATUS_RU.get(order.status, order.status)}</b>")
    else:
        msgs = {
            "new": f"🆕 <b>Buyurtmangiz qabul qilindi!</b>\n\nAssalomu alaykum, {name}. <b>{code}</b> raqamli buyurtmangiz tizimda ro'yxatga olindi. Tez orada menejerimiz siz bilan bog'lanadi.",
            "awaiting_payment": f"💳 <b>To‘lov kutilmoqda</b>\n\n<b>{code}</b> raqamli buyurtmangiz uchun avans to‘lovi kutilmoqda. Menejer bergan rekvizitlar orqali to‘lov qilishingiz mumkin.",
            "paid": f"✅ <b>To‘lov tasdiqlandi!</b>\n\nHurmatli {name}, <b>{code}</b> raqamli buyurtmangiz uchun to‘lov qabul qilindi. Mahsulot zudlik bilan xaridga yo‘naltirildi.",
            "ordered_china": f"🇨🇳 <b>Xitoyda sotib olindi!</b>\n\n<b>{code}</b> raqamli buyurtmangiz yetkazib beruvchidan xarid qilindi va Xitoydagi kargo omboriga yo‘l oldi.",
            "china_warehouse": f"📦 <b>Xitoy omborida qabul qilindi!</b>\n\n<b>{code}</b> buyurtmangiz tekshirildi, qadoqlandi va O‘zbekistonga jo‘natishga tayyorlandi.",
            "in_transit": f"✈️ <b>Buyurtmangiz yo‘lga chiqdi!</b>\n\n<b>{code}</b> raqamli posilka xalqaro kargo reysi orqali O‘zbekistonga parvoz qilmoqda (5-8 kun).",
            "in_uz": f"🏢 <b>Toshkent omboriga yetib keldi!</b>\n\n<b>{code}</b> buyurtmangiz Toshkentdagi bosh omborimizga yetib keldi. Saralanib, BTS / EMU pochtasiga topshirilmoqda.",
            "delivered": f"📮 <b>Pochtaga topshirildi!</b>\n\nHurmatli {name}, <b>{code}</b> raqamli buyurtmangiz BTS / EMU pochta filialiga topshirildi!\n" + (f"📦 Kuzatuv trek-kodi: <code>{tracking}</code>\n" if tracking else "") + f"📍 Manzil: {html.escape(order.city)}, {html.escape(order.address)}\n\nPochta punktidan posilkani olib ketishingiz mumkin. WHITMORE kiyimlari sizga uzoq xizmat qilsin!",
            "cancelled": f"❌ <b>Buyurtma bekor qilindi</b>\n\n<b>{code}</b> raqamli buyurtmangiz bekor qilindi. Savollaringiz bo‘lsa, adminga murojaat qilishingiz mumkin.",
        }
        return msgs.get(order.status, f"Buyurtma <b>{code}</b>: holati - <b>{STATUS_UZ.get(order.status, order.status)}</b>")


def set_status(db: Session, order: Order, status: str, by: str):
    if status not in STATUSES:
        raise HTTPException(422, "Holat noto'g'ri")
    if status == order.status:
        return
    if order.status == "cancelled":
        raise HTTPException(409, "Bekor qilingan buyurtma holatini o'zgartirib bo'lmaydi")
    if status == "cancelled":
        release_stock(db, order)
    if status == "paid" and not order.paid_amount:
        pct = float(get_setting(db, "advance_pct") or 30)
        order.paid_amount = int(order.total * pct / 100)
    order.status = status
    order.history.append(OrderStatusHistory(status=status, by=by))
    c = order.customer
    if get_setting(db, "notify_customer_status") != "0" and c and c.tg_id:
        enqueue(db, "status", c.tg_id, status_text(c, order), order_id=None)
