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
    {"id": "new", "title_uz": "Yangi so'rov", "title_ru": "Новые", "color": "#172641"},
    {"id": "awaiting_payment", "title_uz": "Aloqada / To'lov", "title_ru": "В работе / Оплата", "color": "#aa8a5e"},
    {"id": "paid", "title_uz": "To'langan (Avans)", "title_ru": "Оплачено (Аванс)", "color": "#2c6e49"},
    {"id": "ordered_china", "title_uz": "🇨🇳 Xitoyda olindi", "title_ru": "🇨🇳 Куплено в Китае", "color": "#a3463c"},
    {"id": "in_transit", "title_uz": "✈️ Karvonda / Yo'lda", "title_ru": "✈️ В пути", "color": "#3f5e94"},
    {"id": "in_uz", "title_uz": "🏢 Toshkent omborida", "title_ru": "🏢 Склад в Ташкенте", "color": "#735d78"},
    {"id": "delivered", "title_uz": "📮 Pochtaga berildi", "title_ru": "📮 Отправлено почтой", "color": "#1b4931"},
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
        if o.status not in stage_map:
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

