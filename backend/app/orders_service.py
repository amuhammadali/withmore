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


def status_text(customer: Customer, order: Order, db: Session | None = None) -> str:
    lang = customer.language if customer else "uz"
    code = html.escape(order.code)
    tracking = html.escape(order.tracking) if order.tracking else ""
    name = html.escape(customer.display_name if customer else order.name)
    brand_name = "WITHMORE"
    if db:
        brand_name = get_setting(db, "brand_name") or "WITHMORE"

    if lang == "ru":
        msgs = {
            "new": f"🆕 <b>Заказ принят!</b>\n\nЗдравствуйте, {name}. Ваш заказ <b>{code}</b> успешно зарегистрирован. Наш менеджер скоро свяжется с вами для подтверждения.",
            "awaiting_payment": f"💳 <b>Ожидание оплаты</b>\n\nПо заказу <b>{code}</b> ожидается подтверждение оплаты. Вы можете отправить чек об оплате администратору.",
            "paid": f"✅ <b>Заказ подтверждён и оплачен!</b>\n\nУважаемый(ая) {name}, оплата по заказу <b>{code}</b> успешно получена. Товар передан на склад для сборки.",
            "preparing": f"✂️ <b>Сборка и упаковка!</b>\n\nВаш заказ <b>{code}</b> собирается на складе, проходит контроль качества и упаковывается в фирменную коробку.",
            "ready_to_ship": f"📦 <b>Готов к отправке!</b>\n\nЗаказ <b>{code}</b> полностью упакован и ожидает передачи курьеру почты (BTS / EMU).",
            "ordered_china": f"✂️ <b>Сборка и подготовка!</b>\n\nВаш заказ <b>{code}</b> собирается и готовится к передаче в курьерскую службу.",
            "china_warehouse": f"📦 <b>Готов к отправке!</b>\n\nЗаказ <b>{code}</b> проверен и подготовлен к отправке.",
            "in_transit": f"🚚 <b>Заказ отправлен почтой (BTS / EMU)!</b>\n\nВаш заказ <b>{code}</b> передан в почтовую службу и уже в пути в ваш город." + (f"\n📦 Трек-номер: <code>{tracking}</code>" if tracking else ""),
            "in_uz": f"🏢 <b>Прибыл в пункт выдачи!</b>\n\nЗаказ <b>{code}</b> прибыл в филиал почты BTS / EMU в вашем городе. Вы можете получить посылку или ожидать курьера.\n📍 Адрес: {html.escape(order.city or '')}, {html.escape(order.address or '')}",
            "delivered": f"🎉 <b>Заказ доставлен!</b>\n\nУважаемый(ая) {name}, ваш заказ <b>{code}</b> успешно доставлен!\n\nСпасибо, что выбрали {html.escape(brand_name)}! Носите с удовольствием!",
            "cancelled": f"❌ <b>Заказ отменён</b>\n\nЗаказ <b>{code}</b> был отменён. По всем вопросам обращайтесь к администратору.",
        }
        return msgs.get(order.status, f"Заказ <b>{code}</b>: статус - <b>{STATUS_RU.get(order.status, order.status)}</b>")
    else:
        msgs = {
            "new": f"🆕 <b>Buyurtmangiz qabul qilindi!</b>\n\nAssalomu alaykum, {name}. <b>{code}</b> raqamli buyurtmangiz tizimda ro'yxatga olindi. Tez orada menejerimiz siz bilan bog'lanadi.",
            "awaiting_payment": f"💳 <b>To‘lov kutilmoqda</b>\n\n<b>{code}</b> raqamli buyurtmangiz uchun to'lov kutilmoqda. Click / Payme yoki karta orqali to'lov chekini yuborishingiz mumkin.",
            "paid": f"✅ <b>Buyurtma tasdiqlandi!</b>\n\nHurmatli {name}, <b>{code}</b> raqamli buyurtmangiz tasdiqlandi. Mahsulot omborga yig'ish va qadoqlashga topshirildi.",
            "preparing": f"✂️ <b>Ombordan yig'ilmoqda / Qadoqlanmoqda!</b>\n\n<b>{code}</b> raqamli buyurtmangiz ombordan saralanib, sifat nazoratidan o'tkazilmoqda va brend paketida qadoqlanmoqda.",
            "ready_to_ship": f"📦 <b>Jo'natishga tayyor!</b>\n\n<b>{code}</b> raqamli buyurtmangiz to'liq qadoqlandi va BTS / EMU pochta kuryeriga topshirilish navbatida turibdi.",
            "ordered_china": f"✂️ <b>Ombordan yig'ilmoqda!</b>\n\n<b>{code}</b> raqamli buyurtmangiz saralanib, jo'natishga tayyorlanmoqda.",
            "china_warehouse": f"📦 <b>Jo'natishga tayyor!</b>\n\n<b>{code}</b> raqamli buyurtmangiz qadoqlandi va jo'natilishga tayyor.",
            "in_transit": f"🚚 <b>Pochtada yo‘lga chiqdi (BTS / EMU)!</b>\n\n<b>{code}</b> raqamli buyurtmangiz pochta xizmatiga topshirildi va shahringiz tomon yo'l oldi." + (f"\n📦 Kuzatuv trek-kodi: <code>{tracking}</code>" if tracking else ""),
            "in_uz": f"🏢 <b>Pochta filialiga yetib keldi!</b>\n\n<b>{code}</b> raqamli posilka shahringizdagi BTS / EMU pochta filialiga yetib keldi. Filialdan olib ketishingiz yoki kuryer yetkazishini kutishingiz mumkin.\n📍 Manzil: {html.escape(order.city or '')}, {html.escape(order.address or '')}",
            "delivered": f"🎉 <b>Muvaffaqiyatli yetkazib berildi!</b>\n\nHurmatli {name}, <b>{code}</b> raqamli buyurtmangiz qabul qilindi!\n\n{html.escape(brand_name)} liboslarini tanlaganingiz uchun tashakkur! Liboslarimiz sizga uzoq vaqt chiroyli xizmat qilsin!",
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
        enqueue(db, "status", c.tg_id, status_text(c, order, db), order_id=None)
