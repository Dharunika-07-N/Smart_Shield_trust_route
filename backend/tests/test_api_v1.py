import pytest
from api.schemas.delivery import Coordinate

def test_delivery_flow(client):
    # Register and login as dispatcher to create deliveries
    client.post("/api/v1/auth/register", json={
        "username": "distest", "password": "password", "role": "dispatcher",
        "full_name": "Dis Test", "phone": "123", "email": "d@d.com",
        "admin_code": "SECRET_TEST"
    })
    login = client.post("/api/v1/auth/login", json={"username": "distest", "password": "password", "role": "dispatcher"})

    # 1. Create a delivery (endpoint is /api/v1/deliveries/)
    response = client.post(
        "/api/v1/deliveries/",
        json={
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "pickup_location": {"latitude": 13.0, "longitude": 80.0},
            "dropoff_location": {"latitude": 13.1, "longitude": 80.1}
        },
        cookies=login.cookies
    )
    assert response.status_code == 200
    delivery_id = response.json()["id"]
    
    # 2. Get deliveries list
    response = client.get("/api/v1/deliveries/", cookies=login.cookies)
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_tracking_update(client):
    # Create delivery first
    client.post("/api/v1/auth/register", json={
        "username": "tracktest", "password": "password", "role": "dispatcher",
        "full_name": "Track Test", "phone": "123", "email": "t@t.com",
        "admin_code": "SECRET_TEST"
    })
    login = client.post("/api/v1/auth/login", json={"username": "tracktest", "password": "password", "role": "dispatcher"})
    
    res = client.post("/api/v1/deliveries/", json={
        "order_id": "ORD002",
        "customer_id": "CUST002",
        "pickup_location": {"latitude": 13.0, "longitude": 80.0},
        "dropoff_location": {"latitude": 13.1, "longitude": 80.1}
    }, cookies=login.cookies)
    delivery_id = res.json()["id"]
    
    # Update location (endpoint is /api/v1/tracking/location)
    response = client.post(
        "/api/v1/tracking/location",
        json={
            "delivery_id": delivery_id,
            "latitude": 13.05,
            "longitude": 80.05,
            "status": "in_transit"
        },
        cookies=login.cookies
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_traffic_info(client):
    response = client.get(
        "/api/v1/traffic/status"
    )
    assert response.status_code == 200
    assert "status" in response.json()

def test_user_profile(client):
    # Register/Login
    client.post("/api/v1/auth/register", json={
        "username": "profileuser", "password": "password", "role": "rider",
        "full_name": "Profile User", "phone": "123", "email": "p@p.com"
    })
    login = client.post("/api/v1/auth/login", json={
        "username": "profileuser", "password": "password", "role": "rider"
    })
    
    response = client.get("/api/v1/users/profile", cookies=login.cookies)
    assert response.status_code == 200
    assert response.json()["username"] == "profileuser"

def test_feedback_submission(client):
    # Login
    client.post("/api/v1/auth/register", json={
        "username": "fuser", "password": "password", "role": "rider",
        "full_name": "F User", "phone": "123", "email": "f@f.com"
    })
    login = client.post("/api/v1/auth/login", json={"username": "fuser", "password": "password", "role": "rider"})
    
    response = client.post(
        "/api/v1/feedback/submit",
        json={
            "route_id": "R123",
            "rider_id": "fuser",
            "safety_rating": 5,
            "route_quality_rating": 4,
            "comfort_rating": 4,
            "incidents_reported": [],
            "unsafe_areas": [],
            "feedback_text": "Very safe route"
        },
        cookies=login.cookies
    )
    assert response.status_code == 200
