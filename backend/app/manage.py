"""Create DB (alembic), seed demo data. Usage: python -m app.manage init"""
import sys
from io import BytesIO
from pathlib import Path

from alembic import command
from alembic.config import Config
from PIL import Image, ImageDraw

from .config import ROOT, get_settings
from .core import compute_price, price_for, process_image_bytes, recalc_all_prices
from .db import SessionLocal
from .models import (AdminAccount, Category, Product, ProductVariant, ProductImage, Promocode)
from .security import hash_password


def migrate():
    cfg = Config(str(ROOT / "backend" / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "backend" / "migrations"))
    command.upgrade(cfg, "head")


def placeholder(text: str, color: str) -> bytes:
    img = Image.new("RGB", (900, 1200), color)
    d = ImageDraw.Draw(img)
    # Double editorial luxury frame
    d.rectangle((36, 36, 864, 1164), outline="#D2B98B", width=3)
    d.rectangle((52, 52, 848, 1148), outline="#D9D3C6", width=1)
    # Tailored suit lapel / garment silhouette
    cx = 450
    d.polygon([(cx - 190, 280), (cx - 70, 220), (cx, 480), (cx + 70, 220), (cx + 190, 280),
               (cx + 220, 860), (cx - 220, 860)], outline="#D2B98B", width=3)
    d.line([(cx - 70, 220), (cx, 540), (cx + 70, 220)], fill="#F6F2EA", width=2)
    d.line([(cx, 540), (cx, 860)], fill="#D2B98B", width=2)
    # Pocket square accent
    d.polygon([(cx + 75, 430), (cx + 135, 430), (cx + 115, 405)], fill="#D2B98B")
    # Bottom plaque
    d.rectangle((80, 940, 820, 1090), fill="#14213D", outline="#D2B98B", width=2)
    d.text((115, 968), "WHITMORE SARTORIAL", fill="#D2B98B")
    d.text((115, 1015), text, fill="#F6F2EA")
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


DEMO = [
    ("Kostyum", "Костюмы", [
        ("Klassik kostyum Navy", "Классический костюм Navy", 420, 2.2, "stock", "Jun 70%, poliester 30%", True,
         [("48", "Navy", 4), ("50", "Navy", 2), ("52", "Navy", 0)]),
        ("Ikki tugmali kostyum Grafit", "Двубортный костюм Графит", 460, 2.4, "preorder", "Jun aralashmasi", True,
         [("48", "Grafit", 0), ("50", "Grafit", 0), ("52", "Grafit", 0)]),
    ]),
    ("Ko'ylak", "Рубашки", [
        ("Oq klassik ko'ylak", "Белая классическая рубашка", 110, 0.4, "stock", "Paxta 100%", True,
         [("M", "Oq", 6), ("L", "Oq", 5), ("XL", "Oq", 1)]),
        ("Havorang ko'ylak", "Голубая рубашка", 120, 0.4, "preorder", "Paxta 100%", False,
         [("M", "Havorang", 0), ("L", "Havorang", 0)]),
    ]),
    ("Aksessuar", "Аксессуары", [
        ("Charm kamar", "Кожаный ремень", 80, 0.3, "stock", "Tabiiy charm", False, [("100", "Qora", 8), ("110", "Qora", 3)]),
        ("Ipak galstuk", "Шёлковый галстук", 45, 0.1, "preorder", "Ipak 100%", False, [("STD", "Navy", 0)]),
    ]),
]
COLORS = ["#14213D", "#3A4660", "#7D8AA3", "#5B6B8C", "#2B3A55", "#8A7A5C"]


def seed():
    st = get_settings()
    db = SessionLocal()
    try:
        if not db.query(AdminAccount).first():
            if len(st.ADMIN_PASSWORD) < 10:
                raise SystemExit("ADMIN_PASSWORD .env faylida kamida 10 belgidan iborat bo'lishi kerak")
            db.add(AdminAccount(full_name="Owner", login=st.OWNER_LOGIN.lower(), role="owner",
                                password_hash=hash_password(st.ADMIN_PASSWORD), accepts_orders=False,
                                permissions=[]))
            db.commit()
            print(f"Owner account created (login: {st.OWNER_LOGIN})")
        if not db.query(Category).first():
            n = 0
            for i, (cu, cr, prods) in enumerate(DEMO):
                cat = Category(name_uz=cu, name_ru=cr, sort=i)
                db.add(cat)
                db.flush()
                for nu, nr, yuan, kg, sale, mat, feat, variants in prods:
                    p = Product(category_id=cat.id, name_uz=nu, name_ru=nr, price_yuan=yuan, weight_kg=kg,
                                sale_type=sale, material=mat, featured=feat,
                                desc_uz=f"{nu}. Klassik kesim, sifatli mato.", desc_ru=f"{nr}. Классический крой, качественная ткань.",
                                size_chart=[{"size": v[0], "chest": str(92 + 4 * j), "waist": str(78 + 4 * j),
                                             "length": str(72 + 2 * j)} for j, v in enumerate(variants)])
                    for size, color, stock in variants:
                        p.variants.append(ProductVariant(size=size, color=color, stock=stock))
                    up = process_image_bytes(placeholder(nu, COLORS[n % len(COLORS)]), f"{nu}.png", db, None)
                    p.images.append(ProductImage(path=up.path, sort=0))
                    db.add(p)
                    db.flush()
                    p.price_uzs = price_for(db, p)
                    n += 1
            db.add(Promocode(code="WELCOME10", percent=10, usage_limit=0))
            db.commit()
            print("Demo data created")
        recalc_all_prices(db)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        migrate()
        seed()
    else:
        print("usage: python -m app.manage init")
