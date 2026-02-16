"""Weather service for real-time weather data."""
import httpx
import os
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from config.config import settings
from api.schemas.delivery import Coordinate
from loguru import logger


class WeatherService:
    """Service for fetching weather data."""
    
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY", "")
        # Use OpenWeatherMap as primary, fallback to WorldWeatherOnline
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.worldweather_url = "https://api.worldweatheronline.com/premium/v1"
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl = 1800  # 30 minutes
    
    async def get_weather(self, coord: Coordinate) -> Dict:
        """
        Get current weather conditions for a location.
        Returns weather data with hazard factors.
        """
        cache_key = f"{coord.latitude:.2f},{coord.longitude:.2f}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if (datetime.now().timestamp() - cached_data.get("timestamp", 0)) < self.cache_ttl:
                return cached_data.get("data", {})
        
        try:
            # Try OpenWeatherMap first
            if self.api_key:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    url = f"{self.base_url}/weather"
                    params = {
                        "lat": coord.latitude,
                        "lon": coord.longitude,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                    response = await client.get(url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        weather_data = self._parse_openweather(data)
                        self.cache[cache_key] = {
                            "data": weather_data,
                            "timestamp": datetime.now().timestamp()
                        }
                        return weather_data
        except Exception as e:
            logger.warning(f"Weather API error: {e}, using mock data")
        
        # Fallback to mock data
        return self._get_mock_weather(coord)
    
    def _parse_openweather(self, data: Dict) -> Dict:
        """Parse OpenWeatherMap API response."""
        weather = data.get("weather", [{}])[0]
        main = data.get("main", {})
        wind = data.get("wind", {})
        
        # Calculate hazard score (0-100, higher = more hazardous)
        hazard_score = 0
        conditions = []
        
        # Precipitation
        if "rain" in data:
            precip = data["rain"].get("1h", 0)
            if precip > 0:
                hazard_score += min(40, precip * 4)  # Max 40 points for rain
                conditions.append(f"Rain: {precip}mm/h")
        
        # Wind speed
        wind_speed = wind.get("speed", 0)  # m/s
        if wind_speed > 10:  # > 36 km/h
            hazard_score += min(30, (wind_speed - 10) * 3)
            conditions.append(f"Strong winds: {wind_speed * 3.6:.1f} km/h")
        
        # Visibility
        visibility = data.get("visibility", 10000) / 1000  # km
        if visibility < 1:
            hazard_score += 30
            conditions.append(f"Low visibility: {visibility:.1f} km")
        elif visibility < 5:
            hazard_score += 15
            conditions.append(f"Reduced visibility: {visibility:.1f} km")
        
        # Extreme temperatures
        temp = main.get("temp", 20)
        if temp > 35 or temp < 5:
            hazard_score += 10
            conditions.append(f"Extreme temperature: {temp}°C")
        
        return {
            "temperature": temp,
            "humidity": main.get("humidity", 0),
            "wind_speed": wind_speed * 3.6,  # Convert to km/h
            "wind_direction": wind.get("deg", 0),
            "visibility": visibility,
            "precipitation": data.get("rain", {}).get("1h", 0),
            "condition": weather.get("main", "Clear"),
            "description": weather.get("description", ""),
            "hazard_score": min(100, hazard_score),
            "hazard_conditions": conditions,
            "is_safe": hazard_score < 30
        }
    
    def _get_mock_weather(self, coord: Coordinate) -> Dict:
        """Generate mock weather data for development."""
        # Simulate weather based on location (Coimbatore area)
        import random
        random.seed(int(coord.latitude * 100 + coord.longitude))
        
        # Coimbatore typically has moderate weather
        temp = random.uniform(20, 35)
        humidity = random.uniform(40, 80)
        wind_speed = random.uniform(5, 20)  # km/h
        visibility = random.uniform(5, 15)  # km
        precipitation = random.uniform(0, 2) if random.random() < 0.3 else 0
        
        hazard_score = 0
        conditions = []
        
        if precipitation > 0:
            hazard_score += min(40, precipitation * 4)
            conditions.append(f"Light rain: {precipitation:.1f}mm/h")
        
        if wind_speed > 15:
            hazard_score += min(20, (wind_speed - 15) * 2)
            conditions.append(f"Moderate winds: {wind_speed:.1f} km/h")
        
        return {
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind_speed,
            "wind_direction": random.randint(0, 360),
            "visibility": visibility,
            "precipitation": precipitation,
            "condition": "Rain" if precipitation > 0 else "Clear",
            "description": "Clear sky" if precipitation == 0 else "Light rain",
            "hazard_score": hazard_score,
            "hazard_conditions": conditions,
            "is_safe": hazard_score < 30
        }
    
    async def get_route_weather(self, coordinates: List[Coordinate]) -> List[Dict]:
        """Get weather data for multiple points along a route concurrently."""
        tasks = []
        for coord in coordinates:
            tasks.append(self.get_weather(coord))
        
        weather_results = await asyncio.gather(*tasks)
        
        results = []
        for i, weather in enumerate(weather_results):
            results.append({
                "coordinates": coordinates[i],
                "weather": weather
            })
        return results
    
    def calculate_weather_penalty(self, weather_data: Dict) -> float:
        """
        Calculate route penalty factor based on weather.
        Returns multiplier (1.0 = no penalty, >1.0 = slower/more dangerous).
        """
        hazard_score = weather_data.get("hazard_score", 0)
        
        # Penalty increases with hazard score
        # 0-30: minimal penalty (1.0-1.1)
        # 30-60: moderate penalty (1.1-1.3)
        # 60-100: high penalty (1.3-1.6)
        if hazard_score < 30:
            penalty = 1.0 + (hazard_score / 300)
        elif hazard_score < 60:
            penalty = 1.1 + ((hazard_score - 30) / 150)
        else:
            penalty = 1.3 + ((hazard_score - 60) / 100)
        
        return min(1.6, penalty)

