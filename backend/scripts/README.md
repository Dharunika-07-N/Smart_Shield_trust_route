# Setup Scripts

Helper scripts for setting up the Smart Shield Trust Route system.

## setup_crime_data.py

Sets up the crime data directory and creates a sample CSV file.

**Usage:**
```bash
cd backend
python scripts/setup_crime_data.py
```

This script will:
- Create the `data/crime/` directory
- Generate a sample CSV file with Tamil Nadu crime data structure
- Provide instructions for downloading real data from OpenCity.in

## Data Sources

### Tamil Nadu Crime Data 2022
- **Source**: https://www.data.opencity.in/dataset/tamil-nadu-crime-data-2022
- **License**: Public Domain
- **Format**: CSV files

### Download Instructions
1. Visit the OpenCity.in dataset page
2. Download the following CSV files:
   - District and City-wise Total Crimes Registered 2020 to 2022
   - District and City-wise Death Due to Crimes and Negligence
   - District and City-wise Sexual Harassment Cases
   - District and City-wise Deaths Due to Road Accidents
   - District and City-wise Suicides
3. Place all CSV files in `backend/data/crime/`

### CSV Format
The system expects CSV files with the following columns (case-insensitive):
- `District` - District name
- `Total Crimes` - Total number of crimes
- `Murders` - Number of murders
- `Sexual Harassment` - Number of sexual harassment cases
- `Road Accidents` - Number of road accidents
- `Suicides` - Number of suicides

If your CSV files have different column names, you may need to adjust the parsing in `backend/api/services/crime_data.py`.

