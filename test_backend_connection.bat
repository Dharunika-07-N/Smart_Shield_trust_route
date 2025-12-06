@echo off
echo ========================================
echo Testing Backend Connection
echo ========================================
cd /d %~dp0
echo.
echo Testing health endpoint...
python test_backend.py
echo.
echo ========================================
pause
