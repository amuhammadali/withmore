import os
import re

print("Starting backend implementation for Lookbook, Segmented Broadcast, and Referrals...")

# 1. Update backend/app/models.py
models_path = "backend/app/models.py"
with open(models_path, "r", encoding="utf-8") as f:
    models_code = f.read()

# Add referral fields to Customer if not present
if "bonus_balance:" not in models_code:
    models_code = models_code.replace(
        '    language: Mapped[str] = mapped_column(String(2), default="uz")',
        '    language: Mapped[str] = mapped_column(String(2), default="uz")\n    bonus_balance: Mapped[int] = mapped_column(Integer, default=0)\n    referral_code: Mapped[str] = mapped_column(String(32), default="")\n    referred_by_id: Mapped[int | None] = mapped_column(Integer, nullable=True)'
    )

# Add LookbookBundle and BroadcastCampaign models if not present
new_models = '''
class LookbookBundle(Base):
    __tablename__ = "lookbook_bundles"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_uz: Mapped[str] = mapped_column(String(160))
    title_ru: Mapped[str] = mapped_column(String(160), default="")
    description_uz: Mapped[str] = mapped_column(Text, default="")
    description_ru: Mapped[str] = mapped_column(Text, default="")
    image: Mapped[str] = mapped_column(String(500), default="")
    product_ids: Mapped[list] = mapped_column(JSON, default=list)  # list of product ids
    discount_pct: Mapped[int] = mapped_column(Integer, default=10)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class BroadcastCampaign(Base):
    __tablename__ = "broadcast_campaigns"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160))
    segment: Mapped[str] = mapped_column(String(40), default="all")  # all, vip, inactive_30d, cart_abandoned
    text: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String(500), default="")
    button_text: Mapped[str] = mapped_column(String(64), default="")
    button_url: Mapped[str] = mapped_column(String(500), default="")
    sent_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="sent")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
'''

if "class LookbookBundle(" not in models_code:
    models_code += "\n" + new_models

with open(models_path, "w", encoding="utf-8") as f:
    f.write(models_code)
print("backend/app/models.py updated with LookbookBundle and BroadcastCampaign!")

# 2. Add endpoints to backend/app/routers/shop.py
shop_path = "backend/app/routers/shop.py"
with open(shop_path, "r", encoding="utf-8") as f:
    shop_code = f.read()

shop_extensions = '''
# ---------------- LOOKBOOK & BUY THE LOOK ENDPOINTS ----------------
@router.get("/lookbooks")
def get_lookbooks(db: Session = Depends(get_db)):
    """
    Returns active Lookbook bundles with hydrated products and discounted bundle pricing.
    """
    bundles = (
        db.query(LookbookBundle)
        .filter(LookbookBundle.active == True)
        .order_by(LookbookBundle.sort.asc(), LookbookBundle.id.desc())
        .all()
    )

    result = []
    for b in bundles:
        items = []
        regular_total = 0
        for pid in (b.product_ids or []):
            prod = db.get(Product, pid)
            if prod and prod.active and not prod.deleted_at:
                price = prod.manual_price or prod.price_uzs or 0
                regular_total += price
                first_img = prod.images[0].path if prod.images else None
                first_var = prod.variants[0] if prod.variants else None
                items.append({
                    "id": prod.id,
                    "title_uz": prod.name_uz,
                    "title_ru": prod.name_ru,
                    "price": price,
                    "image": first_img,
                    "default_variant_id": first_var.id if first_var else None,
                    "sizes": [v.size for v in prod.variants if v.available],
                })

        discount_mult = (100 - (b.discount_pct or 10)) / 100.0
        bundle_price = int(regular_total * discount_mult)

        result.append({
            "id": b.id,
            "title_uz": b.title_uz,
            "title_ru": b.title_ru,
            "description_uz": b.description_uz,
            "description_ru": b.description_ru,
            "image": b.image or (items[0]["image"] if items else ""),
            "discount_pct": b.discount_pct or 10,
            "regular_total": regular_total,
            "bundle_price": bundle_price,
            "savings": max(0, regular_total - bundle_price),
            "items": items,
        })

    return result


@router.post("/lookbooks/{bid}/add-bundle")
def add_lookbook_bundle_to_cart(
    bid: int,
    session: ShopSession = Depends(get_shop_session),
    db: Session = Depends(get_db),
):
    """
    Adds all items in the lookbook bundle to the customer's cart in one click.
    """
    b = db.get(LookbookBundle, bid)
    if not b or not b.active:
        raise HTTPException(404, "Obraz topilmadi")

    cart = list(session.cart or [])
    added_count = 0

    for pid in (b.product_ids or []):
        prod = db.get(Product, pid)
        if prod and prod.active and not prod.deleted_at and prod.variants:
            first_avail = next((v for v in prod.variants if v.available), prod.variants[0])
            # Check if variant already in cart
            existing = next((c for c in cart if c.get("variant_id") == first_avail.id), None)
            if existing:
                existing["qty"] = int(existing.get("qty", 1)) + 1
            else:
                cart.append({
                    "variant_id": first_avail.id,
                    "product_id": prod.id,
                    "qty": 1,
                    "price": prod.manual_price or prod.price_uzs or 0,
                })
            added_count += 1

    session.cart = cart
    session.last_seen = now()
    db.commit()

    return {
        "status": "ok",
        "message": f"To'liq obraz ({added_count} ta kiyim) savatingizga qo'shildi!",
        "cart_count": len(cart),
    }


# ---------------- GENTLEMEN REFERRAL CLUB ENDPOINTS ----------------
@router.get("/referral")
def get_customer_referral(
    session: ShopSession = Depends(get_shop_session),
    db: Session = Depends(get_db),
):
    """
    Returns referral status, personal invite link, and bonus balance for customer.
    """
    cust = db.get(Customer, session.customer_id) if session.customer_id else None
    bot_user = (get_setting(db, "contact_username") or "Withmoreuz_bot").replace("@", "")

    cid = cust.id if cust else 0
    ref_code = cust.referral_code if (cust and cust.referral_code) else f"WM{cid:04d}"
    invite_link = f"https://t.me/{bot_user}?start=ref_{cid}"

    # Count friends invited
    friends_count = db.query(Customer).filter(Customer.referred_by_id == cid).count() if cid else 0

    return {
        "customer_id": cid,
        "referral_code": ref_code,
        "invite_link": invite_link,
        "bonus_balance": getattr(cust, "bonus_balance", 0) if cust else 0,
        "friends_count": friends_count,
        "reward_per_friend": 100000,
    }
'''

