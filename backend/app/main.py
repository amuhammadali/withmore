import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from . import botstate
from .config import get_settings
from .core import upload_root
from .outbox import worker_loop
from .routers import admin_auth, admin_catalog, admin_crm, admin_ops, admin_orders, admin_stats, shop

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
for noisy in ("aiogram", "aiohttp", "httpx", "httpcore"):
    logging.getLogger(noisy).setLevel(logging.WARNING)  # keep BOT_TOKEN out of logs
log = logging.getLogger("whitmore")


@asynccontextmanager
async def lifespan(app: FastAPI):
    st = get_settings()
    if not st.SESSION_SECRET or len(st.SESSION_SECRET) < 16:
        raise RuntimeError("SESSION_SECRET .env faylida kamida 16 belgi bo'lishi kerak")
    tasks = [asyncio.create_task(worker_loop())]
    app.state.bg_tasks = tasks
    app.state.dp = None
    if st.BOT_TOKEN and not st.BOT_TOKEN.startswith("test") and not st.BOT_TOKEN.startswith("your_"):
        from . import bot as botmod
        if st.MODE == "production":
            built = botmod.build()
            if built:
                bot, dp = built
                botstate.bot = bot
                app.state.dp = dp
                try:
                    await botmod.setup(bot)
                    await bot.set_webhook(f"{st.APP_URL.rstrip('/')}/api/bot/webhook",
                                          secret_token=st.WEBHOOK_SECRET or None, drop_pending_updates=False)
                except Exception as exc:
                    log.warning("Webhook setup failed (%s), starting long-polling as fallback...", exc)
                    task = asyncio.create_task(botmod.run_polling(bot, dp))
                    tasks.append(task)
        else:
            await botmod.ensure_bot_started(app)
    else:
        log.warning("BOT_TOKEN is not set: the bot and Telegram messages are disabled")
    yield
    for t in tasks:
        t.cancel()
    botstate.tunnel_task = None
    if botstate.bot:
        await botstate.bot.session.close()
        botstate.bot = None


app = FastAPI(title="Withmore", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(GZipMiddleware, minimum_size=500)
app.include_router(admin_auth.router)
app.include_router(admin_catalog.router)
app.include_router(admin_orders.router)
app.include_router(admin_stats.router)
app.include_router(admin_ops.router)
app.include_router(admin_crm.router)
app.include_router(shop.router)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("Referrer-Policy", "same-origin")
    if not request.url.path.startswith("/miniapp"):
        resp.headers.setdefault("X-Frame-Options", "DENY")  # Mini App must stay embeddable by Telegram
    if request.url.path.startswith("/api/"):
        resp.headers["Cache-Control"] = "no-store"
    elif request.url.path.startswith(("/assets/", "/uploads/")):
        resp.headers.setdefault("Cache-Control", "public, max-age=86400")
    return resp


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/bot/webhook")
async def webhook(request: Request):
    st = get_settings()
    if st.WEBHOOK_SECRET and request.headers.get("x-telegram-bot-api-secret-token") != st.WEBHOOK_SECRET:
        raise HTTPException(403, "Forbidden")
    dp = getattr(request.app.state, "dp", None)
    if not dp or not botstate.bot:
        raise HTTPException(503, "Bot is off")
    from aiogram.types import Update
    await dp.feed_update(botstate.bot, Update.model_validate(await request.json(), context={"bot": botstate.bot}))
    return {"ok": True}


app.mount("/uploads", StaticFiles(directory=str(upload_root())), name="uploads")

DIST = Path(get_settings().FRONTEND_DIST)


@app.get("/{full_path:path}", include_in_schema=False)
def spa(full_path: str):
    if full_path.startswith("api/"):
        return JSONResponse({"detail": "Not found"}, status_code=404)
    if not DIST.exists():
        return JSONResponse({"detail": "Frontend is not built. Run start-windows.bat"}, status_code=503)
    target = (DIST / full_path).resolve()
    if full_path and target.is_file() and DIST.resolve() in target.parents:
        resp = FileResponse(target)
        if target.suffix in [".js", ".css"]:
            resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return resp
    resp = FileResponse(DIST / "index.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp
