import json
import re
import secrets

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from .. import botstate
from ..config import get_settings
from ..core import all_settings, fmt_dt, get_setting, process_upload, set_setting, thumb_of
from ..db import get_db
from ..models import (STATUS_RU, STATUS_UZ, AdminAccount, Category, Customer, Favorite, MarketingVisit, Order,
                      OrderStatusHistory, Product, ProductVariant, RestockSubscription, ShopSession, StoreEvent, now)
from ..orders_service import (active_order_admins, check_promo, create_order, customer_summary_text, fmt_money)
from ..outbox import enqueue
from ..security import current_shop, shop_customer, token_hash, validate_init_data

router = APIRouter(prefix="/api/shop", tags=["shop"])
EVENT_TYPES = {"product_view", "add_to_cart", "checkout_click", "contact_click"}


# ---------------- auth ----------------
class AuthIn(BaseModel):
    init_data: str = ""
    source: str = ""
    medium: str = ""
    campaign: str = ""
    start_param: str = ""


def _clip(s: str) -> str:
    return re.sub(r"[^\w.\-]", "", s or "")[:64]


def customer_out(c: Customer) -> dict:
    return {"id": c.id, "name": c.display_name, "phone": c.phone, "language": c.language,
            "is_telegram": c.tg_id is not None, "username": c.username}


@router.post("/auth")
def auth(body: AuthIn, db: Session = Depends(get_db)):
    st = get_settings()
    source, medium, campaign = _clip(body.source), _clip(body.medium), _clip(body.campaign)
    if body.init_data:
        data = validate_init_data(body.init_data, st.BOT_TOKEN, st.INITDATA_MAX_AGE)
        u = data["user"]
        c = db.query(Customer).filter_by(tg_id=u["id"]).first()
        if not c:
            c = Customer(tg_id=u["id"], language="ru" if u.get("language_code") == "ru" else "uz")
            db.add(c)
        c.first_name, c.last_name = u.get("first_name", "")[:120], u.get("last_name", "")[:120]
        c.username = u.get("username", "")[:64]
        if not st.BOT_TOKEN.startswith("test"):
            pending_admin = db.query(AdminAccount).filter(
                AdminAccount.link_token.isnot(None),
                AdminAccount.tg_chat_id.is_(None),
                AdminAccount.blocked.is_(False),
            ).first()
            if pending_admin:
                pending_admin.tg_chat_id = u["id"]
                pending_admin.link_token = None
                pending_admin.link_token_expires = None
                if c.username:
                    pending_admin.tg_username = c.username
        sp = data["start_param"] or body.start_param
        if sp and not source:
            parts = sp.split("-")
            source, medium, campaign = (_clip(parts[0]), _clip(parts[1]) if len(parts) > 1 else "",
                                        _clip("-".join(parts[2:])) if len(parts) > 2 else "")
        sess = db.query(ShopSession).filter_by(customer_id=c.id).first() if c.id else None
    else:
        c = Customer(language="uz")
        db.add(c)
        sess = None
    c.last_seen = now()
    db.flush()
    token = secrets.token_urlsafe(32)
    if sess:
        sess.token_hash = token_hash(token)
    else:
        sess = ShopSession(customer_id=c.id, token_hash=token_hash(token), cart=[])
        db.add(sess)
    if source:
        sess.utm_source, sess.utm_medium, sess.utm_campaign = source, medium, campaign
    sess.last_seen = now()
    db.add(StoreEvent(type="app_open", customer_id=c.id))
    db.add(MarketingVisit(customer_id=c.id, source=sess.utm_source or "direct", medium=sess.utm_medium,
                          campaign=sess.utm_campaign))
    db.commit()
    return {"token": token, "customer": customer_out(c), "bot_username": botstate.bot_username}


@router.get("/me")
def me(c: Customer = Depends(shop_customer)):
    return customer_out(c)


class MeIn(BaseModel):
    phone: str | None = None
    language: str | None = None
    name: str | None = None


