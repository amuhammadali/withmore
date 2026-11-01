from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from ..core import audit, fmt_dt, process_upload
from ..db import get_db
from ..models import (AdminAccount, AdminAudit, Customer, MarketingVisit, Order, OrderItem, OrderMeta,
                      Outbox, Product, Promocode, StoreEvent, now)
from ..outbox import enqueue
from ..security import require, require_owner

router = APIRouter(prefix="/api/admin", tags=["admin-stats"])
stats_perm = require("statistics")
promo_perm = require("promotions")


def _since(days: int) -> datetime:
    if days not in (7, 30, 90, 365):
        raise HTTPException(422, "Davr noto'g'ri")
    return datetime.combine((now() - timedelta(days=days - 1)).date(), datetime.min.time())


def _count_events(db, etype: str, since, distinct=False):
    col = func.count(func.distinct(StoreEvent.customer_id)) if distinct else func.count(StoreEvent.id)
    return db.query(col).filter(StoreEvent.type == etype, StoreEvent.created_at >= since).scalar() or 0


@router.get("/dashboard")
def dashboard(days: int = 30, admin: AdminAccount = Depends(stats_perm), db: Session = Depends(get_db)):
    since = _since(days)
    orders_q = db.query(Order).filter(Order.created_at >= since)
    n_orders = orders_q.count()
    live = orders_q.filter(Order.status != "cancelled")
    ordered_amount = live.with_entities(func.coalesce(func.sum(Order.total), 0)).scalar()
    paid_amount = live.with_entities(func.coalesce(func.sum(Order.paid_amount), 0)).scalar()
    delivered = orders_q.filter(Order.status == "delivered").count()
    cancelled = orders_q.filter(Order.status == "cancelled").count()
    new_customers = db.query(func.count(Customer.id)).filter(Customer.created_at >= since).scalar()
    visits = _count_events(db, "app_open", since)
    views = _count_events(db, "product_view", since)
    contacts = _count_events(db, "contact_click", since)

    # daily series
    def by_day(rows):
        return {str(d): n for d, n in rows}
    day_orders = by_day(db.query(func.date(Order.created_at), func.count(Order.id))
                        .filter(Order.created_at >= since).group_by(func.date(Order.created_at)))
    day_visits = by_day(db.query(func.date(StoreEvent.created_at), func.count(StoreEvent.id))
                        .filter(StoreEvent.type == "app_open", StoreEvent.created_at >= since)
                        .group_by(func.date(StoreEvent.created_at)))
    series = []
    d = since.date()
    while d <= now().date():
        k = d.isoformat()
        series.append({"date": k, "orders": day_orders.get(k, 0), "visits": day_visits.get(k, 0)})
        d += timedelta(days=1)

    funnel = [{"key": "viewed", "value": _count_events(db, "product_view", since, True)},
              {"key": "cart", "value": _count_events(db, "add_to_cart", since, True)},
              {"key": "contact", "value": _count_events(db, "contact_click", since, True)},
              {"key": "order", "value": db.query(func.count(func.distinct(Order.customer_id)))
               .filter(Order.created_at >= since).scalar() or 0}]

    top = db.query(OrderItem.product_id, func.max(OrderItem.name), func.sum(OrderItem.qty),
                   func.sum(OrderItem.qty * OrderItem.price)) \
        .join(Order, Order.id == OrderItem.order_id) \
        .filter(Order.created_at >= since, Order.status != "cancelled") \
        .group_by(OrderItem.product_id).order_by(func.sum(OrderItem.qty).desc()).limit(10).all()

    latest = db.query(Order).options(selectinload(Order.items), selectinload(Order.meta)) \
        .order_by(Order.id.desc()).limit(8).all()
    from .admin_orders import order_row
    awaiting = db.query(Order).options(selectinload(Order.items), selectinload(Order.meta)) \
        .filter(Order.status == "awaiting_payment").order_by(Order.id).limit(10).all()
    failed_msgs = db.query(func.count(Outbox.id)).filter(Outbox.status == "failed").scalar()
    failed_orders = db.query(Order).options(selectinload(Order.items), selectinload(Order.meta)) \
        .join(OrderMeta, OrderMeta.order_id == Order.id).filter(OrderMeta.notification_status == "failed") \
        .limit(10).all()
    return {
        "cards": {"orders": n_orders, "ordered_amount": int(ordered_amount), "paid_amount": int(paid_amount),
                  "delivered": delivered, "cancelled": cancelled, "customers": new_customers, "visits": visits,
                  "views": views, "contacts": contacts,
                  "conversion": round(n_orders * 100 / visits, 1) if visits else 0},
        "series": series, "funnel": funnel,
        "top_products": [{"product_id": pid, "name": name, "qty": int(q), "amount": int(a)} for pid, name, q, a in top],
        "latest_orders": [order_row(o) for o in latest],
        "attention": {"awaiting_payment": [order_row(o) for o in awaiting], "failed_messages": failed_msgs,
                      "failed_orders": [order_row(o) for o in failed_orders]},
    }


