"""Traffic service for fetching and processing traffic data."""
from typing import List, Dict, Optional, Tuple, Any
try:
    from geopy.distance import distance as geopy_distance
except ImportError:
    geopy_distance = None

import random
import sys
import math
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import httpx

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from config.config import settings
from loguru import logger


# --- Traffic Data Providers (OpenTraffic & OSM) ---

class TrafficLevelEnum(Enum):
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
    traffic_level: TrafficLevelEnum
    timestamp: datetime
    source: str


class TrafficDataProvider:
    """Base class for traffic data providers"""
    
    async def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        """Get traffic data for a bounding box: (min_lat, min_lng, max_lat, max_lng)"""
        raise NotImplementedError


class OpenTrafficProvider(TrafficDataProvider):
    """OpenTraffic data provider: Real-time traffic speed data"""
    
    def __init__(self, api_url: str = "https://api.opentraffic.io"):
        self.api_url = api_url
        self.session = requests.Session()
    
    async def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        try:
            min_lat, min_lng, max_lat, max_lng = bbox
            endpoint = f"{self.api_url}/tiles/speeds"
            params = {'bbox': f"{min_lng},{min_lat},{max_lng},{max_lat}", 'format': 'json'}
            
            # Short timeout to not block
            async with httpx.AsyncClient(timeout=2.0) as client:
                response = await client.get(endpoint, params=params)
            
            if response.status_code == 200:
                return self._parse_opentraffic_response(response.json())
            return []
        except Exception:
            # Silent fail for OpenTraffic as it's often unavailable in free tier or regions
            return []
    
    def _parse_opentraffic_response(self, data: Dict) -> List[TrafficSegment]:
        segments = []
        for feature in data.get('features', []):
            try:
                props = feature.get('properties', {})
                coords = feature.get('geometry', {}).get('coordinates', [])
                if len(coords) >= 2:
                    start, end = coords[0], coords[-1]
                    speed = props.get('speed')
                    free_flow = props.get('free_flow_speed', 60)
                    lvl = self._calculate_traffic_level(speed, free_flow)
                    
                    segments.append(TrafficSegment(
                        segment_id=props.get('segment_id', f"ot_{len(segments)}"),
                        start_lat=start[1], start_lng=start[0],
                        end_lat=end[1], end_lng=end[0],
                        speed_kmh=speed, free_flow_speed=free_flow,
                        traffic_level=lvl, timestamp=datetime.now(), source='opentraffic'
                    ))
            except Exception: pass
        return segments

    def _calculate_traffic_level(self, current_speed, free_flow_speed) -> TrafficLevelEnum:
        if current_speed is None: return TrafficLevelEnum.UNKNOWN
        ratio = current_speed / free_flow_speed if free_flow_speed > 0 else 1.0
        if ratio >= 0.85: return TrafficLevelEnum.FREE_FLOW
        elif ratio >= 0.65: return TrafficLevelEnum.LIGHT
        elif ratio >= 0.45: return TrafficLevelEnum.MODERATE
        elif ratio >= 0.25: return TrafficLevelEnum.HEAVY
        else: return TrafficLevelEnum.SEVERE


