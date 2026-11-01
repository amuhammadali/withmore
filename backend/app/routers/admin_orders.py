from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from ..core import audit, fmt_dt, get_setting
from ..db import get_db
from ..models import (STATUS_UZ, STATUSES, AdminAccount, Customer, Order, OrderMeta, Outbox, now)
from ..orders_service import active_order_admins, create_order, set_status
from ..outbox import enqueue, resend_admin_order
from ..security import require
from .shop import clean_phone

router = APIRouter(prefix="/api/admin", tags=["admin-orders"])
orders_perm = require("orders")
customers_perm = require("customers")


def order_row(o: Order) -> dict:
    a = o.meta.assigned_admin if o.meta else None
    return {"id": o.id, "code": o.code, "status": o.status, "name": o.name, "phone": o.phone,
            "tg_username": o.tg_username, "total": o.total, "created_at": fmt_dt(o.created_at),
            "admin": a.full_name if a else None, "notification": o.meta.notification_status if o.meta else "",
            "items_count": sum(i.qty for i in o.items)}


def order_detail(db: Session, o: Order) -> dict:
    m = o.meta
    msgs = db.query(Outbox).filter(Outbox.order_id == o.id, Outbox.kind.in_(["admin_order", "receipt"])) \
        .order_by(Outbox.id.desc()).limit(5).all()
    pct = float(get_setting(db, "advance_pct") or 30)
    return {**order_row(o), "city": o.city, "address": o.address, "comment": o.comment, "delivery": o.delivery,
            "subtotal": o.subtotal, "discount": o.discount, "promo_code": o.promo_code,
            "paid_amount": o.paid_amount, "advance_amount": int(round(o.total * pct / 100)),
            "receipt_photo": get_setting(db, f"receipt:{o.code}") or None,
            "tracking": o.tracking, "internal_note": o.internal_note,
            "customer_id": o.customer_id, "assigned_admin_id": m.assigned_admin_id,
            "source": m.source, "medium": m.medium, "campaign": m.campaign, "stock_reserved": m.stock_reserved,
            "items": [{"id": i.id, "product_id": i.product_id, "name": i.name, "size": i.size, "color": i.color,
                       "price": i.price, "qty": i.qty, "sale_type": i.sale_type} for i in o.items],
            "history": [{"status": h.status, "by": h.by, "at": fmt_dt(h.created_at)} for h in o.history],
            "messages": [{"id": r.id, "status": r.status, "attempts": r.attempts, "error": r.last_error,
                          "at": fmt_dt(r.created_at)} for r in msgs]}


def _load(db: Session, oid: int) -> Order:
    o = db.query(Order).options(selectinload(Order.items), selectinload(Order.history)).filter_by(id=oid).first()
    if not o:
        raise HTTPException(404, "Buyurtma topilmadi")
    return o


