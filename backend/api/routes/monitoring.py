from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd

# Use relative import assuming this file is in backend/api/routes/
# and generic backend import logic
import sys
from pathlib import Path

# Add backend to path if needed for monitoring module resolution
backend_path = str(Path(__file__).parent.parent.parent)
if backend_path not in sys.path:
    sys.path.append(backend_path)

from monitoring.model_monitor import ModelMonitor

router = APIRouter()

# Instantiate global monitor
monitor = ModelMonitor()


@router.get("/monitoring/performance/{model_name}")
async def get_model_performance(
    model_name: str,
    time_window_days: int = 7
):
    """Get recent performance metrics"""
    try:
        metrics = monitor.calculate_performance_metrics(
            model_name,
            time_window_days
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/drift/{model_name}")
async def check_drift(model_name: str):
    """Check for prediction drift"""
    try:
        drift = monitor.detect_prediction_drift(model_name)
        return drift
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/health-check/{model_name}")
async def health_check(model_name: str):
    """Complete health check"""
    try:
        needs_retraining, reasons = monitor.check_retraining_needed(model_name)
        
        return {
            'model_name': model_name,
            'needs_retraining': needs_retraining,
            'reasons': reasons,
            'recommendation': 'Retrain model' if needs_retraining else 'Model healthy'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring/report/{model_name}")
async def get_monitoring_report(model_name: str):
    """Generate comprehensive monitoring report"""
    try:
        report = monitor.generate_monitoring_report(model_name)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