class OSMTrafficEstimator(TrafficDataProvider):
    """Estimates traffic based on OpenStreetMap road types and time of day"""
    
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.session = requests.Session()
    
    async def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        try:
            roads = await self._fetch_osm_roads(bbox)
            return self._estimate_traffic(roads)
        except Exception as e:
            logger.warning(f"OSM estimation failed: {e}")
            return []
    
    async def _fetch_osm_roads(self, bbox: Tuple[float, float, float, float]) -> List[Dict]:
        min_lat, min_lng, max_lat, max_lng = bbox
        query = f"""[out:json][timeout:3];(way["highway"~"motorway|trunk|primary|secondary"]({min_lat},{min_lng},{max_lat},{max_lng}););out geom;"""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                resp = await client.post(self.overpass_url, data={'data': query})
            return resp.json().get('elements', []) if resp.status_code == 200 else []
        except Exception: return []

    def _estimate_traffic(self, roads: List[Dict]) -> List[TrafficSegment]:
        segments = []
        is_peak = (8 <= datetime.now().hour <= 10) or (17 <= datetime.now().hour <= 20)
        
        for road in roads:
            try:
                tags = road.get('tags', {})
                hw_type = tags.get('highway', 'unknown')
                geom = road.get('geometry', [])
                if len(geom) < 2: continue
                
                ff_speed = self._get_ff_speed(hw_type)
                curr_speed = self._est_speed(hw_type, ff_speed, is_peak)
                lvl = self._calc_level(curr_speed, ff_speed)
                
                for i in range(len(geom)-1):
                    s, e = geom[i], geom[i+1]
                    segments.append(TrafficSegment(
                        segment_id=f"osm_{road.get('id', i)}_{i}",
                        start_lat=s['lat'], start_lng=s['lon'],
                        end_lat=e['lat'], end_lng=e['lon'],
                        speed_kmh=curr_speed, free_flow_speed=ff_speed,
                        traffic_level=lvl, timestamp=datetime.now(), source='osm_est'
                    ))
            except Exception: continue
        return segments

    def _get_ff_speed(self, hw):
        return {'motorway': 100, 'trunk': 80, 'primary': 60, 'secondary': 50}.get(hw, 40)

    def _est_speed(self, hw, ff, peak):
        if not peak: return ff * 0.9
        factor = {'motorway': 0.6, 'trunk': 0.65, 'primary': 0.55}.get(hw, 0.5)
        return ff * factor

    def _calc_level(self, curr, ff) -> TrafficLevelEnum:
        ratio = curr / ff if ff > 0 else 1.0
        if ratio >= 0.85: return TrafficLevelEnum.FREE_FLOW
        elif ratio >= 0.65: return TrafficLevelEnum.LIGHT
        elif ratio >= 0.45: return TrafficLevelEnum.MODERATE
        elif ratio >= 0.25: return TrafficLevelEnum.HEAVY
        else: return TrafficLevelEnum.SEVERE


class TrafficDataAggregator:
    def __init__(self):
        self.providers = [] # List of (priority, provider)
        self.cache = {}
        self.cache_duration = timedelta(minutes=5)

    def add_provider(self, provider, priority=1):
        self.providers.append((priority, provider))
        self.providers.sort(key=lambda x: x[0], reverse=True)

    async def get_traffic_data(self, bbox: Tuple[float, float, float, float]) -> List[TrafficSegment]:
        key = f"{bbox}"
        if key in self.cache:
            t, data = self.cache[key]
            if datetime.now() - t < self.cache_duration: return data
        
        for _, p in self.providers:
            data = await p.get_traffic_data(bbox)
            if data:
                self.cache[key] = (datetime.now(), data)
                return data
        return []

# Initialize singleton aggregator
aggregator = TrafficDataAggregator()
aggregator.add_provider(OpenTrafficProvider(), priority=10)
aggregator.add_provider(OSMTrafficEstimator(), priority=1)


# --- API Service Class ---

