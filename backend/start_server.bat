@echo off
echo Starting Smart Shield Backend Server...
echo.

REM Check if virtual environment exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found. Using system Python.
    echo.
)

REM Check if uvicorn is available
python -c "import uvicorn" 2>nul
if errorlevel 1 (
    echo Error: uvicorn is not installed.
    echo Please install dependencies first:
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

echo.
echo Starting server on http://localhost:8000
echo API Documentation will be available at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

pause

