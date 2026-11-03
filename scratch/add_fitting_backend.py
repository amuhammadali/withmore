import os

shop_path = r"c:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\shop.py"
admin_crm_path = r"c:\Users\muham\OneDrive\Desktop\withmore\backend\app\routers\admin_crm.py"

# 1. Update shop.py
with open(shop_path, "r", encoding="utf-8") as f:
    shop_content = f.read()

shop_additions = '''

# ---------------- Bespoke Measurements & Fitting Appointments ----------------
class CustomerMeasurementsIn(BaseModel):
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    suit_size: Optional[str] = Field(default="", max_length=32)
    shirt_collar: Optional[str] = Field(default="", max_length=32)
    shoe_size: Optional[str] = Field(default="", max_length=32)
    preferred_fit: Optional[str] = Field(default="Regular", max_length=64)
    notes: Optional[str] = Field(default="", max_length=1000)


@router.get("/measurements")
def get_customer_measurements(c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    raw = get_setting(db, f"crm:customer:{c.id}")
    data = {}
    if raw:
        try:
            data = json.loads(raw)
        except Exception:
            pass
    return {
        "customer_id": c.id,
        "name": c.display_name,
        "height_cm": data.get("height_cm"),
        "weight_kg": data.get("weight_kg"),
        "suit_size": data.get("suit_size", ""),
        "shirt_collar": data.get("shirt_collar", ""),
        "shoe_size": data.get("shoe_size", ""),
        "preferred_fit": data.get("preferred_fit", "Regular"),
        "vip_tier": data.get("vip_tier", "Standard"),
        "notes": data.get("notes", ""),
    }


@router.put("/measurements")
def save_customer_measurements(body: CustomerMeasurementsIn, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    raw = get_setting(db, f"crm:customer:{c.id}")
    existing = {}
    if raw:
        try:
            existing = json.loads(raw)
        except Exception:
            pass
    existing.update({
        "height_cm": body.height_cm,
        "weight_kg": body.weight_kg,
        "suit_size": body.suit_size or "",
        "shirt_collar": body.shirt_collar or "",
        "shoe_size": body.shoe_size or "",
        "preferred_fit": body.preferred_fit or "Regular",
        "notes": body.notes or existing.get("notes", ""),
    })
    set_setting(db, f"crm:customer:{c.id}", json.dumps(existing, ensure_ascii=False))
    db.commit()
    return {"success": True, "measurements": existing}


class FittingBookingIn(BaseModel):
    date: str = Field(min_length=8, max_length=16)
    time_slot: str = Field(min_length=3, max_length=32)
    product_id: Optional[int] = None
    suit_size: Optional[str] = Field(default="", max_length=32)
    name: Optional[str] = Field(default="", max_length=120)
    phone: Optional[str] = Field(default="", max_length=32)
    notes: Optional[str] = Field(default="", max_length=500)


@router.post("/fitting", status_code=201)
def book_fitting(body: FittingBookingIn, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    prod_name = ""
    if body.product_id:
        p = db.get(Product, body.product_id)
        if p:
            prod_name = p.name_uz

    cust_name = body.name.strip() or c.display_name
    cust_phone = body.phone.strip() or c.phone

    apt = FittingAppointment(
        customer_id=c.id,
        customer_name=cust_name,
        customer_phone=cust_phone,
        tg_username=c.username or "",
        product_id=body.product_id,
        product_name=prod_name,
        suit_size=body.suit_size or "",
        date=body.date.strip(),
        time_slot=body.time_slot.strip(),
        location="Withmore Bespoke Atelier (Toshkent)",
        notes=body.notes or "",
        status="pending",
    )
    db.add(apt)
    db.flush()

    admin_msg = (
        f"🪡 <b>YANGI PRIMERKA BRON QILINDI!</b>\\n\\n"
        f"👤 Mijoz: <b>{cust_name}</b>\\n"
        f"📞 Tel: <code>{cust_phone}</code>\\n"
        f"📅 Sana: <b>{apt.date}</b> ({apt.time_slot})\\n"
        f"👔 Mahsulot: {prod_name or 'Umumiy o‘lcham olish'}\\n"
        f"📏 Razmer: {apt.suit_size or 'Atelyeda aniqlanadi'}\\n"
    )
    if apt.notes:
        admin_msg += f"📝 Izoh: {apt.notes}\\n"

    for adm in active_order_admins(db):
        if adm.tg_chat_id:
            enqueue(db, "direct", adm.tg_chat_id, admin_msg)

    db.commit()

    return {
        "success": True,
        "id": apt.id,
        "date": apt.date,
        "time_slot": apt.time_slot,
        "location": apt.location,
        "status": apt.status,
    }


@router.get("/fitting")
def get_customer_fittings(c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    rows = (
        db.query(FittingAppointment)
        .filter(FittingAppointment.customer_id == c.id)
        .order_by(FittingAppointment.id.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": r.id,
            "date": r.date,
            "time_slot": r.time_slot,
            "location": r.location,
            "product_name": r.product_name,
            "suit_size": r.suit_size,
            "status": r.status,
            "created_at": fmt_dt(r.created_at),
        }
        for r in rows
    ]
'''

if "/measurements" not in shop_content:
    shop_content += shop_additions
    with open(shop_path, "w", encoding="utf-8") as f:
        f.write(shop_content)
    print("shop.py updated with measurements and fittings!")


# 2. Update admin_crm.py
with open(admin_crm_path, "r", encoding="utf-8") as f:
    admin_crm_content = f.read()

# Make sure FittingAppointment is imported
if "FittingAppointment" not in admin_crm_content:
    admin_crm_content = admin_crm_content.replace(
        "from ..models import (",
        "from ..models import (\n    FittingAppointment,"
    )

admin_crm_additions = '''

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
        f"Hurmatli <b>{apt.customer_name}</b>!\\n\\n"
        f"Withmore Bespoke atelyesida kiyib ko‘rish (primerka) bo‘yicha eslatma:\\n"
        f"📅 Sana: <b>{apt.date}</b>\\n"
        f"⏰ Vaqt: <b>{apt.time_slot}</b>\\n"
        f"📍 Manzil: <b>{apt.location}</b>\\n"
    )
    if apt.product_name:
        msg += f"👔 Mahsulot: <b>{apt.product_name}</b> ({apt.suit_size or '-' })\\n"

    msg += (
        f"\\nStilistimiz sizni kutmoqda. Qandaydir o‘zgarish bo‘lsa, adminga xabar berishingiz mumkin.\\n"
        f"<i>Sokin klassika va aniq bichim — Withmore.</i>"
    )

    enqueue(db, "direct", cust.tg_id, msg)
    db.commit()
    audit(db, admin, "notify_fitting", "fitting", str(apt.id), f"Sent to {cust.tg_id}")
    return {"success": True, "message": "Mijozga Telegram orqali eslatma yuborildi!"}
'''

if "/fittings" not in admin_crm_content:
    admin_crm_content += admin_crm_additions
    with open(admin_crm_path, "w", encoding="utf-8") as f:
        f.write(admin_crm_content)
    print("admin_crm.py updated with fittings endpoints!")

print("Backend fitting APIs added successfully!")

