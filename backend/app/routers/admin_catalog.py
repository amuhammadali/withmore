import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import func, or_
from sqlalchemy.orm import Session, selectinload

from ..core import (all_settings, audit, compute_price, fmt_dt, get_setting, price_for,
                    process_upload, recalc_all_prices, set_setting, thumb_of)
from ..db import get_db
from ..models import (AdminAccount, Category, Product, ProductImage, ProductVariant,
                      RestockSubscription, now)
from ..outbox import notify_restock
from ..security import require, require_owner

router = APIRouter(prefix="/api/admin", tags=["admin-catalog"])
products_perm = require("products")
settings_perm = require("settings")

MAX_IMAGES = 6


def product_out(p: Product, detail: bool = True) -> dict:
    out = {
        "id": p.id, "category_id": p.category_id, "name_uz": p.name_uz, "name_ru": p.name_ru,
        "price_uzs": p.price_uzs, "price_yuan": p.price_yuan, "sale_type": p.sale_type,
        "featured": p.featured, "active": p.active, "draft": p.draft, "deleted": p.deleted_at is not None,
        "thumb": thumb_of(p.images[0].path) if p.images else None,
        "stock_total": sum(v.stock for v in p.variants),
    }
    if detail:
        out.update({
            "desc_uz": p.desc_uz, "desc_ru": p.desc_ru, "material": p.material, "size_chart": p.size_chart or [],
            "weight_kg": p.weight_kg, "manual_price": p.manual_price,
            "variants": [{"id": v.id, "size": v.size, "color": v.color, "stock": v.stock} for v in p.variants],
            "images": [{"id": i.id, "path": i.path, "thumb": thumb_of(i.path)} for i in p.images],
        })
    return out


def _load(db: Session, pid: int) -> Product:
    p = db.query(Product).options(selectinload(Product.variants), selectinload(Product.images)) \
        .filter(Product.id == pid).first()
    if not p:
        raise HTTPException(404, "Mahsulot topilmadi")
    return p


# ---------------- categories ----------------
class CategoryIn(BaseModel):
    name_uz: str = Field(min_length=1, max_length=120)
    name_ru: str = ""


def cat_out(db: Session, c: Category):
    n = db.query(func.count(Product.id)).filter(Product.category_id == c.id, Product.deleted_at.is_(None)).scalar()
    return {"id": c.id, "name_uz": c.name_uz, "name_ru": c.name_ru, "sort": c.sort, "products": n}


