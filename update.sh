#!/usr/bin/env bash
# =======================================================
# Whitmore 10-Second Auto-Updater (CI/CD Helper)
# Kod o'zgarganda serverni 0-uzilish bilan yangilash
# =======================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

echo "======================================================="
echo "   🔄 WHITMORE PLATFORMASINI YANGILASH BOSHLANDI"
echo "======================================================="

# 1. Baza zaxirasini olish (Ehtiyot shart)
if [ -f "whitmore.db" ]; then
    cp whitmore.db whitmore.db.bak
    echo "✅ Ma'lumotlar bazasi zaxira qilindi (whitmore.db.bak)"
fi

# 2. Git orqali eng oxirgi kodni tortib olish
echo "📦 Eng oxirgi kod yuklab olinmoqda (git pull)..."
git pull origin main || git pull origin master

# 3. Python kutubxonalari yangilanishi
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -q -r backend/requirements.txt
fi

# 4. Frontend yangilanishi va qayta yig'ilishi (React + Vite)
if [ -d "frontend" ]; then
    echo "⚡ Frontend qayta yig'ilmoqda (build)..."
    cd frontend
    npm install --no-audit --no-fund -q
    npm run build
    cd ..
fi

# 5. Ma'lumotlar bazasi migratsiyasi
export PYTHONPATH=backend
python3 -m app.manage init

# 6. Xizmatni qayta ishga tushirish (Zero-downtime restart)
echo "🚀 Xizmat qayta ishga tushirilmoqda..."
if command -v systemctl &> /dev/null && systemctl is-active --quiet whitmore; then
    sudo systemctl restart whitmore
fi

if command -v systemctl &> /dev/null && systemctl is-active --quiet caddy; then
    sudo systemctl reload caddy
fi

echo "======================================================="
echo "   🎉 MUVAFFAQIYATLI YANGILANDI! (LIVE)"
echo "======================================================="