class TrafficService:
    """Service for traffic data operations."""
    
    def __init__(self):
        self.base_speed_ms = 8.33  # 30 km/h average
        logger.info("TrafficService initialized with real-time providers")

    def _calculate_distance(self, start: Coordinate, end: Coordinate) -> float:
        """Calculate distance in meters (using geopy or fallback)."""
        if geopy_distance:
            return geopy_distance((start.latitude, start.longitude), (end.latitude, end.longitude)).meters
        # Haversine fallback
        R = 6371000
        p1 = start.latitude * math.pi / 180
        p2 = end.latitude * math.pi / 180
        dphi = (end.latitude - start.latitude) * math.pi / 180
        dlam = (end.longitude - start.longitude) * math.pi / 180
        a = math.sin(dphi/2)**2 + math.cos(p1) * math.cos(p2) * math.sin(dlam/2)**2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    async def get_bbox_traffic(self, min_lat, min_lng, max_lat, max_lng) -> List[Dict]:
        """Get flattened traffic segments for a bounding box."""
        segments = await aggregator.get_traffic_data((min_lat, min_lng, max_lat, max_lng))
        return [
            {
                'segment_id': s.segment_id,
                'start': {'lat': s.start_lat, 'lng': s.start_lng},
                'end': {'lat': s.end_lat, 'lng': s.end_lng},
                'speed_kmh': s.speed_kmh,
                'free_flow_speed': s.free_flow_speed,
                'traffic_level': s.traffic_level.name,
                'source': s.source,
                'timestamp': s.timestamp.isoformat()
            }
            for s in segments
        ]

    async def get_traffic_level(self, start: Coordinate, end: Coordinate, use_api: bool = False) -> Tuple[str, float, float]:
        """Get traffic level for a segment (start->end)."""
        # Try to use aggregator for real data along this path
        # Construct a small bbox around the segment
        margin = 0.002 # ~200m
        bbox = (
            min(start.latitude, end.latitude) - margin,
            min(start.longitude, end.longitude) - margin,
            max(start.latitude, end.latitude) + margin,
            max(start.longitude, end.longitude) + margin
        )
        
        segments = await aggregator.get_traffic_data(bbox)
        
        # Simple match: if any segment in bbox is congested, report it
        # This is a simplification; ideal would be geospatial matching
        # Fallback to mock/calc if no segments returned
        
        dist = self._calculate_distance(start, end)
        
        if segments:
            # Average level
            avg_val = sum(s.traffic_level.value for s in segments) / len(segments)
            lvl_val = round(avg_val)
            
            level_map = {0: 'low', 1: 'low', 2: 'low', 3: 'medium', 4: 'high', 5: 'high'}
            traffic = level_map.get(lvl_val, 'low')
            
            speed = self._get_speed_for_traffic(traffic)
            duration = dist / speed
            return traffic, dist, duration
            
        # Fallback to mock
        return self._get_mock_traffic(start, end)
    
    def _get_mock_traffic(self, start: Coordinate, end: Coordinate) -> Tuple[str, float, float]:
        """Generate mock traffic data based on coordinates."""
        seed = int(start.latitude * 1000 + start.longitude * 1000)
        random.seed(seed)
        traffic = random.choices(['low', 'medium', 'high'], weights=[0.5, 0.3, 0.2])[0]
        dist = self._calculate_distance(start, end)
        speed = self._get_speed_for_traffic(traffic)
        return traffic, dist, dist/speed
    
    def _get_speed_for_traffic(self, traffic_level: str) -> float:
        if traffic_level == 'high': return self.base_speed_ms * 0.5
        elif traffic_level == 'medium': return self.base_speed_ms * 0.75
        else: return self.base_speed_ms
    
    async def get_route_traffic(self, coordinates: List[Coordinate]) -> List[Dict]:
        """Get traffic data for entire route."""
        if len(coordinates) < 2: return []
        segments = []
        for i in range(len(coordinates) - 1):
            s, e = coordinates[i], coordinates[i + 1]
            traffic, dist, dur = await self.get_traffic_level(s, e)
            segments.append({
                "start": s, "end": e, "traffic_level": traffic,
                "distance_meters": dist, "duration_seconds": dur,
                "average_speed_ms": dist/dur if dur else 0
            })
        return segments
    
    def calculate_congestion_percentage(self, traffic_level: str) -> float:
        return {'low': 25.0, 'medium': 50.0, 'high': 85.0}.get(traffic_level, 50.0)
    
    def get_traffic_color(self, traffic_level: str) -> str:
        return {'low': '#22c55e', 'medium': '#eab308', 'high': '#ef4444'}.get(traffic_level, '#6b7280')

    def optimize_for_traffic(self, route_segments: List[Dict]) -> Dict:
        """Optimize route based on traffic conditions."""
        total_dist = sum(s['distance_meters'] for s in route_segments)
        total_dur = sum(s['duration_seconds'] for s in route_segments)
        counts = {'low': 0, 'medium': 0, 'high': 0}
        for s in route_segments: counts[s['traffic_level']] += 1
        
        total = len(route_segments)
        if total == 0: avg = 'low'
        elif counts['high']/total > 0.4: avg = 'high'
        elif counts['low']/total > 0.6: avg = 'low'
        else: avg = 'medium'
        
        score = 0
        if total > 0:
            score = (counts['low']/total * 100) + (counts['medium']/total * 70) + (counts['high']/total * 30)
            
        return {
            "total_distance_meters": total_dist,
            "total_duration_seconds": total_dur,
            "average_traffic": avg,
            "traffic_breakdown": counts,
            "route_efficiency_score": round(score, 2)
        }
