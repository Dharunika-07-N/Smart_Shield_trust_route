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
import functools

class CrimeDataService:
    """Service for accessing Tamil Nadu crime data."""
    
    # Tamil Nadu district coordinates (approximate centers)
    # Source: https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022
    DISTRICT_COORDS = {
        "Ariyalur": (11.1370, 79.0680),
        "Chennai": (13.0827, 80.2707),
        "Chengalpattu": (12.6841, 79.9836),
        "Coimbatore": (11.0168, 76.9558),
        "Coimbatore City": (11.0168, 76.9558),
        "Cuddalore": (11.7480, 79.7714),
        "Dharmapuri": (12.1273, 78.1582),
        "Dindigul": (10.3673, 77.9803),
        "Erode": (11.3410, 77.7172),
        "Kallakurichi": (11.7371, 78.9626),
        "Kanchipuram": (12.8342, 79.7036),
        "Kanyakumari": (8.0883, 77.5385),
        "Karur": (10.9504, 78.0844),
        "Krishnagiri": (12.5186, 78.2137),
        "Madurai": (9.9252, 78.1198),
        "Madurai City": (9.9252, 78.1198),
        "Nagapattinam": (10.7672, 79.8444),
        "Namakkal": (11.2189, 78.1672),
        "Nilgiris": (11.4102, 76.6991),
        "Perambalur": (11.2342, 78.8820),
        "Pudukkottai": (10.3792, 78.8202),
        "Ramanathapuram": (9.3639, 78.8395),
        "Ramnathapuram": (9.3639, 78.8395),
        "Ranipet": (12.9272, 79.3331),
        "Salem": (11.6643, 78.1460),
        "Salem City": (11.6643, 78.1460),
        "Sivagangai": (9.8433, 78.4809),
        "Tenkasi": (8.9591, 77.3117),
        "Thanjavur": (10.7870, 79.1378),
        "Theni": (10.0104, 77.4768),
        "Thirunelveli": (8.7139, 77.7567),
        "Thirunelveli City": (8.7139, 77.7567),
        "Tirunelveli": (8.7139, 77.7567),
        "Thiruvallur": (13.1231, 79.9120),
        "Thiruvannamalai": (12.2253, 79.0747),
        "Thiruvarur": (10.7672, 79.6425),
        "Thoothukudi": (8.7642, 78.1348),
        "Tiruppur": (11.1085, 77.3411),
        "Tiruppur City": (11.1085, 77.3411),
        "Tiruchirappalli": (10.7905, 78.7047),
        "Trichy": (10.7905, 78.7047),
        "Trichy City": (10.7905, 78.7047),
        "Vellore": (12.9165, 79.1325),
        "Villupuram": (11.9401, 79.4861),
        "Virudhunagar": (9.5850, 77.9515),
        "Tirupattur": (12.4939, 78.5678),
        "Tiruppattur": (12.4939, 78.5678),
        "Avadi": (13.1206, 80.1012),
        "Tambaram": (12.9239, 80.1336),
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
        """Parse a row of crime data with flexible column matching."""
        if district not in self.crime_data:
            self.crime_data[district] = {
                "total_crimes": 0,
                "murders": 0,
                "sexual_harassment": 0,
                "road_accidents": 0,
                "suicides": 0,
                "theft": 0,
                "coordinates": self.DISTRICT_COORDS.get(district, (11.0, 77.0))
            }
        
        # Helper to safely parse int from string with commas
        def get_val(val_str):
            try:
                if not val_str:
                    return 0
                clean_val = str(val_str).replace(',', '').strip()
                return int(float(clean_val))
            except (ValueError, TypeError):
                return 0

        # 1. Try explicit columns first (backward compatibility)
        if 'Total Crimes' in row:
            self.crime_data[district]["total_crimes"] += get_val(row.get('Total Crimes'))
        if 'Murders' in row:
            self.crime_data[district]["murders"] += get_val(row.get('Murders'))
        if 'Road Accidents' in row:
            self.crime_data[district]["road_accidents"] += get_val(row.get('Road Accidents'))
            
        # 2. Scan all columns for keywords (handling the detailed dataset provided)
        # We assume columns like "Assault on women...", "Sexual Harassment...", etc.
        for key, value in row.items():
            if not key or not value:
                continue
                
            key_lower = key.lower()
            val = get_val(value)
            
            if val == 0:
                continue

            # Sexual Harassment & Women Safety Indicators
            if any(k in key_lower for k in ['sexual', 'harassment', 'rape', 'modesty', 'dowry', 'women', 'assault']):
                self.crime_data[district]["sexual_harassment"] += val
                
            # Murders
            elif 'murder' in key_lower:
                self.crime_data[district]["murders"] += val
                
            # Accidents
            elif any(k in key_lower for k in ['accident', 'fatal', 'traffic death']):
                self.crime_data[district]["road_accidents"] += val
            
            # Suicides
            elif 'suicide' in key_lower:
                 self.crime_data[district]["suicides"] += val
            
            # Theft & Robbery & Burglary
            elif any(k in key_lower for k in ['theft', 'robbery', 'burglary', 'extortion', 'snatching']):
                self.crime_data[district]["theft"] += val
                self.crime_data[district]["total_crimes"] += val

        # Ensure total crimes is at least the sum of components
        calculated_total = (
            self.crime_data[district]["murders"] + 
            self.crime_data[district]["sexual_harassment"] + 
            self.crime_data[district]["road_accidents"] +
            self.crime_data[district]["suicides"] +
            self.crime_data[district]["theft"]
        )
        self.crime_data[district]["total_crimes"] = max(
            self.crime_data[district]["total_crimes"], 
            calculated_total
        )
    
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
                "theft": 5000,
                "coordinates": self.DISTRICT_COORDS["Chennai"]
            },
            "Coimbatore": {
                "total_crimes": 18000,
                "murders": 45,
                "sexual_harassment": 320,
                "road_accidents": 850,
                "suicides": 180,
                "theft": 500,
                "coordinates": self.DISTRICT_COORDS["Coimbatore"]
            },
            "Madurai": {
                "total_crimes": 15000,
                "murders": 38,
                "sexual_harassment": 280,
                "road_accidents": 720,
                "suicides": 150,
                 "theft": 400,
                "coordinates": self.DISTRICT_COORDS["Madurai"]
            },
            "Tiruchirappalli": {
                "total_crimes": 12000,
                "murders": 30,
                "sexual_harassment": 220,
                "road_accidents": 580,
                "suicides": 120,
                "theft": 300,
                "coordinates": self.DISTRICT_COORDS["Tiruchirappalli"]
            },
            "Salem": {
                "total_crimes": 10000,
                "murders": 25,
                "sexual_harassment": 180,
                "road_accidents": 490,
                "suicides": 100,
                "theft": 200,
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
                    "theft": 100,
                    "coordinates": coords
                }
        
        self.crime_data = default_data
    
    @functools.lru_cache(maxsize=1024)
    def _get_cached_crime_score(self, lat_rounded: float, lng_rounded: float, radius_km: float) -> float:
        """Internal cached version of crime score calculation."""
        coord = Coordinate(latitude=lat_rounded, longitude=lng_rounded)
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
                crime_density += data["sexual_harassment"] * 20 * weight # Critical for women safety
                crime_density += data["road_accidents"] * 2 * weight
                crime_density += data.get("theft", 0) * 1 * weight # Lower weight for theft
                
                max_crime_density = max(max_crime_density, crime_density)
        
        # Normalize to 0-100 scale (inverse safety score)
        if max_crime_density == 0:
            return 0.0
        
        normalized_score = min(100.0, (max_crime_density / 50000) * 100)
        return float(normalized_score)

    def get_crime_score(self, coord: Coordinate, radius_km: float = 10.0) -> float:
        """
        Get crime risk score (0-100) for a location.
        Uses caching with rounded coordinates (~1km precision).
        """
        # Round to 2 decimal places (~1.1km at equator) for effective caching
        lat_rounded = round(float(coord.latitude), 2)
        lng_rounded = round(float(coord.longitude), 2)
        
        return self._get_cached_crime_score(lat_rounded, lng_rounded, radius_km)
    
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
            "suicides": 0,
            "theft": 0
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

