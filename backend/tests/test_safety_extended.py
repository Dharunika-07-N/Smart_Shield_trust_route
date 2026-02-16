import pytest
from fastapi.testclient import TestClient
from api.main import app
from database.models import User, RiderProfile
from database.database import SessionLocal, Base, engine

@pytest.fixture
def client():
    # Setup tables
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

def test_panic_button_flow(client):
    # 1. Register a rider
    client.post("/api/v1/auth/register", json={
        "username": "panic_rider", "password": "password", "role": "rider",
        "full_name": "Panic Rider", "phone": "123", "email": "p@p.com"
    })
    login = client.post("/api/v1/auth/login", json={"username": "panic_rider", "password": "password", "role": "rider"})
    user_id = login.json()["user_id"]
    
    # 2. Trigger panic button
    response = client.post(
        "/api/v1/safety/panic-button",
        json={
            "rider_id": user_id,
            "location": {"latitude": 13.0, "longitude": 80.0}
        },
        cookies=login.cookies
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_safe_zones(client):
    response = client.post(
        "/api/v1/safety/safe-zones",
        json={
            "location": {"latitude": 13.0, "longitude": 80.0},
            "radius_meters": 5000
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_ride_along(client):
    # Need a rider
    client.post("/api/v1/auth/register", json={"username": "r1", "password": "p", "role": "rider"})
    
    l1 = client.post("/api/v1/auth/login", json={"username": "r1", "password": "p", "role": "rider"})
    u1 = l1.json()["user_id"]
    
    response = client.post(
        "/api/v1/safety/ride-along",
        json={
            "rider_id": u1,
            "tracker_name": "Companion",
            "route_id": "ROUTE1"
        },
        cookies=l1.cookies
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_check_in(client):
    client.post("/api/v1/auth/register", json={"username": "checker", "password": "p", "role": "rider"})
    login = client.post("/api/v1/auth/login", json={"username": "checker", "password": "p", "role": "rider"})
    u_id = login.json()["user_id"]
    
    response = client.post(
        "/api/v1/safety/check-in",
        json={
            "rider_id": u_id,
            "location": {"latitude": 13.0, "longitude": 80.0},
            "status": "safe"
        },
        cookies=login.cookies
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
