#!/bin/bash

# AI Smart Shield Trust Route - Setup Script

echo "🛡️  AI Smart Shield Trust Route - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [ -z "$python_version" ]; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi
echo "✅ Python $python_version found"
echo ""

# Check Node.js
echo "Checking Node.js version..."
node_version=$(node --version 2>&1)
if [ -z "$node_version" ]; then
    echo "❌ Node.js not found. Please install Node.js 16+"
    exit 1
fi
echo "✅ $node_version found"
echo ""

# Setup Backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Backend setup complete"
echo ""

# Setup Frontend
cd ../frontend
echo "📦 Setting up frontend..."
npm install

echo "✅ Frontend setup complete"
echo ""

# Create .env files if they don't exist
cd ..
echo "⚙️  Checking configuration files..."

if [ ! -f "backend/.env" ]; then
    echo "Creating backend/.env..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env with your API keys"
fi

if [ ! -f "frontend/.env" ]; then
    echo "Creating frontend/.env..."
    cp frontend/.env.example frontend/.env
    echo "⚠️  Please edit frontend/.env with your API URL"
fi

echo "✅ Configuration files created"
echo ""

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env with your database credentials and API keys"
echo "2. Create database: createdb smartshield"
echo "3. Run backend: cd backend && source venv/bin/activate && python -m api.main"
echo "4. Run frontend: cd frontend && npm start"
echo ""
echo "For detailed instructions, see SETUP.md"

