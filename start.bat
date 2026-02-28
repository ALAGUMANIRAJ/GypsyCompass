@echo off
echo.
echo ============================================
echo    🧭 GypsyCompass - Starting Servers
echo ============================================
echo.
echo [1/2] Starting Django Backend (Port 8000)...
start cmd /k "cd /d D:\GypsyCompass && .venv\Scripts\python.exe manage.py runserver 8000"
timeout /t 3 /nobreak >nul

echo [2/2] Starting React Frontend (Port 3000)...
start cmd /k "cd /d D:\GypsyCompass\frontend && npm start"
timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo  ✅ Both servers are starting!
echo.
echo  Backend API: http://localhost:8000/api/
echo  Frontend:    http://localhost:3000
echo ============================================
echo.

