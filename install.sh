#!/usr/bin/env bash
# =======================================================
# Whitmore Linux / Ubuntu VPS Avtomatik O'rnatish Skripti
# =======================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "======================================================="
echo "   WHITMORE CRM VA DO'KON TIZIMINI O'RNATISH (LINUX)"
echo "======================================================="

# 1. Python tekshirish
if ! command -v python3 &> /dev/null; then
    echo "Python3 topilmadi. O'rnatilmoqda..."
    sudo apt-get update && sudo apt-get install -y python3 python3-venv python3-pip
fi

# 2. Virtualenv yaratish
if [ ! -d ".venv" ]; then
    echo "[1/4] Python virtual muhiti yaratilmoqda (.venv)..."
    python3 -m venv .venv
fi

source .venv/bin/activate
echo "[2/4] Python kutubxonalari o'rnatilmoqda..."
pip install --upgrade pip -q
pip install -q -r backend/requirements.txt

# 3. .env fayli
if [ ! -f ".env" ]; then
    echo "[3/4] .env fayli yaratilmoqda..."
    cp .env.example .env
    echo "DIQQAT: .env faylini ochib, BOT_TOKEN va ADMIN_PASSWORD ni kiriting."
fi

# 4. Frontendni yig'ish (agar dist yo'q bo'lsa)
if [ ! -f "frontend/dist/index.html" ]; then
    echo "[4/4] Frontend yig'ilmoqda (Node.js)..."
    if command -v npm &> /dev/null; then
        cd frontend
        npm install --no-audit --no-fund
        npm run build
        cd ..
    else
        echo "Node.js topilmadi. Frontend allaqachon dist papkasida bo'lishi kerak."
    fi
fi

# 5. DB Initsializatsiyasi
export PYTHONPATH=backend
python3 -m app.manage init

echo ""
echo "======================================================="
echo "   MUVAFFAQIYATLI O'RNATILDI!"
echo "======================================================="
echo "Serverni ishga tushirish uchun:"
echo "   bash run.sh"
echo "Yoki fonda ishlashi uchun (systemd / nohup):"
echo "   nohup bash run.sh > server.log 2>&1 &"
echo "======================================================="

