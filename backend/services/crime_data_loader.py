import pandas as pd
import os
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.models import CrimeData

class CrimeDataLoader:
    def __init__(self, db: Session):
        self.db = db
        self.crime_data_path = os.path.join(Path(__file__).parent.parent, "data", "crime")
    
    def load_tamil_nadu_crime_data(self):
        """
        Load Tamil Nadu 2022 crime data from CSV files
        Data source: https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022
        """
        
        # District coordinates for Tamil Nadu (38 districts)
        district_coords = {
            "Chennai": (13.0827, 80.2707),
            "Coimbatore": (11.0168, 76.9558),
            "Madurai": (9.9252, 78.1198),
            "Tiruchirappalli": (10.7905, 78.7047),
            "Salem": (11.6643, 78.1460),
            "Tirunelveli": (8.7139, 77.7567),
            "Erode": (11.3410, 77.7172),
            "Vellore": (12.9165, 79.1325),
            "Tiruppur": (11.1085, 77.3411),
            "Tuticorin": (8.8049, 78.1464),
            "Thanjavur": (10.7850, 79.1391),
            "Dindigul": (10.3673, 77.9803),
            "Ranipet": (12.9272, 79.3330),
            "Virudhunagar": (9.5872, 77.9515),
            "Sivaganga": (9.8433, 78.4809),
            "Theni": (10.0104, 77.4768),
            "Tenkasi": (8.9591, 77.3146),
            "Kancheepuram": (12.8342, 79.7036),
            "Chengalpattu": (12.6939, 79.9754),
            "Tiruvallur": (13.1394, 79.9079),
            "Cuddalore": (11.7480, 79.7714),
            "Villupuram": (11.9401, 79.4861),
            "Kallakurichi": (11.7384, 78.9639),
            "Tiruvannamalai": (12.2253, 79.0747),
            "Dharmapuri": (12.1270, 78.1582),
            "Krishnagiri": (12.5186, 78.2137),
            "Namakkal": (11.2189, 78.1672),
            "Nilgiris": (11.4102, 76.6950),
            "Karur": (10.9601, 78.0766),
            "Perambalur": (11.2342, 78.8820),
            "Ariyalur": (11.1401, 79.0747),
            "Nagapattinam": (10.7672, 79.8444),
            "Mayiladuthurai": (11.1017, 79.6521),
            "Tiruvarur": (10.7725, 79.6361),
            "Pudukkottai": (10.3797, 78.8202),
            "Ramanathapuram": (9.3639, 78.8395),
            "Kanniyakumari": (8.0883, 77.5385),
        }
        
        crime_files = [
            "murders_2022.csv",
            "sexual_harassment_2022.csv",
            "road_accidents_2022.csv",
            "thefts_2022.csv"
        ]
        
        crime_data_dict = {}
        
        # Check if directory exists
        if not os.path.exists(self.crime_data_path):
            os.makedirs(self.crime_data_path, exist_ok=True)
            print(f"📁 Created directory: {self.crime_data_path}")
        
        for file in crime_files:
            file_path = os.path.join(self.crime_data_path, file)
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    crime_type = file.split('_')[0]
                    
                    for district in df['District'].unique():
                        if district not in crime_data_dict:
                            crime_data_dict[district] = {}
                        
                        crime_count = df[df['District'] == district]['Count'].sum()
                        crime_data_dict[district][crime_type] = crime_count
                except Exception as e:
                    print(f"❌ Error reading {file}: {e}")
            else:
                print(f"⚠️ Crime data file not found: {file_path}")
        
        if not crime_data_dict:
            print("⚠️ No crime data found to load. Please place CSV files in backend/data/crime/")
            return
            
        # Insert into database
        loaded_count = 0
        for district, crime_stats in crime_data_dict.items():
            if district in district_coords:
                lat, lng = district_coords[district]
                
                # Calculate risk score (0-100)
                risk_score = self._calculate_risk_score(crime_stats)
                
                crime_entry = CrimeData(
                    district=district,
                    location={"latitude": lat, "longitude": lng},
                    murder_count=crime_stats.get('murders', 0),
                    sexual_harassment_count=crime_stats.get('sexual', 0),
                    road_accident_count=crime_stats.get('road', 0),
                    theft_count=crime_stats.get('thefts', 0),
                    crime_risk_score=risk_score,
                    year=2022
                )
                
                self.db.add(crime_entry)
                loaded_count += 1
        
        self.db.commit()
        print(f"✅ Loaded crime data for {loaded_count} districts")
    
    def _calculate_risk_score(self, crime_stats):
        """Calculate composite risk score from crime statistics"""
        weights = {
            'murders': 0.35,
            'sexual': 0.30,
            'road': 0.20,
            'thefts': 0.15
        }
        
        # Normalize to 0-100 scale (using max values)
        max_values = {
            'murders': 50,
            'sexual': 100,
            'road': 500,
            'thefts': 200
        }
        
        risk_score = 0
        for crime_type, count_key in [('murders', 'murders'), ('sexual', 'sexual'), ('road', 'road'), ('thefts', 'thefts')]:
            count = crime_stats.get(crime_type, 0)
            normalized = min(count / max_values[crime_type], 1.0)
            risk_score += normalized * weights[crime_type] * 100
        
        return risk_score
