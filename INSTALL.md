# 🚀 WHITMORE PLATFORMASINI O‘RNATISH VA ISHGA TUSHIRISH QO‘LLANMASI

Ushbu tizim — kiyim-kechak, poyabzal va xorijdan (Xitoy, Turkiya, AQSH, Dubay) buyurtma asosida ishlovchi onlayn do‘konlar uchun tayyor **CRM + Telegram Mini App + Avtomatlashtirilgan Kargo Boshqaruvi** ekotizimidir.

---

## 💻 1. WINDOWS KOMPYUTERDA ISHGA TUSHIRISH (Eng oson usul)

Tizimda barcha kerakli skriptlar 1 klikda ishlashga moslab tayyorlangan:

### 1-Qadam: O'rnatish (Faqat 1 marta qilinadi)
* Papkadagi **`install.bat`** faylini sichqoncha bilan ikki marta bosing.
* U avtomatik tarzda:
  1. Python virtual muhitini (`.venv`) yaratadi.
  2. Barcha zarur kutubxonalarni o‘rnatadi (`FastAPI`, `Uvicorn`, `SQLAlchemy`, `Aiogram`).
  3. Konfiguratsiya faylini (`.env`) tayyorlaydi.
  4. Zamonaviy Mini App va Admin Panel interfeysini yig‘adi (`React + Vite`).
  5. Boshlang‘ich ma’lumotlar bazasini (`whitmore.db`) yaratib, demo tovarlarni yuklaydi.

### 2-Qadam: Ishga tushirish (Har kuni)
* Papkadagi **`run.bat`** faylini ikki marta bosing.
* Tizim serverni ishga tushiradi va brauzeringizda avtomatik ochiladi:
  * 👑 **Admin Panel:** [http://localhost:8000/admin](http://localhost:8000/admin)
  * 📱 **Telegram Mini App:** [http://localhost:8000/miniapp](http://localhost:8000/miniapp)

---

## 🤖 2. TELEGRAM BOTNI ULASH (5 daqiqada)

Do‘koningiz Telegram Mini App orqali buyurtma qabul qilishi va mijozlarga kargo holatini yuborishi uchun:

1. Telegramda **`@BotFather`** ga kiring va `/newbot` buyrug‘ini bering.
2. Botingiz nomini (masalan: `Zara Men Boutique`) va username'ini (masalan: `zaramen_shop_bot`) kiriting.
3. BotFather bergan **HTTP API Token**ni nusxalab oling (masalan: `7823456789:AAH...`).
4. Papkadagi **`.env`** faylini oching va quyidagilarni kiriting:
   ```env
   BOT_TOKEN=7823456789:AAH...sizning_tokeningiz
   ADMIN_PASSWORD=SizningKuchliParolingiz123
   ```
5. Botingizga Mini App tugmasini qo‘shish:
   * `@BotFather` ga `/setmenubutton` yuboring.
   * Botingizni tanlang va Mini App havolangizni kiriting: `https://sizning-domen.uz/miniapp`

---

## 👑 3. ADMIN PANELGA KIRISH VA DASTLABKI SOZLAMALAR

1. Brauzeringizda [http://localhost:8000/admin](http://localhost:8000/admin) sahifasini oching.
2. Login va parol:
   * **Login:** `owner`
   * **Parol:** `.env` faylidagi `ADMIN_PASSWORD` (boshlang‘ich standart qiymat)
3. **"Sozlamalar" (Settings) bo‘limiga kiring:**
   * **Brending:** Do‘koningiz nomi, shiori, Instagram havolasi va logotipi.
   * **Narx va Kargo:** Yuan kursi (masalan, `1750`), kargo tarifi (masalan, `65,000 so'm/kg`), avans foizi (`50%` yoki `100%`).
   * **To‘lov kartasi:** Mijozlar to‘lov qiladigan Uzcard/Humo karta raqamingiz va karta egasining ismi.
   * **Pochta:** BTS Pochta yoki EMU Pochta operatorlari.

---

## 🏢 4. 10 TA ONLINE MAGAZINGA ALOHIDA SOTISH / O‘RNATIB BERISH (Multi-Store Cloner)

Har bir onlayn do‘konga alohida mustaqil baza va alohida bot o‘rnatib berish uchun maxsus skript:

```powershell
python setup_store.py --name "Dior Boutique" --bot_token "BOT_TOKEN" --port 8001
```

**Natijada:**
* 📁 Yonma-yon yangi `store_dior_boutique` papkasi ochiladi.
* 🗄️ Unga alohida SQLite bazasi yaratiladi (boshqa do‘konlar ma’lumotlariga aralashmaydi).
* ⚙️ Unda `start_store.bat` va `CLIENT_INFO.txt` (login va parollar bilan) yaratiladi.
* Do‘kon egasiga shu papkani topshirasiz — u shunchaki `start_store.bat` ni bosadi va o‘z do‘konini mustaqil ishlatadi!

---

## ☁️ 5. VPS / LINUX (UBUNTU) SERVERGA O‘RNATISH

Agar tizimni 24/7 internetda doimiy ishlaydigan qilishni istasangiz (masalan, Timeweb, Hetzner, DigitalOcean):

### A) Avtomatik o‘rnatish:
```bash
git clone <repository_url> withmore
cd withmore
chmod +x install.sh run.sh
./install.sh
```

### B) Fonda doimiy ishlashi uchun (Systemd servisi):
`/etc/systemd/system/whitmore.service` faylini yarating:
```ini
[Unit]
Description=Whitmore Store & CRM Service
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/withmore
ExecStart=/var/www/withmore/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
Environment="PYTHONPATH=backend"

[Install]
WantedBy=multi-user.target
```

Servisni yoqish:
```bash
sudo systemctl daemon-reload
sudo systemctl enable whitmore
sudo systemctl start whitmore
```

### C) Docker orqali ishga tushirish (Muqobil):
```bash
docker compose up -d --build
```
Caddy avtomatik bepul SSL sertifikat (HTTPS) ulab beradi.

---

## 🔒 6. XAVFSIZLIK VA MA'LUMOTLAR BAZASI ZAXIRASI (BACKUP)

* Barcha ma'lumotlar bitta ixcham `whitmore.db` faylida saqlanadi.
* Admin panelning **Sozlamalar** bo‘limida **"Zaxira nusxasini yuklab olish (Backup)"** tugmasi mavjud. Istalgan vaqtda bazani 1 sekundda yuklab olib saqlab qo‘yishingiz mumkin.