@router.get("/orders/admins")
def order_admins(admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    return [{"id": a.id, "full_name": a.full_name, "accepts_orders": a.accepts_orders, "blocked": a.blocked}
            for a in db.query(AdminAccount).order_by(AdminAccount.id)]


@router.get("/orders")
def orders(status: str = "", admin_id: int | None = None, date_from: str = "", date_to: str = "", q: str = "",
           page: int = 1, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    query = db.query(Order).join(OrderMeta, OrderMeta.order_id == Order.id)
    if status:
        query = query.filter(Order.status == status)
    if admin_id:
        query = query.filter(OrderMeta.assigned_admin_id == admin_id)
    try:
        if date_from:
            query = query.filter(Order.created_at >= datetime.fromisoformat(date_from))
        if date_to:
            query = query.filter(Order.created_at < datetime.fromisoformat(date_to) + timedelta(days=1))
    except ValueError:
        raise HTTPException(422, "Sana noto'g'ri")
    if q.strip():
        like = f"%{q.strip().lstrip('@')}%"
        query = query.filter(or_(Order.code.ilike(like), Order.name.ilike(like), Order.phone.ilike(like),
                                 Order.tg_username.ilike(like)))
    total = query.count()
    rows = query.options(selectinload(Order.items), selectinload(Order.meta)).order_by(Order.id.desc()) \
        .offset((max(page, 1) - 1) * 30).limit(30).all()
    return {"total": total, "items": [order_row(o) for o in rows]}


@router.get("/orders/{oid}")
def order_get(oid: int, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    return order_detail(db, _load(db, oid))


class OrderPatch(BaseModel):
    status: str | None = None
    tracking: str | None = Field(default=None, max_length=120)
    internal_note: str | None = Field(default=None, max_length=4000)
    assigned_admin_id: int | None = None
    paid_amount: int | None = Field(default=None, ge=0)


@router.patch("/orders/{oid}")
def order_patch(oid: int, body: OrderPatch, admin: AdminAccount = Depends(orders_perm),
                db: Session = Depends(get_db)):
    o = _load(db, oid)
    changes = []
    if body.status and body.status != o.status:
        set_status(db, o, body.status, admin.full_name)
        changes.append(f"status={body.status}")
    if body.tracking is not None and body.tracking != o.tracking:
        o.tracking = body.tracking.strip()
        changes.append("tracking")
    if body.internal_note is not None:
        o.internal_note = body.internal_note
    if body.paid_amount is not None and body.paid_amount != o.paid_amount:
        o.paid_amount = body.paid_amount
        changes.append(f"paid={body.paid_amount}")
    if body.assigned_admin_id and body.assigned_admin_id != o.meta.assigned_admin_id:
        a = db.get(AdminAccount, body.assigned_admin_id)
        if not a or a.blocked:
            raise HTTPException(422, "Admin topilmadi")
        o.meta.assigned_admin_id = a.id
        resend_admin_order(db, o, a.tg_chat_id)
        changes.append(f"assigned={a.full_name}")
    if changes:
        audit(db, admin, "order_update", "order", o.id, f"{o.code}: {', '.join(changes)}")
    db.commit()
    return order_detail(db, _load(db, oid))


@router.post("/orders/{oid}/resend")
def order_resend(oid: int, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    o = _load(db, oid)
    a = o.meta.assigned_admin
    if (not a or not a.tg_chat_id) and admin.tg_chat_id:
        o.meta.assigned_admin_id = admin.id
        a = admin
    if not a or not a.tg_chat_id:
        fallback = db.query(AdminAccount).filter(
            AdminAccount.tg_chat_id.isnot(None),
            AdminAccount.blocked.is_(False)
        ).first()
        if fallback:
            o.meta.assigned_admin_id = fallback.id
            a = fallback
    if not a or not a.tg_chat_id:
        raise HTTPException(409, "Admin Telegram bilan ulanmagan")
    resend_admin_order(db, o, a.tg_chat_id)
    audit(db, admin, "order_resend", "order", o.id, o.code)
    db.commit()
    return order_detail(db, _load(db, oid))


class ManualItem(BaseModel):
    variant_id: int
    qty: int = Field(ge=1, le=20)


class ManualOrder(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str
    tg_username: str = ""
    city: str = ""
    address: str = ""
    comment: str = ""
    delivery: str = "courier"
    promo_code: str = ""
    assigned_admin_id: int | None = None
    items: list[ManualItem]


@router.post("/orders", status_code=201)
def order_manual(body: ManualOrder, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    import secrets
    phone = clean_phone(body.phone)
    c = db.query(Customer).filter_by(phone=phone).first()
    if not c:
        c = Customer(first_name=body.name.strip(), phone=phone, username=body.tg_username.lstrip("@"))
        db.add(c)
        db.flush()
    o, _ = create_order(db, customer=c, name=body.name, phone=phone, tg_username=body.tg_username,
                        city=body.city, address=body.address, comment=body.comment, delivery=body.delivery,
                        items=[i.model_dump() for i in body.items], promo_code=body.promo_code,
                        idem_key="admin:" + secrets.token_hex(12), source="admin",
                        assign_admin_id=body.assigned_admin_id)
    audit(db, admin, "order_manual", "order", o.id, o.code)
    db.commit()
    return order_detail(db, _load(db, o.id))


# ---------------- customers ----------------
def customer_row(db: Session, c: Customer) -> dict:
    cnt, spent = db.query(func.count(Order.id), func.coalesce(func.sum(Order.total), 0)) \
        .filter(Order.customer_id == c.id, Order.status != "cancelled").one()
    return {"id": c.id, "name": c.display_name, "phone": c.phone, "username": c.username, "tg_id": c.tg_id,
            "language": c.language, "orders": cnt, "total_spent": int(spent), "last_seen": fmt_dt(c.last_seen),
            "created_at": fmt_dt(c.created_at)}


@router.get("/customers")
def customers(q: str = "", page: int = 1, admin: AdminAccount = Depends(customers_perm),
              db: Session = Depends(get_db)):
    query = db.query(Customer)
    if q.strip():
        like = f"%{q.strip().lstrip('@')}%"
        query = query.filter(or_(Customer.first_name.ilike(like), Customer.last_name.ilike(like),
                                 Customer.phone.ilike(like), Customer.username.ilike(like)))
    total = query.count()
    rows = query.order_by(Customer.id.desc()).offset((max(page, 1) - 1) * 30).limit(30).all()
    return {"total": total, "items": [customer_row(db, c) for c in rows]}


@router.get("/customers/{cid}")
def customer_get(cid: int, admin: AdminAccount = Depends(customers_perm), db: Session = Depends(get_db)):
    c = db.get(Customer, cid)
    if not c:
        raise HTTPException(404, "Mijoz topilmadi")
    ords = db.query(Order).options(selectinload(Order.items), selectinload(Order.meta)) \
        .filter_by(customer_id=cid).order_by(Order.id.desc()).limit(100).all()
    return {**customer_row(db, c), "order_list": [order_row(o) for o in ords]}


@router.post("/customers/{cid}/message")
def customer_message(cid: int, body: dict, admin: AdminAccount = Depends(customers_perm),
                     db: Session = Depends(get_db)):
    import html
    c = db.get(Customer, cid)
    if not c:
        raise HTTPException(404, "Mijoz topilmadi")
    text = str(body.get("text", "")).strip()
    if not text:
        raise HTTPException(422, "Xabar matni bo'sh")
    if not c.tg_id:
        raise HTTPException(409, "Mijoz Telegram orqali kirmagan")
    enqueue(db, "direct", c.tg_id, html.escape(text[:3500]))
    audit(db, admin, "customer_message", "customer", c.id)
    db.commit()
    return {"ok": True}
