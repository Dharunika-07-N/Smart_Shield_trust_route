@echo off
REM AI Smart Shield Trust Route - Windows Setup Script

echo.
echo 🛡️  AI Smart Shield Trust Route - Setup Script
echo ================================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)
echo ✅ Python found
echo.

REM Check Node.js
echo Checking Node.js version...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js not found. Please install Node.js 16+
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

REM Setup Backend
echo 📦 Setting up backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo ✅ Backend setup complete
echo.

REM Setup Frontend
cd ..\frontend
echo 📦 Setting up frontend...
call npm install

echo ✅ Frontend setup complete
echo.

REM Create .env files
cd ..
echo ⚙️  Checking configuration files...

if not exist "backend\.env" (
    echo Creating backend\.env...
    copy .env.example backend\.env
    echo ⚠️  Please edit backend\.env with your API keys
)

if not exist "frontend\.env" (
    echo Creating frontend\.env...
    (
        echo REACT_APP_API_URL=http://localhost:8000
        echo REACT_APP_MAPBOX_TOKEN=your_mapbox_token_here
    ) > frontend\.env
)

echo ✅ Configuration files created
echo.

echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Edit backend\.env with your database credentials and API keys
echo 2. Create database: createdb smartshield
echo 3. Run backend: cd backend ^&^& venv\Scripts\activate ^&^& python -m api.main
echo 4. Run frontend: cd frontend ^&^& npm start
echo.
echo For detailed instructions, see SETUP.md
echo.
pause

