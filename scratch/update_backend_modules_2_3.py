import os
import re

print("Starting backend implementation for Feature 2 (Abandoned Carts) and Feature 3 (Unit Economics)...")

# 1. Update backend/app/routers/admin_crm.py with Abandoned Carts endpoints
crm_path = "backend/app/routers/admin_crm.py"
with open(crm_path, "r", encoding="utf-8") as f:
    crm_code = f.read()

abandoned_endpoints = '''
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
            f"Salom, {first_name}! 👔\\n\\n"
            f"Withmore savatingizda siz tanlagan nafis kiyimlar sizni kutmoqda.\\n"
            f"Bugun buyurtmangizni yakunlash uchun maxsus chegirma promokodini taqdim etamiz: <b>{promo}</b> (-{payload.discount_percent or 5}%)\\n\\n"
            f"🛒 Savatni ko'rish va rasmiylashtirish:\\nhttps://t.me/{bot_username}/shop"
        )

    enqueue(db, cust.tg_user_id, text)
    set_setting(db, f"crm:abandoned_recovered:{sid}", "1")

    return {
        "status": "ok",
        "message": f"Telegram orqali {first_name} ga maxsus chegirma va eslatma yuborildi!",
    }
'''

if "/abandoned-carts" not in crm_code:
    crm_code += "\n" + abandoned_endpoints
    with open(crm_path, "w", encoding="utf-8") as f:
        f.write(crm_code)
    print("admin_crm.py updated with abandoned-carts endpoints!")

# 2. Update backend/app/routers/admin_ops.py with Order-by-Order Unit Economics & Settings
ops_path = "backend/app/routers/admin_ops.py"
with open(ops_path, "r", encoding="utf-8") as f:
    ops_code = f.read()

# Enhance get_finance in admin_ops.py to return detailed orders
old_finance_return = '''    return {"days": days, "orders": len(orders), "revenue": revenue, "discounts": discounts, "paid": paid,
            "cost_goods": cost_goods, "cost_cargo": cost_cargo, "post_fee": post_fee, "post_total": post_total,
            "profit": profit, "margin_pct": round(profit * 100 / revenue, 1) if revenue else 0,
            "debt": max(0, revenue - paid), "yuan_rate": rate, "shipping_per_kg": ship, "top": top}'''

new_finance_return = '''    # Order-by-Order Unit Economics Breakdown
    order_details = []
    for o in orders[:50]:  # Top 50 recent orders
        o_cogs = 0
        o_cargo = 0
        items_desc = []
        for it in o.items:
            p = db.get(Product, it.product_id) if it.product_id else None
            g = int((p.price_yuan if p else 0) * rate) * it.qty
            c = int((p.weight_kg if p else 0) * ship) * it.qty
            o_cogs += g
            o_cargo += c
            items_desc.append(f"{it.name} ({it.qty} dona)")

        o_delivery = post_fee
        o_profit = o.total - o_cogs - o_cargo - o_delivery
        o_margin = round(o_profit * 100 / o.total, 1) if o.total > 0 else 0

        order_details.append({
            "id": o.id,
            "code": o.code,
            "date": o.created_at.strftime("%Y-%m-%d %H:%M"),
            "customer_name": o.name or "Mijoz",
            "items_summary": ", ".join(items_desc),
            "revenue": o.total,
            "cogs": o_cogs,
            "cargo": o_cargo,
            "delivery": o_delivery,
            "profit": o_profit,
            "margin_pct": o_margin,
            "status": o.status,
        })

    return {"days": days, "orders": len(orders), "revenue": revenue, "discounts": discounts, "paid": paid,
            "cost_goods": cost_goods, "cost_cargo": cost_cargo, "post_fee": post_fee, "post_total": post_total,
            "profit": profit, "margin_pct": round(profit * 100 / revenue, 1) if revenue else 0,
            "debt": max(0, revenue - paid), "yuan_rate": rate, "shipping_per_kg": ship, "top": top,
            "order_details": order_details}'''

if old_finance_return in ops_code:
    ops_code = ops_code.replace(old_finance_return, new_finance_return)

finance_settings_endpoints = '''
# ---------------- Unit Economics Settings ----------------
class FinanceSettingsPayload(BaseModel):
    cny_rate: int | None = None
    shipping_per_kg: int | None = None
    post_fee: int | None = None


@router.post("/finance/settings")
def update_finance_settings(
    payload: FinanceSettingsPayload,
    admin: AdminAccount = Depends(stats_perm),
    db: Session = Depends(get_db),
):
    if payload.cny_rate is not None:
        set_setting(db, "cny_rate", str(payload.cny_rate))
    if payload.shipping_per_kg is not None:
        set_setting(db, "shipping_per_kg", str(payload.shipping_per_kg))
    if payload.post_fee is not None:
        set_setting(db, "post_fee", str(payload.post_fee))
    return {"status": "ok", "message": "Moliya va unit-economics koeffitsiyentlari yangilandi"}
'''

if "/finance/settings" not in ops_code:
    ops_code += "\n" + finance_settings_endpoints

with open(ops_path, "w", encoding="utf-8") as f:
    f.write(ops_code)
print("admin_ops.py updated with detailed Unit Economics and settings!")

