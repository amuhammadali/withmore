@echo off
title Whitmore - Do'kon va CRM Serveri
cd /d "%~dp0"

echo =======================================================
echo    WHITMORE PLATFORMASI ISHGA TUSHMOQDA...
echo =======================================================

if not exist ".venv\Scripts\python.exe" (
    echo [OGOHLANTIRISH] Tizim hali o'rnatilmagan.
    echo Avval "install.bat" faylini ishga tushiring!
    pause
    exit /b 1
)

:: Eski ochiq qolgan 8000-port jarayonlarini tozalash
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Server porti: 8000
echo   Mini App:     http://localhost:8000/miniapp
echo   Admin Panel:  http://localhost:8000/admin
echo.
echo Brauzer avtomatik ochilmoqda...
start http://localhost:8000/admin

set PYTHONPATH=backend
call .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause

