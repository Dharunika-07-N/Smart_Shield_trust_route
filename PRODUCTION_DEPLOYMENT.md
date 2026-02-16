# 🚀 Smart Shield - Production Deployment Guide

## Complete Step-by-Step Guide for Production Deployment

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Environment Configuration](#environment-configuration)
4. [Database Setup](#database-setup)
5. [Backend Deployment](#backend-deployment)
6. [Frontend Deployment](#frontend-deployment)
7. [Nginx Configuration](#nginx-configuration)
8. [SSL/TLS Setup](#ssltls-setup)
9. [Monitoring & Logging](#monitoring--logging)
10. [Post-Deployment Verification](#post-deployment-verification)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04+ / Debian 11+ / CentOS 8+
- **RAM:** Minimum 2GB (4GB recommended)
- **Storage:** Minimum 20GB
- **CPU:** 2+ cores recommended

### Software Requirements
- Python 3.9+
- Node.js 16+
- PostgreSQL 12+ (recommended) or SQLite for small deployments
- Nginx
- Git
- PM2 or systemd for process management

### API Keys Required
- Google Maps API Key (required)
- At least one AI provider key (OpenAI, Anthropic, or Gemini)
- SMTP credentials for email notifications (optional)

---

## Pre-Deployment Checklist

- [ ] Domain name configured and DNS pointing to server
- [ ] SSL certificate obtained (Let's Encrypt recommended)
- [ ] All API keys acquired
- [ ] Database server set up
- [ ] Firewall configured (ports 80, 443, 8000)
- [ ] Backup strategy in place
- [ ] Monitoring tools ready

---

## Environment Configuration

### 1. Clone Repository

```bash
cd /var/www
git clone https://github.com/your-org/smart-shield.git
cd smart-shield
```

### 2. Backend Environment Variables

Create `backend/.env`:

```env
# Core Configuration
PROJECT_NAME="AI Smart Shield Trust Route"
VERSION="1.0.0"
ENVIRONMENT="production"
DEBUG="False"

# Database (PostgreSQL recommended for production)
DATABASE_URL="postgresql://smartshield_user:strong_password@localhost:5432/smartshield_db"

# Security (GENERATE STRONG KEYS!)
SECRET_KEY="<generate-with-openssl-rand-hex-32>"
JWT_SECRET_KEY="<generate-with-openssl-rand-hex-32>"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server Configuration
BACKEND_HOST="0.0.0.0"
BACKEND_PORT=8000
BACKEND_CORS_ORIGINS=["https://yourdomain.com", "https://www.yourdomain.com"]

# Google Maps API (REQUIRED)
GOOGLE_MAPS_API_KEY="your-google-maps-api-key"

# AI Providers (at least one required)
OPENAI_API_KEY="sk-your-openai-key"
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"
GOOGLE_API_KEY="your-gemini-key"
DEFAULT_AI_PROVIDER="gemini"

# Email Configuration
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
SMTP_USERNAME="your-email@gmail.com"
SMTP_PASSWORD="your-app-password"
SMTP_USE_TLS=True
FROM_EMAIL="noreply@yourdomain.com"
EMERGENCY_EMAIL="emergency@yourdomain.com"

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
AI_RATE_LIMIT_PER_MINUTE=10
```

**Generate secure keys:**
```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate JWT_SECRET_KEY
openssl rand -hex 32
```

### 3. Frontend Environment Variables

Create `frontend/.env.production`:

```env
REACT_APP_API_URL=https://api.yourdomain.com
REACT_APP_WS_HOST=api.yourdomain.com
```

---

## Database Setup

### Option 1: PostgreSQL (Recommended)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib postgis

# Create database and user
sudo -u postgres psql

CREATE DATABASE smartshield_db;
CREATE USER smartshield_user WITH ENCRYPTED PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE smartshield_db TO smartshield_user;

# Enable PostGIS extension
\c smartshield_db
CREATE EXTENSION postgis;

\q
```

### Option 2: SQLite (Small Deployments Only)

```env
DATABASE_URL="sqlite:///./smartshield.db"
```

---

## Backend Deployment

### 1. Install Python Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Database Migrations

```bash
# Initialize database
alembic upgrade head

# Or create tables directly
python create_tables.py
```

### 3. Validate Environment

```bash
# Run environment validator
python -m api.utils.env_validator --strict
```

### 4. Test Backend

```bash
# Test run
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Visit http://your-server-ip:8000/docs to verify
```

### 5. Set Up Process Manager

#### Option A: Using systemd

Create `/etc/systemd/system/smartshield-backend.service`:

```ini
[Unit]
Description=Smart Shield Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/smart-shield/backend
Environment="PATH=/var/www/smart-shield/backend/venv/bin"
ExecStart=/var/www/smart-shield/backend/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable smartshield-backend
sudo systemctl start smartshield-backend
sudo systemctl status smartshield-backend
```

#### Option B: Using PM2

```bash
# Install PM2
npm install -g pm2

# Start backend
cd /var/www/smart-shield/backend
pm2 start "uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4" --name smartshield-backend

# Save PM2 configuration
pm2 save
pm2 startup
```

---

## Frontend Deployment

### 1. Build Production Bundle

```bash
cd frontend

# Install dependencies
npm install

# Build for production
npm run build
```

This creates an optimized production build in `frontend/build/`.

### 2. Deploy Static Files

#### Option A: Serve with Nginx (Recommended)

```bash
# Copy build files to web root
sudo mkdir -p /var/www/smartshield-frontend
sudo cp -r build/* /var/www/smartshield-frontend/
sudo chown -R www-data:www-data /var/www/smartshield-frontend
```

#### Option B: Use CDN (e.g., Cloudflare, AWS S3)

Upload `build/` contents to your CDN.

---

## Nginx Configuration

### 1. Install Nginx

```bash
sudo apt update
sudo apt install nginx
```

### 2. Create Nginx Configuration

Create `/etc/nginx/sites-available/smartshield`:

```nginx
# Backend API
server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to Backend
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;
}

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    root /var/www/smartshield-frontend;
    index index.html;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;

    # React Router support
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3. Enable Configuration

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/smartshield /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## SSL/TLS Setup

### Using Let's Encrypt (Free)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificates
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Auto-renewal (already set up by certbot)
sudo certbot renew --dry-run
```

---

## Monitoring & Logging

### 1. Application Logs

```bash
# Backend logs (systemd)
sudo journalctl -u smartshield-backend -f

# Backend logs (PM2)
pm2 logs smartshield-backend

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 2. Set Up Log Rotation

Create `/etc/logrotate.d/smartshield`:

```
/var/www/smart-shield/backend/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
}
```

### 3. Monitoring Tools (Optional)

- **Uptime Monitoring:** UptimeRobot, Pingdom
- **Performance Monitoring:** New Relic, DataDog
- **Error Tracking:** Sentry

---

## Post-Deployment Verification

### 1. Health Checks

```bash
# Backend API
curl https://api.yourdomain.com/
# Expected: {"message":"Welcome to Smart Shield API",...}

# Frontend
curl https://yourdomain.com/
# Expected: HTML content

# API Documentation
# Visit: https://api.yourdomain.com/docs
```

### 2. Test Critical Endpoints

```bash
# Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'

# Test route optimization
curl https://api.yourdomain.com/api/v1/delivery/optimize
```

### 3. Performance Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API performance
ab -n 1000 -c 10 https://api.yourdomain.com/
```

---

## Troubleshooting

### Common Issues

#### 1. Backend Not Starting
```bash
# Check logs
sudo journalctl -u smartshield-backend -n 50

# Check environment variables
python -m api.utils.env_validator

# Check database connection
python -c "from database.database import engine; print(engine)"
```

#### 2. Frontend 404 Errors
```bash
# Verify Nginx configuration
sudo nginx -t

# Check file permissions
ls -la /var/www/smartshield-frontend

# Rebuild frontend
cd frontend && npm run build
```

#### 3. SSL Certificate Issues
```bash
# Renew certificates
sudo certbot renew

# Check certificate expiry
sudo certbot certificates
```

#### 4. Database Connection Errors
```bash
# Test PostgreSQL connection
psql -h localhost -U smartshield_user -d smartshield_db

# Check PostgreSQL status
sudo systemctl status postgresql
```

---

## Backup Strategy

### 1. Database Backups

```bash
# Create backup script: /usr/local/bin/backup-smartshield-db.sh
#!/bin/bash
BACKUP_DIR="/var/backups/smartshield"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

pg_dump -U smartshield_user smartshield_db | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-smartshield-db.sh

# Add to crontab (daily at 2 AM)
sudo crontab -e
0 2 * * * /usr/local/bin/backup-smartshield-db.sh
```

### 2. Application Backups

```bash
# Backup application files
tar -czf /var/backups/smartshield/app_backup_$(date +%Y%m%d).tar.gz /var/www/smart-shield
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer:** Use Nginx or HAProxy
2. **Multiple Backend Instances:** Run multiple uvicorn workers
3. **Database:** Use PostgreSQL with replication
4. **Caching:** Implement Redis for session and API caching

### Vertical Scaling

1. Increase server resources (RAM, CPU)
2. Optimize database queries
3. Enable CDN for static assets

---

## Security Best Practices

1. **Firewall:** Configure UFW or iptables
2. **SSH:** Disable password authentication, use SSH keys
3. **Updates:** Regular system and package updates
4. **Secrets:** Use environment variables, never commit secrets
5. **Rate Limiting:** Implement at Nginx and application level
6. **Monitoring:** Set up intrusion detection (fail2ban)

---

## Maintenance Schedule

- **Daily:** Monitor logs and error rates
- **Weekly:** Review performance metrics
- **Monthly:** Security updates and dependency updates
- **Quarterly:** Full security audit and penetration testing

---

## Support & Resources

- **Documentation:** https://docs.smartshield.com
- **GitHub Issues:** https://github.com/your-org/smart-shield/issues
- **Email Support:** support@smartshield.com

---

**Deployment Complete! 🎉**

Your Smart Shield application is now running in production. Monitor logs and metrics regularly to ensure optimal performance.
