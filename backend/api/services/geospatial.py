import h3
from typing import List, Dict, Set, Optional
import time
from loguru import logger

# Check H3 version to use correct API
H3_VERSION = int(h3.__version__.split('.')[0])

class GeospatialService:
    """
    Advanced Geospatial Service using Uber's H3 Hexagonal Indexing.
    Provides O(1) proximity searching and grid-based fleet management.
    Compatible with H3 v3 and v4.
    """
    
    def __init__(self, resolution: int = 9):
        # Resolution 9 is approx 0.1 sq km (hex edge ~174m) - perfect city scale
        self.resolution = resolution
        # In-memory 'Hive' structure: {hex_id: {rider_id: last_ping_time}}
        self._hive: Dict[str, Dict[str, float]] = {}
        # TTL for online status: 5 minutes (300 seconds)
        self.online_timeout = 300
    
    def get_hex_id(self, latitude: float, longitude: float) -> str:
        """Convert GPS coordinates to H3 Hexagon ID."""
        try:
            if H3_VERSION >= 4:
                return h3.latlng_to_cell(latitude, longitude, self.resolution)
            else:
                return h3.geo_to_h3(latitude, longitude, self.resolution)
        except Exception as e:
            logger.error(f"H3 Conversion Error (v{H3_VERSION}): {e}")
            return ""

    def update_rider_location(self, rider_id: str, latitude: float, longitude: float):
        """
        Update the Hive registry with the rider's current hexagonal cell.
        This handles the O(1) indexing part of the system.
        """
        hex_id = self.get_hex_id(latitude, longitude)
        if not hex_id:
            return

        currentTime = time.time()
        
        # Add to new hex
        if hex_id not in self._hive:
            self._hive[hex_id] = {}
        
        self._hive[hex_id][rider_id] = currentTime
        
        # Clean up stale riders from this hex occasionally
        self._cleanup_hex(hex_id)

    def find_nearby_riders(self, latitude: float, longitude: float, k_rings: int = 1) -> List[str]:
        """
        Find all active rider IDs in the hexagonal neighborhood (K-Ring).
        """
        center_hex = self.get_hex_id(latitude, longitude)
        if not center_hex:
            return []

        # Get the ring of cells around the center
        try:
            if H3_VERSION >= 4:
                search_cells = h3.grid_disk(center_hex, k_rings)
            else:
                search_cells = h3.k_ring(center_hex, k_rings)
        except Exception as e:
            logger.error(f"H3 Neighbor Error: {e}")
            return []
        
        nearby_riders = []
        now = time.time()
        
        for cell in search_cells:
            if cell in self._hive:
                for rider_id, timestamp in self._hive[cell].items():
                    # Only include if rider hasn't timed out
                    if now - timestamp < self.online_timeout:
                        nearby_riders.append(rider_id)
        
        return list(set(nearby_riders))

    def _cleanup_hex(self, hex_id: str):
        """Remove stale riders from a specific hex."""
        if hex_id not in self._hive:
            return
            
        now = time.time()
        stale_ids = [
            rid for rid, ts in self._hive[hex_id].items() 
            if now - ts > self.online_timeout
        ]
        
        for rid in stale_ids:
            del self._hive[hex_id][rid]
            
        if not self._hive[hex_id]:
            del self._hive[hex_id]

    def get_cluster_stats(self) -> Dict[str, int]:
        """Get distribution of riders across hexagons."""
        stats = {}
        now = time.time()
        for hex_id, riders in self._hive.items():
            active_count = len([rid for rid, ts in riders.items() if now - ts < self.online_timeout])
            if active_count > 0:
                stats[hex_id] = active_count
        return stats

# Global Singleton instance
geo_service = GeospatialService()
