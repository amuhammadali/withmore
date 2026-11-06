"""Admin CRM: Kanban pipeline, customer 360 dossiers, sartorial measurements & tasks."""
import json
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from ..core import audit, fmt_dt, get_setting, set_setting, thumb_of
from ..db import get_db
from ..models import (
    FittingAppointment,
    STATUS_RU,
    STATUS_UZ,
    STATUSES,
    AdminAccount,
    Customer,
    Order,
    OrderItem,
    Product,
    now,
)
from ..orders_service import fmt_money, set_status
from ..security import require

router = APIRouter(prefix="/api/admin/crm", tags=["admin-crm"])
orders_perm = require("orders")
customers_perm = require("customers")

KANBAN_STAGES = [
    {"id": "new", "title_uz": "Yangi buyurtma", "title_ru": "Новые", "color": "#172641"},
    {"id": "awaiting_payment", "title_uz": "Aloqada / To'lov", "title_ru": "В работе / Оплата", "color": "#aa8a5e"},
    {"id": "paid", "title_uz": "Tasdiqlangan", "title_ru": "Подтвержден", "color": "#2c6e49"},
    {"id": "preparing", "title_uz": "✂️ Ombordan yig'ish / Qadoqlash", "title_ru": "✂️ Сборка / Упаковка", "color": "#a3463c"},
    {"id": "in_transit", "title_uz": "🚚 Pochtada yo'lda (BTS / EMU)", "title_ru": "🚚 В пути (Почта)", "color": "#3f5e94"},
    {"id": "in_uz", "title_uz": "🏢 Filialga yetib borgan", "title_ru": "🏢 Прибыл в пункт выдачи", "color": "#735d78"},
    {"id": "delivered", "title_uz": "🎉 Yetkazildi", "title_ru": "🎉 Доставлено", "color": "#1b4931"},
    {"id": "cancelled", "title_uz": "❌ Bekor qilingan", "title_ru": "❌ Отменено", "color": "#782823"},
]


# ---------------- 1. KANBAN PIPELINE ----------------
@router.get("/pipeline")
def get_pipeline(admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    """Fetch orders grouped by status for visual CRM Kanban board."""
    orders = (
        db.query(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.meta).selectinload(Order.meta.property.mapper.class_.assigned_admin),
        )
        .order_by(Order.id.desc())
        .limit(200)
        .all()
    )

    stage_map = {s["id"]: [] for s in KANBAN_STAGES}

    for o in orders:
        status_key = o.status
        if status_key in ("ordered_china", "china_warehouse", "ready_to_ship"):
            status_key = "preparing"
        if status_key not in stage_map:
            continue
        items_summary = ", ".join(f"{it.name} ({it.size or '-'}) x{it.qty}" for it in o.items[:2])
        if len(o.items) > 2:
            items_summary += f" +{len(o.items) - 2}"

        assigned = o.meta.assigned_admin.full_name if (o.meta and o.meta.assigned_admin) else None

        card = {
            "id": o.id,
            "code": o.code,
            "customer_id": o.customer_id,
            "customer_name": o.name,
            "phone": o.phone,
            "tg_username": o.tg_username,
            "city": o.city,
            "address": o.address,
            "total": o.total,
            "paid_amount": o.paid_amount,
            "status": o.status,
            "items_count": sum(it.qty for it in o.items),
            "items_summary": items_summary,
            "assigned_admin": assigned,
            "tracking": o.tracking,
            "comment": o.comment,
            "has_note": bool(o.internal_note.strip()),
            "created_at": fmt_dt(o.created_at),
        }
        stage_map[o.status].append(card)

    columns = []
    for s in KANBAN_STAGES:
        cards = stage_map[s["id"]]
        total_sum = sum(c["total"] for c in cards)
        columns.append({
            "id": s["id"],
            "title_uz": s["title_uz"],
            "title_ru": s["title_ru"],
            "color": s["color"],
            "count": len(cards),
            "total_sum": total_sum,
            "cards": cards,
        })

    return {"columns": columns, "total_orders": len(orders)}


class MoveStageIn(BaseModel):
    order_id: int
    new_status: str


