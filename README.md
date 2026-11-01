# WHITMORE — Onlayn Do'kon Tizimi (Telegram Mini App + Admin Panel + Telegram Bot)

Ushbu tizim **Whitmore** klassik erkaklar kiyimi brendi uchun mo'ljallangan bo'lib, bitta backend va bitta ma'lumotlar bazasida ishlovchi 3 ta qismdan iborat:
1. **Telegram Mini App** (`/miniapp`) — mijozlar uchun mobil katalog, savat, buyurtma berish va adminga yozish.
2. **Web Admin Panel** (`/admin`) — statistika, mahsulotlar (tezkor qo'shish bilan), kategoriyalar, buyurtmalar, mijozlar, aksiyalar, jamoa, kontent, sozlamalar, marketing va harakatlar tarixi.
3. **Telegram Bot** (`aiogram 3`) — `/start`, til tanlash, telefon raqamini ulashish, buyurtma xabarlari, ombor ogohlantirishlari va mijoz bildirishnomalari (Outbox orqali qayta urinish bilan).

---

## 1. Windows noutbukda 1 ta buyruq bilan ishga tushirish (Docker-siz)

Kompyuteringizda **Python 3.12+** va **Node.js 20+** o'rnatilgan bo'lishi kerak.

1. Loyiha papkasidagi `.env.example` faylidan `.env` nusxa oling (yoki `start-windows.bat` buni o'zi bajaradi) va `.env` ichida quyidagilarni kiriting:
   - `BOT_TOKEN` — `@BotFather` dan olingan Telegram bot tokeni
   - `ADMIN_PASSWORD` — Owner hisobi uchun boshlang'ich parol (kamida 10 ta belgi)
   - `SESSION_SECRET` — sessiya imzosi uchun maxfiy satr (kamida 16 ta belgi)
2. `start-windows.bat` faylini ikki marta bosing yoki terminalda ishga tushiring:
   ```bat
   start-windows.bat
   ```
   Skript avtomatik ravishda:
   - Python virtual muhitini (`.venv`) yaratadi va kutubxonalarni o'rnatadi;
   - Frontend (`frontend/dist`) ilovasini yig'adi;
   - SQLite bazasini (`data/whitmore.db`) yaratadi, Alembic migratsiyasini o'tkazadi va demo ma'lumotlarni (3 ta kategoriya, 6 ta mahsulot, Owner akkaunt) qo'shadi;
   - Serverni `http://localhost:8000` manzilida ishga tushiradi.

3. Brauzerda oching:
   - **Mini App**: `http://localhost:8000/miniapp`
   - **Admin panel**: `http://localhost:8000/admin` (Login: `owner`, Parol: `.env` dagi `ADMIN_PASSWORD`)

---

## 2. Testlarni ishga tushirish

Barcha avtomatlashtirilgan testlarni (avtorizatsiya va ruxsatlar, narx formulasi, rasm yuklash, buyurtma idempotentligi, ombor poygasi / stock race) tekshirish uchun:

```powershell
$env:PYTHONPATH="backend"
.\.venv\Scripts\python.exe -m pytest backend/tests/test_all.py -v
```

---

## 3. VPS serverda ishga tushirish (Docker Compose + PostgreSQL + Caddy HTTPS)

Telegram Mini App faqat **HTTPS** manzilda ochiladi. Shu sababli VPS uchun `docker-compose.yml` ichida **Caddy** avtomatik SSL sertifikat oladi.

1. Domeningizning A-yozuvini VPS IP manziliga yo'naltiring.
2. Serverda `.env` faylini yarating:
   ```env
   BOT_TOKEN=123456:ABCDEF...
   ADMIN_PASSWORD=KuchliParolKamida10Belgi
   SESSION_SECRET=JudaUzunTasodifiyMaxfiySatr1234567890
   MODE=production
   DOMAIN=shop.sizningdomeningiz.uz
   APP_URL=https://shop.sizningdomeningiz.uz
   WEBHOOK_SECRET=WebhookMaxfiyToken123
   POSTGRES_PASSWORD=BazaUchunMaxfiyParol
   ```
3. Konteynerlarni ishga tushiring:
   ```bash
   docker compose up -d --build
   ```
4. Admin panelga kiring (`https://shop.sizningdomeningiz.uz/admin`), chap menyudagi **"Telegramni ulash"** tugmasini bosing va hosil bo'lgan bir martalik havola orqali Telegram botga `/start` bering — shundan so'ng yangi buyurtmalar va kam qoldiq xabarlari Telegramingizga boradi.

