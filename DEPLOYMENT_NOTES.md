# 📋 Smart Shield - Deployment Notes

## 🔄 Deployment Scripts
- `scripts/deploy.sh`: Automated deployment script for pulling code, migration, and restarting services.
- `scripts/generate_secrets.py`: Utility to generate secure `SECRET_KEY` and `JWT_SECRET_KEY`.

## ⚙️ Environment Configuration
- `.env.production`: Template for production environment variables.
- `.env.staging`: Template for staging environment variables.

## 🛡️ Monitoring & Health
- `/api/v1/system/health`: Detailed system health checks (DB, Disk, Memory).
- `/api/v1/system/metrics`: Basic resource usage metrics (CPU, RAM).
- **Sentry Integration**: Configure `SENTRY_DSN` in `.env` to enable error tracking.
- **Request Timing**: Middleware adds `X-Process-Time` header and logs request duration.

## 📝 Logging
- Logs are automatically rotated (10 MB files, 10 days retention) and compressed (.zip).
- Log file location: `backend/logs/app.log` (configurable via `LOG_FILE`).

## 🚀 Quick Deployment Steps
1. SSH into server.
2. Clone repository.
3. specificy `.env` from `.env.production`.
4. Run `python scripts/generate_secrets.py` and update `.env`.
5. Run `./scripts/deploy.sh`.
