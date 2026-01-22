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
    return {"id": new_delivery.id, "status": new_delivery.status}

@router.get("/", response_model=List[dict])
def list_deliveries(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List deliveries (filtered for rider if applicable)."""
    query = db.query(Delivery)
    if current_user.role == "rider":
        query = query.filter(Delivery.assigned_rider_id == current_user.id)
    if status:
        query = query.filter(Delivery.status == status)
    return [{"id": d.id, "order_id": d.order_id, "status": d.status} for d in query.all()]

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
        from datetime import datetime
        delivery.delivered_at = datetime.utcnow()
    
    db.commit()
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