@router.post("/pipeline/move")
def move_pipeline_stage(body: MoveStageIn, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    if body.new_status not in STATUSES:
        raise HTTPException(422, "Noto'g'ri holat tanlandi")
    o = db.get(Order, body.order_id)
    if not o:
        raise HTTPException(404, "Buyurtma topilmadi")

    old_status = o.status
    if old_status != body.new_status:
        set_status(db, o, body.new_status, admin.full_name)
        audit(db, admin, "crm_pipeline_move", "order", str(o.id), f"{old_status} -> {body.new_status}")
        db.commit()

    return {
        "success": True,
        "order_id": o.id,
        "status": o.status,
        "status_uz": STATUS_UZ.get(o.status),
        "status_ru": STATUS_RU.get(o.status),
    }


# ---------------- 2. CUSTOMER 360 & SARTORIAL MEASUREMENTS ----------------
class CustomerDossierIn(BaseModel):
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    suit_size: Optional[str] = Field(default="", max_length=32)
    shirt_collar: Optional[str] = Field(default="", max_length=32)
    shoe_size: Optional[str] = Field(default="", max_length=32)
    preferred_fit: Optional[str] = Field(default="", max_length=64)
    birthday: Optional[str] = Field(default="", max_length=32)
    vip_tier: Optional[str] = Field(default="Standard", max_length=32)
    notes: Optional[str] = Field(default="", max_length=2000)


def _get_cust_dossier(db: Session, cid: int) -> dict:
    raw = get_setting(db, f"crm:customer:{cid}")
    if raw:
        try:
            return json.loads(raw)
        except Exception:
            pass
    return {
        "height_cm": None,
        "weight_kg": None,
        "suit_size": "",
        "shirt_collar": "",
        "shoe_size": "",
        "preferred_fit": "Regular",
        "birthday": "",
        "vip_tier": "Standard",
        "notes": "",
    }


@router.get("/customer/{cid}")
def get_customer_profile(cid: int, admin: AdminAccount = Depends(customers_perm), db: Session = Depends(get_db)):
    cust = db.get(Customer, cid)
    if not cust:
        raise HTTPException(404, "Mijoz topilmadi")

    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.customer_id == cid)
        .order_by(Order.id.desc())
        .all()
    )

    total_spent = sum(o.total for o in orders if o.status != "cancelled")
    paid_spent = sum(o.paid_amount for o in orders)
    dossier = _get_cust_dossier(db, cid)

    # Auto compute VIP tier if standard
    if dossier.get("vip_tier") in ("Standard", "", None):
        if total_spent >= 10_000_000:
            dossier["vip_tier"] = "Platinum Club"
        elif total_spent >= 5_000_000:
            dossier["vip_tier"] = "Gold VIP"
        elif total_spent >= 2_000_000:
            dossier["vip_tier"] = "Silver Member"

    order_items = []
    for o in orders:
        order_items.append({
            "id": o.id,
            "code": o.code,
            "status": o.status,
            "status_uz": STATUS_UZ.get(o.status),
            "status_ru": STATUS_RU.get(o.status),
            "total": o.total,
            "paid_amount": o.paid_amount,
            "created_at": fmt_dt(o.created_at),
            "tracking": o.tracking,
            "items": [{"name": it.name, "size": it.size, "color": it.color, "qty": it.qty} for it in o.items],
        })

    return {
        "customer": {
            "id": cust.id,
            "name": cust.display_name,
            "phone": cust.phone,
            "username": cust.username,
            "language": cust.language,
            "created_at": fmt_dt(cust.created_at),
            "last_seen": fmt_dt(cust.last_seen),
        },
        "stats": {
            "total_orders": len(orders),
            "total_spent": total_spent,
            "paid_spent": paid_spent,
            "active_orders": sum(1 for o in orders if o.status not in ("delivered", "cancelled")),
        },
        "dossier": dossier,
        "orders": order_items,
    }


@router.put("/customer/{cid}")
def update_customer_dossier(
    cid: int, body: CustomerDossierIn, admin: AdminAccount = Depends(customers_perm), db: Session = Depends(get_db)
):
    if not db.get(Customer, cid):
        raise HTTPException(404, "Mijoz topilmadi")

    data = body.model_dump()
    set_setting(db, f"crm:customer:{cid}", json.dumps(data, ensure_ascii=False))
    audit(db, admin, "crm_update_dossier", "customer", str(cid), f"Razmer va izohlar yangilandi")
    db.commit()
    return {"success": True, "dossier": data}


# ---------------- 3. CRM TASKS & FOLLOW-UPS ----------------
class TaskCreateIn(BaseModel):
    customer_id: Optional[int] = None
    customer_name: str = Field(default="", max_length=120)
    customer_phone: str = Field(default="", max_length=32)
    title: str = Field(min_length=2, max_length=255)
    due_date: str = Field(default="", max_length=32)
    assigned_admin_name: str = Field(default="", max_length=120)


