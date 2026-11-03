"""Admin operations: China purchase list, bulk cargo status, net profit, postal label (nakladnoy)."""
import html
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, selectinload

from ..core import all_settings, audit, fmt_dt, get_setting, set_setting, thumb_of
from ..db import get_db
from ..models import STATUS_UZ, STATUSES, AdminAccount, Order, Product, now
from ..orders_service import fmt_money, set_status
from ..security import require

router = APIRouter(prefix="/api/admin/ops", tags=["admin-ops"])
orders_perm = require("orders")
products_perm = require("products")
stats_perm = require("statistics")


# ---------------- supplier links (1688 / Taobao / Poizon) ----------------
class SupplierIn(BaseModel):
    url: str = Field(default="", max_length=500)


@router.get("/supplier/{pid}")
def supplier_get(pid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    return {"product_id": pid, "url": get_setting(db, f"supplier:{pid}")}


@router.put("/supplier/{pid}")
def supplier_put(pid: int, body: SupplierIn, admin: AdminAccount = Depends(products_perm),
                 db: Session = Depends(get_db)):
    if not db.get(Product, pid):
        raise HTTPException(404, "Mahsulot topilmadi")
    url = body.url.strip()
    if url and not url.startswith(("http://", "https://")):
        raise HTTPException(422, "Havola http:// yoki https:// bilan boshlanishi kerak")
    set_setting(db, f"supplier:{pid}", url)
    audit(db, admin, "supplier_link", "product", pid)
    db.commit()
    return {"product_id": pid, "url": url}


# ---------------- China purchase list ----------------
@router.get("/china-list")
def china_list(status: str = "paid", admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    """Aggregate all items of orders with given status (default: paid) for buying in China."""
    if status not in STATUSES:
        raise HTTPException(422, "Holat noto'g'ri")
    orders = db.query(Order).options(selectinload(Order.items)).filter(Order.status == status) \
        .order_by(Order.id).all()
    s = all_settings(db)
    agg: dict[tuple, dict] = {}
    for o in orders:
        for it in o.items:
            if it.sale_type == "stock":
                continue
            key = (it.product_id, it.size, it.color)
            row = agg.get(key)
            if not row:
                p = db.get(Product, it.product_id) if it.product_id else None
                row = {"product_id": it.product_id, "name": it.name, "size": it.size, "color": it.color,
                       "qty": 0, "orders": [], "price_yuan": p.price_yuan if p else 0,
                       "thumb": thumb_of(p.images[0].path) if p and p.images else None,
                       "supplier_url": get_setting(db, f"supplier:{it.product_id}") if it.product_id else ""}
                agg[key] = row
            row["qty"] += it.qty
            row["orders"].append(o.code)
    items = sorted(agg.values(), key=lambda r: (r["name"], r["size"]))
    total_yuan = sum(r["price_yuan"] * r["qty"] for r in items)
    return {"status": status, "orders_count": len(orders), "order_ids": [o.id for o in orders],
            "items": items, "total_qty": sum(r["qty"] for r in items),
            "total_yuan": round(total_yuan, 2), "total_uzs": int(total_yuan * float(s["yuan_rate"]))}


# ---------------- bulk cargo status ----------------
class BulkStatusIn(BaseModel):
    order_ids: list[int] = Field(min_length=1, max_length=300)
    status: str
    tracking: str = Field(default="", max_length=120)


@router.post("/bulk-status")
def bulk_status(body: BulkStatusIn, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    if body.status not in STATUSES:
        raise HTTPException(422, "Holat noto'g'ri")
    done, skipped = [], []
    for o in db.query(Order).filter(Order.id.in_(body.order_ids)).all():
        if o.status == "cancelled" or o.status == body.status:
            skipped.append(o.code)
            continue
        set_status(db, o, body.status, admin.full_name)
        if body.tracking.strip():
            o.tracking = body.tracking.strip()
        done.append(o.code)
    audit(db, admin, "bulk_status", "order", "", f"{body.status}: {len(done)} ta")
    db.commit()
    return {"updated": len(done), "skipped": len(skipped), "codes": done,
            "status_uz": STATUS_UZ[body.status]}


# ---------------- net profit / finance ----------------
@router.get("/finance")
def finance(days: int = 30, admin: AdminAccount = Depends(stats_perm), db: Session = Depends(get_db)):
    if days not in (7, 30, 90, 365):
        raise HTTPException(422, "Davr noto'g'ri")
    since = datetime.combine((now() - timedelta(days=days - 1)).date(), datetime.min.time())
    s = all_settings(db)
    rate, ship = float(s["yuan_rate"]), float(s["shipping_per_kg"])
    post_fee = int(float(get_setting(db, "post_fee") or 0))
    orders = db.query(Order).options(selectinload(Order.items)).filter(
        Order.created_at >= since, Order.status != "cancelled").all()
    revenue = cost_goods = cost_cargo = discounts = paid = 0
    per_product: dict[int, dict] = {}
    for o in orders:
        revenue += o.total
        discounts += o.discount
        paid += o.paid_amount
        for it in o.items:
            p = db.get(Product, it.product_id) if it.product_id else None
            g = int((p.price_yuan if p else 0) * rate) * it.qty
            c = int((p.weight_kg if p else 0) * ship) * it.qty
            cost_goods += g
            cost_cargo += c
            row = per_product.setdefault(it.product_id or 0, {"name": it.name, "qty": 0, "revenue": 0, "cost": 0})
            row["qty"] += it.qty
            row["revenue"] += it.price * it.qty
            row["cost"] += g + c
    post_total = post_fee * len(orders)
    profit = revenue - cost_goods - cost_cargo - post_total
    top = sorted(({**v, "profit": v["revenue"] - v["cost"]} for v in per_product.values()),
                 key=lambda r: r["profit"], reverse=True)[:10]
    # Order-by-Order Unit Economics Breakdown
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
            "order_details": order_details}


# ---------------- postal label (nakladnoy) ----------------
@router.get("/label/{oid}", response_class=HTMLResponse)
def postal_label(oid: int, admin: AdminAccount = Depends(orders_perm), db: Session = Depends(get_db)):
    o = db.query(Order).options(selectinload(Order.items)).filter_by(id=oid).first()
    if not o:
        raise HTTPException(404, "Buyurtma topilmadi")
    e = html.escape
    remaining = max(0, o.total - o.paid_amount)
    rows = "".join(
        f"<tr><td>{e(i.name)}</td><td>{e(i.size)} {e(i.color)}</td><td>{i.qty}</td>"
        f"<td style='text-align:right'>{fmt_money(i.price * i.qty)}</td></tr>" for i in o.items)
    sender = e(get_setting(db, "contact_username") or "whitmore")
    pay_block = (
        "<div class='ok'>✅ TO'LIQ TO'LANGAN — pochtaga topshirish mumkin</div>" if remaining == 0 else
        f"<div class='warn'>⚠️ QOLGAN TO'LOV: <b>{fmt_money(remaining)}</b><br>"
        "Pochtaga topshirishdan oldin mijozdan undirilsin!</div>")
    page = f"""<!doctype html><html lang="uz"><head><meta charset="utf-8">
<title>Nakladnoy {e(o.code)}</title>
<style>
body{{font-family:Arial,sans-serif;color:#172641;margin:0;padding:24px;background:#f4efe5}}
.sheet{{max-width:720px;margin:0 auto;background:#fff;border:2px solid #172641;padding:24px}}
h1{{font-family:Georgia,serif;letter-spacing:.2em;margin:0;font-size:22px}}
.top{{display:flex;justify-content:space-between;align-items:flex-start;border-bottom:2px dashed #172641;padding-bottom:12px}}
.code{{font-family:monospace;font-size:26px;font-weight:bold;border:2px solid #172641;padding:6px 12px}}
.grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:16px 0}}
.box{{border:1px solid #172641;padding:10px}} .lbl{{font-size:10px;text-transform:uppercase;letter-spacing:.14em;color:#8a6c43;font-weight:bold}}
.big{{font-size:17px;font-weight:bold;margin-top:4px}}
table{{width:100%;border-collapse:collapse;font-size:13px}} td,th{{border-bottom:1px solid #ddd;padding:6px;text-align:left}}
.warn{{margin-top:14px;padding:12px;border:2px solid #a3463c;color:#a3463c;font-size:15px}}
.ok{{margin-top:14px;padding:12px;border:2px solid #397252;color:#397252;font-size:15px;font-weight:bold}}
.sum{{display:flex;justify-content:space-between;margin-top:6px;font-size:14px}}
@media print{{body{{background:#fff;padding:0}} .noprint{{display:none}} .sheet{{border:2px solid #000}}}}
</style></head><body>
<div class="noprint" style="text-align:center;margin-bottom:14px">
<button onclick="window.print()" style="padding:10px 26px;background:#172641;color:#f4efe5;border:0;font-weight:bold;cursor:pointer">🖨 Chop etish</button></div>
<div class="sheet">
<div class="top"><div><h1>WHITMORE</h1><div style="font-size:11px;letter-spacing:.2em">POCHTA NAKLADNOYI · BTS / EMU</div>
<div style="font-size:11px;margin-top:6px">Sana: {fmt_dt(now())}</div></div><div class="code">{e(o.code)}</div></div>
<div class="grid">
<div class="box"><div class="lbl">Qabul qiluvchi</div><div class="big">{e(o.name)}</div><div class="big">{e(o.phone or '-')}</div>
{f"<div>@{e(o.tg_username)}</div>" if o.tg_username else ""}</div>
<div class="box"><div class="lbl">Pochta manzili</div><div class="big">{e(o.city or '-')}</div><div>{e(o.address or '-')}</div></div>
</div>
<div class="box"><div class="lbl">Jo'natuvchi</div><div>WHITMORE Menswear · Telegram: @{sender}</div></div>
<h3 style="margin:16px 0 6px">Posilka tarkibi</h3>
<table><tr><th>Mahsulot</th><th>O'lcham/rang</th><th>Soni</th><th style="text-align:right">Summa</th></tr>{rows}</table>
<div class="sum"><span>Jami:</span><b>{fmt_money(o.total)}</b></div>
<div class="sum"><span>To'langan (avans):</span><b>{fmt_money(o.paid_amount)}</b></div>
{pay_block}
{f"<div style='margin-top:10px'><span class='lbl'>Trek-kod:</span> <b style='font-family:monospace'>{e(o.tracking)}</b></div>" if o.tracking else ""}
{f"<div style='margin-top:8px;font-size:12px'><span class='lbl'>Izoh:</span> {e(o.comment)}</div>" if o.comment else ""}
</div></body></html>"""
    return HTMLResponse(page)


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