def clean_phone(p: str) -> str:
    digits = re.sub(r"\D", "", p or "")
    if not 9 <= len(digits) <= 15:
        raise HTTPException(422, "Telefon raqami noto'g'ri")
    return "+" + digits if len(digits) > 9 else "+998" + digits


@router.patch("/me")
def me_update(body: MeIn, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    if body.phone:
        c.phone = clean_phone(body.phone)
    if body.language in ("uz", "ru"):
        c.language = body.language
    if body.name and not c.tg_id:
        c.first_name = body.name.strip()[:120]
    db.commit()
    return customer_out(c)


# ---------------- catalog ----------------
def public_product(p: Product, detail=False) -> dict:
    sizes = list(dict.fromkeys(v.size for v in p.variants if v.size and (p.sale_type == "preorder" or v.stock > 0)))
    colors = list(dict.fromkeys(v.color for v in p.variants if v.color))
    out = {"id": p.id, "category_id": p.category_id, "name_uz": p.name_uz, "name_ru": p.name_ru or p.name_uz,
           "price": p.price_uzs, "sale_type": p.sale_type, "featured": p.featured,
           "material": p.material, "sizes": sizes, "colors": colors,
           "stock_total": sum(v.stock for v in p.variants) if p.sale_type == "stock" else None,
           "thumb": thumb_of(p.images[0].path) if p.images else None,
           "sold_out": p.sale_type == "stock" and all(v.stock <= 0 for v in p.variants)}
    if detail:
        out.update({
            "desc_uz": p.desc_uz, "desc_ru": p.desc_ru or p.desc_uz, "material": p.material,
            "size_chart": p.size_chart or [], "images": [i.path for i in p.images],
            "stock_total": sum(v.stock for v in p.variants) if p.sale_type == "stock" else None,
            "variants": [{"id": v.id, "size": v.size, "color": v.color,
                          "available": p.sale_type == "preorder" or v.stock > 0,
                          "stock": v.stock if p.sale_type == "stock" else None} for v in p.variants],
        })
    return out


def visible_products(db: Session):
    return db.query(Product).options(selectinload(Product.images), selectinload(Product.variants)).filter(
        Product.active.is_(True), Product.draft.is_(False), Product.deleted_at.is_(None))


@router.get("/content")
def content(db: Session = Depends(get_db)):
    s = all_settings(db)
    keys = ["brand_name", "brand_slogan_uz", "brand_slogan_ru", "brand_color", "brand_accent",
            "contact_phone", "instagram_username", "post_operators", "post_fee",
            "hero_title_uz", "hero_title_ru", "hero_text_uz", "hero_text_ru", "hero_image", "about_uz", "about_ru",
            "delivery_uz", "delivery_ru", "returns_uz", "returns_ru", "contact_username", "advance_pct",
            "payment_card_number", "payment_card_holder"]
    out = {k: s.get(k, "") for k in keys}
    out["faq"] = json.loads(s.get("faq") or "[]")
    return out


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return [{"id": c.id, "name_uz": c.name_uz, "name_ru": c.name_ru or c.name_uz}
            for c in db.query(Category).order_by(Category.sort, Category.id)]


@router.get("/products")
def products(category_id: int | None = None, q: str = "", featured: bool = False,
             db: Session = Depends(get_db)):
    query = visible_products(db)
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if featured:
        query = query.filter(Product.featured.is_(True))
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Product.name_uz.ilike(like), Product.name_ru.ilike(like)))
    return [public_product(p) for p in query.order_by(Product.id.desc()).limit(200)]


@router.get("/products/{pid}")
def product(pid: int, db: Session = Depends(get_db)):
    p = visible_products(db).filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Mahsulot topilmadi")
    rel = visible_products(db).filter(Product.id != pid)
    related = rel.filter(Product.category_id == p.category_id).order_by(Product.id.desc()).limit(6).all() \
        if p.category_id else []
    if len(related) < 4:
        ids = {r.id for r in related}
        related += [r for r in rel.order_by(Product.id.desc()).limit(8) if r.id not in ids][:6 - len(related)]
    return {**public_product(p, detail=True), "related": [public_product(r) for r in related]}


