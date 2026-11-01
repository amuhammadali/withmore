# Whitmore – reja (milestones)

1. Skeleton, DB, Alembic migrations, admin auth (sessions, CSRF, rate limit), team + permissions.
2. Categories, products (price formula, variants), image upload (WebP), quick add.
3. Mini App: auth by Telegram initData, catalog, product, cart (server side), about.
4. Orders: idempotency, atomic stock reservation, round-robin admin, outbox + worker, aiogram bot.
5. Dashboard, charts, marketing, activity log, promotions/broadcast, content, settings.
6. Tests, start-windows.bat, README (uz), docker-compose + Caddy.

Layout: `backend/` (FastAPI, SQLAlchemy, Alembic, aiogram), `frontend/` (React+TS+Vite+Tailwind; `/admin`, `/miniapp`).
The backend serves `frontend/dist`, so one process runs everything.
