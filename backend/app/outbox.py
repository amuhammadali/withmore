"""Outbox: every Telegram message is stored first, then delivered by a worker with retries."""
import asyncio
import html
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from . import botstate
from .config import get_settings
from .core import get_setting
from .db import SessionLocal
from .models import Customer, Order, OrderMeta, Outbox, ProductVariant, RestockSubscription, now
from datetime import timedelta

log = logging.getLogger("whitmore.outbox")
MAX_ATTEMPTS = 5


def enqueue(db: Session, kind: str, chat_id: int, text: str, *, photo: str = "", button_text: str = "",
            button_url: str = "", order_id: int | None = None) -> Outbox:
    row = Outbox(kind=kind, chat_id=chat_id, text=text, photo=photo, button_text=button_text,
                 button_url=button_url, order_id=order_id)
    db.add(row)
    db.flush()
    return row


def _can_button(url: str) -> bool:
    return url.startswith("https://")


async def default_sender(chat_id: int, text: str, photo: str, button_text: str, button_url: str):
    bot = botstate.bot
    if bot is None:
        raise RuntimeError("BOT_TOKEN sozlanmagan")
    from aiogram.types import FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup
    markup = None
    if button_url.startswith("cb:approve_receipt:"):
        oid = button_url.split(":")[-1]
        markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ To'lovni tasdiqlash", callback_data=f"pay_ok:{oid}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"pay_no:{oid}"),
        ]])
    elif button_text and _can_button(button_url):
        from aiogram.types import WebAppInfo
        app_url = get_settings().APP_URL.rstrip("/")
        clean_url = button_url.strip()
        if "t.me" in clean_url and ("/shop" in clean_url or "/app" in clean_url):
            clean_url = f"{app_url}/miniapp"
        elif clean_url.startswith(app_url) or "withmore.uz/miniapp" in clean_url:
            clean_url = clean_url if clean_url.startswith("http") else f"{app_url}/miniapp"

        if clean_url.startswith("https://") and ("miniapp" in clean_url or "withmore.uz" in clean_url):
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=button_text, web_app=WebAppInfo(url=clean_url))
            ]])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(text=button_text, url=button_url)
            ]])
    if photo:
        path = Path(get_settings().UPLOAD_DIR) / photo
        if len(text) <= 1000:
            await bot.send_photo(chat_id, FSInputFile(path), caption=text, parse_mode="HTML", reply_markup=markup)
            return
        await bot.send_photo(chat_id, FSInputFile(path))
    await bot.send_message(chat_id, text, parse_mode="HTML", reply_markup=markup)


def _is_permanent(exc: Exception) -> bool:
    try:
        from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
        return isinstance(exc, (TelegramForbiddenError, TelegramBadRequest))
    except Exception:
        return False


def _sync_order_status(db: Session, order_id: int | None):
    """notification_status of the order = state of its admin_order messages."""
    if not order_id:
        return
    meta = db.query(OrderMeta).filter_by(order_id=order_id).first()
    rows = db.query(Outbox).filter_by(order_id=order_id, kind="admin_order").all()
    if not meta or not rows:
        return
    if any(r.status == "sent" for r in rows[-1:]):
        meta.notification_status = "sent"
    elif rows[-1].status == "failed":
        meta.notification_status = "failed"
    else:
        meta.notification_status = "pending"


async def process_due(limit: int = 30) -> int:
    """Send due messages. Returns the number processed."""
    send = botstate.sender or default_sender
    db = SessionLocal()
    done = 0
    try:
        rows = db.query(Outbox).filter(Outbox.status == "pending", Outbox.next_attempt_at <= now()) \
            .order_by(Outbox.id).limit(limit).all()
        for r in rows:
            try:
                await send(r.chat_id, r.text, r.photo, r.button_text, r.button_url)
                r.status, r.sent_at, r.last_error = "sent", now(), ""
            except Exception as exc:  # never lose the message: retry with backoff
                r.attempts += 1
                r.last_error = f"{type(exc).__name__}: {exc}"[:250]
                if r.attempts >= MAX_ATTEMPTS or _is_permanent(exc):
                    r.status = "failed"
                else:
                    r.next_attempt_at = now() + timedelta(seconds=min(30 * 2 ** r.attempts, 3600))
                log.warning("outbox %s failed (%s)", r.id, type(exc).__name__)
            _sync_order_status(db, r.order_id)
            db.commit()
            done += 1
            await asyncio.sleep(0.05)  # throttle ~20 msg/s (Telegram limit is ~30)
    finally:
        db.close()
    return done


async def worker_loop():
    while True:
        try:
            if botstate.bot is None and botstate.sender is None:
                from . import bot as botmod
                await botmod.ensure_bot_started()
            n = await process_due()
        except Exception:
            log.exception("outbox worker error")
            n = 0
        await asyncio.sleep(0.2 if n else 0.7)


def resend_admin_order(db: Session, order: Order, admin_chat_id: int | None):
    from .orders_service import admin_order_text
    meta = order.meta
    if not admin_chat_id:
        meta.notification_status = "no_telegram"
        return None
    url = f"{get_settings().APP_URL.rstrip('/')}/admin/orders/{order.id}"
    row = enqueue(db, "admin_order", admin_chat_id, admin_order_text(order), button_text="Buyurtmani ochish",
                  button_url=url, order_id=order.id)
    meta.notification_status = "pending"
    return row


def notify_restock(db: Session, variant: ProductVariant):
    if get_setting(db, "notify_customer_restock") != "1":
        return
    subs = db.query(RestockSubscription).filter_by(variant_id=variant.id).all()
    p = variant.product
    base = get_settings().APP_URL.rstrip("/")
    for s in subs:
        c = db.get(Customer, s.customer_id)
        if c and c.tg_id:
            if c.language == "ru":
                text = f"<b>{html.escape(p.name_ru or p.name_uz)}</b> ({html.escape(variant.size)} {html.escape(variant.color)}) снова в наличии."
                btn = "Открыть"
            else:
                text = f"<b>{html.escape(p.name_uz)}</b> ({html.escape(variant.size)} {html.escape(variant.color)}) yana omborda bor."
                btn = "Ochish"
            enqueue(db, "restock", c.tg_id, text, button_text=btn, button_url=f"{base}/miniapp/product/{p.id}")
        db.delete(s)