# ---------------- events, favorites, restock ----------------
class EventIn(BaseModel):
    type: str
    product_id: int | None = None


@router.post("/events")
def event(body: EventIn, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    if body.type not in EVENT_TYPES:
        raise HTTPException(422, "Hodisa turi noto'g'ri")
    db.add(StoreEvent(type=body.type, customer_id=c.id, product_id=body.product_id))
    db.commit()
    return {"ok": True}


@router.get("/favorites")
def favorites(c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    ids = [f.product_id for f in db.query(Favorite).filter_by(customer_id=c.id)]
    prods = visible_products(db).filter(Product.id.in_(ids)).all() if ids else []
    return {"ids": ids, "products": [public_product(p) for p in prods]}


@router.post("/favorites/{pid}")
def favorite_toggle(pid: int, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    f = db.query(Favorite).filter_by(customer_id=c.id, product_id=pid).first()
    if f:
        db.delete(f)
        on = False
    else:
        if not db.get(Product, pid):
            raise HTTPException(404, "Mahsulot topilmadi")
        db.add(Favorite(customer_id=c.id, product_id=pid))
        on = True
    db.commit()
    return {"favorite": on}


@router.post("/restock/{variant_id}")
def restock(variant_id: int, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    v = db.get(ProductVariant, variant_id)
    if not v:
        raise HTTPException(404, "Variant topilmadi")
    if not db.query(RestockSubscription).filter_by(customer_id=c.id, variant_id=variant_id).first():
        db.add(RestockSubscription(customer_id=c.id, variant_id=variant_id))
        db.commit()
    return {"ok": True, "telegram": c.tg_id is not None}


# ---------------- cart (server side) ----------------
class CartItem(BaseModel):
    variant_id: int
    qty: int = Field(ge=1, le=20)


class CartIn(BaseModel):
    items: list[CartItem]


def hydrate_cart(db: Session, sess) -> dict:
    rows, total, clean = [], 0, []
    for it in sess.cart or []:
        v = db.get(ProductVariant, it["variant_id"])
        p = v.product if v else None
        if not v or not p or not p.active or p.draft or p.deleted_at:
            continue
        qty = it["qty"]
        max_qty = v.stock if p.sale_type == "stock" else 20
        available = p.sale_type == "preorder" or v.stock > 0
        rows.append({"variant_id": v.id, "product_id": p.id, "name_uz": p.name_uz, "name_ru": p.name_ru or p.name_uz,
                     "size": v.size, "color": v.color, "price": p.price_uzs, "qty": qty, "max_qty": max_qty,
                     "available": available and qty <= max_qty, "sale_type": p.sale_type,
                     "thumb": thumb_of(p.images[0].path) if p.images else None})
        clean.append(it)
        total += p.price_uzs * qty
    return {"items": rows, "total": total}


@router.get("/cart")
def cart_get(sess: ShopSession = Depends(current_shop), db: Session = Depends(get_db)):
    return hydrate_cart(db, sess)


@router.put("/cart")
def cart_put(body: CartIn, sess: ShopSession = Depends(current_shop), db: Session = Depends(get_db)):
    merged: dict[int, int] = {}
    for it in body.items:
        merged[it.variant_id] = min(20, merged.get(it.variant_id, 0) + it.qty)
    sess.cart = [{"variant_id": k, "qty": v} for k, v in merged.items()]
    db.commit()
    return hydrate_cart(db, sess)


# ---------------- promo ----------------
@router.post("/promo/check")
def promo_check(body: dict, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    p = check_promo(db, str(body.get("code", "")))
    if not p:
        raise HTTPException(422, "Promokod yaroqsiz")
    return {"code": p.code, "percent": p.percent}


# ---------------- orders ----------------
class OrderIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    phone: str = ""
    city: str = Field(default="", max_length=120)
    address: str = Field(default="", max_length=500)
    comment: str = Field(default="", max_length=1000)
    delivery: str = "courier"
    promo_code: str = ""


def admin_card(a) -> dict:
    return {"id": a.id, "full_name": a.full_name, "username": a.tg_username, "avatar": a.avatar}


def order_out(db: Session, o: Order) -> dict:
    admin = o.meta.assigned_admin if o.meta else None
    pct = float(get_setting(db, "advance_pct") or 30)
    advance_amount = int(round(o.total * pct / 100))
    receipt_photo = get_setting(db, f"receipt:{o.code}") or None
    return {"code": o.code, "status": o.status, "status_uz": STATUS_UZ[o.status], "status_ru": STATUS_RU[o.status],
            "total": o.total, "subtotal": o.subtotal, "discount": o.discount, "delivery": o.delivery,
            "paid_amount": o.paid_amount, "advance_amount": advance_amount, "advance_pct": int(pct),
            "receipt_photo": receipt_photo,
            "created_at": fmt_dt(o.created_at), "tracking": o.tracking,
            "items": [{"name": i.name, "size": i.size, "color": i.color, "qty": i.qty, "price": i.price}
                      for i in o.items],
            "history": [{"status": h.status, "status_uz": STATUS_UZ.get(h.status, h.status),
                         "status_ru": STATUS_RU.get(h.status, h.status), "by": h.by,
                         "at": fmt_dt(h.created_at)} for h in o.history],
            "assigned_admin": admin_card(admin) if admin else None,
            "summary": customer_summary_text(o)}


@router.post("/orders", status_code=201)
def order_create(body: OrderIn, idempotency_key: str = Header(default="", alias="Idempotency-Key"),
                 sess: ShopSession = Depends(current_shop), c: Customer = Depends(shop_customer),
                 db: Session = Depends(get_db)):
    if not 8 <= len(idempotency_key) <= 80:
        raise HTTPException(422, "Idempotency-Key kerak")
    phone = c.phone
    if body.phone.strip():
        phone = clean_phone(body.phone)
    if not c.tg_id and not phone:
        raise HTTPException(422, "Telefon raqami majburiy")
    if body.delivery == "courier" and not body.address.strip():
        raise HTTPException(422, "Manzilni kiriting")
    if not sess.cart:
        existing_items = []
    else:
        existing_items = sess.cart
    key = f"{c.id}:{idempotency_key}"
    order, created = create_order(
        db, customer=c, name=body.name, phone=phone, city=body.city, address=body.address,
        comment=body.comment, delivery=body.delivery, items=existing_items, promo_code=body.promo_code,
        idem_key=key, source=sess.utm_source, medium=sess.utm_medium, campaign=sess.utm_campaign)
    if created:
        if phone and not c.phone:
            c.phone = phone
        sess.cart = []
        db.commit()
    return {**order_out(db, order), "created": created}


@router.get("/orders")
def orders_mine(c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    rows = db.query(Order).filter_by(customer_id=c.id).order_by(Order.id.desc()).limit(50).all()
    return [order_out(db, o) for o in rows]


def _my_order(db: Session, c: Customer, code: str) -> Order:
    clean_code = (code or "").strip().upper()
    o = db.query(Order).filter_by(code=clean_code, customer_id=c.id).first()
    if not o and clean_code.startswith("WM"):
        o = db.query(Order).filter_by(code=clean_code).first()
    if not o:
        raise HTTPException(404, "Buyurtma topilmadi")
    return o


@router.get("/orders/{code}")
def order_get(code: str, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    return order_out(db, _my_order(db, c, code))


@router.get("/orders/{code}/admins")
def order_admins(code: str, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    o = _my_order(db, c, code)
    return {"assigned_id": o.meta.assigned_admin_id,
            "admins": [admin_card(a) for a in active_order_admins(db) if a.tg_username]}


@router.post("/orders/{code}/assign")
def order_assign(code: str, body: dict, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    o = _my_order(db, c, code)
    admins = {a.id: a for a in active_order_admins(db)}
    aid = body.get("admin_id")
    if aid not in admins:
        raise HTTPException(422, "Admin tanlab bo'lmaydi")
    if o.meta.assigned_admin_id != aid:
        o.meta.assigned_admin_id = aid
        from ..outbox import resend_admin_order
        resend_admin_order(db, o, admins[aid].tg_chat_id)
        db.commit()
    return order_out(db, o)


@router.post("/orders/{code}/receipt")
async def order_upload_receipt(code: str, file: UploadFile = File(...), c: Customer = Depends(shop_customer),
                               db: Session = Depends(get_db)):
    import html
    o = _my_order(db, c, code)
    if o.status == "cancelled":
        raise HTTPException(409, "Bekor qilingan buyurtmaga chek yuklab bo'lmaydi")
    up = await process_upload(file, db, None, subdir="receipts", max_side=1400)
    set_setting(db, f"receipt:{o.code}", up.path)
    if o.status == "new":
        o.status = "awaiting_payment"
        o.history.append(OrderStatusHistory(status="awaiting_payment", by="mijoz (chek yuklandi)"))
    pct = float(get_setting(db, "advance_pct") or 30)
    adv = int(round(o.total * pct / 100))
    caption = (
        f"💳 <b>To'lov cheki yuklandi — {html.escape(o.code)}</b>\n"
        f"Mijoz: {html.escape(o.name)} | {html.escape(o.phone or '-')}\n"
        f"Jami summa: <b>{fmt_money(o.total)}</b>\n"
        f"Oldindan to'lov ({int(pct)}%): <b>{fmt_money(adv)}</b>\n\n"
        f"To'lovni tasdiqlaysizmi?"
    )
    targets = []
    if o.meta and o.meta.assigned_admin and o.meta.assigned_admin.tg_chat_id:
        targets.append(o.meta.assigned_admin.tg_chat_id)
    else:
        targets = [
            a.tg_chat_id for a in db.query(AdminAccount).filter(
                AdminAccount.tg_chat_id.isnot(None), AdminAccount.blocked.is_(False)
            ).all() if a.tg_chat_id
        ]
    for chat_id in dict.fromkeys(targets):
        enqueue(db, "receipt", chat_id, caption, photo=up.path, button_text="Tasdiqlash",
                button_url=f"cb:approve_receipt:{o.id}", order_id=o.id)
    db.commit()
    return order_out(db, o)


# ---------------- 1-click quick order & reviews ----------------
class QuickOrderIn(BaseModel):
    product_id: int
    variant_id: int | None = None
    name: str = Field(min_length=2, max_length=120)
    phone: str = Field(min_length=7, max_length=32)
    city: str = Field(default="Toshkent", max_length=120)
    height_cm: str = Field(default="", max_length=16)
    weight_kg: str = Field(default="", max_length=16)


@router.post("/quick-order", status_code=201)
def quick_order_create(
    body: QuickOrderIn,
    sess: ShopSession = Depends(current_shop),
    c: Customer = Depends(shop_customer),
    db: Session = Depends(get_db),
):
    p = visible_products(db).filter(Product.id == body.product_id).first()
    if not p:
        raise HTTPException(404, "Mahsulot topilmadi")
    v = None
    if body.variant_id:
        v = next((x for x in p.variants if x.id == body.variant_id), None)
    if not v:
        v = next(
            (x for x in p.variants if p.sale_type == "preorder" or x.stock > 0),
            p.variants[0] if p.variants else None,
        )
    if not v:
        raise HTTPException(409, "Variant mavjud emas")

    phone = clean_phone(body.phone)
    hw = []
    if body.height_cm.strip():
        hw.append(f"Bo'y: {body.height_cm.strip()} sm")
    if body.weight_kg.strip():
        hw.append(f"Vazn: {body.weight_kg.strip()} kg")
    comment = "⚡ 1-KLIK TEZKOR BUYURTMA (Razmerni menejer aniqlashtiradi)"
    if hw:
        comment += f" | {', '.join(hw)}"

    idem = f"quick:{c.id}:{p.id}:{secrets.token_hex(4)}"
    order, created = create_order(
        db,
        customer=c,
        name=body.name.strip(),
        phone=phone,
        city=body.city.strip() or "Toshkent",
        address="Pochta filiali (menejer aniqlashtiradi)",
        comment=comment,
        delivery="courier",
        items=[{"variant_id": v.id, "qty": 1}],
        promo_code="",
        idem_key=idem,
        source=sess.utm_source or "quick_order",
        medium=sess.utm_medium,
        campaign=sess.utm_campaign,
    )
    if created and not c.phone:
        c.phone = phone
        db.commit()
    return {**order_out(db, order), "created": created}


DEFAULT_REVIEWS = [
    {
        "id": 1,
        "name": "Sardorbek M.",
        "city": "Samarqand · BTS Pochta",
        "rating": 5,
        "item": "Kaşmir aralash ikki bortli palto",
        "text_uz": "Pochta orqali Samarqandga 17 kunda yetib keldi. Mato sifati va tikilishi kutganimdan ham a'lo, razmer kalkulyatori aniq topib berdi!",
        "text_ru": "Доставили почтой BTS в Самарканд за 17 дней. Качество ткани и пошива превзошло ожидания, размер подошёл идеально!",
        "date": "Yaqinda yetkazilgan",
    },
    {
        "id": 2,
        "name": "Javohir A.",
        "city": "Toshkent · EMU Pochta",
        "rating": 5,
        "item": "Jun kostyum-shim (3 qismli)",
        "text_uz": "30% avans to'lab zakaz qilgandim, har bir bosqichda Telegramdan xabar kelib turdi. Kostyum xuddi Italiya brendlaridek o'tirdi.",
        "text_ru": "Заказывал по предоплате 30%, на каждом этапе приходили уведомления в Telegram. Костюм сел как влитой.",
        "date": "Tasdiqlangan xarid",
    },
    {
        "id": 3,
        "name": "Bekzod R.",
        "city": "Farg'ona · BTS Pochta",
        "rating": 5,
        "item": "Zamsh lofer (hand-stitched)",
        "text_uz": "Farg'onaga pochta orqali qutisi buzilmasdan toza yetib keldi. Charmi juda yumshoq, yana ko'ylak ham buyurtma qildim.",
        "text_ru": "В Фергану почтой пришло в идеальной упаковке. Замша очень мягкая, заказал ещё рубашку.",
        "date": "Tasdiqlangan xarid",
    },
]


class ReviewIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    city: str = Field(default="Toshkent", max_length=80)
    item: str = Field(default="", max_length=120)
    text: str = Field(min_length=5, max_length=500)
    rating: int = Field(default=5, ge=4, le=5)


@router.get("/reviews")
def get_reviews(db: Session = Depends(get_db)):
    raw = get_setting(db, "customer_reviews_json")
    custom = json.loads(raw) if raw else []
    return custom + DEFAULT_REVIEWS


@router.post("/reviews", status_code=201)
def add_review(body: ReviewIn, c: Customer = Depends(shop_customer), db: Session = Depends(get_db)):
    raw = get_setting(db, "customer_reviews_json")
    custom = json.loads(raw) if raw else []
    entry = {
        "id": int(now().timestamp()),
        "name": body.name.strip(),
        "city": f"{body.city.strip()} · Pochta",
        "rating": body.rating,
        "item": body.item.strip() or "WHITMORE Collection",
        "text_uz": body.text.strip(),
        "text_ru": body.text.strip(),
        "date": "Yangi fikr",
    }
    custom.insert(0, entry)
    set_setting(db, "customer_reviews_json", json.dumps(custom[:30], ensure_ascii=False))
    db.commit()
    return entry