if "/lookbooks" not in shop_code:
    shop_code += "\n" + shop_extensions
    with open(shop_path, "w", encoding="utf-8") as f:
        f.write(shop_code)
    print("backend/app/routers/shop.py updated with Lookbook and Referral endpoints!")

# 3. Add Broadcast & Lookbook Admin Endpoints in backend/app/routers/admin_ops.py
with open("backend/app/routers/admin_ops.py", "r", encoding="utf-8") as f:
    ops_code = f.read()

ops_extensions = '''
# ---------------- TELEGRAM SEGMENTED BROADCAST ----------------
@router.get("/broadcast/segments")
def get_broadcast_segments(
    admin: AdminAccount = Depends(marketing_perm),
    db: Session = Depends(get_db),
):
    """
    Counts audiences for different broadcast segments.
    """
    all_count = db.query(Customer).filter(Customer.tg_id != None).count()

    # VIP customers (LTV > 2,000,000 UZS)
    from sqlalchemy import func
    vip_subq = (
        db.query(Order.customer_id)
        .group_by(Order.customer_id)
        .having(func.sum(Order.total) >= 2000000)
        .subquery()
    )
    vip_count = (
        db.query(Customer)
        .filter(Customer.tg_id != None, Customer.id.in_(vip_subq))
        .count()
    )

    # Inactive customers (no orders in 30+ days)
    cutoff_30d = now() - timedelta(days=30)
    active_recent_subq = (
        db.query(Order.customer_id)
        .filter(Order.created_at >= cutoff_30d)
        .subquery()
    )
    inactive_count = (
        db.query(Customer)
        .filter(Customer.tg_id != None, ~Customer.id.in_(active_recent_subq))
        .count()
    )

    # Abandoned cart customers
    cart_subq = (
        db.query(ShopSession.customer_id)
        .filter(ShopSession.cart != None)
        .subquery()
    )
    cart_count = (
        db.query(Customer)
        .filter(Customer.tg_id != None, Customer.id.in_(cart_subq))
        .count()
    )

    return {
        "all": all_count,
        "vip": vip_count,
        "inactive_30d": inactive_count,
        "cart_abandoned": cart_count,
    }


class SendBroadcastPayload(BaseModel):
    title: str
    segment: str = "all"  # all, vip, inactive_30d, cart_abandoned
    text: str
    image_url: str | None = None
    button_text: str | None = None
    button_url: str | None = None


@router.post("/broadcast/send")
def send_broadcast_campaign(
    payload: SendBroadcastPayload,
    admin: AdminAccount = Depends(marketing_perm),
    db: Session = Depends(get_db),
):
    """
    Enqueues targeted Telegram blast to selected customer segment.
    """
    q = db.query(Customer).filter(Customer.tg_id != None)

    if payload.segment == "vip":
        from sqlalchemy import func
        vip_subq = (
            db.query(Order.customer_id)
            .group_by(Order.customer_id)
            .having(func.sum(Order.total) >= 2000000)
            .subquery()
        )
        q = q.filter(Customer.id.in_(vip_subq))
    elif payload.segment == "inactive_30d":
        cutoff_30d = now() - timedelta(days=30)
        active_subq = db.query(Order.customer_id).filter(Order.created_at >= cutoff_30d).subquery()
        q = q.filter(~Customer.id.in_(active_subq))
    elif payload.segment == "cart_abandoned":
        cart_subq = db.query(ShopSession.customer_id).filter(ShopSession.cart != None).subquery()
        q = q.filter(Customer.id.in_(cart_subq))

    recipients = q.all()
    sent_count = 0

    for cust in recipients:
        if cust.tg_id:
            formatted_text = payload.text.replace("{name}", cust.first_name or "Hurmatli mijoz")
            if payload.image_url and payload.image_url.strip():
                formatted_text = f"{payload.image_url.strip()}\\n\\n" + formatted_text
            if payload.button_text and payload.button_url:
                formatted_text += f"\\n\\n🔗 <a href='{payload.button_url}'>{payload.button_text}</a>"
            enqueue(db, cust.tg_id, formatted_text)
            sent_count += 1

    # Save campaign log
    camp = BroadcastCampaign(
        title=payload.title,
        segment=payload.segment,
        text=payload.text,
        image_url=payload.image_url or "",
        button_text=payload.button_text or "",
        button_url=payload.button_url or "",
        sent_count=sent_count,
        status="sent",
    )
    db.add(camp)
    db.commit()

    return {
        "status": "ok",
        "message": f"Xabarnoma {sent_count} ta mijozga muvaffaqiyatli jo'natildi!",
        "sent_count": sent_count,
    }


@router.get("/broadcast/history")
def get_broadcast_history(
    admin: AdminAccount = Depends(marketing_perm),
    db: Session = Depends(get_db),
):
    campaigns = db.query(BroadcastCampaign).order_by(BroadcastCampaign.id.desc()).limit(20).all()
    return [
        {
            "id": c.id,
            "title": c.title,
            "segment": c.segment,
            "text": c.text,
            "image_url": c.image_url,
            "button_text": c.button_text,
            "sent_count": c.sent_count,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for c in campaigns
    ]


# ---------------- ADMIN LOOKBOOK MANAGEMENT ----------------
@router.get("/lookbooks")
def admin_get_lookbooks(
    admin: AdminAccount = Depends(catalog_perm),
    db: Session = Depends(get_db),
):
    bundles = db.query(LookbookBundle).order_by(LookbookBundle.sort.asc(), LookbookBundle.id.desc()).all()
    res = []
    for b in bundles:
        res.append({
            "id": b.id,
            "title_uz": b.title_uz,
            "title_ru": b.title_ru,
            "description_uz": b.description_uz,
            "image": b.image,
            "product_ids": b.product_ids or [],
            "discount_pct": b.discount_pct or 10,
            "sort": b.sort,
            "active": b.active,
        })
    return res


class SaveLookbookPayload(BaseModel):
    title_uz: str
    title_ru: str | None = ""
    description_uz: str | None = ""
    description_ru: str | None = ""
    image: str | None = ""
    product_ids: list[int] = []
    discount_pct: int = 10
    active: bool = True


@router.post("/lookbooks")
def admin_create_lookbook(
    payload: SaveLookbookPayload,
    admin: AdminAccount = Depends(catalog_perm),
    db: Session = Depends(get_db),
):
    b = LookbookBundle(
        title_uz=payload.title_uz,
        title_ru=payload.title_ru or "",
        description_uz=payload.description_uz or "",
        description_ru=payload.description_ru or "",
        image=payload.image or "",
        product_ids=payload.product_ids,
        discount_pct=payload.discount_pct,
        active=payload.active,
    )
    db.add(b)
    db.commit()
    return {"status": "ok", "id": b.id}
'''

if "/broadcast/segments" not in ops_code:
    ops_code += "\n" + ops_extensions
    with open("backend/app/routers/admin_ops.py", "w", encoding="utf-8") as f:
        f.write(ops_code)
    print("backend/app/routers/admin_ops.py updated with Broadcast and Lookbook admin endpoints!")

print("All backend code prepared successfully!")

