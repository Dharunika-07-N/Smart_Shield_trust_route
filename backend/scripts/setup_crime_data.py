#!/usr/bin/env python3
"""
Helper script to download and prepare Tamil Nadu crime data.

This script helps you set up crime data for the Smart Shield Trust Route system.
You can either:
1. Download crime data from OpenCity.in
2. Place your own CSV files in the data/crime directory
3. Use the default mock data (for development/testing)

Usage:
    python scripts/setup_crime_data.py
"""

import os
import sys
import csv
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_data_directory():
    """Create the data/crime directory if it doesn't exist."""
    data_dir = Path(__file__).parent.parent / "data" / "crime"
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created data directory: {data_dir}")
    return data_dir

def create_sample_crime_data(data_dir):
    """Create a sample CSV file with Tamil Nadu crime data structure."""
    sample_file = data_dir / "tamil_nadu_crime_2022_sample.csv"
    
    # Sample data structure based on OpenCity.in dataset
    sample_data = [
        {
            "District": "Chennai",
            "Total Crimes": "45000",
            "Murders": "120",
            "Sexual Harassment": "850",
            "Road Accidents": "2100",
            "Suicides": "450"
        },
        {
            "District": "Coimbatore",
            "Total Crimes": "18000",
            "Murders": "45",
            "Sexual Harassment": "320",
            "Road Accidents": "850",
            "Suicides": "180"
        },
        {
            "District": "Madurai",
            "Total Crimes": "15000",
            "Murders": "38",
            "Sexual Harassment": "280",
            "Road Accidents": "720",
            "Suicides": "150"
        },
        {
            "District": "Tiruchirappalli",
            "Total Crimes": "12000",
            "Murders": "30",
            "Sexual Harassment": "220",
            "Road Accidents": "580",
            "Suicides": "120"
        },
        {
            "District": "Salem",
            "Total Crimes": "10000",
            "Murders": "25",
            "Sexual Harassment": "180",
            "Road Accidents": "490",
            "Suicides": "100"
        },
    ]
    
    if not sample_file.exists():
        with open(sample_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_data)
        print(f"✓ Created sample CSV file: {sample_file}")
        print(f"  You can edit this file or add more CSV files to include additional districts.")
    else:
        print(f"✓ Sample CSV file already exists: {sample_file}")

def print_instructions():
    """Print instructions for downloading real crime data."""
    print("\n" + "="*70)
    print("📊 TAMIL NADU CRIME DATA SETUP")
    print("="*70)
    print("\nThe system will use crime data from CSV files in the data/crime directory.")
    print("\nOption 1: Download from OpenCity.in")
    print("  → Visit: https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022")
    print("  → Download the CSV files:")
    print("    - District and City-wise Total Crimes Registered 2020 to 2022")
    print("    - District and City-wise Death Due to Crimes and Negligence")
    print("    - District and City-wise Sexual Harassment Cases")
    print("    - District and City-wise Deaths Due to Road Accidents")
    print("    - District and City-wise Suicides")
    print("  → Place the CSV files in: backend/data/crime/")
    print("\nOption 2: Use Sample Data (for development)")
    print("  → A sample CSV file has been created with basic data")
    print("  → Edit backend/data/crime/tamil_nadu_crime_2022_sample.csv to add more districts")
    print("\nOption 3: Use Default Mock Data")
    print("  → If no CSV files are found, the system will use built-in default data")
    print("  → This is fine for development and testing")
    print("\n" + "="*70)
    print("\n✅ Setup complete! The system is ready to use crime data.")
    print("\nNote: The crime data service will automatically:")
    print("  - Load CSV files from data/crime/ on startup")
    print("  - Parse district-wise crime statistics")
    print("  - Use the data for route safety scoring")
    print("\n")

def main():
    """Main setup function."""
    print("Setting up crime data directory...")
    data_dir = create_data_directory()
    create_sample_crime_data(data_dir)
    print_instructions()

if __name__ == "__main__":
    main()

