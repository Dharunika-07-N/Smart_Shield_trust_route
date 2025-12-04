# Smart Shield - Start Script
# Starts both backend and frontend servers

Write-Host "🚀 Starting AI Smart Shield Trust Route..." -ForegroundColor Green
Write-Host ""

# Check if backend directory exists
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: backend directory not found!" -ForegroundColor Red
    exit 1
}

# Check if frontend directory exists
if (-not (Test-Path "frontend")) {
    Write-Host "❌ Error: frontend directory not found!" -ForegroundColor Red
    exit 1
}

# Start Backend
Write-Host "📦 Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; .\venv\Scripts\Activate.ps1; python -m api.main"

# Wait for backend to initialize
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "🎨 Starting Frontend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm start"

Write-Host ""
Write-Host "✅ Servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend API:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "📍 API Docs:     http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📍 Frontend:     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

