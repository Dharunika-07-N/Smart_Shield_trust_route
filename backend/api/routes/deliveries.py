from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import Delivery, DeliveryProof, User
from api.deps import get_current_active_user, get_current_dispatcher
from api.services.dispatch import DispatchService
from loguru import logger

from typing import List, Optional
from pydantic import BaseModel
import uuid
import os

from api.routes.notifications import manager as notification_manager
import json
from datetime import datetime

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])

class DeliveryCreate(BaseModel):
    order_id: str
    customer_id: str
    pickup_location: dict
    dropoff_location: dict

class DeliveryUpdate(BaseModel):
    status: str

@router.post("/", response_model=dict)
def create_delivery(
    delivery_in: DeliveryCreate,
    db: Session = Depends(get_db),
    dispatcher: User = Depends(get_current_dispatcher)
):
    """Create a new delivery."""
    new_delivery = Delivery(
        order_id=delivery_in.order_id,
        customer_id=delivery_in.customer_id,
        pickup_location=delivery_in.pickup_location,
        dropoff_location=delivery_in.dropoff_location,
        status="pending"
    )
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    
    # Broadcast new delivery to dispatchers
    notification_manager.broadcast_sync({
        "type": "new_delivery",
        "delivery": {
            "id": new_delivery.id,
            "order_id": new_delivery.order_id,
            "status": new_delivery.status,
            "created_at": new_delivery.created_at.isoformat() if new_delivery.created_at else datetime.now().isoformat()
        }
    })
    
    return {"id": new_delivery.id, "status": new_delivery.status}

@router.get("/", response_model=List[dict])
def list_deliveries(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List deliveries (filtered for rider if applicable)."""
    query = db.query(Delivery)
    
    # Riders only see their own
    if current_user.role in ["rider", "driver"]:
        query = query.filter(Delivery.assigned_rider_id == current_user.id)
    
    # Filter by status if provided
    if status:
        query = query.filter(Delivery.status == status)
    
    deliveries = query.order_by(Delivery.created_at.desc()).all()
    
    return [
        {
            "id": d.id,
            "order_id": d.order_id,
            "customer_id": d.customer_id,
            "status": d.status,
            "pickup_location": d.pickup_location,
            "dropoff_location": d.dropoff_location,
            "assigned_rider_id": d.assigned_rider_id,
            "safety_score": d.safety_score,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in deliveries
    ]

@router.put("/{delivery_id}/status")
def update_delivery_status(
    delivery_id: str,
    update: DeliveryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update delivery status."""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    # Simple permission check
    if current_user.role == "rider" and delivery.assigned_rider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not assigned to this delivery")
    
    delivery.status = update.status
    if update.status == "delivered":
        delivery.delivered_at = datetime.utcnow()
    
    db.commit()
    
    # Broadcast status update
    notification_manager.broadcast_sync({
        "type": "delivery_status_update",
        "delivery_id": delivery_id,
        "status": update.status,
        "rider_id": current_user.id if current_user.role == "rider" else delivery.assigned_rider_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"id": delivery.id, "status": delivery.status}

@router.post("/auto-dispatch")
async def trigger_auto_dispatch(
    db: Session = Depends(get_db),
    dispatcher: User = Depends(get_current_dispatcher)
):
    """Trigger automated delivery assignment."""
    dispatch_service = DispatchService(db)
    result = await dispatch_service.auto_assign_deliveries()
    return result

class DeliveryAssign(BaseModel):
    rider_id: str

@router.patch("/{delivery_id}/assign")
def assign_delivery(
    delivery_id: str,
    assign_in: DeliveryAssign,
    db: Session = Depends(get_db),
    dispatcher: User = Depends(get_current_dispatcher)
):
    """Manually assign a delivery to a rider."""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    rider = db.query(User).filter(User.id == assign_in.rider_id, User.role == "rider").first()
    if not rider:
        raise HTTPException(status_code=400, detail="Invalid rider ID")
    
    delivery.assigned_rider_id = rider.id
    delivery.status = "assigned"
    db.commit()
    
    # Broadcast update
    notification_manager.broadcast_sync({
        "type": "delivery_assigned",
        "delivery_id": delivery_id,
        "rider_id": rider.id,
        "rider_name": rider.full_name or rider.username
    })
    
    return {"id": delivery.id, "status": delivery.status, "assigned_rider_id": rider.id}


@router.post("/{delivery_id}/proof")
async def upload_proof(
    delivery_id: str,
    photo: UploadFile = File(None),
    signature: UploadFile = File(None),
    notes: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Upload proof of delivery."""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    # Save files (simplified for now, would use S3 in production)
    photo_url = None
    signature_url = None
    
    os.makedirs("data/proofs", exist_ok=True)
    
    if photo:
        file_ext = photo.filename.split(".")[-1]
        filename = f"{delivery_id}_photo.{file_ext}"
        filepath = os.path.join("data/proofs", filename)
        with open(filepath, "wb") as f:
            f.write(await photo.read())
        photo_url = f"/static/proofs/{filename}"
        
    if signature:
        file_ext = signature.filename.split(".")[-1]
        filename = f"{delivery_id}_sign.{file_ext}"
        filepath = os.path.join("data/proofs", filename)
        with open(filepath, "wb") as f:
            f.write(await signature.read())
        signature_url = f"/static/proofs/{filename}"
        
    proof = db.query(DeliveryProof).filter(DeliveryProof.delivery_id == delivery_id).first()
    if not proof:
        proof = DeliveryProof(delivery_id=delivery_id)
        db.add(proof)
        
    if photo_url: proof.photo_url = photo_url
    if signature_url: proof.signature_url = signature_url
    if notes: proof.notes = notes
    
    db.commit()
    return {"success": True, "photo_url": photo_url, "signature_url": signature_url}

@router.get("/search/{order_id}")
def search_delivery(
    order_id: str,
    db: Session = Depends(get_db)
):
    """Search for a delivery by order ID (for customers)."""
    delivery = db.query(Delivery).filter(Delivery.order_id == order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Booking ID not found")
    
    # Get assigned rider info if any
    rider_info = None
    if delivery.assigned_rider_id:
        rider = db.query(User).filter(User.id == delivery.assigned_rider_id).first()
        if rider:
            rider_info = {
                "name": rider.full_name or rider.username,
                "phone": rider.phone,
                "role": rider.role
            }

    return {
        "id": delivery.id,
        "order_id": delivery.order_id,
        "status": delivery.status,
        "pickup_location": delivery.pickup_location,
        "dropoff_location": delivery.dropoff_location,
        "estimated_distance": delivery.estimated_distance,
        "estimated_duration": delivery.estimated_duration,
        "safety_score": delivery.safety_score,
        "created_at": delivery.created_at.isoformat() if delivery.created_at else None,
        "rider": rider_info
    }
