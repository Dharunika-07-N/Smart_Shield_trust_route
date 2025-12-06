@echo off
echo ========================================
echo Starting Backend Server
echo ========================================
cd /d %~dp0backend
echo.
echo Starting uvicorn server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
pause
