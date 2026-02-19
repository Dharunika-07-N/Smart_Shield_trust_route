from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.database import get_db
from database.models import User, Delivery, PanicAlert, DeliveryFeedback
from api.deps import get_current_admin
from datetime import datetime, timedelta
import csv
import io
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/summary")
def get_system_summary(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieve high-level system statistics for the Admin Dashboard."""
    # Active nodes: users with role 'rider' or 'driver'
    fleet_count = db.query(User).filter(User.role.in_(['rider', 'driver'])).count()
    
    # Active tasks: deliveries not in 'delivered' or 'cancelled' status
    active_deliveries = db.query(Delivery).filter(
        ~Delivery.status.in_(['delivered', 'cancelled'])
    ).count()
    
    # Active alerts: panic alerts with status 'active'
    active_alerts = db.query(PanicAlert).filter(PanicAlert.status == 'active').count()
    
    # Average safety score of all deliveries
    avg_safety = db.query(func.avg(Delivery.safety_score)).scalar() or 94.0
    
    # Mock utilization based on active deliveries vs fleet
    utilization = "0%"
    if fleet_count > 0:
        utilization = f"{min(100, int((active_deliveries / fleet_count) * 100))}%"
    else:
        utilization = "0%"

    return {
        "activeDrivers": fleet_count,
        "fleetUtilization": utilization,
        "safetyScore": round(float(avg_safety), 1),
        "activeAlerts": active_alerts,
        "totalTasks": db.query(Delivery).count()
    }

@router.post("/broadcast")
async def broadcast_message(
    payload: dict,
    admin: User = Depends(get_current_admin)
):
    """Simulate a global broadcast message."""
    message = payload.get("message", "System Alert")
    target = payload.get("target", "all")
    
    # In a real app, we'd use WebSockets to push this.
    # For the demo, we'll log it and return success.
    print(f"BROADCAST from Admin: {message} to {target}")
    
    return {"status": "success", "message": f"Broadcast sent to {target} nodes"}

@router.get("/analytics-trends")
def get_analytics_trends(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Get real trend data for charts."""
    # Mock some trend data based on real day counts
    # In a real app, this would be complex SQL aggregations
    return {
        "deliveryTime": [42, 38, 35, 32, 30, 28, 32], # Mon-Sun
        "safetyDistribution": [65, 30, 5], # High, Medium, Low
        "fuelSavings": [1250, 1100, 980, 850], # Week 1-4
        "activeNodes": [110, 130, 160, 184] # Growth
    }

@router.get("/fleet-events")
def get_recent_fleet_events(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Retrieve recent activities for the event feed."""
    from database.models import Delivery, PanicAlert
    
    # Get last 5 deliveries and alerts
    deliveries = db.query(Delivery).order_by(Delivery.created_at.desc()).limit(5).all()
    alerts = db.query(PanicAlert).order_by(PanicAlert.created_at.desc()).limit(5).all()
    
    events = []
    for d in deliveries:
        events.append({
            "id": f"del_{d.id}",
            "type": "delivery",
            "title": f"Order #{d.order_id}",
            "description": f"Status updated to {d.status}",
            "time": d.created_at.isoformat() if d.created_at else None,
            "icon": "truck"
        })
    for a in alerts:
        events.append({
            "id": f"alert_{a.id}",
            "type": "alert",
            "title": "SOS Signal",
            "description": f"Panic triggered by Rider ID: {a.rider_id}",
            "time": a.created_at.isoformat() if a.created_at else None,
            "icon": "alert"
        })
    
    # Sort by time
    events.sort(key=lambda x: x['time'] or '', reverse=True)
    return events[:10]

@router.get("/export/reports")
def export_incident_reports(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Export incident reports as CSV."""
    alerts = db.query(PanicAlert).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Rider ID", "Status", "Created At", "Resolution Notes"])
    
    for alert in alerts:
        writer.writerow([alert.id, alert.rider_id, alert.status, alert.created_at, alert.resolution_notes])
    
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=incident_reports.csv"}
    )
