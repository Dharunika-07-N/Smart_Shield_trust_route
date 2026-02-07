import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from database.database import Base, get_db
from database.models import (
    User, Route, SafetyFeedback, SafetyScore, DeliveryCompany, Rider, 
    DeliveryStatus, RouteMonitoring, PanicAlert, RiderCheckIn, SafeZone, 
    RideAlong, DeliveryRoute, RouteSegment, CrimeData, DeliveryFeedback, 
    HistoricalDelivery, CrowdsourcedAlert, RiderProfile, DriverProfile, 
    UserSession, Delivery, DeliveryBatch, DeliveryProof, Customer, BuddyPair
)

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    # Add some mock crime data for heatmap
    db = TestingSessionLocal()
    mock_crime = CrimeData(
        district="Chennai",
        murder_count=10,
        sexual_harassment_count=50,
        road_accident_count=100,
        crime_risk_score=65.5,
        location={"latitude": 13.0827, "longitude": 80.2707}
    )
    db.add(mock_crime)
    db.commit()
    yield
    # No drop_all here

def test_get_safety_heatmap():
    # Heatmap should work even without auth (public safety info)
    response = client.get(
        "/api/v1/safety/heatmap",
        params={
            "min_lat": 13.0,
            "min_lng": 80.0,
            "max_lat": 13.2,
            "max_lng": 80.3,
            "grid_size": 5
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "points" in data
    # Now that we fixed the endpoint, it should return points
    # (Actually CrimeDataService uses hardcoded TN districts if DB is empty or filters don't match, 
    # but we added a record in setup_db)
    assert len(data["points"]) > 0

def test_panic_button():
    # 1. Register and Login to get auth
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "panicuser",
            "password": "password",
            "role": "rider",
            "full_name": "Panic User",
            "phone": "1234567890",
            "email": "panic@example.com"
        },
    )
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "panicuser", "password": "password", "role": "rider"}
    )
    cookies = login_res.cookies
    
    # 2. Trigger panic button
    response = client.post(
        "/api/v1/safety/panic-button",
        json={
            "rider_id": "panicuser",
            "location": {"latitude": 13.0827, "longitude": 80.2707}
        },
        cookies=cookies
    )
    assert response.status_code == 200
    assert response.json()["status"] == "active"
