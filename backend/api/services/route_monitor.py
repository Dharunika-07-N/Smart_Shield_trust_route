"""Route monitoring service for deviation detection and re-optimization."""
from typing import Dict, Optional, Tuple, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from loguru import logger
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from api.services.maps import MapsService
from api.models.route_optimizer import RouteOptimizer
from database.models import Route, DeliveryStatus, RouteMonitoring
from api.services.database import DatabaseService


class RouteMonitor:
    """Monitors rider location vs planned route and triggers re-optimization."""
    
    # Thresholds
    DEVIATION_THRESHOLD_METERS = 500  # 500m deviation
    TIME_DELAY_THRESHOLD_SECONDS = 600  # 10 minutes
    
    def __init__(self):
        self.maps_service = MapsService()
        self.route_optimizer = RouteOptimizer()
    
    def check_deviation(
        self,
        db: Session,
        route_id: str,
        rider_id: str,
        delivery_id: str,
        actual_location: Coordinate,
        current_time: datetime
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Check if rider has deviated from planned route.
        
        Returns:
            (needs_reoptimization, monitoring_data)
        """
        try:
            # Get route from database
            db_service = DatabaseService(db)
            route = db_service.get_route(route_id)
            
            if not route:
                logger.warning(f"Route {route_id} not found")
                return False, None
            
            # Get planned location based on current time and route progress
            planned_location, deviation_meters, time_delay = self._calculate_planned_location(
                route, current_time, actual_location
            )
            
            # Check if deviation exceeds threshold
            deviation_exceeded = deviation_meters > self.DEVIATION_THRESHOLD_METERS
            time_delay_exceeded = time_delay and time_delay > self.TIME_DELAY_THRESHOLD_SECONDS
            
            needs_reoptimization = deviation_exceeded or time_delay_exceeded
            
            # Save monitoring record
            monitoring_data = {
                "route_id": route_id,
                "rider_id": rider_id,
                "delivery_id": delivery_id,
                "planned_location": {
                    "latitude": planned_location.latitude,
                    "longitude": planned_location.longitude
                },
                "actual_location": {
                    "latitude": actual_location.latitude,
                    "longitude": actual_location.longitude
                },
                "deviation_meters": deviation_meters,
                "time_delay_seconds": time_delay,
                "requires_reoptimization": needs_reoptimization,
                "timestamp": current_time
            }
            
            # Save to database
            monitoring = RouteMonitoring(**monitoring_data)
            db.add(monitoring)
            db.commit()
            
            logger.info(
                f"Route {route_id}: deviation={deviation_meters:.1f}m, "
                f"delay={time_delay}s, reoptimize={needs_reoptimization}"
            )
            
            return needs_reoptimization, monitoring_data
            
        except Exception as e:
            logger.error(f"Error checking deviation: {e}")
            db.rollback()
            return False, None
    
    def _calculate_planned_location(
        self,
        route: Route,
        current_time: datetime,
        actual_location: Coordinate
    ) -> Tuple[Coordinate, float, Optional[float]]:
        """
        Calculate where the rider should be based on route plan.
        
        Returns:
            (planned_location, deviation_meters, time_delay_seconds)
        """
        try:
            # Get route start time (use created_at or estimated start)
            route_start = route.created_at
            if route.estimated_arrivals:
                # Find the first stop's estimated arrival
                first_stop_time = min(route.estimated_arrivals.values())
                if isinstance(first_stop_time, str):
                    first_stop_time = datetime.fromisoformat(first_stop_time)
                route_start = first_stop_time - timedelta(seconds=route.total_duration_seconds)
            
            # Calculate elapsed time
            elapsed_seconds = (current_time - route_start).total_seconds()
            
            # Estimate progress (0.0 to 1.0)
            if route.total_duration_seconds > 0:
                progress = min(1.0, elapsed_seconds / route.total_duration_seconds)
            else:
                progress = 0.0
            
            # Get planned location based on progress
            # For simplicity, interpolate between start and stops
            starting_point = route.starting_point
            stops = route.stops
            sequence = route.optimized_sequence or []
            
            if not stops or not sequence:
                # No stops, return starting point
                planned_loc = Coordinate(
                    latitude=starting_point.get("lat") or starting_point.get("latitude"),
                    longitude=starting_point.get("lng") or starting_point.get("longitude")
                )
            else:
                # Interpolate based on progress
                num_stops = len(sequence)
                if progress >= 1.0:
                    # Should be at last stop
                    last_stop_idx = sequence[-1] if sequence else 0
                    last_stop = stops[last_stop_idx] if last_stop_idx < len(stops) else stops[0]
                    planned_loc = Coordinate(
                        latitude=last_stop.get("coordinates", {}).get("latitude", starting_point.get("lat")),
                        longitude=last_stop.get("coordinates", {}).get("longitude", starting_point.get("lng"))
                    )
                else:
                    # Interpolate between current and next stop
                    current_stop_idx = int(progress * num_stops)
                    current_stop_idx = min(current_stop_idx, num_stops - 1)
                    
                    if current_stop_idx < num_stops:
                        stop_id = sequence[current_stop_idx]
                        stop = next((s for s in stops if s.get("stop_id") == stop_id), stops[0])
                        planned_loc = Coordinate(
                            latitude=stop.get("coordinates", {}).get("latitude", starting_point.get("lat")),
                            longitude=stop.get("coordinates", {}).get("longitude", starting_point.get("lng"))
                        )
                    else:
                        planned_loc = Coordinate(
                            latitude=starting_point.get("lat") or starting_point.get("latitude"),
                            longitude=starting_point.get("lng") or starting_point.get("longitude")
                        )
            
            # Calculate deviation
            deviation_meters = self.maps_service.calculate_straight_distance(
                planned_loc, actual_location
            )
            
            # Calculate time delay
            time_delay = None
            if elapsed_seconds > route.total_duration_seconds:
                time_delay = elapsed_seconds - route.total_duration_seconds
            
            return planned_loc, deviation_meters, time_delay
            
        except Exception as e:
            logger.error(f"Error calculating planned location: {e}")
            # Fallback to starting point
            starting_point = route.starting_point
            planned_loc = Coordinate(
                latitude=starting_point.get("lat") or starting_point.get("latitude"),
                longitude=starting_point.get("lng") or starting_point.get("longitude")
            )
            deviation_meters = self.maps_service.calculate_straight_distance(
                planned_loc, actual_location
            )
            return planned_loc, deviation_meters, None
    
    async def reoptimize_route(
        self,
        db: Session,
        route_id: str,
        current_location: Coordinate,
        new_stops: Optional[List[Dict]] = None
    ) -> Optional[Dict]:
        """
        Re-optimize route from current location.
        
        Args:
            route_id: Original route ID
            current_location: Current rider location
            new_stops: Optional new stops to add
        
        Returns:
            Re-optimized route data
        """
        try:
            db_service = DatabaseService(db)
            route = db_service.get_route(route_id)
            
            if not route:
                logger.error(f"Route {route_id} not found for reoptimization")
                return None
            
            # Get remaining stops (not yet delivered)
            stops = route.stops
            sequence = route.optimized_sequence or []
            
            # Filter out completed stops (simplified - in production, track which stops are done)
            remaining_stops = []
            for stop_id in sequence:
                stop = next((s for s in stops if s.get("stop_id") == stop_id), None)
                if stop:
                    remaining_stops.append(stop)
            
            # Add new stops if provided
            if new_stops:
                remaining_stops.extend(new_stops)
            
            if not remaining_stops:
                logger.warning(f"No remaining stops for route {route_id}")
                return None
            
            # Convert stops to DeliveryStop format
            from api.schemas.delivery import DeliveryStop, DeliveryPriority
            delivery_stops = []
            for stop in remaining_stops:
                coords = stop.get("coordinates", {})
                delivery_stops.append(DeliveryStop(
                    stop_id=stop.get("stop_id", f"STOP_{len(delivery_stops)}"),
                    address=stop.get("address", ""),
                    coordinates=Coordinate(
                        latitude=coords.get("latitude", 0),
                        longitude=coords.get("longitude", 0)
                    ),
                    priority=DeliveryPriority(stop.get("priority", "medium")),
                    package_weight=stop.get("package_weight", 1.0)
                ))
            
            # Re-optimize from current location
            rider_info = route.rider_info or {}
            optimized_data = await self.route_optimizer.optimize_route(
                starting_point=current_location,
                stops=delivery_stops,
                optimize_for=route.optimizations_applied or ["time", "distance", "safety"],
                rider_info=rider_info,
                vehicle_type=route.vehicle_type or "motorcycle",
                departure_time=datetime.now()
            )
            
            # Update route in database
            route.starting_point = {
                "lat": current_location.latitude,
                "lng": current_location.longitude
            }
            route.optimized_sequence = optimized_data["sequence"]
            route.total_distance_meters = optimized_data["total_distance_meters"]
            route.total_duration_seconds = optimized_data["total_duration_seconds"]
            route.average_safety_score = optimized_data["average_safety_score"]
            route.total_fuel_liters = optimized_data["total_fuel_liters"]
            route.estimated_arrivals = {
                k: v.isoformat() if isinstance(v, datetime) else v
                for k, v in optimized_data["estimated_arrivals"].items()
            }
            route.updated_at = datetime.utcnow()
            
            # Mark monitoring record as reoptimized
            monitoring = db.query(RouteMonitoring).filter(
                RouteMonitoring.route_id == route_id,
                RouteMonitoring.requires_reoptimization == True,
                RouteMonitoring.reoptimized_at == None
            ).order_by(RouteMonitoring.timestamp.desc()).first()
            
            if monitoring:
                monitoring.reoptimized_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Route {route_id} reoptimized successfully")
            
            return optimized_data
            
        except Exception as e:
            logger.error(f"Error reoptimizing route: {e}")
            db.rollback()
            return None

