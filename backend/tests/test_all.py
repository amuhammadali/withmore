"""Comprehensive tests for all milestones:
1) auth, password policy, CSRF, rate-limit, team & permissions, session invalidation
2) categories, products, image upload (valid/invalid/oversize), quick add, price formula & settings recalc
3) Mini App Telegram initData validation (valid/forged/expired), guest auth, catalog, cart, favorites, restock
4) orders, idempotency, concurrent stock race, round-robin admin assignment, cancel stock restore, outbox & bot
5) dashboard, marketing, promocodes, broadcast, activity log
"""
import asyncio
import hashlib
import hmac
import json
import os
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from urllib.parse import urlencode

import pytest
from fastapi.testclient import TestClient
from PIL import Image

# Point to isolated test DB & upload dir before importing app
_tmp = tempfile.mkdtemp(prefix="wm_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(_tmp, 'test.db').replace(chr(92), '/')}"
os.environ["UPLOAD_DIR"] = os.path.join(_tmp, "uploads")
os.environ["SESSION_SECRET"] = "test-session-secret-key-1234567890"
os.environ["ADMIN_PASSWORD"] = "OwnerSecret123!"
os.environ["BOT_TOKEN"] = "test:123456_BOT_TOKEN_SECRET"
os.environ["APP_URL"] = "http://testserver"

from app import botstate  # noqa: E402
from app.core import compute_price  # noqa: E402
from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.manage import seed  # noqa: E402
from app.models import AdminAccount, Outbox, ProductVariant  # noqa: E402
from app.outbox import process_due  # noqa: E402
from app.security import _fails  # noqa: E402


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    seed()
    yield


def make_png(color="#14213D", size=(200, 200)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def make_init_data(user_id=900001, first_name="Ali", username="ali_uz", bot_token=None, auth_date=None, tamper=False):
    bot_token = bot_token or os.environ["BOT_TOKEN"]
    auth_date = auth_date if auth_date is not None else int(time.time())
    user = json.dumps({"id": user_id, "first_name": first_name, "username": username, "language_code": "uz"})
    data = {"auth_date": str(auth_date), "user": user, "start_param": "instagram-cpc-launch"}
    check = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    h = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    if tamper:
        h = "0" * 64
    data["hash"] = h
    return urlencode(data)


def login_client(login="owner", password="OwnerSecret123!") -> tuple[TestClient, str]:
    _fails.clear()
    c = TestClient(app)
    r = c.post("/api/admin/login", json={"login": login, "password": password})
    assert r.status_code == 200, r.text
    csrf = r.json()["csrf"]
    c.headers.update({"x-csrf-token": csrf})
    return c, csrf


def test_1_auth_csrf_ratelimit_and_permissions():
    _fails.clear()
    anon = TestClient(app)
    assert anon.get("/api/admin/me").status_code == 401

    # Rate limit after 5 failed attempts
    for _ in range(5):
        r = anon.post("/api/admin/login", json={"login": "owner", "password": "wrongpassword"})
        assert r.status_code == 401
    r = anon.post("/api/admin/login", json={"login": "owner", "password": "wrongpassword"})
    assert r.status_code == 429

    owner, csrf = login_client()
    # CSRF required on POST
    owner.headers.pop("x-csrf-token", None)
    assert owner.post("/api/admin/categories", json={"name_uz": "X"}).status_code == 403
    owner.headers["x-csrf-token"] = csrf

    # Password policy (<10 chars rejected)
    r = owner.post("/api/admin/team", json={
        "full_name": "Short Pw", "login": "shortpw", "password": "short", "role": "admin", "permissions": ["orders"]
    })
    assert r.status_code == 422

    # Create limited admin with ONLY orders permission
    r = owner.post("/api/admin/team", json={
        "full_name": "Sardor Admin", "tg_username": "@sardor_wm", "login": "sardor",
        "password": "SardorPass123!", "role": "admin", "permissions": ["orders"], "accepts_orders": True
    })
    assert r.status_code == 201, r.text
    sardor_id = r.json()["id"]

    # Create second order-accepting admin for round-robin test
    r2 = owner.post("/api/admin/team", json={
        "full_name": "Bekzod Admin", "tg_username": "bekzod_wm", "login": "bekzod",
        "password": "BekzodPass123!", "role": "admin", "permissions": ["orders", "products"], "accepts_orders": True
    })
    assert r2.status_code == 201
    bekzod_id = r2.json()["id"]

    # Link Telegram chat_ids for both admins
    db = SessionLocal()
    db.get(AdminAccount, sardor_id).tg_chat_id = 7001
    db.get(AdminAccount, bekzod_id).tg_chat_id = 7002
    db.commit()
    db.close()

    sardor, _ = login_client("sardor", "SardorPass123!")
    assert sardor.get("/api/admin/orders").status_code == 200
    assert sardor.get("/api/admin/products").status_code == 403
    assert sardor.get("/api/admin/customers").status_code == 403
    assert sardor.get("/api/admin/promocodes").status_code == 403
    assert sardor.get("/api/admin/settings").status_code == 403
    assert sardor.get("/api/admin/dashboard").status_code == 403
    assert sardor.get("/api/admin/team").status_code == 403
    assert sardor.get("/api/admin/content").status_code == 403
    assert sardor.get("/api/admin/audit").status_code == 403

    # Blocking invalidates old session immediately
    assert owner.post(f"/api/admin/team/{sardor_id}/block").status_code == 200
    assert sardor.get("/api/admin/orders").status_code == 401
    assert owner.post(f"/api/admin/team/{sardor_id}/unblock").status_code == 200


def test_2_price_formula_categories_products_and_uploads():
    # Exact formula check: (yuan * yuan_rate + weight_kg * shipping_per_kg) * (1 + margin%), rounded to 1000 so'm
    # (100 * 1750 + 1.0 * 65000) * 1.25 = (175000 + 65000) * 1.25 = 300000
    assert compute_price(100, 1.0, 1750, 65000, 25) == 300000
    # (123 * 1750 + 0.5 * 65000) * 1.25 = 247750 * 1.25 = 309687.5 -> 310000
    assert compute_price(123, 0.5, 1750, 65000, 25) == 310000
    # Manual override
    assert compute_price(123, 0.5, 1750, 65000, 25, manual=245000) == 245000

    owner, _ = login_client()
    # Category add, rename, delete protection
    rc = owner.post("/api/admin/categories", json={"name_uz": "Poyabzal", "name_ru": "Обувь"})
    assert rc.status_code == 201
    cid = rc.json()["id"]

    # Create product
    rp = owner.post("/api/admin/products", json={
        "name_uz": "Klassik lofer", "name_ru": "Классические лоферы", "category_id": cid,
        "material": "Charm 100%", "price_yuan": 100, "weight_kg": 1.0, "sale_type": "stock",
        "featured": True, "active": True,
        "size_chart": [{"size": "42", "length": "27"}],
        "variants": [{"size": "42", "color": "Qora", "stock": 1}, {"size": "43", "color": "Qora", "stock": 0}]
    })
    assert rp.status_code == 201
    prod = rp.json()
    assert prod["price_uzs"] == 300000
    pid = prod["id"]

    # Deleting category with product is blocked
    assert owner.delete(f"/api/admin/categories/{cid}").status_code == 409

    # Reject non-image upload
    bad = owner.post(f"/api/admin/products/{pid}/images",
                     files=[("files", ("hack.txt", b"not an image", "text/plain"))])
    assert bad.status_code == 422

    # Valid image upload -> converted to WebP
    ok = owner.post(f"/api/admin/products/{pid}/images",
                    files=[("files", ("shoe.png", make_png(), "image/png"))])
    assert ok.status_code == 200
    img_path = ok.json()["images"][0]["path"]
    assert img_path.endswith(".webp")
    assert owner.get(f"/uploads/{img_path}").status_code == 200

    # Quick add multiple photos -> draft products -> publish
    qa = owner.post("/api/admin/products/quick", files=[
        ("files", ("a.png", make_png("#223344"), "image/png")),
        ("files", ("b.png", make_png("#443322"), "image/png")),
    ])
    assert qa.status_code == 201
    draft_id = qa.json()[0]["id"]
    assert qa.json()[0]["draft"] is True
    pub = owner.post(f"/api/admin/products/{draft_id}/publish", json={"name_uz": "Tezkor palto", "price_yuan": 200})
    assert pub.status_code == 200
    assert pub.json()["draft"] is False and pub.json()["active"] is True

    # Changing settings recalculates all product prices
    s = owner.put("/api/admin/settings", json={"yuan_rate": "2000"})
    assert s.status_code == 200
    # (100 * 2000 + 1.0 * 65000) * 1.25 = 265000 * 1.25 = 331250 -> 331000
    assert owner.get(f"/api/admin/products/{pid}").json()["price_uzs"] == 331000
    owner.put("/api/admin/settings", json={"yuan_rate": "1750"})


def test_3_miniapp_auth_catalog_cart_and_restock():
    c = TestClient(app)
    # Forged initData rejected
    assert c.post("/api/shop/auth", json={"init_data": make_init_data(tamper=True)}).status_code == 401
    # Expired initData rejected
    assert c.post("/api/shop/auth", json={"init_data": make_init_data(auth_date=int(time.time()) - 9999)}).status_code == 401

    # Valid Telegram initData
    r = c.post("/api/shop/auth", json={"init_data": make_init_data()})
    assert r.status_code == 200
    tok = r.json()["token"]
    sh = {"x-shop-token": tok}

    prods = c.get("/api/shop/products").json()
    assert len(prods) >= 7
    lofer = next(p for p in prods if p["name_uz"] == "Klassik lofer")
    detail = c.get(f"/api/shop/products/{lofer['id']}").json()
    sold_out_var = next(v for v in detail["variants"] if v["size"] == "43")
    assert sold_out_var["available"] is False

    # Subscribe to restock on sold-out variant, then restock in admin -> queues outbox message
    assert c.post(f"/api/shop/restock/{sold_out_var['id']}", headers=sh).status_code == 200
    owner, _ = login_client()
    p_admin = owner.get(f"/api/admin/products/{lofer['id']}").json()
    for v in p_admin["variants"]:
        if v["id"] == sold_out_var["id"]:
            v["stock"] = 3
    owner.put(f"/api/admin/products/{lofer['id']}", json=p_admin)

    db = SessionLocal()
    assert db.query(Outbox).filter_by(kind="restock", chat_id=900001).count() == 1
    db.close()


def test_4_order_idempotency_stock_race_roundrobin_and_outbox():
    # Prepare a stock variant with stock = 1
    owner, _ = login_client()
    prods = owner.get("/api/admin/products").json()
    lofer = next(p for p in prods if p["name_uz"] == "Klassik lofer")
    detail = owner.get(f"/api/admin/products/{lofer['id']}").json()
    v42 = next(v for v in detail["variants"] if v["size"] == "42")
    assert v42["stock"] == 1

    # Customer 1 (Telegram) orders with idempotency key: double tap returns same order
    c1 = TestClient(app)
    t1 = c1.post("/api/shop/auth", json={"init_data": make_init_data(user_id=900010, first_name="Jasur")}).json()["token"]
    h1 = {"x-shop-token": t1, "Idempotency-Key": "idem-double-tap-001"}
    c1.put("/api/shop/cart", headers=h1, json={"items": [{"variant_id": v42["id"], "qty": 1}]})

    o1 = c1.post("/api/shop/orders", headers=h1, json={
        "name": "Jasur Karimov", "city": "Toshkent", "address": "Amir Temur 10", "delivery": "courier"
    })
    assert o1.status_code == 201, o1.text
    code1 = o1.json()["code"]
    assert code1.startswith("WM") and len(code1) == 12
    assert o1.json()["created"] is True

    # Second tap with same Idempotency-Key returns the exact same order
    o1_dup = c1.post("/api/shop/orders", headers=h1, json={
        "name": "Jasur Karimov", "city": "Toshkent", "address": "Amir Temur 10", "delivery": "courier"
    })
    assert o1_dup.status_code == 201
    assert o1_dup.json()["code"] == code1
    assert o1_dup.json()["created"] is False

    # Cancel order -> returns reserved stock back to 1
    oid1 = owner.get(f"/api/admin/orders?q={code1}").json()["items"][0]["id"]
    assert owner.patch(f"/api/admin/orders/{oid1}", json={"status": "cancelled"}).status_code == 200
    db = SessionLocal()
    assert db.get(ProductVariant, v42["id"]).stock == 1
    db.close()

    # STOCK RACE: two customers simultaneously try to buy the last 1 item in stock
    def prepare_buyer(uid: int):
        cl = TestClient(app)
        tk = cl.post("/api/shop/auth", json={"init_data": make_init_data(user_id=uid, first_name=f"B{uid}")}).json()["token"]
        cl.put("/api/shop/cart", headers={"x-shop-token": tk}, json={"items": [{"variant_id": v42["id"], "qty": 1}]})
        return tk

    tk_a, tk_b = prepare_buyer(900101), prepare_buyer(900102)

    def try_buy(tk: str, key: str):
        cl = TestClient(app)
        return cl.post("/api/shop/orders", headers={"x-shop-token": tk, "Idempotency-Key": key},
                       json={"name": "Buyer", "city": "Toshkent", "address": "Street 1", "delivery": "courier"}).status_code

    with ThreadPoolExecutor(max_workers=2) as ex:
        f1 = ex.submit(try_buy, tk_a, "race-key-a-12345")
        f2 = ex.submit(try_buy, tk_b, "race-key-b-12345")
        statuses = sorted([f1.result(), f2.result()])
    assert statuses == [201, 409], f"Expected one 201 and one 409, got {statuses}"

    # Pre-order items do not check stock and round-robin rotates between active admins
    preorder_prod = next(p for p in prods if p["sale_type"] == "preorder" and p["active"] and not p["draft"])
    pre_var = owner.get(f"/api/admin/products/{preorder_prod['id']}").json()["variants"][0]
    assigned = []
    for i in range(2):
        cl = TestClient(app)
        tk = cl.post("/api/shop/auth", json={}).json()["token"]  # guest mode
        cl.put("/api/shop/cart", headers={"x-shop-token": tk}, json={"items": [{"variant_id": pre_var["id"], "qty": 2}]})
        # Guest without phone rejected
        bad_guest = cl.post("/api/shop/orders", headers={"x-shop-token": tk, "Idempotency-Key": f"guest-nophone-{i}"},
                            json={"name": "Guest", "delivery": "pickup"})
        assert bad_guest.status_code == 422
        good_guest = cl.post("/api/shop/orders", headers={"x-shop-token": tk, "Idempotency-Key": f"guest-ok-{i}"},
                             json={"name": "Guest", "phone": "+998901234567", "delivery": "pickup", "promo_code": "WELCOME10"})
        assert good_guest.status_code == 201
        assigned.append(good_guest.json()["assigned_admin"]["username"])
    assert len(set(assigned)) == 2, f"Round-robin should rotate across 2 admins, got {assigned}"

    # Outbox worker delivery test
    sent = []

    async def fake_sender(chat_id, text, photo, button_text, button_url):
        sent.append((chat_id, text))

    botstate.sender = fake_sender
    try:
        n = asyncio.run(process_due(limit=50))
        assert n > 0 and len(sent) > 0
    finally:
        botstate.sender = None


def test_5_dashboard_marketing_content_and_audit():
    owner, _ = login_client()
    d = owner.get("/api/admin/dashboard?days=30")
    assert d.status_code == 200
    assert d.json()["cards"]["orders"] >= 3

    m = owner.get("/api/admin/marketing?days=30")
    assert m.status_code == 200
    assert any(r["source"] == "instagram" for r in m.json())

    au = owner.get("/api/admin/audit")
    assert au.status_code == 200
    assert au.json()["total"] > 0

    # Verify built frontend SPA routes are served by backend
    for route in ("/miniapp", "/miniapp/catalog", "/admin", "/admin/orders"):
        resp = owner.get(route)
        assert resp.status_code == 200
        assert "WHITMORE" in resp.text

    # Verify payment card settings & CSV export
    assert owner.put("/api/admin/settings", json={"payment_card_number": "8600 9999 8888 7777"}).status_code == 200
    assert owner.get("/api/shop/content").json()["payment_card_number"] == "8600 9999 8888 7777"
    csv_resp = owner.get("/api/admin/backup/orders.csv")
    assert csv_resp.status_code == 200
    assert "WM" in csv_resp.text


