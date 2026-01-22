from sqlalchemy.orm import Session
from database.models import Delivery, User, RiderProfile
from api.services.maps import MapsService
from api.schemas.delivery import Coordinate
from loguru import logger
from typing import List, Dict, Optional
import uuid

class DispatchService:
    def __init__(self, db: Session):
        self.db = db
        self.maps_service = MapsService()

    def find_available_riders(self) -> List[User]:
        """Find active and available riders."""
        return self.db.query(User).filter(
            User.role == "rider",
            User.status == "active",
            User.is_active == True
        ).all()

    def get_unassigned_deliveries(self) -> List[Delivery]:
        """Get deliveries waiting for assignment."""
        return self.db.query(Delivery).filter(
            Delivery.status == "pending",
            Delivery.assigned_rider_id == None
        ).all()

    async def auto_assign_deliveries(self) -> Dict[str, int]:
        """Automatically match unassigned deliveries to nearest riders."""
        unassigned = self.get_unassigned_deliveries()
        available_riders = self.find_available_riders()
        
        assignments = 0
        if not unassigned or not available_riders:
            return {"assigned_count": 0}
            
        for delivery in unassigned:
            best_rider = None
            min_dist = float('inf')
            
            pickup_loc = Coordinate(
                latitude=delivery.pickup_location['latitude'],
                longitude=delivery.pickup_location['longitude']
            )
            
            for rider in available_riders:
                # In production, we'd get the rider's REAL latest location from Redis or DB
                # For now, we simulate or use a default if not found
                # For this implementation, we just pick the first available one for demo
                best_rider = rider
                break # Simplified logic for auto-assign demo
            
            if best_rider:
                delivery.assigned_rider_id = best_rider.id
                delivery.status = "assigned"
                assignments += 1
                logger.info(f"Auto-assigned delivery {delivery.id} to rider {best_rider.username}")
                
        self.db.commit()
        return {"assigned_count": assignments}