@router.get("/marketing")
def marketing(days: int = 30, admin: AdminAccount = Depends(stats_perm), db: Session = Depends(get_db)):
    since = _since(days)
    rows: dict[tuple, dict] = {}

    def row(s, m, c):
        return rows.setdefault((s or "direct", m or "", c or ""), {"source": s or "direct", "medium": m or "",
                                                                    "campaign": c or "", "visits": 0, "orders": 0,
                                                                    "amount": 0})
    for s, m, c, n in db.query(MarketingVisit.source, MarketingVisit.medium, MarketingVisit.campaign,
                               func.count(MarketingVisit.id)).filter(MarketingVisit.created_at >= since) \
            .group_by(MarketingVisit.source, MarketingVisit.medium, MarketingVisit.campaign):
        row(s, m, c)["visits"] += n
    for s, m, c, n, amt in db.query(OrderMeta.source, OrderMeta.medium, OrderMeta.campaign, func.count(Order.id),
                                    func.coalesce(func.sum(Order.total), 0)).join(Order, Order.id == OrderMeta.order_id) \
            .filter(Order.created_at >= since, Order.status != "cancelled") \
            .group_by(OrderMeta.source, OrderMeta.medium, OrderMeta.campaign):
        r = row(s, m, c)
        r["orders"] += n
        r["amount"] += int(amt)
    return sorted(rows.values(), key=lambda r: -r["visits"])


@router.get("/audit")
def audit_list(q: str = "", page: int = 1, owner: AdminAccount = Depends(require_owner),
               db: Session = Depends(get_db)):
    query = db.query(AdminAudit)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(AdminAudit.admin_name.ilike(like), AdminAudit.action.ilike(like),
                                 AdminAudit.entity.ilike(like), AdminAudit.detail.ilike(like)))
    total = query.count()
    rows = query.order_by(AdminAudit.id.desc()).offset((max(page, 1) - 1) * 50).limit(50).all()
    return {"total": total, "items": [{"id": r.id, "admin": r.admin_name, "action": r.action, "entity": r.entity,
                                       "entity_id": r.entity_id, "detail": r.detail,
                                       "at": fmt_dt(r.created_at)} for r in rows]}


# ---------------- promocodes ----------------
class PromoIn(BaseModel):
    code: str = Field(min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_-]+$")
    percent: int = Field(ge=1, le=90)
    expires_at: str | None = None
    usage_limit: int = Field(default=0, ge=0)
    active: bool = True


def promo_out(p: Promocode) -> dict:
    return {"id": p.id, "code": p.code, "percent": p.percent, "expires_at": fmt_dt(p.expires_at),
            "usage_limit": p.usage_limit, "used_count": p.used_count, "active": p.active}


def _exp(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "")[:19])
    except ValueError:
        raise HTTPException(422, "Sana noto'g'ri")


@router.get("/promocodes")
def promos(admin: AdminAccount = Depends(promo_perm), db: Session = Depends(get_db)):
    return [promo_out(p) for p in db.query(Promocode).order_by(Promocode.id.desc())]


@router.post("/promocodes", status_code=201)
def promo_add(body: PromoIn, admin: AdminAccount = Depends(promo_perm), db: Session = Depends(get_db)):
    code = body.code.upper()
    if db.query(Promocode).filter_by(code=code).first():
        raise HTTPException(409, "Bunday promokod mavjud")
    p = Promocode(code=code, percent=body.percent, expires_at=_exp(body.expires_at),
                  usage_limit=body.usage_limit, active=body.active)
    db.add(p)
    db.flush()
    audit(db, admin, "promo_add", "promocode", p.id, code)
    db.commit()
    return promo_out(p)


@router.patch("/promocodes/{pid}")
def promo_edit(pid: int, body: PromoIn, admin: AdminAccount = Depends(promo_perm), db: Session = Depends(get_db)):
    p = db.get(Promocode, pid)
    if not p:
        raise HTTPException(404, "Topilmadi")
    p.code, p.percent, p.expires_at = body.code.upper(), body.percent, _exp(body.expires_at)
    p.usage_limit, p.active = body.usage_limit, body.active
    audit(db, admin, "promo_edit", "promocode", p.id, p.code)
    db.commit()
    return promo_out(p)


@router.delete("/promocodes/{pid}")
def promo_del(pid: int, admin: AdminAccount = Depends(promo_perm), db: Session = Depends(get_db)):
    p = db.get(Promocode, pid)
    if not p:
        raise HTTPException(404, "Topilmadi")
    audit(db, admin, "promo_delete", "promocode", p.id, p.code)
    db.delete(p)
    db.commit()
    return {"ok": True}


