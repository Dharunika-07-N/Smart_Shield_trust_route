"""Traffic service for fetching and processing traffic data."""
from typing import List, Dict, Optional, Tuple
from geopy.distance import distance as geopy_distance
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from config.config import settings
from loguru import logger


class TrafficService:
    """Service for traffic data operations."""
    
    def __init__(self):
        self.base_speed_ms = 8.33  # 30 km/h average
        logger.info("TrafficService initialized")
    
    def get_traffic_level(
        self,
        start: Coordinate,
        end: Coordinate,
        use_api: bool = False
    ) -> Tuple[str, float, float]:
        """Get traffic level for a segment.
        
        Returns:
            Tuple of (traffic_level, distance_meters, duration_seconds)
        """
        # In production, this would call Google Maps Traffic API or similar
        if use_api and settings.GOOGLE_MAPS_API_KEY:
            return self._get_traffic_from_api(start, end)
        
        # Mock traffic data for development
        return self._get_mock_traffic(start, end)
    
    def _get_mock_traffic(
        self,
        start: Coordinate,
        end: Coordinate
    ) -> Tuple[str, float, float]:
        """Generate mock traffic data based on coordinates."""
        # Use coordinates as seed for consistent results
        seed = int(start.latitude * 1000 + start.longitude * 1000)
        random.seed(seed)
        
        traffic_levels = ['low', 'medium', 'high']
        weights = [0.5, 0.3, 0.2]  # 50% low, 30% medium, 20% high
        traffic = random.choices(traffic_levels, weights=weights)[0]
        
        # Calculate distance
        dist = geopy_distance(
            (start.latitude, start.longitude),
            (end.latitude, end.longitude)
        ).meters
        
        # Calculate speed based on traffic
        speed = self._get_speed_for_traffic(traffic)
        duration = dist / speed
        
        return traffic, dist, duration
    
    def _get_speed_for_traffic(self, traffic_level: str) -> float:
        """Get speed in m/s based on traffic level."""
        if traffic_level == 'high':
            return self.base_speed_ms * 0.5  # 50% slower
        elif traffic_level == 'medium':
            return self.base_speed_ms * 0.75  # 25% slower
        else:  # low
            return self.base_speed_ms
    
    def _get_traffic_from_api(
        self,
        start: Coordinate,
        end: Coordinate
    ) -> Tuple[str, float, float]:
        """Get traffic data from Google Maps API (future implementation)."""
        # TODO: Implement Google Maps Traffic API integration
        logger.warning("Traffic API integration not yet implemented, using mock data")
        return self._get_mock_traffic(start, end)
    
    def get_route_traffic(
        self,
        coordinates: List[Coordinate]
    ) -> List[Dict]:
        """Get traffic data for entire route."""
        if len(coordinates) < 2:
            return []
        
        segments = []
        for i in range(len(coordinates) - 1):
            start = coordinates[i]
            end = coordinates[i + 1]
            
            traffic, dist, duration = self.get_traffic_level(start, end)
            
            segments.append({
                "start": start,
                "end": end,
                "traffic_level": traffic,
                "distance_meters": dist,
                "duration_seconds": duration,
                "average_speed_ms": dist / duration if duration > 0 else 0
            })
        
        return segments
    
    def calculate_congestion_percentage(self, traffic_level: str) -> float:
        """Convert traffic level to congestion percentage."""
        mapping = {
            'low': 25.0,
            'medium': 50.0,
            'high': 85.0
        }
        return mapping.get(traffic_level, 50.0)
    
    def get_traffic_color(self, traffic_level: str) -> str:
        """Get color code for traffic level."""
        mapping = {
            'low': '#22c55e',      # green
            'medium': '#eab308',   # yellow
            'high': '#ef4444'      # red
        }
        return mapping.get(traffic_level, '#6b7280')  # gray default
    
    def optimize_for_traffic(
        self,
        route_segments: List[Dict]
    ) -> Dict:
        """Optimize route based on traffic conditions."""
        total_distance = sum(seg['distance_meters'] for seg in route_segments)
        total_duration = sum(seg['duration_seconds'] for seg in route_segments)
        
        # Count traffic levels
        traffic_counts = {'low': 0, 'medium': 0, 'high': 0}
        for seg in route_segments:
            traffic_counts[seg['traffic_level']] += 1
        
        total_segments = len(route_segments)
        avg_traffic = 'medium'
        if traffic_counts['high'] / total_segments > 0.4:
            avg_traffic = 'high'
        elif traffic_counts['low'] / total_segments > 0.6:
            avg_traffic = 'low'
        
        return {
            "total_distance_meters": total_distance,
            "total_duration_seconds": total_duration,
            "average_traffic": avg_traffic,
            "traffic_breakdown": traffic_counts,
            "route_efficiency_score": self._calculate_efficiency_score(traffic_counts, total_segments)
        }
    
    def _calculate_efficiency_score(
        self,
        traffic_counts: Dict[str, int],
        total_segments: int
    ) -> float:
        """Calculate route efficiency score (0-100)."""
        if total_segments == 0:
            return 0.0
        
        # More low traffic = higher score
        low_ratio = traffic_counts['low'] / total_segments
        medium_ratio = traffic_counts['medium'] / total_segments
        high_ratio = traffic_counts['high'] / total_segments
        
        score = (low_ratio * 100) + (medium_ratio * 70) + (high_ratio * 30)
        return round(score, 2)

