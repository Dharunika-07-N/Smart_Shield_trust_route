import pytest
from fastapi.testclient import TestClient
from api.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_optimize_route_simple(client):
    response = client.post(
        "/api/v1/optimize-route",
        json={
            "origin": {"lat": 13.0, "lng": 80.0},
            "destination": {"lat": 13.1, "lng": 80.1}
        }
    )
    assert response.status_code in [200, 400] 

def test_dashboard_stats(client):
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "active_deliveries" in response.json()["data"]

def test_delivery_queue(client):
    response = client.get("/api/v1/dashboard/deliveries/queue")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["data"]) > 0

def test_zone_safety(client):
    response = client.get("/api/v1/dashboard/zones/safety")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_weather_endpoint(client):
    response = client.get("/api/v1/dashboard/weather?lat=13.0&lon=80.0")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_safety_heatmap(client):
    response = client.get(
        "/api/v1/safety/heatmap",
        params={
            "min_lat": 12.9,
            "min_lng": 79.9,
            "max_lat": 13.1,
            "max_lng": 80.1,
            "grid_size": 2
        }
    )
    assert response.status_code == 200
    assert "points" in response.json()
