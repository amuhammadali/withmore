@echo off
setlocal
cd /d "%~dp0"

echo ==============================================
echo   WHITMORE — Online do'kon tizimini ishga tushirish
echo ==============================================

if not exist ".env" (
    echo [1/5] .env fayli topilmadi, .env.example dan nusxa olinmoqda...
    copy /Y ".env.example" ".env" >nul
    echo DIQQAT: .env faylidagi BOT_TOKEN, ADMIN_PASSWORD va SESSION_SECRET qiymatlarini tekshiring.
)

if not exist ".venv\Scripts\python.exe" (
    echo [2/5] Python virtual muhiti yaratilmoqda...
    python -m venv .venv
)

echo [3/5] Python kutubxonalari o'rnatilmoqda...
call .venv\Scripts\python.exe -m pip install -q -r backend\requirements.txt

echo [4/5] Frontend yig'ilmoqda ^(React + Vite^)...
pushd frontend
if not exist "node_modules" (
    call npm.cmd install --no-audit --no-fund
)
call npm.cmd run build
popd

echo [5/5] Ma'lumotlar bazasi migratsiyasi va boshlang'ich ma'lumotlar...
set PYTHONPATH=backend
call .venv\Scripts\python.exe -m app.manage init

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Tayyor! Brauzerda oching:
echo   Mini App:     http://localhost:8000/miniapp
echo   Admin panel:  http://localhost:8000/admin
echo   Telegram bot: @Withmoreuz_bot ^(avtomatik HTTPS tunnel bilan^)
echo.
call .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
