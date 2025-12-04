"""Crime data service for Tamil Nadu crime statistics."""
import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from geopy.distance import distance as geopy_distance
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from api.schemas.delivery import Coordinate
from loguru import logger


class CrimeDataService:
    """Service for accessing Tamil Nadu crime data."""
    
    # Tamil Nadu district coordinates (approximate centers)
    # Source: https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022
    DISTRICT_COORDS = {
        "Chennai": (13.0827, 80.2707),
        "Coimbatore": (11.0168, 76.9558),
        "Madurai": (9.9252, 78.1198),
        "Tiruchirappalli": (10.7905, 78.7047),
        "Salem": (11.6643, 78.1460),
        "Tirunelveli": (8.7139, 77.7567),
        "Erode": (11.3410, 77.7172),
        "Thanjavur": (10.7869, 79.1378),
        "Tiruppur": (11.1085, 77.3411),
        "Dindigul": (10.3629, 77.9750),
    }
    
    def __init__(self):
        self.crime_data: Dict[str, Dict] = {}
        self.data_dir = Path("data/crime")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_crime_data()
    
    def _load_crime_data(self):
        """Load crime data from CSV files or use defaults."""
        # Try to load from CSV files if they exist
        csv_files = list(self.data_dir.glob("*.csv"))
        
        if csv_files:
            logger.info(f"Loading crime data from {len(csv_files)} CSV files")
            for csv_file in csv_files:
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            district = row.get('District', '').strip()
                            if district:
                                self._parse_crime_row(district, row)
                except Exception as e:
                    logger.warning(f"Error loading {csv_file}: {e}")
        else:
            # Use default crime data for Tamil Nadu districts
            logger.info("Using default crime data for Tamil Nadu districts")
            self._load_default_crime_data()
    
    def _parse_crime_row(self, district: str, row: Dict):
        """Parse a row of crime data."""
        if district not in self.crime_data:
            self.crime_data[district] = {
                "total_crimes": 0,
                "murders": 0,
                "sexual_harassment": 0,
                "road_accidents": 0,
                "suicides": 0,
                "coordinates": self.DISTRICT_COORDS.get(district, (11.0, 77.0))
            }
        
        # Parse different crime types
        try:
            self.crime_data[district]["total_crimes"] += int(row.get('Total Crimes', 0) or 0)
            self.crime_data[district]["murders"] += int(row.get('Murders', 0) or 0)
            self.crime_data[district]["sexual_harassment"] += int(row.get('Sexual Harassment', 0) or 0)
            self.crime_data[district]["road_accidents"] += int(row.get('Road Accidents', 0) or 0)
            self.crime_data[district]["suicides"] += int(row.get('Suicides', 0) or 0)
        except (ValueError, TypeError):
            pass
    
    def _load_default_crime_data(self):
        """Load default crime statistics for Tamil Nadu districts."""
        # Based on 2022 Tamil Nadu crime statistics
        # Normalized values for demonstration (actual values would come from CSV)
        default_data = {
            "Chennai": {
                "total_crimes": 45000,
                "murders": 120,
                "sexual_harassment": 850,
                "road_accidents": 2100,
                "suicides": 450,
                "coordinates": self.DISTRICT_COORDS["Chennai"]
            },
            "Coimbatore": {
                "total_crimes": 18000,
                "murders": 45,
                "sexual_harassment": 320,
                "road_accidents": 850,
                "suicides": 180,
                "coordinates": self.DISTRICT_COORDS["Coimbatore"]
            },
            "Madurai": {
                "total_crimes": 15000,
                "murders": 38,
                "sexual_harassment": 280,
                "road_accidents": 720,
                "suicides": 150,
                "coordinates": self.DISTRICT_COORDS["Madurai"]
            },
            "Tiruchirappalli": {
                "total_crimes": 12000,
                "murders": 30,
                "sexual_harassment": 220,
                "road_accidents": 580,
                "suicides": 120,
                "coordinates": self.DISTRICT_COORDS["Tiruchirappalli"]
            },
            "Salem": {
                "total_crimes": 10000,
                "murders": 25,
                "sexual_harassment": 180,
                "road_accidents": 490,
                "suicides": 100,
                "coordinates": self.DISTRICT_COORDS["Salem"]
            },
        }
        
        # Add other districts with lower crime rates
        for district, coords in self.DISTRICT_COORDS.items():
            if district not in default_data:
                default_data[district] = {
                    "total_crimes": 5000,
                    "murders": 12,
                    "sexual_harassment": 90,
                    "road_accidents": 240,
                    "suicides": 50,
                    "coordinates": coords
                }
        
        self.crime_data = default_data
    
    def get_crime_score(self, coord: Coordinate, radius_km: float = 10.0) -> float:
        """
        Get crime risk score (0-100) for a location.
        Higher score = more crime = lower safety.
        """
        min_score = 0
        max_crime_density = 0
        
        # Find nearest districts and calculate weighted crime density
        for district, data in self.crime_data.items():
            dist_coords = data["coordinates"]
            dist_km = geopy_distance(
                (coord.latitude, coord.longitude),
                dist_coords
            ).km
            
            if dist_km <= radius_km:
                # Weight by distance (closer = more impact)
                weight = 1.0 / (1.0 + dist_km / 5.0)
                
                # Calculate crime density (crimes per 1000 people, approximated)
                # Using total crimes as proxy
                crime_density = data["total_crimes"] * weight
                
                # Add specific crime type weights
                crime_density += data["murders"] * 10 * weight  # Heavy weight for murders
                crime_density += data["sexual_harassment"] * 5 * weight
                crime_density += data["road_accidents"] * 2 * weight
                
                max_crime_density = max(max_crime_density, crime_density)
        
        # Normalize to 0-100 scale (inverse safety score)
        # Higher crime density = lower safety
        if max_crime_density == 0:
            return 0  # No crime data = safe
        
        # Normalize based on observed max values
        normalized_score = min(100, (max_crime_density / 50000) * 100)
        
        return normalized_score
    
    def get_crime_data_for_location(self, coord: Coordinate) -> Dict:
        """Get detailed crime data for a specific location."""
        nearest_district = None
        min_distance = float('inf')
        
        for district, data in self.crime_data.items():
            dist_coords = data["coordinates"]
            dist_km = geopy_distance(
                (coord.latitude, coord.longitude),
                dist_coords
            ).km
            
            if dist_km < min_distance:
                min_distance = dist_km
                nearest_district = district
        
        if nearest_district:
            return {
                "district": nearest_district,
                "distance_km": min_distance,
                **self.crime_data[nearest_district]
            }
        
        return {
            "district": "Unknown",
            "distance_km": 0,
            "total_crimes": 0,
            "murders": 0,
            "sexual_harassment": 0,
            "road_accidents": 0,
            "suicides": 0
        }
    
    def get_heatmap_data(self, bbox: Dict[str, float], resolution: int = 50) -> List[Dict]:
        """Generate crime heatmap data for a bounding box."""
        min_lat = bbox.get("min_lat", 10.0)
        max_lat = bbox.get("max_lat", 13.0)
        min_lon = bbox.get("min_lon", 76.0)
        max_lon = bbox.get("max_lon", 80.0)
        
        lat_step = (max_lat - min_lat) / resolution
        lon_step = (max_lon - min_lon) / resolution
        
        heatmap_points = []
        
        for i in range(resolution):
            for j in range(resolution):
                lat = min_lat + i * lat_step
                lon = min_lon + j * lon_step
                
                coord = Coordinate(latitude=lat, longitude=lon)
                crime_score = self.get_crime_score(coord)
                
                heatmap_points.append({
                    "coordinates": coord,
                    "crime_score": crime_score,
                    "density": int(crime_score / 10)  # Convert to density scale
                })
        
        return heatmap_points

