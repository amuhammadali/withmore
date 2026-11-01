@echo off
setlocal enabledelayedexpansion
title Whitmore - O'rnatish va Sozlash
cd /d "%~dp0"

echo =======================================================
echo    WHITMORE SARTORIAL / CRM PLATFORMASINI O'RNATISH
echo =======================================================
echo.

:: 1. Python tekshirish
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [XATO] Kompyuteringizda Python o'rnatilmagan!
    echo Iltimos, https://www.python.org saytidan Python 3.11 yoki 3.12 ni yuklab oling
    echo va o'rnatishda "Add Python to PATH" katagiga belgi qo'ying.
    pause
    exit /b 1
)
echo [1/6] Python aniqlandi: 
python --version

:: 2. Node.js tekshirish
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [OGOHLANTIRISH] Node.js topilmadi.
    echo Agar frontend allaqachon yig'ilgan bo'lsa (frontend/dist mavjud), o'rnatish davom etadi.
    echo Yangilash uchun https://nodejs.org saytidan Node.js LTS versiyasini o'rnating.
) else (
    echo [2/6] Node.js aniqlandi:
    node --version
)

:: 3. Virtual muhit (.venv)
echo.
echo [3/6] Python virtual muhiti sozlanmoqda...
if not exist ".venv\Scripts\python.exe" (
    echo .venv yaratilmoqda...
    python -m venv .venv
)

echo Kutubxonalar o'rnatilmoqda (pip install)...
call .venv\Scripts\python.exe -m pip install --upgrade pip -q
call .venv\Scripts\python.exe -m pip install -q -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [XATO] Python kutubxonalarini o'rnatishda xatolik yuz berdi.
    pause
    exit /b 1
)
echo Python kutubxonalari muvaffaqiyatli o'rnatildi.

:: 4. .env faylini sozlash
echo.
echo [4/6] Konfiguratsiya (.env) tekshirilmoqda...
if not exist ".env" (
    echo .env fayli yaratilmoqda...
    copy /Y ".env.example" ".env" >nul
    echo .env fayli yaratildi. Undagi BOT_TOKEN va ADMIN_PASSWORD ni keyinroq kiritishingiz mumkin.
) else (
    echo .env fayli mavjud.
)

:: 5. Frontendni yig'ish (React + Vite)
echo.
echo [5/6] Mini App va Admin Panel interfeysi tayyorlanmoqda...
if exist "frontend\dist\index.html" (
    echo Tayyor yig'ilgan frontend topildi (frontend/dist).
) else (
    pushd frontend
    if exist "..\frontend\node_modules" (
        echo Node modullari mavjud.
    ) else (
        echo npm paketlari o'rnatilmoqda...
        call npm.cmd install --no-audit --no-fund
    )
    echo Frontend build qilinmoqda...
    call npm.cmd run build
    popd
)

:: 6. Ma'lumotlar bazasi initsializatsiyasi
echo.
echo [6/6] Ma'lumotlar bazasi va dastlabki ma'lumotlar kiritilmoqda...
set PYTHONPATH=backend
call .venv\Scripts\python.exe -m app.manage init

echo.
echo =======================================================
echo    MUVAFFAQIYATLI O'RNATILDI!
echo =======================================================
echo.
echo Tizim ishga tushirishga 100%% tayyor!
echo Endi har doim serverni yoqish uchun:
echo    "run.bat" faylini ikki marta bosing.
echo.
echo Havolalar:
echo   - Admin Panel: http://localhost:8000/admin
echo   - Mini App:    http://localhost:8000/miniapp
echo.
echo Batafsil qo'llanma: INSTALL.md faylida yozilgan.
echo =======================================================
pause

