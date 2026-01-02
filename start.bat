@echo off
echo ========================================
echo  Multi-Agent AI System - Startup
echo ========================================
echo.

REM Check if frontend dependencies are installed
if not exist "frontend\node_modules\" (
    echo Installing frontend dependencies...
    cd frontend
    call npm install
    cd ..
    echo.
)

echo Starting Backend Server...
start "Backend" cmd /k "uv run uvicorn main:app --reload"
timeout /t 3 /nobreak > nul

echo Starting Frontend Development Server...
start "Frontend" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo  Services Starting...
echo ========================================
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo  API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press any key to exit (servers will keep running)
pause > nul
