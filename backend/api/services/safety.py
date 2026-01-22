"""Safety features service for women riders."""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger
import sys
from pathlib import Path
import uuid

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from api.services.maps import MapsService
from api.services.email import EmailService
from database.models import (
    Rider, PanicAlert, RiderCheckIn, SafeZone, RideAlong,
    DeliveryCompany, DeliveryStatus, BuddyPair, User
)

from api.services.database import DatabaseService


class SafetyService:
    """Safety features for women riders."""
    
    CHECK_IN_INTERVAL_MINUTES = 30  # 30 minutes for night shifts
    
    def __init__(self):
        self.maps_service = MapsService()
        self.email_service = EmailService()
        self.hospitals = self._load_hospitals()
    
    def _load_hospitals(self) -> List[Dict]:
        """Load hospitals from JSON file."""
        from config.config import settings
        import json
        try:
            base_dir = Path(__file__).parent.parent.parent
            data_path = base_dir / "data" / "hospitals.json"
            if data_path.exists():
                with open(data_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading hospitals in SafetyService: {e}")
        return []
    
    def trigger_panic_button(
        self,
        db: Session,
        rider_id: str,
        location: Coordinate,
        route_id: Optional[str] = None,
        delivery_id: Optional[str] = None
    ) -> Dict:
        """
        Trigger panic button - sends alerts to company and emergency contacts.
        
        Returns:
            Alert data with notification status
        """
        try:
            # Get rider info
            rider = db.query(Rider).filter(Rider.id == rider_id).first()
            if not rider:
                raise ValueError(f"Rider {rider_id} not found")
            
            # Create panic alert
            alert = PanicAlert(
                rider_id=rider_id,
                route_id=route_id,
                delivery_id=delivery_id,
                location={
                    "latitude": location.latitude,
                    "longitude": location.longitude
                },
                status="active"
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # Notify emergency contacts
            emergency_contacts = rider.emergency_contacts or []
            alerted_contacts = []
            emails_sent = 0
            
            for contact in emergency_contacts:
                success = self._notify_emergency_contact(contact, rider, alert)
                if success:
                    alerted_contacts.append({
                        "name": contact.get("name"),
                        "phone": contact.get("phone"),
                        "email": contact.get("email"),
                        "notified": True
                    })
                    if contact.get("email"):
                        emails_sent += 1
            
            alert.alerted_contacts = alerted_contacts
            
            # Send email to the system emergency email as a backup
            system_email_sent = self._send_sos_email(rider, alert)
            
            # Notify company
            company_notified = self._notify_company(db, rider, alert)
            alert.company_notified = company_notified
            
            # Optionally notify emergency services (can be configured)
            # In production, integrate with emergency services API
            emergency_services_notified = False  # Placeholder
            
            alert.emergency_services_notified = emergency_services_notified
            db.commit()
            
            logger.critical(
                f"PANIC ALERT: Rider {rider_id} at {location.latitude}, {location.longitude}"
            )
            
            return {
                "alert_id": alert.id,
                "status": "active",
                "email_sent": emails_sent > 0 or system_email_sent,
                "company_notified": company_notified,
                "emergency_contacts_notified": len(alerted_contacts),
                "location": {
                    "latitude": location.latitude,
                    "longitude": location.longitude
                },
                "timestamp": alert.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error triggering panic button: {e}")
            db.rollback()
            raise
    
    def _send_sos_email(self, rider: Rider, alert: PanicAlert, to_email: Optional[str] = None) -> bool:
        """Send SOS alert email to emergency contact."""
        try:
            # Get location from alert
            location = alert.location
            
            # Send email using email service
            email_sent = self.email_service.send_sos_alert(
                rider_name=rider.name or "Unknown Rider",
                rider_id=rider.id,
                location=location,
                to_email=to_email
            )
            
            if email_sent:
                logger.info(f"SOS email sent successfully for rider {rider.id}")
            else:
                logger.warning(f"Failed to send SOS email for rider {rider.id}")
            
            return email_sent
            
        except Exception as e:
            logger.error(f"Error sending SOS email: {e}")
            return False
    
    def _notify_company(self, db: Session, rider: Rider, alert: PanicAlert) -> bool:
        """Notify delivery company about panic alert."""
        try:
            if rider.company_id:
                company = db.query(DeliveryCompany).filter(
                    DeliveryCompany.id == rider.company_id
                ).first()
                
                if company:
                    # In production, send email/SMS/WebSocket notification
                    logger.warning(
                        f"PANIC ALERT for rider {rider.name} ({rider.id}) - "
                        f"Company: {company.company_name} should be notified"
                    )
                    # TODO: Implement actual notification (email, SMS, push notification)
                    return True
            return False
        except Exception as e:
            logger.error(f"Error notifying company: {e}")
            return False
    
    def _notify_emergency_contact(
        self,
        contact: Dict,
        rider: Rider,
        alert: PanicAlert
    ) -> bool:
        """Notify emergency contact about panic alert via email/SMS."""
        try:
            contact_name = contact.get("name", "Emergency Contact")
            contact_email = contact.get("email")
            contact_phone = contact.get("phone")
            
            success = False
            
            # Send Email if available
            if contact_email:
                logger.info(f"Sending SOS email to {contact_name} at {contact_email}")
                email_success = self._send_sos_email(rider, alert, to_email=contact_email)
                if email_success:
                    success = True
            
            # Log SMS notification (Placeholder for actual SMS service like Twilio)
            if contact_phone:
                logger.warning(
                    f"SMS NOTIFICATION (MOCK): Sending SOS to {contact_name} ({contact_phone}) "
                    f"for rider {rider.name}. Location: {alert.location}"
                )
                success = True # Consider SMS notification "sent" in mock mode
                
            if not contact_email and not contact_phone:
                logger.warning(f"No contact info (email/phone) for emergency contact: {contact_name}")
                
            return success
        except Exception as e:
            logger.error(f"Error notifying emergency contact {contact.get('name')}: {e}")
            return False
    
    def check_in(
        self,
        db: Session,
        rider_id: str,
        location: Coordinate,
        route_id: Optional[str] = None,
        delivery_id: Optional[str] = None,
        is_night_shift: bool = False
    ) -> Dict:
        """
        Record rider check-in.
        
        For night shifts, checks if check-in is on time (every 30 minutes).
        """
        try:
            # Check if this is a night shift
            current_hour = datetime.now().hour
            is_night = is_night_shift or (current_hour >= 22 or current_hour < 6)
            
            # Get last check-in
            last_checkin = db.query(RiderCheckIn).filter(
                RiderCheckIn.rider_id == rider_id
            ).order_by(RiderCheckIn.timestamp.desc()).first()
            
            missed_checkin = False
            if last_checkin and is_night:
                # Check if check-in is overdue
                if last_checkin.next_checkin_due:
                    if datetime.utcnow() > last_checkin.next_checkin_due:
                        missed_checkin = True
                        # Send alert for missed check-in
                        self._handle_missed_checkin(db, rider_id, last_checkin)
            
            # Calculate next check-in time
            next_checkin_due = None
            if is_night:
                next_checkin_due = datetime.utcnow() + timedelta(
                    minutes=self.CHECK_IN_INTERVAL_MINUTES
                )
            
            # Create check-in record
            checkin = RiderCheckIn(
                rider_id=rider_id,
                route_id=route_id,
                delivery_id=delivery_id,
                location={
                    "latitude": location.latitude,
                    "longitude": location.longitude
                },
                check_in_type="scheduled" if not missed_checkin else "manual",
                is_night_shift=is_night,
                next_checkin_due=next_checkin_due,
                missed_checkin=missed_checkin
            )
            db.add(checkin)
            db.commit()
            db.refresh(checkin)
            
            logger.info(f"Check-in recorded for rider {rider_id}")
            
            return {
                "checkin_id": checkin.id,
                "timestamp": checkin.timestamp.isoformat(),
                "is_night_shift": is_night,
                "next_checkin_due": next_checkin_due.isoformat() if next_checkin_due else None,
                "missed_checkin": missed_checkin
            }
            
        except Exception as e:
            logger.error(f"Error recording check-in: {e}")
            db.rollback()
            raise
    
    def _handle_missed_checkin(
        self,
        db: Session,
        rider_id: str,
        last_checkin: RiderCheckIn
    ):
        """Handle missed check-in by sending alerts."""
        try:
            if last_checkin.alert_sent:
                return  # Already sent alert
            
            rider = db.query(Rider).filter(Rider.id == rider_id).first()
            if not rider:
                return
            
            # Mark alert as sent
            last_checkin.alert_sent = True
            db.commit()
            
            # Notify company and emergency contacts
            logger.warning(
                f"MISSED CHECK-IN: Rider {rider.name} ({rider_id}) "
                f"missed check-in at {last_checkin.next_checkin_due}"
            )
            
            # TODO: Send actual notifications
            # In production, send alerts to company and emergency contacts
            
        except Exception as e:
            logger.error(f"Error handling missed check-in: {e}")
    
    def get_safe_zones(
        self,
        location: Coordinate,
        radius_meters: int = 2000,
        zone_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get nearby safe zones (police stations, 24hr shops, well-lit areas).
        
        Args:
            location: Current location
            radius_meters: Search radius
            zone_types: Types of zones to find (police_station, shop_24hr, well_lit_area)
        
        Returns:
            List of safe zones with distance
        """
        try:
            safe_zones = []
            
            # Map internal types to Google Places types
            type_mapping = {
                "police_station": "police",
                "shop_24hr": "convenience_store",
                "well_lit_area": "store"  # Fallback as there isn't a direct "well lit" type
            }
            
            types_to_search = []
            if zone_types:
                for zt in zone_types:
                    if zt in type_mapping:
                        types_to_search.append(type_mapping[zt])
            else:
                # Default search
                types_to_search = ["police", "convenience_store"]

            # Add local hospitals as safe zones if "hospital" is requested or by default
            if not zone_types or "hospital" in zone_types:
                for hospital in self.hospitals:
                    dist = self.maps_service.calculate_straight_distance(
                        location, 
                        Coordinate(latitude=hospital['latitude'], longitude=hospital['longitude'])
                    )
                    if dist <= radius_meters:
                        safe_zones.append({
                            "id": f"hosp_{hospital['name'].lower().replace(' ', '_')}",
                            "name": hospital['name'],
                            "zone_type": "hospital",
                            "location": {"lat": hospital['latitude'], "lng": hospital['longitude']},
                            "address": hospital.get('address', ''),
                            "rating": 5.0,
                            "distance_meters": dist,
                            "is_open": True,
                            "phone": hospital.get('phone', ''),
                            "services": hospital.get('services', '')
                        })
            
            # Search for each type
            for place_type in types_to_search:
                places = self.maps_service.find_nearby_places(
                    location=location,
                    radius_meters=radius_meters,
                    place_type=place_type
                )
                
                # Transform to SafeZone format
                for place in places:
                    zone_type = "safe_zone"
                    # Reverse map type
                    for internal, external in type_mapping.items():
                        if external == place_type:
                            zone_type = internal
                            break
                    
                    safe_zones.append({
                        "id": place.get("place_id"),
                        "name": place.get("name"),
                        "zone_type": zone_type,
                        "location": place.get("location"),
                        "address": place.get("address"),
                        "rating": place.get("rating"),
                        "distance_meters": place.get("distance_meters"),
                        "is_open": place.get("is_open")
                    })
            
            # Sort by distance
            safe_zones.sort(key=lambda x: x.get("distance_meters", float('inf')))
            
            logger.info(f"Found {len(safe_zones)} safe zones near location")
            
            return safe_zones
            
        except Exception as e:
            logger.error(f"Error getting safe zones: {e}")
            return []
    
    def create_ride_along(
        self,
        db: Session,
        rider_id: str,
        tracker_name: str,
        tracker_phone: Optional[str] = None,
        tracker_email: Optional[str] = None,
        route_id: Optional[str] = None,
        delivery_id: Optional[str] = None,
        expires_hours: int = 24
    ) -> Dict:
        """
        Create ride-along tracking link for friends/family.
        
        Returns:
            Share token and tracking URL
        """
        try:
            # Generate unique share token
            share_token = str(uuid.uuid4())
            
            # Create ride-along record
            ride_along = RideAlong(
                rider_id=rider_id,
                route_id=route_id,
                delivery_id=delivery_id,
                tracker_name=tracker_name,
                tracker_phone=tracker_phone,
                tracker_email=tracker_email,
                share_token=share_token,
                is_active=True,
                expires_at=datetime.utcnow() + timedelta(hours=expires_hours)
            )
            db.add(ride_along)
            db.commit()
            db.refresh(ride_along)
            
            logger.info(f"Ride-along created for rider {rider_id}, token: {share_token}")
            
            return {
                "ride_along_id": ride_along.id,
                "share_token": share_token,
                "tracking_url": f"/track/{share_token}",
                "expires_at": ride_along.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating ride-along: {e}")
            db.rollback()
            raise
    
    def get_ride_along_status(
        self,
        db: Session,
        share_token: str
    ) -> Optional[Dict]:
        """Get current rider location for ride-along tracking."""
        try:
            ride_along = db.query(RideAlong).filter(
                RideAlong.share_token == share_token,
                RideAlong.is_active == True
            ).first()
            
            if not ride_along:
                return None
            
            # Check if expired
            if ride_along.expires_at and datetime.utcnow() > ride_along.expires_at:
                ride_along.is_active = False
                db.commit()
                return None
            
            # Get latest location
            latest_status = db.query(DeliveryStatus).filter(
                DeliveryStatus.rider_id == ride_along.rider_id
            ).order_by(DeliveryStatus.timestamp.desc()).first()
            
            # Update last accessed
            ride_along.last_accessed = datetime.utcnow()
            db.commit()
            
            if not latest_status:
                return {
                    "rider_id": ride_along.rider_id,
                    "status": "no_location_data",
                    "tracker_name": ride_along.tracker_name
                }
            
            return {
                "rider_id": ride_along.rider_id,
                "location": latest_status.current_location,
                "status": latest_status.status,
                "timestamp": latest_status.timestamp.isoformat(),
                "speed_kmh": latest_status.speed_kmh,
                "heading": latest_status.heading,
                "tracker_name": ride_along.tracker_name
            }
            
        except Exception as e:
            logger.error(f"Error getting ride-along status: {e}")
            return None

    def request_buddy(self, db: Session, rider_id: str, route_id: Optional[str] = None) -> Dict:
        """Request a buddy for a delivery shift."""
        # Find another rider searching for a buddy
        other_request = db.query(BuddyPair).filter(
            BuddyPair.status == "matching",
            BuddyPair.rider1_id != rider_id
        ).first()
        
        if other_request:
            other_request.rider2_id = rider_id
            other_request.status = "matched"
            if route_id: other_request.route_id = route_id
            db.commit()
            return {"status": "matched", "buddy_id": other_request.rider1_id, "pair_id": other_request.id}
        else:
            new_request = BuddyPair(
                rider1_id=rider_id,
                status="matching",
                route_id=route_id
            )
            db.add(new_request)
            db.commit()
            return {"status": "matching", "pair_id": new_request.id}

    def get_buddy_pair(self, db: Session, rider_id: str) -> Optional[Dict]:
        """Get current buddy pair for a rider."""
        pair = db.query(BuddyPair).filter(
            ((BuddyPair.rider1_id == rider_id) | (BuddyPair.rider2_id == rider_id)),
            BuddyPair.status == "matched"
        ).order_by(BuddyPair.created_at.desc()).first()
        
        if pair:
            buddy_id = pair.rider2_id if pair.rider1_id == rider_id else pair.rider1_id
            buddy = db.query(User).filter(User.id == buddy_id).first()
            return {
                "pair_id": pair.id,
                "buddy_id": buddy_id,
                "buddy_name": buddy.full_name if buddy else "Unknown",
                "buddy_phone": buddy.phone if buddy else None,
                "status": pair.status
            }
        return None