# ---------------- broadcast ----------------
@router.post("/broadcast")
async def broadcast(text: str = Form(...), photo: UploadFile | None = File(None),
                    admin: AdminAccount = Depends(promo_perm), db: Session = Depends(get_db)):
    import html
    text = text.strip()
    if not text:
        raise HTTPException(422, "Xabar matni bo'sh")
    path = ""
    if photo and photo.filename:
        up = await process_upload(photo, db, admin.id, subdir="broadcast")
        path = up.path
    n = 0
    for (tg_id,) in db.query(Customer.tg_id).filter(Customer.tg_id.is_not(None)):
        enqueue(db, "broadcast", tg_id, html.escape(text[:3500]), photo=path)  # worker throttles ~20/s
        n += 1
    audit(db, admin, "broadcast", "broadcast", "", f"{n} recipients")
    db.commit()
    return {"queued": n}


@router.get("/broadcast/status")
def broadcast_status(admin: AdminAccount = Depends(promo_perm), db: Session = Depends(get_db)):
    out = {"pending": 0, "sent": 0, "failed": 0}
    for st, n in db.query(Outbox.status, func.count(Outbox.id)).filter(Outbox.kind == "broadcast").group_by(Outbox.status):
        out[st] = n
    return out


# ---------------- backup & export ----------------
def _build_orders_csv(db: Session) -> str:
    import csv
    import io
    from ..models import STATUS_UZ
    buf = io.StringIO()
    buf.write("\ufeff")  # UTF-8 BOM for Excel
    w = csv.writer(buf)
    w.writerow(["Kod", "Holat", "Mijoz", "Telefon", "Telegram", "Shahar", "Manzil", "Yetkazish",
                "Jami (so'm)", "To'langan (so'm)", "Trek-kod", "Sana"])
    for o in db.query(Order).order_by(Order.id.desc()).limit(5000).all():
        w.writerow([o.code, STATUS_UZ.get(o.status, o.status), o.name, o.phone,
                    f"@{o.tg_username}" if o.tg_username else "", o.city, o.address,
                    "Kuryer" if o.delivery == "courier" else "Olib ketish",
                    o.total, o.paid_amount, o.tracking, fmt_dt(o.created_at) or ""])
    return buf.getvalue()


@router.get("/backup/orders.csv")
def export_orders_csv(admin: AdminAccount = Depends(stats_perm), db: Session = Depends(get_db)):
    from fastapi.responses import Response
    csv_text = _build_orders_csv(db)
    audit(db, admin, "backup_export_csv", "orders")
    db.commit()
    return Response(
        content=csv_text.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="whitmore-orders.csv"'},
    )


@router.post("/backup/telegram")
async def send_backup_telegram(admin: AdminAccount = Depends(stats_perm), db: Session = Depends(get_db)):
    from pathlib import Path
    from .. import botstate
    from ..config import get_settings
    target_chat = admin.tg_chat_id
    if not target_chat:
        fallback = db.query(AdminAccount).filter(
            AdminAccount.tg_chat_id.isnot(None), AdminAccount.blocked.is_(False)
        ).first()
        if fallback:
            target_chat = fallback.tg_chat_id
    if not target_chat:
        raise HTTPException(409, "Avval Admin panelda Telegram hisobingizni ulang")
    if not botstate.bot:
        raise HTTPException(503, "Telegram bot ulanmagan")

    from aiogram.types import BufferedInputFile, FSInputFile
    csv_bytes = _build_orders_csv(db).encode("utf-8")
    n_orders = db.query(func.count(Order.id)).scalar() or 0
    n_cust = db.query(func.count(Customer.id)).scalar() or 0
    n_prod = db.query(func.count(Product.id)).filter(Product.deleted_at.is_(None)).scalar() or 0
    caption = (
        f"💾 <b>WHITMORE — Zaxira nusxasi (Backup)</b>\n\n"
        f"• Buyurtmalar: <b>{n_orders} ta</b>\n"
        f"• Mijozlar: <b>{n_cust} ta</b>\n"
        f"• Mahsulotlar: <b>{n_prod} ta</b>\n"
        f"• Vaqt: <code>{now().strftime('%Y-%m-%d %H:%M UTC')}</code>"
    )
    await botstate.bot.send_document(
        target_chat,
        BufferedInputFile(csv_bytes, filename=f"whitmore-orders-{now().strftime('%Y%m%d')}.csv"),
        caption=caption,
    )
    st = get_settings()
    if st.DATABASE_URL.startswith("sqlite:///"):
        db_path = Path(st.DATABASE_URL.replace("sqlite:///", "", 1))
        if db_path.exists():
            await botstate.bot.send_document(
                target_chat,
                FSInputFile(db_path, filename=f"whitmore-backup-{now().strftime('%Y%m%d')}.db"),
                caption="🗄 SQLite ma'lumotlar bazasi to'liq fayli (.db)",
            )
    audit(db, admin, "backup_telegram", "system")
    db.commit()
    return {"ok": True}
