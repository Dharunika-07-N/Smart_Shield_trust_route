# Smart Shield - Real-World Data Sources

This directory contains instructions and scripts to use the professional datasets provided for route optimization.

## 📦 Recommended Datasets

### 1. Delivery & Logistics (High Priority)
*   **Wolt Delivery Dataset** ([Kaggle](https://www.kaggle.com/datasets/muhammadwajeeharif/wolt-delivery-dataset)): Excellent for multi-stop food delivery logistics.
*   **FedEx Logistics Data** ([Kaggle](https://www.kaggle.com/datasets/vasudevmaduri/fedexdata)): Best for long-range and supply chain optimization.
*   **Amazon Last Mile** ([Kaggle](https://www.kaggle.com/datasets/pingpang/lastmiledeliverytimes)): Specifically for high-density urban deliveries.

### 2. GPS Trajectories (Heuristic Accuracy)
*   **NYC Taxi (TLC) Data** ([Official](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)): 697M+ trips. The "Gold Standard" for city traffic and travel time modeling.
*   **Microsoft GeoLife** ([Microsoft](https://www.microsoft.com/en-us/download/details.aspx?id=52367)): High-resolution GPS points (every 1-5s). Perfect for fine-tuning the **A* Algorithm**'s turn penalties.

---

## 🚀 How to Ingest Data

We have provided mappers to convert these formats into the Smart Shield format.

### Using the NYC Taxi Mapper
1. Download a "Yellow Taxi Trip Record" (CSV/Parquet) from the [TLC Website](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page).
2. Place it in `backend/data/raw/`.
3. Run the mapper:
```bash
python backend/ml/ingestion/nyc_taxi_mapper.py
```

### Map Requirements
To work with our **A* Heuristic**, your data should ideally contain:
*   `Origin Latitude/Longitude`
*   `Destination Latitude/Longitude`
*   `Total Time (minutes)`
*   `Total Distance (km)`

---

## 🛠️ Data Mapping Tool (`backend/ml/ingestion/`)
| Source | Script | Status |
| :--- | :--- | :--- |
| NYC Taxi | `nyc_taxi_mapper.py` | ✅ Ready |
| Wolt / Food App | `wolt_mapper.py` | 📝 In Progress |
| GeoLife | `geolife_mapper.py` | 📝 Planned |

Use these scripts to fill `backend/data/ml_training/historical_deliveries.csv`.
