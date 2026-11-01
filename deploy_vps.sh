#!/usr/bin/env bash
# =======================================================
# Whitmore VPS 1-Click Auto-Deployer (Ubuntu / Debian)
# Ushbu skript yangi toza VPS serverda hamma narsani avtomat o'rnatadi
# =======================================================
set -e

echo "======================================================="
echo "   🚀 WHITMORE CRM & TELEGRAM MINI APP — VPS DEPLOY"
echo "======================================================="

# Root ruxsatini tekshirish
if [ "$EUID" -ne 0 ]; then
  echo "Iltimos, ushbu skriptni root yoki sudo bilan ishga tushiring: sudo bash deploy_vps.sh"
  exit 1
fi

# 1. Foydalanuvchidan domen va bot token so'rash (agar berilmagan bo'lsa)
read -p "Domen nomingizni kiriting (masalan: shop.mydomain.uz): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    echo "Xato: Domen nomi kiritilishi shart!"
    exit 1
fi

read -p "Telegram Bot Tokenini kiriting (@BotFather dan): " TELEGRAM_TOKEN
read -p "Admin kirish parolini kiriting (kamida 10 belgi): " ADMIN_PASS

if [ ${#ADMIN_PASS} -lt 10 ]; then
    ADMIN_PASS="AdminSecurePass_$(openssl rand -hex 4)"
    echo "Parol 10 belgidan kam bo'lgani uchun avtomat kuchli parol generatsiya qilindi: $ADMIN_PASS"
fi

APP_DIR="/var/www/withmore"
CURRENT_DIR="$(pwd)"

# 2. Tizim paketlarini yangilash va keraklilarni o'rnatish
echo ""
echo "[1/6] Kerakli paketlar o'rnatilmoqda (Python3, Caddy, Node.js, Git)..."
apt-get update -y -q
apt-get install -y -q python3 python3-venv python3-pip curl git debian-keyring debian-archive-keyring apt-transport-https

# Caddy (Avtomatik bepul SSL / HTTPS server)
if ! command -v caddy &> /dev/null; then
    echo "Caddy veb-serveri o'rnatilmoqda..."
    curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg --yes
    curl -1sLF 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update -y -q
    apt-get install -y -q caddy
fi

# Node.js LTS (agar kerak bo'lsa)
if ! command -v node &> /dev/null; then
    echo "Node.js o'rnatilmoqda..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
    apt-get install -y -q nodejs
fi

# 3. Loyiha fayllarini /var/www/withmore ga ko'chirish
echo ""
echo "[2/6] Loyiha fayllari sozlanmoqda..."
mkdir -p "$APP_DIR"
if [ "$CURRENT_DIR" != "$APP_DIR" ]; then
    cp -ru "$CURRENT_DIR"/* "$APP_DIR"/ 2>/dev/null || true
fi
cd "$APP_DIR"

# 4. .env faylini yaratish
echo ""
echo "[3/6] Konfiguratsiya (.env) yaratilmoqda..."
SESSION_SECRET=$(openssl rand -hex 32)
cat <<EOF > .env
MODE=production
APP_URL=https://${DOMAIN_NAME}
BOT_TOKEN=${TELEGRAM_TOKEN}
ADMIN_PASSWORD=${ADMIN_PASS}
OWNER_LOGIN=owner
SESSION_SECRET=${SESSION_SECRET}
DATABASE_URL=sqlite:///./whitmore.db
FRONTEND_DIST=frontend/dist
UPLOAD_DIR=uploads
EOF

# 5. Virtualenv va Python kutubxonalari
echo ""
echo "[4/6] Python virtual muhiti sozlanmoqda (.venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip -q
pip install -q -r backend/requirements.txt

# Frontendni build qilish (agar dist bo'lmasa)
if [ ! -f "frontend/dist/index.html" ]; then
    echo "Frontend React ilovasi yig'ilmoqda..."
    cd frontend
    npm install --no-audit --no-fund
    npm run build
    cd ..
fi

# Baza initsializatsiyasi
echo "Ma'lumotlar bazasi initsializatsiya qilinmoqda..."
export PYTHONPATH=backend
python3 -m app.manage init

# 6. Systemd xizmatini yaratish (Avtomatik 24/7 ishlashi va rebootda qayta yonishi)
echo ""
echo "[5/6] Systemd xizmati (whitmore.service) sozlanmoqda..."
cat <<EOF > /etc/systemd/system/whitmore.service
[Unit]
Description=Whitmore E-Commerce & CRM Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=${APP_DIR}
ExecStart=${APP_DIR}/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3
Environment="PYTHONPATH=backend"

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable whitmore
systemctl restart whitmore

# 7. Caddy veb-serveri va Avtomatik HTTPS (SSL)
echo ""
echo "[6/6] Caddy orqali avtomatik bepul SSL (HTTPS) ulanmoqda..."
cat <<EOF > /etc/caddy/Caddyfile
${DOMAIN_NAME} {
    encode gzip zstd
    reverse_proxy 127.0.0.1:8000 {
        header_up Host {host}
        header_up X-Real-IP {remote_host}
        header_up X-Forwarded-For {remote_host}
        header_up X-Forwarded-Proto https
    }
}
EOF

systemctl reload caddy

echo ""
echo "======================================================="
echo "   🎉 MUVAFFAQIYATLI O'RNATILDI VA ISHGA TUSHIRILDI!"
echo "======================================================="
echo ""
echo "🌐 Havolalar:"
echo "   - Webhook & Sayt:  https://${DOMAIN_NAME}"
echo "   - Telegram Mini App: https://${DOMAIN_NAME}/miniapp"
echo "   - Admin Panel:     https://${DOMAIN_NAME}/admin"
echo ""
echo "🔑 Kirish ma'lumotlari:"
echo "   - Login: owner"
echo "   - Parol: ${ADMIN_PASS}"
echo ""
echo "🤖 Telegram Botni sozlash (BotFather):"
echo "   1. @BotFather ga kiring"
echo "   2. /setmenubutton buyrug'ini bering"
echo "   3. Botingizni tanlang va URL ga quyidagini kiriting:"
echo "      https://${DOMAIN_NAME}/miniapp"
echo ""
echo "Xizmat holatini tekshirish:"
echo "   systemctl status whitmore"
echo "   systemctl status caddy"
echo "======================================================="

