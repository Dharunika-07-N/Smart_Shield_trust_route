"""
In-Memory Location Cache Service
Simulates Redis-like behavior for ultra-fast location lookups.
- No database hit on every GPS update
- O(1) read for latest rider position
- Thread-safe with asyncio locks
- TTL (Time To Live) support for stale data cleanup
"""
import asyncio
import time
from typing import Dict, Optional, Any
from loguru import logger
from datetime import datetime


class LocationCacheEntry:
    """A single cached location entry with TTL."""
    def __init__(self, data: Dict[str, Any], ttl_seconds: int = 300):
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl_seconds

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl

    @property
    def age_seconds(self) -> float:
        return time.time() - self.created_at


class LocationCache:
    """
    High-performance in-memory cache for rider GPS locations.
    
    Architecture:
    - delivery_id → latest location (for order-specific queries)
    - rider_id → latest location (for fleet-wide queries)
    - All reads are O(1) dictionary lookups — no DB hit
    - Writes update both indexes simultaneously
    
    Interview keywords: in-memory caching, Redis pattern, hot path optimization
    """

    def __init__(self, default_ttl: int = 300):
        """
        Args:
            default_ttl: Seconds before a cached location is considered stale (default 5 min)
        """
        # Primary cache: delivery_id -> LocationCacheEntry
        self._delivery_cache: Dict[str, LocationCacheEntry] = {}
        
        # Secondary index: rider_id -> delivery_id (for fleet queries)
        self._rider_to_delivery: Dict[str, str] = {}
        
        # Fleet-wide cache: rider_id -> latest location
        self._fleet_cache: Dict[str, LocationCacheEntry] = {}
        
        self._default_ttl = default_ttl
        self._lock = asyncio.Lock()
        
        # Statistics
        self._hits = 0
        self._misses = 0
        
        logger.info("📦 LocationCache initialized (in-memory, Redis-like)")

    async def set_location(
        self,
        delivery_id: str,
        rider_id: str,
        latitude: float,
        longitude: float,
        status: str = "in_transit",
        speed_kmh: Optional[float] = None,
        heading: Optional[float] = None,
        battery_level: Optional[int] = None,
        reoptimization_needed: bool = False
    ) -> None:
        """
        Store the latest rider location in cache.
        This is called on EVERY GPS update — must be ultra-fast.
        """
        entry_data = {
            "delivery_id": delivery_id,
            "rider_id": rider_id,
            "latitude": latitude,
            "longitude": longitude,
            "status": status,
            "speed_kmh": speed_kmh,
            "heading": heading,
            "battery_level": battery_level,
            "reoptimization_needed": reoptimization_needed,
            "timestamp": datetime.utcnow().isoformat(),
            "cached_at": time.time()
        }

        async with self._lock:
            # Update delivery-specific cache
            self._delivery_cache[delivery_id] = LocationCacheEntry(
                entry_data, self._default_ttl
            )

            # Update fleet cache
            self._fleet_cache[rider_id] = LocationCacheEntry(
                entry_data, self._default_ttl
            )

            # Update rider → delivery index
            self._rider_to_delivery[rider_id] = delivery_id

    async def get_by_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached location for a specific delivery.
        O(1) lookup — no database hit.
        """
        async with self._lock:
            entry = self._delivery_cache.get(delivery_id)
            if entry and not entry.is_expired:
                self._hits += 1
                return {**entry.data, "cache_age_seconds": entry.age_seconds}
            elif entry and entry.is_expired:
                # Cleanup stale entry
                del self._delivery_cache[delivery_id]
            
            self._misses += 1
            return None

    async def get_by_rider(self, rider_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached location for a specific rider (fleet monitor use case).
        O(1) lookup.
        """
        async with self._lock:
            entry = self._fleet_cache.get(rider_id)
            if entry and not entry.is_expired:
                self._hits += 1
                return {**entry.data, "cache_age_seconds": entry.age_seconds}
            
            self._misses += 1
            return None

    async def get_all_fleet(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active rider locations (for dispatcher fleet view).
        Returns only non-expired entries.
        """
        async with self._lock:
            result = {}
            expired_keys = []
            
            for rider_id, entry in self._fleet_cache.items():
                if not entry.is_expired:
                    result[rider_id] = {**entry.data, "cache_age_seconds": entry.age_seconds}
                else:
                    expired_keys.append(rider_id)
            
            # Cleanup expired entries
            for key in expired_keys:
                del self._fleet_cache[key]
                if key in self._rider_to_delivery:
                    delivery_id = self._rider_to_delivery.pop(key)
                    self._delivery_cache.pop(delivery_id, None)
            
            return result

    async def invalidate(self, delivery_id: str) -> None:
        """Remove a delivery from cache (e.g., delivery completed)."""
        async with self._lock:
            if delivery_id in self._delivery_cache:
                del self._delivery_cache[delivery_id]
                logger.debug(f"Cache invalidated for delivery {delivery_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Cache statistics for monitoring."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate_percent": round(hit_rate, 2),
            "active_deliveries": len(self._delivery_cache),
            "active_riders": len(self._fleet_cache),
            "total_requests": total
        }

    async def cleanup_expired(self) -> int:
        """Cleanup all expired entries. Call this periodically."""
        async with self._lock:
            before = len(self._delivery_cache) + len(self._fleet_cache)
            
            self._delivery_cache = {
                k: v for k, v in self._delivery_cache.items() if not v.is_expired
            }
            self._fleet_cache = {
                k: v for k, v in self._fleet_cache.items() if not v.is_expired
            }
            
            after = len(self._delivery_cache) + len(self._fleet_cache)
            cleaned = before - after
            if cleaned > 0:
                logger.debug(f"Cache cleanup: removed {cleaned} expired entries")
            return cleaned


# Singleton instance — shared across all requests (like a Redis connection pool)
location_cache = LocationCache(default_ttl=300)
