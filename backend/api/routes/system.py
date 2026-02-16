from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.database import get_db
import psutil
import time
import os
from typing import Dict, Any
from config.config import settings

router = APIRouter(prefix="/system", tags=["System"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Detailed health check of the system."""
    health_status = "healthy"
    checks = {}
    
    # 1. Database Check
    try:
        # Simple query to check DB connectivity
        db.execute(text("SELECT 1"))
        checks["database"] = "connected"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"
        health_status = "unhealthy"
        
    # 2. Disk Space Check
    try:
        disk = psutil.disk_usage('/')
        checks["disk_usage_percent"] = disk.percent
        if disk.percent > 90:
            checks["disk_status"] = "warning: low space"
            if health_status == "healthy":
                health_status = "degraded"
        else:
            checks["disk_status"] = "ok"
    except Exception as e:
        checks["disk_status"] = f"error: {str(e)}"
        
    # 3. Memory Check
    try:
        memory = psutil.virtual_memory()
        checks["memory_usage_percent"] = memory.percent
        if memory.percent > 95:
            health_status = "degraded"
    except Exception as e:
        checks["memory_usage_percent"] = f"error: {str(e)}"
        
    # 4. Environment Check
    checks["environment"] = settings.ENVIRONMENT
    checks["version"] = settings.VERSION
    
    return {
        "status": health_status,
        "timestamp": time.time(),
        "checks": checks
    }

@router.get("/metrics")
async def get_metrics():
    """Basic system metrics for monitoring tools."""
    try:
        process = psutil.Process(os.getpid())
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_info": process.memory_info()._asdict(),
            "num_threads": process.num_threads(),
            "uptime": time.time() - process.create_time()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error gathering metrics: {str(e)}")
