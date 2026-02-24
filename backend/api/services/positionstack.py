"""
PositionStack Geocoding Service
=================================
Accurate Geocoding API for forward and reverse geocoding.
Built for logistics and delivery tracking.
"""

import httpx
from typing import Dict, Optional, List
from loguru import logger
from config.config import settings
from api.schemas.delivery import Coordinate

class PositionStackService:
    """Service for geocoding using PositionStack API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.POSITIONSTACK_API_KEY
        self.base_url = "http://api.positionstack.com/v1" # http for free tier, https for paid
        
        if not self.api_key:
            logger.warning("PositionStack API key missing. Geocoding will fall back to other providers.")

    async def geocode(self, query: str) -> Optional[Coordinate]:
        """Convert address string to coordinates."""
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/forward"
            params = {
                'access_key': self.api_key,
                'query': query,
                'limit': 1
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', [])
                if results:
                    res = results[0]
                    return Coordinate(
                        latitude=float(res['latitude']),
                        longitude=float(res['longitude'])
                    )
            else:
                logger.error(f"PositionStack Geocoding Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"PositionStack request failed: {e}")
            
        return None

    async def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """Convert coordinates to address string."""
        if not self.api_key:
            return None
            
        try:
            url = f"{self.base_url}/reverse"
            params = {
                'access_key': self.api_key,
                'query': f"{lat},{lng}",
                'limit': 1
            }
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', [])
                if results:
                    return results[0].get('label', f"{lat}, {lng}")
            else:
                logger.error(f"PositionStack Reverse Geocoding Error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"PositionStack Reverse Geocoding request failed: {e}")
            
        return None
