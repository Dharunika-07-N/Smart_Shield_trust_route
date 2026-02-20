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
from api.services.sms import SMSService
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
        self.sms_service = SMSService()
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
    
    async def trigger_panic_button(
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
            # 1. Immediate DB record
            user = db.query(User).filter(User.id == rider_id).first()
            rider = user if user else db.query(Rider).filter(Rider.id == rider_id).first()
            
            rider_name = "Unknown Rider"
            if rider:
                rider_name = getattr(rider, 'full_name', getattr(rider, 'name', "Rider"))

            alert = PanicAlert(
                rider_id=rider_id,
                route_id=route_id,
                delivery_id=delivery_id,
                location={"latitude": location.latitude, "longitude": location.longitude},
                status="active"
            )
            db.add(alert)
            db.commit()
            db.refresh(alert)
            
            # 2. IMMEDIATE WebSocket Broadcast (Critical for Dispatchers)
            try:
                from api.routes.notifications import manager as notification_manager
                notification_manager.broadcast_sync({
                    "type": "panic_alert",
                    "alert_id": alert.id,
                    "rider_id": rider_id,
                    "rider_name": rider_name,
                    "location": {"latitude": location.latitude, "longitude": location.longitude},
                    "message": f"🚨 SOS ALERT: {rider_name} triggered panic button!",
                    "timestamp": alert.created_at.isoformat()
                })
            except Exception as notify_err:
                logger.error(f"WS Broadcast Error: {notify_err}")

            # 3. Async background notification tasks
            import asyncio
            
            # Notify emergency contacts
            emergency_contacts = getattr(rider, 'emergency_contacts', []) or [] if rider else []
            alerted_contacts = []
            
            for contact in emergency_contacts:
                try:
                    success = await self._notify_emergency_contact(contact, rider, alert)
                    if success:
                        alerted_contacts.append({
                            "name": contact.get("name"), 
                            "notified": True
                        })
                except Exception as contact_err:
                    logger.error(f"Error notifying contact {contact}: {contact_err}")
            
            # Critical Backup Email (Run in thread to avoid blocking loop)
            system_email_task = asyncio.to_thread(self._send_sos_email, rider, alert)
            
            # System SMS (Already async)
            loc_str = f"{location.latitude}, {location.longitude}"
            system_sms_task = self.sms_service.send_emergency_alert(rider_name, loc_str)
            
            # Company notification
            company_notified_task = self._notify_company(db, rider, alert) if rider else None
            
            # We don't necessarily need to wait for all of these before returning success to the rider app
            # but for consistency we await them here or wrap in a background task
            system_email_sent, system_sms_sent = await asyncio.gather(
                system_email_task, 
                system_sms_task,
                return_exceptions=True
            )
            
            # Convert exceptions to False
            if isinstance(system_email_sent, Exception): system_email_sent = False
            if isinstance(system_sms_sent, Exception): system_sms_sent = False

            company_notified = False
            if company_notified_task:
                company_notified = await company_notified_task

            alert.company_notified = company_notified
            db.commit()
            
            logger.critical(f"PANIC ALERT: User {rider_id} at {location.latitude}, {location.longitude}")
            
            return {
                "alert_id": alert.id,
                "status": "active",
                "email_sent": system_email_sent,
                "sms_sent": system_sms_sent,
                "company_notified": company_notified,
                "emergency_contacts_notified": len(alerted_contacts),
                "location": {"latitude": location.latitude, "longitude": location.longitude},
                "timestamp": alert.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Critical failure in trigger_panic_button: {e}")
            db.rollback()
            raise
    
    
    def resolve_panic_button(
        self,
        db: Session,
        alert_id: str,
        rider_id: str,
        resolution_notes: Optional[str] = None
    ) -> Dict:
        """Resolve a panic/SOS alert."""
        try:
            alert = db.query(PanicAlert).filter(
                PanicAlert.id == alert_id,
                PanicAlert.rider_id == rider_id
            ).first()
            
            if not alert:
                raise ValueError("Alert not found or access denied")
                
            alert.status = "resolved"
            alert.resolved_at = datetime.utcnow()
            # In a real app, we would store resolution notes in a separate field or JSON
            
            db.commit()
            
            # Broadcast resolution via WebSocket
            try:
                from api.routes.notifications import manager as notification_manager
                notification_manager.broadcast_sync({
                    "type": "panic_resolved",
                    "alert_id": alert_id,
                    "rider_id": rider_id,
                    "status": "resolved",
                    "message": f"✅ SOS Resolved: Alert for rider {rider_id} has been cleared.",
                    "timestamp": alert.resolved_at.isoformat()
                })
            except Exception as notify_err:
                logger.error(f"WS Resolve Broadcast Error: {notify_err}")
            
            logger.info(f"Panic alert {alert_id} resolved by rider {rider_id}")
            
            return {
                "success": True,
                "alert_id": alert.id,
                "status": "resolved",
                "resolved_at": alert.resolved_at.isoformat()
            }
        except Exception as e:
            logger.error(f"Error resolving panic alert: {e}")
            db.rollback()
            raise
    
    def _send_sos_email(self, rider: Optional[User] = None, alert: Optional[PanicAlert] = None, to_email: Optional[str] = None) -> bool:
        """Send SOS alert email to emergency contact."""
        try:
            # Get location from alert
            location = alert.location if alert else {}
            
            # Extract rider name and ID
            rider_name = "Unknown Rider"
            rider_id = "Unknown"
            
            if rider:
                rider_name = getattr(rider, 'full_name', getattr(rider, 'name', rider.username if hasattr(rider, 'username') else "Unknown Rider"))
                rider_id = getattr(rider, 'id', "Unknown")

            # Send email using email service
            email_sent = self.email_service.send_sos_alert(
                rider_name=rider_name,
                rider_id=rider_id,
                location=location,
                to_email=to_email
            )
            
            if email_sent:
                logger.info(f"SOS email sent successfully for rider {rider_id}")
            else:
                logger.warning(f"Failed to send SOS email for rider {rider_id}")
            
            return email_sent
            
        except Exception as e:
            logger.error(f"Error sending SOS email: {e}")
            return False
    
    async def _notify_company(self, db: Session, rider: Rider, alert: PanicAlert) -> bool:
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
    
    async def _notify_emergency_contact(
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
            
            # Send SMS if available
            if contact_phone:
                logger.info(f"Sending SOS SMS to {contact_name} at {contact_phone}")
                # We need to make this async or run it properly
                import asyncio
                sms_body = f"🚨 SOS! {rider.full_name if hasattr(rider, 'full_name') else 'A rider'} needs help! Location: https://maps.google.com/?q={alert.location['latitude']},{alert.location['longitude']}"
                
                # Note: this is inside a sync-style helper or should we make it async?
                # _notify_emergency_contact is called from trigger_panic_button which is async
                # but trigger_panic_button is not await-ing this currently in the loop.
                # Let's see if we can await it.
                # I'll update the caller in trigger_panic_button to be async-friendly.
                
                sms_success = await self.sms_service.send_sms(contact_phone, sms_body)
                if sms_success:
                    success = True
                
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


    def get_all_panic_alerts(self, db: Session, limit: int = 50) -> List[Dict]:
        """Get all panic alerts for admin dashboard."""
        alerts = db.query(PanicAlert).order_by(PanicAlert.created_at.desc()).limit(limit).all()
        return [
            {
                "id": a.id,
                "rider_id": a.rider_id,
                "location": a.location,
                "status": a.status,
                "created_at": a.created_at.isoformat(),
                "resolved_at": a.resolved_at.isoformat() if a.resolved_at else None,
                "alerted_contacts": a.alerted_contacts
            } for a in alerts
        ]
