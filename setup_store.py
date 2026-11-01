"""Turnkey Store Cloner & Setup Script for Online Clothing Stores.

Use this script to deploy a brand new standalone store instance for a client in seconds.

Usage:
  python setup_store.py --name "Zara Men" --bot_token "123456:ABC-DEF..." --port 8001
"""
import argparse
import os
import shutil
import sqlite3
import secrets
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def create_store(name: str, bot_token: str, port: int, admin_login: str = "admin", admin_pass: str = None):
    slug = "".join(c.lower() if c.isalnum() else "_" for c in name).strip("_")
    dest_dir = ROOT.parent / f"store_{slug}"

    if not admin_pass:
        admin_pass = secrets.token_urlsafe(8)

    print(f"\n==========================================")
    print(f"🚀 Yangi Do‘kon Yaratilmoqda: {name}")
    print(f"📁 Papka: {dest_dir}")
    print(f"🌐 Port: {port}")
    print(f"==========================================\n")

    if dest_dir.exists():
        print(f"⚠️  Ogohlantirish: {dest_dir} allaqachon mavjud. Yangilanmoqda...")
    else:
        dest_dir.mkdir(parents=True, exist_ok=True)

    # 1. Copy backend and frontend build
    for folder in ("backend", "frontend"):
        src = ROOT / folder
        dst = dest_dir / folder
        if dst.exists():
            shutil.rmtree(dst)
        print(f"📦 Nusxalanmoqda: {folder}...")
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "node_modules", ".git", ".venv"))

    # 2. Copy root files
    for f in ("requirements.txt",):
        if (ROOT / f).exists():
            shutil.copy2(ROOT / f, dest_dir / f)

    # 3. Create .env for the new store
    session_secret = secrets.token_hex(24)
    env_content = f"""# ==========================================
# STORE CONFIGURATION: {name.upper()}
# ==========================================
MODE=development
APP_URL=http://localhost:{port}
DATABASE_URL=sqlite:///./{slug}.db
SESSION_SECRET={session_secret}
ADMIN_LOGIN={admin_login}
ADMIN_PASSWORD={admin_pass}
ADMIN_NAME={name} Admin
BOT_TOKEN={bot_token}
FRONTEND_DIST=frontend/dist
UPLOAD_DIR=uploads
"""
    with open(dest_dir / ".env", "w", encoding="utf-8") as f:
        f.write(env_content)

    # 4. Generate startup bat files for Windows
    start_bat = f"""@echo off
title Store: {name} (Port: {port})
echo Starting {name} on port {port}...
set PYTHONPATH=backend
call ..\\withmore\\.venv\\Scripts\\activate.bat
python -m uvicorn app.main:app --host 0.0.0.0 --port {port}
pause
"""
    with open(dest_dir / "start_store.bat", "w", encoding="utf-8") as f:
        f.write(start_bat)

    # 4b. Initialize database for this new store
    venv_py = ROOT / ".venv" / "Scripts" / "python.exe"
    if not venv_py.exists():
        venv_py = Path(sys.executable)
    print("🔄 Yangi do'kon ma'lumotlar bazasi initsializatsiya qilinmoqda...")
    try:
        subprocess.run(
            [str(venv_py), "-m", "app.manage", "init"],
            cwd=str(dest_dir),
            env={**os.environ, "PYTHONPATH": "backend"},
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Yangi do'kon ma'lumotlar bazasi va dastlabki sozlamalari tayyorlandi!")
    except Exception as e:
        print(f"⚠️ DB initsializatsiya: {e}")

    # 5. Client Handoff card
    handoff_text = f"""=====================================================
🎉 DO‘KON TIZIMI MUVAFFAQIYATLI ISHGA TUSHIRILDI!
=====================================================

Do‘kon nomi: {name}
Admin panel: http://localhost:{port}/admin
Login:       {admin_login}
Parol:       {admin_pass}

Mini App:    http://localhost:{port}/miniapp
Telegram bot token: {bot_token}

Qo'llanma:
1. `start_store.bat` faylini ikki marta bosing.
2. Brauzerda http://localhost:{port}/admin sahifasini oching.
3. "Sozlamalar" bo'limida do'kon logotipi, kargo va to'lov kartangizni kiriting!
=====================================================
"""
    with open(dest_dir / "CLIENT_INFO.txt", "w", encoding="utf-8") as f:
        f.write(handoff_text)

    print("\n" + handoff_text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Online kiyim do'konlari uchun avtomat klonlash skripti")
    parser.add_argument("--name", type=str, default="Demo Store", help="Do'kon nomi")
    parser.add_argument("--bot_token", type=str, default="", help="Telegram bot token (@BotFather dan)")
    parser.add_argument("--port", type=int, default=8005, help="Server porti (masalan: 8001, 8002)")
    parser.add_argument("--login", type=str, default="admin", help="Admin login")
    parser.add_argument("--password", type=str, default="", help="Admin parol")

    args = parser.parse_args()
    create_store(args.name, args.bot_token, args.port, args.login, args.password)