@router.get("/categories")
def cats(admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    return [cat_out(db, c) for c in db.query(Category).order_by(Category.sort, Category.id)]


@router.post("/categories", status_code=201)
def cat_add(body: CategoryIn, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    mx = db.query(func.max(Category.sort)).scalar() or 0
    c = Category(name_uz=body.name_uz.strip(), name_ru=body.name_ru.strip() or body.name_uz.strip(), sort=mx + 1)
    db.add(c)
    db.flush()
    audit(db, admin, "category_add", "category", c.id, c.name_uz)
    db.commit()
    return cat_out(db, c)


@router.put("/categories/order")
def cat_order(body: dict, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    for i, cid in enumerate(body.get("ids", [])):
        c = db.get(Category, cid)
        if c:
            c.sort = i
    audit(db, admin, "category_reorder", "category")
    db.commit()
    return {"ok": True}


@router.patch("/categories/{cid}")
def cat_edit(cid: int, body: CategoryIn, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    c = db.get(Category, cid) or _nf()
    c.name_uz, c.name_ru = body.name_uz.strip(), body.name_ru.strip() or body.name_uz.strip()
    audit(db, admin, "category_rename", "category", c.id, c.name_uz)
    db.commit()
    return cat_out(db, c)


@router.delete("/categories/{cid}")
def cat_del(cid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    c = db.get(Category, cid) or _nf()
    if db.query(Product).filter(Product.category_id == cid).count():
        raise HTTPException(409, "Kategoriyada mahsulotlar bor, o'chirib bo'lmaydi")
    audit(db, admin, "category_delete", "category", c.id, c.name_uz)
    db.delete(c)
    db.commit()
    return {"ok": True}


def _nf():
    raise HTTPException(404, "Topilmadi")


# ---------------- products ----------------
class VariantIn(BaseModel):
    id: int | None = None
    size: str = Field(default="", max_length=32)
    color: str = Field(default="", max_length=64)
    stock: int = Field(default=0, ge=0)


class ProductIn(BaseModel):
    name_uz: str = Field(min_length=1, max_length=200)
    name_ru: str = ""
    desc_uz: str = ""
    desc_ru: str = ""
    category_id: int | None = None
    material: str = ""
    size_chart: list[dict] = []
    price_yuan: float = Field(default=0, ge=0)
    weight_kg: float = Field(default=1, ge=0)
    manual_price: int | None = Field(default=None, ge=0)
    sale_type: str = "preorder"
    featured: bool = False
    active: bool = True
    variants: list[VariantIn] = []


@router.get("/pricing-params")
def pricing_params(admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    s = all_settings(db)
    return {k: float(s[k]) for k in ("yuan_rate", "shipping_per_kg", "margin_pct")}


@router.get("/products")
def products(q: str = "", category_id: int | None = None, status: str = "all", sale_type: str = "",
             admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    query = db.query(Product).options(selectinload(Product.images), selectinload(Product.variants))
    if status == "deleted":
        query = query.filter(Product.deleted_at.is_not(None))
    else:
        query = query.filter(Product.deleted_at.is_(None))
        if status == "active":
            query = query.filter(Product.active.is_(True), Product.draft.is_(False))
        elif status == "hidden":
            query = query.filter(Product.active.is_(False), Product.draft.is_(False))
        elif status == "draft":
            query = query.filter(Product.draft.is_(True))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if sale_type:
        query = query.filter(Product.sale_type == sale_type)
    if q.strip():
        like = f"%{q.strip()}%"
        query = query.filter(or_(Product.name_uz.ilike(like), Product.name_ru.ilike(like)))
    return [product_out(p, detail=False) for p in query.order_by(Product.id.desc()).limit(500)]


@router.get("/products/{pid}")
def product_get(pid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    return product_out(_load(db, pid))


def _validate(db: Session, body: ProductIn):
    if body.sale_type not in ("preorder", "stock"):
        raise HTTPException(422, "Sotuv turi noto'g'ri")
    if body.category_id and not db.get(Category, body.category_id):
        raise HTTPException(422, "Kategoriya topilmadi")
    if len(body.size_chart) > 20:
        raise HTTPException(422, "O'lchamlar jadvali juda katta")


def _apply(db: Session, p: Product, body: ProductIn):
    p.name_uz, p.name_ru = body.name_uz.strip(), body.name_ru.strip()
    p.desc_uz, p.desc_ru = body.desc_uz, body.desc_ru
    p.category_id, p.material = body.category_id, body.material
    p.size_chart = [{k: str(v)[:20] for k, v in row.items()} for row in body.size_chart]
    p.price_yuan, p.weight_kg = body.price_yuan, body.weight_kg
    p.manual_price = body.manual_price or None
    p.sale_type, p.featured, p.active = body.sale_type, body.featured, body.active
    p.price_uzs = price_for(db, p)


def _sync_variants(db: Session, p: Product, items: list[VariantIn]):
    existing = {v.id: v for v in p.variants}
    keep = set()
    restocked = []
    for it in items:
        v = existing.get(it.id) if it.id else None
        if v:
            if v.stock <= 0 and it.stock > 0:
                restocked.append(v)
            v.size, v.color, v.stock = it.size.strip(), it.color.strip(), it.stock
            keep.add(v.id)
        else:
            v = ProductVariant(size=it.size.strip(), color=it.color.strip(), stock=it.stock)
            p.variants.append(v)
    for vid, v in existing.items():
        if vid not in keep:
            db.query(RestockSubscription).filter_by(variant_id=vid).delete()
            p.variants.remove(v)
    db.flush()
    return restocked


@router.post("/products", status_code=201)
def product_add(body: ProductIn, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    _validate(db, body)
    p = Product()
    db.add(p)
    _apply(db, p, body)
    _sync_variants(db, p, body.variants)
    db.flush()
    audit(db, admin, "product_add", "product", p.id, p.name_uz)
    db.commit()
    return product_out(_load(db, p.id))


@router.put("/products/{pid}")
@router.patch("/products/{pid}")
def product_edit(pid: int, body: ProductIn, admin: AdminAccount = Depends(products_perm),
                 db: Session = Depends(get_db)):
    _validate(db, body)
    p = _load(db, pid)
    _apply(db, p, body)
    restocked = _sync_variants(db, p, body.variants)
    p.draft = False if p.draft and body.name_uz and p.price_uzs > 0 else p.draft
    audit(db, admin, "product_edit", "product", p.id, p.name_uz)
    db.flush()
    for v in restocked:
        if p.active and not p.deleted_at:
            notify_restock(db, v)
    db.commit()
    return product_out(_load(db, p.id))


@router.post("/products/{pid}/duplicate", status_code=201)
def product_dup(pid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    src = _load(db, pid)
    p = Product(category_id=src.category_id, name_uz=src.name_uz + " (nusxa)", name_ru=src.name_ru,
                desc_uz=src.desc_uz, desc_ru=src.desc_ru, material=src.material, size_chart=src.size_chart,
                price_yuan=src.price_yuan, weight_kg=src.weight_kg, manual_price=src.manual_price,
                price_uzs=src.price_uzs, sale_type=src.sale_type, featured=False, active=False)
    for v in src.variants:
        p.variants.append(ProductVariant(size=v.size, color=v.color, stock=v.stock))
    for i in src.images:
        p.images.append(ProductImage(path=i.path, sort=i.sort))  # shares files
    db.add(p)
    db.flush()
    audit(db, admin, "product_duplicate", "product", p.id, f"from {src.id}")
    db.commit()
    return product_out(_load(db, p.id))


class BulkIn(BaseModel):
    ids: list[int]
    action: str  # hide | show | delete | restore


def _act(p: Product, action: str):
    if action == "hide":
        p.active = False
    elif action == "show":
        p.active = True
        p.draft = False
    elif action == "delete":
        p.deleted_at = now()
    elif action == "restore":
        p.deleted_at = None
    else:
        raise HTTPException(422, "Amal noto'g'ri")


@router.post("/products/bulk")
def product_bulk(body: BulkIn, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    n = 0
    for p in db.query(Product).filter(Product.id.in_(body.ids)).all():
        _act(p, body.action)
        n += 1
    audit(db, admin, f"product_bulk_{body.action}", "product", "", f"ids={body.ids}")
    db.commit()
    return {"count": n}


@router.post("/products/{pid}/toggle")
def product_toggle(pid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    p = _load(db, pid)
    _act(p, "hide" if p.active else "show")
    audit(db, admin, "product_toggle", "product", p.id, f"active={p.active}")
    db.commit()
    return product_out(p, detail=False)


@router.delete("/products/{pid}")
def product_delete(pid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    p = _load(db, pid)
    p.deleted_at = now()
    audit(db, admin, "product_delete", "product", p.id, p.name_uz)
    db.commit()
    return {"ok": True}


@router.post("/products/{pid}/restore")
def product_restore(pid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    p = _load(db, pid)
    p.deleted_at = None
    audit(db, admin, "product_restore", "product", p.id, p.name_uz)
    db.commit()
    return product_out(p, detail=False)


# ---------------- images ----------------
@router.post("/products/{pid}/images")
async def image_add(
    pid: int,
    files: list[UploadFile] = File(default=[]),
    file: UploadFile | None = File(default=None),
    admin: AdminAccount = Depends(products_perm),
    db: Session = Depends(get_db)
):
    upload_list = list(files)
    if file is not None:
        upload_list.append(file)
    if not upload_list:
        raise HTTPException(422, "Kamida 1 ta rasm yuklang")
    p = _load(db, pid)
    if len(p.images) + len(upload_list) > MAX_IMAGES:
        raise HTTPException(422, f"Ko'pi bilan {MAX_IMAGES} ta rasm")
    for f in upload_list:
        up = await process_upload(f, db, admin.id)
        p.images.append(ProductImage(path=up.path, sort=len(p.images)))
    audit(db, admin, "product_images_add", "product", p.id, f"{len(upload_list)} files")
    db.commit()
    return product_out(_load(db, pid))


@router.put("/products/{pid}/images/order")
def image_order(pid: int, body: dict, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    p = _load(db, pid)
    by_id = {i.id: i for i in p.images}
    for n, iid in enumerate(body.get("ids", [])):
        if iid in by_id:
            by_id[iid].sort = n
    audit(db, admin, "product_images_reorder", "product", p.id)
    db.commit()
    return product_out(_load(db, pid))


@router.delete("/products/{pid}/images/{iid}")
def image_del(pid: int, iid: int, admin: AdminAccount = Depends(products_perm), db: Session = Depends(get_db)):
    p = _load(db, pid)
    img = next((i for i in p.images if i.id == iid), None)
    if not img:
        raise HTTPException(404, "Rasm topilmadi")
    p.images.remove(img)
    for n, i in enumerate(p.images):
        i.sort = n
    audit(db, admin, "product_image_delete", "product", p.id)
    db.commit()
    return product_out(_load(db, pid))


# ---------------- quick add ----------------
@router.post("/products/quick", status_code=201)
async def quick_add(files: list[UploadFile] = File(...), admin: AdminAccount = Depends(products_perm),
                    db: Session = Depends(get_db)):
    if len(files) > 50:
        raise HTTPException(422, "Bir vaqtda ko'pi bilan 50 ta rasm")
    out = []
    for f in files:
        up = await process_upload(f, db, admin.id)
        p = Product(name_uz="", active=False, draft=True, price_yuan=0, weight_kg=1.0)
        p.images.append(ProductImage(path=up.path, sort=0))
        p.variants.append(ProductVariant(size="STD", color="", stock=0))
        db.add(p)
        db.flush()
        out.append(p)
    audit(db, admin, "product_quick_add", "product", "", f"{len(out)} drafts")
    db.commit()
    return [product_out(_load(db, p.id), detail=False) for p in out]


class PublishIn(BaseModel):
    name_uz: str = Field(min_length=1, max_length=200)
    price_yuan: float = Field(gt=0)


@router.post("/products/{pid}/publish")
def quick_publish(pid: int, body: PublishIn, admin: AdminAccount = Depends(products_perm),
                  db: Session = Depends(get_db)):
    p = _load(db, pid)
    p.name_uz, p.price_yuan = body.name_uz.strip(), body.price_yuan
    p.price_uzs = price_for(db, p)
    p.draft, p.active = False, True
    audit(db, admin, "product_publish", "product", p.id, p.name_uz)
    db.commit()
    return product_out(p, detail=False)


# ---------------- settings ----------------
SETTING_KEYS = ["yuan_rate", "margin_pct", "shipping_per_kg", "advance_pct", "low_stock",
                "payment_card_number", "payment_card_holder",
                "notify_admin_order", "notify_admin_lowstock", "notify_customer_status",
                "notify_customer_restock",
                "brand_name", "brand_slogan_uz", "brand_slogan_ru", "brand_color", "brand_accent",
                "contact_phone", "contact_username", "instagram_username", "post_operators", "post_fee"]
NUMERIC = {"yuan_rate", "margin_pct", "shipping_per_kg", "advance_pct", "low_stock", "post_fee"}


@router.get("/settings")
def settings_get(admin: AdminAccount = Depends(settings_perm), db: Session = Depends(get_db)):
    s = all_settings(db)
    return {k: s[k] for k in SETTING_KEYS}


@router.put("/settings")
def settings_put(body: dict, admin: AdminAccount = Depends(settings_perm), db: Session = Depends(get_db)):
    changed = {}
    for k, v in body.items():
        if k not in SETTING_KEYS:
            continue
        v = str(v).strip()
        if k in NUMERIC:
            try:
                if float(v) < 0:
                    raise ValueError
            except ValueError:
                raise HTTPException(422, f"{k}: noto'g'ri qiymat")
        set_setting(db, k, v)
        changed[k] = v
    db.flush()
    recalc_all_prices(db)
    audit(db, admin, "settings_change", "settings", "", json.dumps(changed))
    db.commit()
    return settings_get(admin, db)


# ---------------- content (owner only) ----------------
CONTENT_KEYS = ["hero_title_uz", "hero_title_ru", "hero_text_uz", "hero_text_ru", "about_uz", "about_ru",
                "delivery_uz", "delivery_ru", "returns_uz", "returns_ru", "faq", "contact_username"]


@router.get("/content")
def content_get(owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    s = all_settings(db)
    out = {k: s[k] for k in CONTENT_KEYS + ["hero_image"]}
    out["faq"] = json.loads(out["faq"] or "[]")
    return out


@router.put("/content")
def content_put(body: dict, owner: AdminAccount = Depends(require_owner), db: Session = Depends(get_db)):
    for k in CONTENT_KEYS:
        if k in body:
            v = body[k]
            if k == "faq":
                if not isinstance(v, list):
                    raise HTTPException(422, "FAQ noto'g'ri")
                v = json.dumps([{kk: str(x.get(kk, ""))[:2000] for kk in ("q_uz", "a_uz", "q_ru", "a_ru")}
                                for x in v], ensure_ascii=False)
            if k == "contact_username":
                v = str(v).strip().lstrip("@")
            set_setting(db, k, str(v))
    audit(db, owner, "content_change", "content")
    db.commit()
    return content_get(owner, db)


@router.post("/content/hero-image")
async def hero_image(file: UploadFile = File(...), owner: AdminAccount = Depends(require_owner),
                     db: Session = Depends(get_db)):
    up = await process_upload(file, db, owner.id, subdir="content", max_side=1800)
    set_setting(db, "hero_image", up.path)
    audit(db, owner, "hero_image_change", "content")
    db.commit()
    return {"hero_image": up.path}
