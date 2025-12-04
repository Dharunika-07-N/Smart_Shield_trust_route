@echo off
echo ========================================
echo  AI Smart Shield Trust Route
echo  Starting Backend and Frontend
echo ========================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python -m api.main"

timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ========================================
echo  Servers are starting!
echo.
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:3000
echo ========================================
echo.
pause

