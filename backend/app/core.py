"""Settings access, price formula, audit helper, image processing."""
import json
import uuid
from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session

from .config import get_settings
from .models import AdminAccount, AdminAudit, ImageUpload, Product, Setting

DEFAULTS = {
    "brand_name": "WHITMORE",
    "brand_slogan_uz": "Klassik erkaklar kiyimi",
    "brand_slogan_ru": "Классическая мужская одежда",
    "brand_color": "#172641",
    "brand_accent": "#d6bd92",
    "contact_phone": "+998 90 123 45 67",
    "instagram_username": "whitmore.uz",
    "post_operators": "BTS / EMU",
    "post_fee": "0",
    "yuan_rate": "1750", "margin_pct": "25", "shipping_per_kg": "65000", "advance_pct": "30",
    "low_stock": "3",
    "payment_card_number": "8600 1234 5678 9012",
    "payment_card_holder": "WHITMORE MENSWEAR",
    "notify_admin_order": "1", "notify_admin_lowstock": "1",
    "notify_customer_status": "1", "notify_customer_restock": "1",
    "contact_username": "whitmore_admin",
    "hero_title_uz": "Klassik erkaklar kiyimi", "hero_title_ru": "Классическая мужская одежда",
    "hero_text_uz": "Xitoydan buyurtma asosida. Sifat, sokin uslub, aniq narx.",
    "hero_text_ru": "Под заказ из Китая. Качество, спокойный стиль, честная цена.",
    "hero_image": "",
    "about_uz": "Whitmore — klassik erkaklar kiyimi brendi. Biz tanlangan modellarni Xitoydan buyurtma asosida olib kelamiz va O'zbekiston bo'ylab yetkazamiz.",
    "about_ru": "Whitmore — бренд классической мужской одежды. Мы привозим отобранные модели из Китая под заказ и доставляем по Узбекистану.",
    "delivery_uz": "Buyurtma Xitoydan 14-25 kun ichida keladi. O'zbekiston bo'ylab barcha viloyatlarga faqat pochta orqali (BTS / EMU) jo'natamiz. Oldindan to'lov — 30%, qolgan qismi pochtaga topshirishdan oldin to'lanadi.",
    "delivery_ru": "Заказ приходит из Китая за 14-25 дней. Отправляем по всему Узбекистану только почтой (BTS / EMU). Предоплата — 30%, остаток оплачивается перед отправкой почтой.",
    "returns_uz": "O'lcham mos kelmasa, mahsulot kiyilmagan holatda 3 kun ichida almashtiriladi. Buyurtma asosida olib kelingan mahsulotlar uchun to'lov qaytarilmaydi.",
    "returns_ru": "Если размер не подошёл, товар в нетронутом виде можно обменять в течение 3 дней. Предоплата за товары под заказ не возвращается.",
    "faq": json.dumps([
        {"q_uz": "Buyurtma qancha vaqtda keladi?", "a_uz": "Odatda 14-25 kun.",
         "q_ru": "Как долго идёт заказ?", "a_ru": "Обычно 14-25 дней."},
        {"q_uz": "To'lov qanday amalga oshiriladi?", "a_uz": "Admin siz bilan bog'lanib, to'lov usulini kelishadi.",
         "q_ru": "Как оплатить?", "a_ru": "Администратор свяжется с вами и согласует способ оплаты."},
    ], ensure_ascii=False),
}


def get_setting(db: Session, key: str) -> str:
    row = db.get(Setting, key)
    return row.value if row else DEFAULTS.get(key, "")


def all_settings(db: Session) -> dict:
    out = dict(DEFAULTS)
    for r in db.query(Setting).all():
        out[r.key] = r.value
    return out


def set_setting(db: Session, key: str, value: str):
    row = db.get(Setting, key)
    if row:
        row.value = value
    else:
        db.add(Setting(key=key, value=value))


# ---------- pricing ----------
def round_1000(x: float) -> int:
    return int((x + 500) // 1000 * 1000)


def compute_price(price_yuan: float, weight_kg: float, yuan_rate: float, shipping_per_kg: float,
                  margin_pct: float, manual: int | None = None) -> int:
    if manual:
        return int(manual)
    base = price_yuan * yuan_rate + weight_kg * shipping_per_kg
    return round_1000(base * (1 + margin_pct / 100))


def price_for(db: Session, p: Product) -> int:
    s = all_settings(db)
    return compute_price(p.price_yuan, p.weight_kg, float(s["yuan_rate"]), float(s["shipping_per_kg"]),
                         float(s["margin_pct"]), p.manual_price)


def recalc_all_prices(db: Session):
    s = all_settings(db)
    args = (float(s["yuan_rate"]), float(s["shipping_per_kg"]), float(s["margin_pct"]))
    for p in db.query(Product).all():
        p.price_uzs = compute_price(p.price_yuan, p.weight_kg, *args, p.manual_price)


# ---------- audit ----------
def audit(db: Session, admin: AdminAccount | None, action: str, entity: str = "", entity_id="", detail: str = ""):
    db.add(AdminAudit(admin_id=admin.id if admin else None, admin_name=admin.full_name if admin else "system",
                      action=action, entity=entity, entity_id=str(entity_id), detail=detail[:2000]))


# ---------- images ----------
MAX_BYTES = 10 * 1024 * 1024
ALLOWED = {"JPEG", "PNG", "WEBP"}


def upload_root() -> Path:
    p = Path(get_settings().UPLOAD_DIR)
    p.mkdir(parents=True, exist_ok=True)
    return p


def process_image_bytes(data: bytes, original_name: str, db: Session, admin_id: int | None,
                        subdir: str = "products", max_side: int = 1600) -> ImageUpload:
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "Rasm 10 MB dan oshmasligi kerak")
    try:
        probe = Image.open(BytesIO(data))
        fmt = probe.format
        probe.verify()
        img = Image.open(BytesIO(data))
    except (UnidentifiedImageError, Exception):
        raise HTTPException(422, "Fayl haqiqiy rasm emas")
    if fmt not in ALLOWED:
        raise HTTPException(422, "Faqat jpg, png yoki webp qabul qilinadi")
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB")
    img.thumbnail((max_side, max_side))
    d = upload_root() / subdir
    d.mkdir(parents=True, exist_ok=True)
    name = uuid.uuid4().hex
    rel, rel_t = f"{subdir}/{name}.webp", f"{subdir}/{name}_t.webp"
    img.save(d / f"{name}.webp", "WEBP", quality=82)
    thumb = img.copy()
    thumb.thumbnail((480, 480))
    thumb.save(d / f"{name}_t.webp", "WEBP", quality=78)
    up = ImageUpload(path=rel, thumb=rel_t, original_name=original_name[:255], size_bytes=len(data),
                     width=img.width, height=img.height, admin_id=admin_id)
    db.add(up)
    db.flush()
    return up


async def process_upload(file: UploadFile, db: Session, admin_id: int | None, subdir="products",
                         max_side=1600) -> ImageUpload:
    data = await file.read(MAX_BYTES + 1)
    return process_image_bytes(data, file.filename or "", db, admin_id, subdir, max_side)


def thumb_of(path: str) -> str:
    return path[:-5] + "_t.webp" if path.endswith(".webp") else path


def fmt_dt(d: datetime | None) -> str | None:
    return d.isoformat() + "Z" if d else None
