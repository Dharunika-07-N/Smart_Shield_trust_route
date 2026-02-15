"""
Traffic Data Integration Module
Integrates multiple open-source traffic data providers:
- OpenTraffic (community traffic speed data)
- OpenStreetMap road networks
- Popular Places crowd data
- Custom traffic estimation algorithms
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TrafficLevel(Enum):
    """Traffic congestion levels"""
    UNKNOWN = 0
    FREE_FLOW = 1
    LIGHT = 2
    MODERATE = 3
    HEAVY = 4
    SEVERE = 5


@dataclass
class TrafficSegment:
    """Represents a road segment with traffic data"""
    segment_id: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float
    speed_kmh: Optional[float]
    free_flow_speed: float
    traffic_level: TrafficLevel
    timestamp: datetime
    source: str


class TrafficDataProvider:
    """Base class for traffic data providers"""
    
    def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        """
        Get traffic data for a bounding box
        Args:
            bbox: (min_lat, min_lng, max_lat, max_lng)
        Returns:
            List of TrafficSegment objects
        """
        raise NotImplementedError


class OpenTrafficProvider(TrafficDataProvider):
    """
    OpenTraffic data provider
    Uses OpenTraffic API for real-time traffic speed data
    """
    
    def __init__(self, api_url: str = "https://api.opentraffic.io"):
        self.api_url = api_url
        self.session = requests.Session()
    
    def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        """Fetch traffic data from OpenTraffic"""
        try:
            min_lat, min_lng, max_lat, max_lng = bbox
            
            # OpenTraffic API endpoint for traffic tiles
            endpoint = f"{self.api_url}/tiles/speeds"
            
            params = {
                'bbox': f"{min_lng},{min_lat},{max_lng},{max_lat}",
                'format': 'json'
            }
            
            response = self.session.get(endpoint, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_opentraffic_response(data)
            else:
                logger.warning(f"OpenTraffic API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching OpenTraffic data: {e}")
            return []
    
    def _parse_opentraffic_response(self, data: Dict) -> List[TrafficSegment]:
        """Parse OpenTraffic API response"""
        segments = []
        
        for feature in data.get('features', []):
            try:
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [])
                
                if len(coords) >= 2:
                    start = coords[0]
                    end = coords[-1]
                    
                    speed = props.get('speed', None)
                    free_flow = props.get('free_flow_speed', 60)  # Default 60 km/h
                    
                    # Calculate traffic level based on speed ratio
                    traffic_level = self._calculate_traffic_level(speed, free_flow)
                    
                    segment = TrafficSegment(
                        segment_id=props.get('segment_id', f"seg_{len(segments)}"),
                        start_lat=start[1],
                        start_lng=start[0],
                        end_lat=end[1],
                        end_lng=end[0],
                        speed_kmh=speed,
                        free_flow_speed=free_flow,
                        traffic_level=traffic_level,
                        timestamp=datetime.now(),
                        source='opentraffic'
                    )
                    segments.append(segment)
                    
            except Exception as e:
                logger.error(f"Error parsing traffic segment: {e}")
                continue
        
        return segments
    
    def _calculate_traffic_level(self, current_speed: Optional[float], 
                                 free_flow_speed: float) -> TrafficLevel:
        """Calculate traffic level from speed ratio"""
        if current_speed is None:
            return TrafficLevel.UNKNOWN
        
        ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
        
        if ratio >= 0.85:
            return TrafficLevel.FREE_FLOW
        elif ratio >= 0.65:
            return TrafficLevel.LIGHT
        elif ratio >= 0.45:
            return TrafficLevel.MODERATE
        elif ratio >= 0.25:
            return TrafficLevel.HEAVY
        else:
            return TrafficLevel.SEVERE


class OSMTrafficEstimator(TrafficDataProvider):
    """
    Estimates traffic based on OpenStreetMap road types and time of day
    Fallback when real traffic data is unavailable
    """
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
    
    def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        """Estimate traffic from OSM road data"""
        try:
            roads = self._fetch_osm_roads(bbox)
            return self._estimate_traffic(roads)
        except Exception as e:
            logger.error(f"Error estimating traffic from OSM: {e}")
            return []
    
    def _fetch_osm_roads(self, bbox: Tuple[float, float, float, float]) -> List[Dict]:
        """Fetch road data from OpenStreetMap"""
        min_lat, min_lng, max_lat, max_lng = bbox
        
        # Overpass QL query for major roads
        query = f"""
        [out:json][timeout:25];
        (
          way["highway"~"motorway|trunk|primary|secondary"]
              ({min_lat},{min_lng},{max_lat},{max_lng});
        );
        out geom;
        """
        
        try:
            response = self.session.post(
                self.overpass_url,
                data={'data': query},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('elements', [])
            else:
                logger.warning(f"Overpass API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching OSM roads: {e}")
            return []
    
    def _estimate_traffic(self, roads: List[Dict]) -> List[TrafficSegment]:
        """Estimate traffic levels based on road type and time"""
        segments = []
        current_hour = datetime.now().hour
        
        # Peak hours: 8-10 AM and 5-8 PM
        is_peak_hour = (8 <= current_hour <= 10) or (17 <= current_hour <= 20)
        
        for road in roads:
            try:
                tags = road.get('tags', {})
                highway_type = tags.get('highway', 'unknown')
                geometry = road.get('geometry', [])
                
                if len(geometry) < 2:
                    continue
                
                # Estimate free flow speed based on road type
                free_flow_speed = self._get_free_flow_speed(highway_type)
                
                # Estimate current speed based on time and road type
                current_speed = self._estimate_current_speed(
                    highway_type, 
                    free_flow_speed, 
                    is_peak_hour
                )
                
                # Create segment for each road section
                for i in range(len(geometry) - 1):
                    start = geometry[i]
                    end = geometry[i + 1]
                    
                    traffic_level = self._calculate_traffic_level(
                        current_speed, 
                        free_flow_speed
                    )
                    
                    segment = TrafficSegment(
                        segment_id=f"osm_{road.get('id', i)}_{i}",
                        start_lat=start['lat'],
                        start_lng=start['lon'],
                        end_lat=end['lat'],
                        end_lng=end['lon'],
                        speed_kmh=current_speed,
                        free_flow_speed=free_flow_speed,
                        traffic_level=traffic_level,
                        timestamp=datetime.now(),
                        source='osm_estimated'
                    )
                    segments.append(segment)
                    
            except Exception as e:
                logger.error(f"Error processing road segment: {e}")
                continue
        
        return segments
    
    def _get_free_flow_speed(self, highway_type: str) -> float:
        """Get typical free flow speed for road type"""
        speed_map = {
            'motorway': 100,
            'trunk': 80,
            'primary': 60,
            'secondary': 50,
            'tertiary': 40,
            'residential': 30,
        }
        return speed_map.get(highway_type, 50)
    
    def _estimate_current_speed(self, highway_type: str, 
                                free_flow_speed: float, 
                                is_peak_hour: bool) -> float:
        """Estimate current speed based on conditions"""
        if not is_peak_hour:
            return free_flow_speed * 0.9  # 90% of free flow during off-peak
        
        # Peak hour congestion factors by road type
        congestion_factors = {
            'motorway': 0.6,
            'trunk': 0.65,
            'primary': 0.55,
            'secondary': 0.5,
            'tertiary': 0.6,
            'residential': 0.7,
        }
        
        factor = congestion_factors.get(highway_type, 0.6)
        return free_flow_speed * factor
    
    def _calculate_traffic_level(self, current_speed: float, 
                                 free_flow_speed: float) -> TrafficLevel:
        """Calculate traffic level from speed ratio"""
        ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
        
        if ratio >= 0.85:
            return TrafficLevel.FREE_FLOW
        elif ratio >= 0.65:
            return TrafficLevel.LIGHT
        elif ratio >= 0.45:
            return TrafficLevel.MODERATE
        elif ratio >= 0.25:
            return TrafficLevel.HEAVY
        else:
            return TrafficLevel.SEVERE


class TrafficDataAggregator:
    """
    Aggregates traffic data from multiple providers
    Falls back to estimation if real data unavailable
    """
    
    def __init__(self):
        self.providers = []
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)
    
    def add_provider(self, provider: TrafficDataProvider, priority: int = 1):
        """Add a traffic data provider with priority (higher = preferred)"""
        self.providers.append((priority, provider))
        self.providers.sort(key=lambda x: x[0], reverse=True)
    
    def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        """Get traffic data from available providers"""
        cache_key = f"{bbox}"
        
        # Check cache
        if cache_key in self.cache:
            cached_time, cached_data = self.cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                logger.info("Returning cached traffic data")
                return cached_data
        
        # Try providers in priority order
        for priority, provider in self.providers:
            try:
                logger.info(f"Fetching traffic data from {provider.__class__.__name__}")
                segments = provider.get_traffic_data(bbox)
                
                if segments:
                    # Cache the result
                    self.cache[cache_key] = (datetime.now(), segments)
                    logger.info(f"Got {len(segments)} traffic segments from {provider.__class__.__name__}")
                    return segments
                    
            except Exception as e:
                logger.error(f"Provider {provider.__class__.__name__} failed: {e}")
                continue
        
        logger.warning("No traffic data available from any provider")
        return []
    
    def get_traffic_for_route(self, route_coords: List[Tuple[float, float]]) -> Dict:
        """
        Get traffic information for a specific route
        Returns overall traffic level and segment details
        """
        if not route_coords:
            return {'overall_level': TrafficLevel.UNKNOWN, 'segments': []}
        
        # Calculate bounding box for route
        lats = [c[0] for c in route_coords]
        lngs = [c[1] for c in route_coords]
        bbox = (min(lats), min(lngs), max(lats), max(lngs))
        
        # Get all traffic segments in area
        all_segments = self.get_traffic_data(bbox)
        
        # Find segments that intersect with route
        route_segments = self._match_segments_to_route(route_coords, all_segments)
        
        # Calculate overall traffic level
        if route_segments:
            avg_level = sum(s.traffic_level.value for s in route_segments) / len(route_segments)
            overall_level = TrafficLevel(round(avg_level))
        else:
            overall_level = TrafficLevel.UNKNOWN
        
        return {
            'overall_level': overall_level,
            'segments': route_segments,
            'total_segments': len(route_segments),
            'timestamp': datetime.now()
        }
    
    def _match_segments_to_route(self, route_coords: List[Tuple[float, float]], 
                                 segments: List[TrafficSegment]) -> List[TrafficSegment]:
        """Find traffic segments that match the route"""
        matched = []
        threshold = 0.01  # ~1km tolerance
        
        for segment in segments:
            for lat, lng in route_coords:
                # Simple distance check (can be improved with proper geospatial libraries)
                if (abs(segment.start_lat - lat) < threshold and 
                    abs(segment.start_lng - lng) < threshold):
                    matched.append(segment)
                    break
        
        return matched


# Initialize default aggregator
default_aggregator = TrafficDataAggregator()

# Add providers in priority order
# Try OpenTraffic first (real data)
try:
    default_aggregator.add_provider(OpenTrafficProvider(), priority=10)
except:
    logger.warning("OpenTraffic provider not available")

# Always add OSM estimator as fallback
default_aggregator.add_provider(OSMTrafficEstimator(), priority=1)


def get_traffic_data(bbox: Tuple[float, float, float, float]) -> List[Dict]:
    """
    Public API: Get traffic data for a bounding box
    Returns list of traffic segments as dictionaries
    """
    segments = default_aggregator.get_traffic_data(bbox)
    
    return [
        {
            'segment_id': s.segment_id,
            'start': {'lat': s.start_lat, 'lng': s.start_lng},
            'end': {'lat': s.end_lat, 'lng': s.end_lng},
            'speed_kmh': s.speed_kmh,
            'free_flow_speed': s.free_flow_speed,
            'traffic_level': s.traffic_level.name,
            'traffic_level_value': s.traffic_level.value,
            'timestamp': s.timestamp.isoformat(),
            'source': s.source
        }
        for s in segments
    ]


def get_route_traffic(route_coords: List[Tuple[float, float]]) -> Dict:
    """
    Public API: Get traffic information for a route
    """
    result = default_aggregator.get_traffic_for_route(route_coords)
    
    return {
        'overall_level': result['overall_level'].name,
        'overall_level_value': result['overall_level'].value,
        'total_segments': result['total_segments'],
        'timestamp': result['timestamp'].isoformat(),
        'segments': [
            {
                'segment_id': s.segment_id,
                'speed_kmh': s.speed_kmh,
                'traffic_level': s.traffic_level.name,
                'source': s.source
            }
            for s in result['segments']
        ]
    }
