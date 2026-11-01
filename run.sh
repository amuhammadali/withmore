#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$DIR"

if [ ! -d ".venv" ]; then
    echo "Tizim hali o'rnatilmagan. Avval 'bash install.sh' ni ishga tushiring!"
    exit 1
fi

source .venv/bin/activate
export PYTHONPATH=backend
echo "Whitmore serveri 8000-portda ishga tushmoqda..."
echo "Admin panel: http://localhost:8000/admin"
echo "Mini App:    http://localhost:8000/miniapp"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000