@router.get("/tasks")
def list_tasks(status: str = "pending", admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    raw = get_setting(db, "crm:tasks_list")
    tasks = json.loads(raw) if raw else []

    if status in ("pending", "done"):
        filtered = [t for t in tasks if t.get("status") == status]
    else:
        filtered = tasks

    return {
        "tasks": filtered,
        "pending_count": sum(1 for t in tasks if t.get("status") == "pending"),
        "done_count": sum(1 for t in tasks if t.get("status") == "done"),
    }


@router.post("/tasks")
def create_task(body: TaskCreateIn, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    raw = get_setting(db, "crm:tasks_list")
    tasks = json.loads(raw) if raw else []

    new_task = {
        "id": int(datetime.now().timestamp() * 1000),
        "customer_id": body.customer_id,
        "customer_name": body.customer_name,
        "customer_phone": body.customer_phone,
        "title": body.title,
        "due_date": body.due_date or datetime.now().strftime("%Y-%m-%d"),
        "assigned_admin_name": body.assigned_admin_name or admin.full_name,
        "created_by": admin.full_name,
        "status": "pending",
        "created_at": fmt_dt(now()),
    }
    tasks.insert(0, new_task)
    set_setting(db, "crm:tasks_list", json.dumps(tasks, ensure_ascii=False))
    audit(db, admin, "crm_create_task", "task", str(new_task["id"]), body.title)
    db.commit()
    return {"success": True, "task": new_task}


@router.post("/tasks/{tid}/toggle")
def toggle_task(tid: int, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    raw = get_setting(db, "crm:tasks_list")
    tasks = json.loads(raw) if raw else []

    target = None
    for t in tasks:
        if t.get("id") == tid:
            t["status"] = "done" if t.get("status") == "pending" else "pending"
            t["completed_at"] = fmt_dt(now()) if t["status"] == "done" else None
            target = t
            break

    if not target:
        raise HTTPException(404, "Vazifa topilmadi")

    set_setting(db, "crm:tasks_list", json.dumps(tasks, ensure_ascii=False))
    db.commit()
    return {"success": True, "task": target}



# ---------------- 4. FITTING APPOINTMENTS (PRIMERKA KALENDARI) ----------------
class AdminFittingIn(BaseModel):
    customer_id: Optional[int] = None
    customer_name: str = Field(min_length=2, max_length=120)
    customer_phone: str = Field(default="", max_length=32)
    tg_username: Optional[str] = Field(default="", max_length=64)
    product_id: Optional[int] = None
    product_name: Optional[str] = Field(default="", max_length=200)
    suit_size: Optional[str] = Field(default="", max_length=32)
    date: str = Field(min_length=8, max_length=16)  # YYYY-MM-DD
    time_slot: str = Field(min_length=3, max_length=32)
    location: Optional[str] = Field(default="Withmore Bespoke Atelier (Toshkent)", max_length=200)
    notes: Optional[str] = Field(default="", max_length=500)
    status: Optional[str] = Field(default="pending", max_length=24)


class AdminFittingUpdateIn(BaseModel):
    status: Optional[str] = None
    date: Optional[str] = None
    time_slot: Optional[str] = None
    notes: Optional[str] = None
    suit_size: Optional[str] = None


@router.get("/fittings")
def get_all_fittings(
    date: Optional[str] = None,
    status: Optional[str] = None,
    admin: AdminAccount = Depends(orders_perm),
    db: Session = Depends(get_db)
):
    q = db.query(FittingAppointment)
    if date:
        q = q.filter(FittingAppointment.date == date)
    if status and status != "all":
        q = q.filter(FittingAppointment.status == status)

    rows = q.order_by(FittingAppointment.date.desc(), FittingAppointment.time_slot.asc()).limit(150).all()

    # Pre-fetch customer dossiers if available
    result = []
    for r in rows:
        dossier = None
        if r.customer_id:
            dossier = _get_cust_dossier(db, r.customer_id)
        result.append({
            "id": r.id,
            "customer_id": r.customer_id,
            "customer_name": r.customer_name,
            "customer_phone": r.customer_phone,
            "tg_username": r.tg_username,
            "product_id": r.product_id,
            "product_name": r.product_name,
            "suit_size": r.suit_size,
            "date": r.date,
            "time_slot": r.time_slot,
            "location": r.location,
            "notes": r.notes,
            "status": r.status,
            "created_at": fmt_dt(r.created_at),
            "dossier": dossier,
        })
    return {"fittings": result, "total": len(result)}


@router.post("/fittings")
def create_fitting(body: AdminFittingIn, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    apt = FittingAppointment(
        customer_id=body.customer_id,
        customer_name=body.customer_name.strip(),
        customer_phone=body.customer_phone.strip(),
        tg_username=body.tg_username or "",
        product_id=body.product_id,
        product_name=body.product_name or "",
        suit_size=body.suit_size or "",
        date=body.date.strip(),
        time_slot=body.time_slot.strip(),
        location=body.location or "Withmore Bespoke Atelier (Toshkent)",
        notes=body.notes or "",
        status=body.status or "pending",
    )
    db.add(apt)
    db.commit()
    audit(db, admin, "create_fitting", "fitting", str(apt.id), f"{apt.customer_name} on {apt.date}")
    return {"success": True, "id": apt.id}


@router.put("/fittings/{fid}")
def update_fitting(fid: int, body: AdminFittingUpdateIn, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    apt = db.get(FittingAppointment, fid)
    if not apt:
        raise HTTPException(404, "Primerka topilmadi")

    if body.status:
        apt.status = body.status
    if body.date:
        apt.date = body.date
    if body.time_slot:
        apt.time_slot = body.time_slot
    if body.notes is not None:
        apt.notes = body.notes
    if body.suit_size is not None:
        apt.suit_size = body.suit_size

    db.commit()
    audit(db, admin, "update_fitting", "fitting", str(apt.id), f"status={apt.status}")
    return {"success": True, "status": apt.status}


@router.post("/fittings/{fid}/notify")
def notify_customer_fitting(fid: int, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    from ..outbox import enqueue
    apt = db.get(FittingAppointment, fid)
    if not apt:
        raise HTTPException(404, "Primerka topilmadi")

    if not apt.customer_id:
        raise HTTPException(422, "Ushbu primerka mijoz hisobiga bog'lanmagan")

    cust = db.get(Customer, apt.customer_id)
    if not cust or not cust.tg_id:
        raise HTTPException(422, "Mijozning Telegram ID si mavjud emas")

    msg = (
        f"Hurmatli <b>{apt.customer_name}</b>!\n\n"
        f"Withmore Bespoke atelyesida kiyib ko‘rish (primerka) bo‘yicha eslatma:\n"
        f"📅 Sana: <b>{apt.date}</b>\n"
        f"⏰ Vaqt: <b>{apt.time_slot}</b>\n"
        f"📍 Manzil: <b>{apt.location}</b>\n"
    )
    if apt.product_name:
        msg += f"👔 Mahsulot: <b>{apt.product_name}</b> ({apt.suit_size or '-' })\n"

    msg += (
        f"\nStilistimiz sizni kutmoqda. Qandaydir o‘zgarish bo‘lsa, adminga xabar berishingiz mumkin.\n"
        f"<i>Sokin klassika va aniq bichim — Withmore.</i>"
    )

    enqueue(db, "direct", cust.tg_id, msg)
    db.commit()
    audit(db, admin, "notify_fitting", "fitting", str(apt.id), f"Sent to {cust.tg_id}")
    return {"success": True, "message": "Mijozga Telegram orqali eslatma yuborildi!"}


# ---------------- 4. ABANDONED CARTS & LIVE RADAR ----------------
@router.get("/abandoned-carts")
def get_abandoned_carts(
    admin: AdminAccount = Depends(customers_perm),
    db: Session = Depends(get_db),
):
    """
    Finds customer sessions that have active items in their cart,
    sorted by most recently active, excluding customers who already ordered recently.
    """
    sessions = (
        db.query(ShopSession)
        .filter(ShopSession.cart != None)
        .order_by(ShopSession.last_seen.desc())
        .limit(100)
        .all()
    )

    result = []
    total_abandoned_val = 0

    for s in sessions:
        cart = s.cart or []
        if not cart or not isinstance(cart, list) or len(cart) == 0:
            continue

        cust = db.get(Customer, s.customer_id) if s.customer_id else None
        if not cust:
            continue

        # Check if customer placed an order after or near this session
        recent_order = (
            db.query(Order)
            .filter(Order.customer_id == cust.id, Order.created_at >= s.created_at)
            .first()
        )
        if recent_order:
            continue  # They completed an order

        # Hydrate items
        hydrated_items = []
        cart_total = 0
        for item in cart:
            var_id = item.get("variant_id") or item.get("id")
            qty = int(item.get("qty", 1))
            var = db.get(ProductVariant, var_id) if var_id else None
            prod = db.get(Product, var.product_id) if var and var.product_id else None
            if not prod and item.get("product_id"):
                prod = db.get(Product, item.get("product_id"))

            if prod:
                price = prod.manual_price or prod.price_uzs or 0
                item_sum = price * qty
                cart_total += item_sum
                first_img = prod.images[0].path if prod.images else None
                hydrated_items.append({
                    "product_id": prod.id,
                    "title": prod.name_uz or prod.name_ru or "Mahsulot",
                    "price": price,
                    "qty": qty,
                    "size": var.size if var else "",
                    "color": var.color if var else "",
                    "image": first_img,
                    "total": item_sum,
                })

        if not hydrated_items:
            continue

        total_abandoned_val += cart_total

        # Find customer's latest store event
        last_event = (
            db.query(StoreEvent)
            .filter(StoreEvent.customer_id == cust.id)
            .order_by(StoreEvent.created_at.desc())
            .first()
        )
        last_action_text = "Savatga kiyim qo'shdi"
        if last_event:
            if last_event.type == "checkout_click":
                last_action_text = "Rasmiylashtirish tugmasini bosdi"
            elif last_event.type == "add_to_cart":
                last_action_text = "Savatga kiyim qo'shdi"
            elif last_event.type == "product_view":
                last_action_text = "Mahsulot sahifasini ko'rdi"

        # Check if reminder was already sent
        recovery_flag = get_setting(db, f"crm:abandoned_recovered:{s.id}")

        result.append({
            "session_id": s.id,
            "customer_id": cust.id,
            "customer_name": f"{cust.first_name or ''} {cust.last_name or ''}".strip() or "Noma'lum mijoz",
            "customer_phone": cust.phone or "",
            "tg_username": cust.username or "",
            "tg_user_id": cust.tg_user_id,
            "items": hydrated_items,
            "items_count": len(hydrated_items),
            "cart_total": cart_total,
            "last_seen": s.last_seen.isoformat() if s.last_seen else s.created_at.isoformat(),
            "last_action": last_action_text,
            "recovery_sent": bool(recovery_flag),
        })

    return {
        "summary": {
            "total_abandoned_count": len(result),
            "total_abandoned_value": total_abandoned_val,
        },
        "abandoned_carts": result,
    }


class RecoverCartRequest(BaseModel):
    message: str | None = None
    discount_code: str | None = None
    discount_percent: int | None = 5


@router.post("/abandoned-carts/{sid}/recover")
def recover_abandoned_cart(
    sid: int,
    payload: RecoverCartRequest = RecoverCartRequest(),
    admin: AdminAccount = Depends(customers_perm),
    db: Session = Depends(get_db),
):
    """
    Sends an automated, elegant recovery message directly to the customer's Telegram chat.
    """
    session = db.get(ShopSession, sid)
    if not session or not session.customer_id:
        raise HTTPException(404, "Sessiya yoki mijoz topilmadi")

    cust = db.get(Customer, session.customer_id)
    if not cust or not cust.tg_user_id:
        raise HTTPException(400, "Mijozning Telegram ID raqami mavjud emas")

    first_name = cust.first_name or "Hurmatli mijoz"
    bot_username = (get_setting(db, "contact_username") or "Withmoreuz_bot").replace("@", "")

    if payload.message and payload.message.strip():
        text = payload.message.strip()
    else:
        promo = payload.discount_code or f"WITHMORE{payload.discount_percent or 5}"
        text = (
            f"Salom, {first_name}! 👔\n\n"
            f"Withmore savatingizda siz tanlagan nafis kiyimlar sizni kutmoqda.\n"
            f"Bugun buyurtmangizni yakunlash uchun maxsus chegirma promokodini taqdim etamiz: <b>{promo}</b> (-{payload.discount_percent or 5}%)\n\n"
            f"🛒 Savatni ko'rish va rasmiylashtirish:\nhttps://t.me/{bot_username}/shop"
        )

    enqueue(db, "crm_direct", cust.tg_user_id, text)
    set_setting(db, f"crm:abandoned_recovered:{sid}", "1")

    return {
        "status": "ok",
        "message": f"Telegram orqali {first_name} ga maxsus chegirma va eslatma yuborildi!",
    }
