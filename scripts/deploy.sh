#!/bin/bash
# Smart Shield Deployment Script

echo "🚀 Starting deployment sequence..."

# 1. Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# 2. Setup Backend
echo "🐍 Updating backend dependencies..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Running Database Migrations
echo "🗄️ Running migrations..."
# alembic upgrade head 
python create_tables.py

# 4. Build Frontend
echo "⚛️ Building frontend production bundle..."
cd ../frontend
npm install
npm run build

# 5. Restart Services
echo "🔄 Restarting services..."
# If using pm2
pm2 restart all || pm2 start ../backend/api/main.py --name smartshield-backend

echo "✅ Deployment successful!"
