from sqlalchemy.orm import Session
from database.models import Delivery, User, RiderProfile
from api.services.maps import MapsService
from api.schemas.delivery import Coordinate
from loguru import logger
from typing import List, Dict, Optional, Any
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

    async def auto_assign_deliveries(self) -> Dict[str, Any]:
        """Automatically match unassigned deliveries to nearest riders using distance logic."""
        import math
        unassigned = self.get_unassigned_deliveries()
        available_riders = self.find_available_riders()
        
        assignments = 0
        if not unassigned or not available_riders:
            return {"assigned_count": 0, "message": "No unassigned orders or available riders found"}
            
        # Get latest locations for all riders from cache
        from api.services.location_cache import location_cache
        
        for delivery in unassigned:
            best_rider = None
            min_dist = float('inf')
            
            p_lat = delivery.pickup_location.get('latitude') or delivery.pickup_location.get('lat')
            p_lng = delivery.pickup_location.get('longitude') or delivery.pickup_location.get('lng')
            
            if p_lat is None: continue

            for rider in available_riders:
                # Try to get rider's real position from cache
                rider_loc = await location_cache.get_by_rider(rider.id)
                
                if rider_loc:
                    r_lat, r_lng = rider_loc['latitude'], rider_loc['longitude']
                else:
                    # Fallback to a default if no cache (e.g. RS Puram)
                    r_lat, r_lng = 11.0168, 76.9558
                
                # Simple Haversine approximation
                dlat = math.radians(r_lat - p_lat)
                dlng = math.radians(r_lng - p_lng)
                a = (math.sin(dlat / 2) ** 2 + 
                     math.cos(math.radians(p_lat)) * math.cos(math.radians(r_lat)) * 
                     math.sin(dlng / 2) ** 2)
                c = 2 * math.asin(math.sqrt(a))
                dist = 6371 * c # Distance in km
                
                if dist < min_dist:
                    min_dist = dist
                    best_rider = rider
            
            if best_rider:
                delivery.assigned_rider_id = best_rider.id
                delivery.status = "assigned"
                assignments += 1
                logger.info(f"Auto-assigned delivery {delivery.order_id} to rider {best_rider.username} (Dist: {min_dist:.2f}km)")
                
                # Broadcast assignment
                from api.routes.notifications import manager as notification_manager
                await notification_manager.broadcast({
                    "type": "delivery_assigned",
                    "delivery_id": delivery.id,
                    "order_id": delivery.order_id,
                    "rider_id": best_rider.id,
                    "rider_name": best_rider.full_name or best_rider.username
                })
                
        self.db.commit()
        return {
            "assigned_count": assignments, 
            "status": "success",
            "message": f"Successfully optimized fleet. {assignments} orders dispatched."
        }
