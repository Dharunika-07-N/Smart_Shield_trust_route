"""
Maps and Routing Service Hub
Prioritizes Google Maps, then GraphHopper, then OSRM, then Mock Data.
"""
import googlemaps
import polyline
import httpx
import asyncio
import concurrent.futures
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from loguru import logger
from config.config import settings

# Providers
from api.services.graphhopper import GraphHopperService
from api.services.osrm_service import OSRMService

class MapsService:
    """Unified maps service with intelligent fallbacks."""
    
    def __init__(self):
        # Initialize Google Maps
        self.gmaps_key = settings.GOOGLE_MAPS_API_KEY
        if self.gmaps_key and not self.gmaps_key.startswith('YOUR_'):
            try:
                self.gmaps = googlemaps.Client(key=self.gmaps_key)
                logger.info("Google Maps Client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Google Maps: {e}")
                self.gmaps = None
        else:
            self.gmaps = None
            logger.warning("Google Maps API key missing or invalid")

        # Initialize GraphHopper
        self.gh_api_key = settings.GRAPHHOPPER_API_KEY
        if self.gh_api_key and not self.gh_api_key.startswith('YOUR_'):
            self.graphhopper = GraphHopperService(api_key=self.gh_api_key)
            logger.info("GraphHopper Service initialized")
        else:
            self.graphhopper = None
            logger.warning("GraphHopper API key missing")

        # Initialize OSRM (FREE!)
        try:
            self.osrm = OSRMService()
            logger.info("OSRM Service initialized (FREE Fallback)")
        except Exception as e:
            logger.error(f"Failed to initialize OSRM: {e}")
            self.osrm = None

    def _get_lat_lng(self, point: any) -> Tuple[float, float]:
        """Convert various point formats to (lat, lng) tuple."""
        if hasattr(point, 'latitude'):
            return (point.latitude, point.longitude)
        if isinstance(point, (list, tuple)) and len(point) >= 2:
            return (float(point[0]), float(point[1]))
        if isinstance(point, dict):
            if 'lat' in point:
                return (float(point['lat']), float(point['lng']))
            if 'latitude' in point:
                return (float(point['latitude']), float(point['longitude']))
        return (0.0, 0.0)

    def decode_polyline(self, points: str) -> List[Tuple[float, float]]:
        """Decode a polyline string into coordinates."""
        try:
            return polyline.decode(points)
        except Exception:
            return []

    def get_directions(
        self, 
        origin: any, 
        destination: any, 
        waypoints: Optional[List[any]] = None,
        alternatives: bool = True,
        **kwargs
    ) -> Optional[List[Dict]]:
        """
        Get driving directions with multiple alternatives and traffic data.
        Falls back through providers: Google -> GraphHopper -> OSRM -> Mock.
        """
        orig = self._get_lat_lng(origin)
        dest = self._get_lat_lng(destination)
        waypoint_list = None
        if waypoints:
            waypoint_list = [self._get_lat_lng(wp) for wp in waypoints]

        # 1. Try Google Maps First
        if self.gmaps:
            try:
                logger.info(f"Routing request: {orig} to {dest} via Google")
                g_waypoints = [f"{wp[0]},{wp[1]}" for wp in waypoint_list] if waypoint_list else None
                directions = self.gmaps.directions(
                    origin=orig,
                    destination=dest,
                    waypoints=g_waypoints,
                    mode="driving",
                    alternatives=alternatives,
                    departure_time=datetime.now(),
                    traffic_model="best_guess",
                    optimize_waypoints=True if waypoints else False
                )
                
                if directions:
                    logger.info(f"Google Maps returned {len(directions)} route(s)")
                    for route in directions:
                        route_coords = []
                        # HIGH-RES: Use polyline if possible
                        if route.get('overview_polyline', {}).get('points'):
                            try:
                                decoded = self.decode_polyline(route['overview_polyline']['points'])
                                route_coords = [{'lat': p[0], 'lng': p[1]} for p in decoded]
                            except Exception: pass
                        
                        # Fallback to steps
                        if not route_coords:
                            for leg in route.get('legs', []):
                                for step in leg.get('steps', []):
                                    start = step.get('start_location', {})
                                    route_coords.append({'lat': start.get('lat'), 'lng': start.get('lng')})
                                    end = step.get('end_location', {})
                                    route_coords.append({'lat': end.get('lat'), 'lng': end.get('lng')})
                        
                        route['route_coordinates'] = route_coords
                        route['provider'] = 'google'
                    return directions
            except Exception as e:
                logger.warning(f"Google Maps API error: {e}. Trying GraphHopper...")

        # 2. Try GraphHopper
        if self.graphhopper:
            try:
                logger.info("Routing request: via GraphHopper")
                gh_kwargs = {k: v for k, v in kwargs.items() if k in ('vehicle', 'locale')}
                gh_route = self.graphhopper.get_directions(orig, dest, waypoint_list, **gh_kwargs)
                if gh_route:
                    gh_route['provider'] = 'graphhopper'
                    return [gh_route]
            except Exception as e:
                logger.warning(f"GraphHopper API error: {e}. Trying OSRM...")

        # 3. Try OSRM (Free Fallback)
        if self.osrm:
            try:
                logger.info("Routing request: via OSRM (FREE)")
                import asyncio
                import concurrent.futures
                
                osrm_routes = None
                if asyncio.iscoroutinefunction(self.osrm.get_directions):
                    def run_osrm():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(
                                self.osrm.get_directions(orig, dest, waypoint_list, alternatives=alternatives)
                            )
                        finally:
                            new_loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_osrm)
                        osrm_routes = future.result(timeout=10)
                else:
                    osrm_routes = self.osrm.get_directions(orig, dest, waypoint_list, alternatives=alternatives)
                
                if osrm_routes:
                    for r in osrm_routes:
                        r['provider'] = 'osrm'
                    return osrm_routes
            except Exception as e:
                logger.warning(f"OSRM API error: {e}. Final fallback to Mock.")

        # 4. Final Fallback: Mock Data (Enriched with jitter to avoid straight lines)
        logger.info("Routing request: FALLBACK TO MOCK DATA")
        return self._get_mock_directions(origin, destination, waypoints)

    def _get_mock_directions(self, origin, destination, waypoints=None) -> List[Dict]:
        """Generate mock directions with non-straight paths."""
        orig = self._get_lat_lng(origin)
        dest = self._get_lat_lng(destination)
        
        # Calculate midpoint with jitter
        mid_lat = (orig[0] + dest[0]) / 2
        mid_lng = (orig[1] + dest[1]) / 2
        
        # Add slight curve to path
        offset_lat = mid_lat + 0.005 # ~500m
        offset_lng = mid_lng + 0.005
        
        mock_points = [orig, (offset_lat, offset_lng), dest]
        
        route = {
            'summary': 'Secure Corridor (Fallback)',
            'legs': [{
                'distance': {'text': '12.5 km', 'value': 12500},
                'duration': {'text': '18 mins', 'value': 1080},
                'start_address': f'{orig[0]}, {orig[1]}',
                'end_address': f'{dest[0]}, {dest[1]}',
                'steps': [{
                    'distance': {'text': '12.5 km', 'value': 12500},
                    'duration': {'text': '18 mins', 'value': 1080},
                    'html_instructions': 'Head towards destination via secure route',
                    'start_location': {'lat': orig[0], 'lng': orig[1]},
                    'end_location': {'lat': dest[0], 'lng': dest[1]},
                    'maneuver': 'straight'
                }]
            }],
            'overview_polyline': {'points': polyline.encode(mock_points)},
            'route_coordinates': [{'lat': p[0], 'lng': p[1]} for p in mock_points],
            'warnings': ['Using mock data - provider offline'],
            'provider': 'mock'
        }
        return [route]

    def calculate_straight_distance(self, p1: any, p2: any) -> float:
        """Calculate Haversine distance in meters."""
        import math
        lat1, lon1 = self._get_lat_lng(p1)
        lat2, lon2 = self._get_lat_lng(p2)
        
        R = 6371000 # Earth radius
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlam = math.radians(lon2 - lon1)
        
        a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    # Alias for compatibility
    get_all_directions = get_directions
