import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"

def test_workflow():
    print("--- STARTING CORE FLOW VALIDATION ---")
    
    # 1. Health Check
    try:
        resp = requests.get(f"http://127.0.0.1:8000/") # Use root for health check
        print(f"Health Check: {resp.status_code} - {resp.json().get('message')}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    # 2. Login
    login_data = [
        {"username": "test_rider", "password": "password123", "role": "rider"},
        {"username": "admin@farmsecure.com", "password": "password123", "role": "admin"}
    ]
    
    token = None
    headers = None
    
    print("\nAttempting Login...")
    for creds in login_data:
        login_resp = requests.post(f"http://127.0.0.1:8000/api/v1/auth/login", json=creds)
        if login_resp.status_code == 200:
            token = login_resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print(f"Login Successful as {creds['username']}")
            break
    
    if not token:
        print("Login failed with known accounts. Attempting Registration...")
        timestamp = int(time.time())
        reg_data = {
            "username": f"test_user_{timestamp}",
            "password": "password123",
            "full_name": "Test User",
            "role": "rider",
            "email": f"test_{timestamp}@example.com"
        }
        reg_resp = requests.post(f"http://127.0.0.1:8000/api/v1/auth/register", json=reg_data)
        if reg_resp.status_code == 200:
            print(f"Registration Successful: {reg_data['username']}")
            login_creds = {"username": reg_data["username"], "password": "password123", "role": "rider"}
            login_resp = requests.post(f"http://127.0.0.1:8000/api/v1/auth/login", json=login_creds)
            token = login_resp.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            print("Login Successful")
        else:
            print(f"Registration failed: {reg_resp.text}")
            return

    token = login_resp.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    print("Login Successful")

    # 3. Route Optimization
    print("\nTesting Route Optimization...")
    route_data = {
        "starting_point": {"latitude": 11.0168, "longitude": 76.9558},
        "stops": [
            {
                "stop_id": "STOP001",
                "address": "Destination Point",
                "coordinates": {"latitude": 11.0200, "longitude": 76.9600},
                "priority": "medium"
            }
        ],
        "optimize_for": ["time", "safety"],
        "rider_info": {"gender": "female", "prefers_safe_routes": True}
    }
    route_resp = requests.post(f"http://127.0.0.1:8000/api/v1/delivery/optimize", json=route_data, headers=headers)
    if route_resp.status_code == 200:
        res_data = route_resp.json().get('data', {})
        route_id = res_data.get('route_id', 'N/A')
        alternatives = len(res_data.get('alternatives', []))
        print(f"Route Optimization: Route {route_id} found with {alternatives} alternatives")
    else:
        print(f"Route Optimization failed: {route_resp.status_code} - {route_resp.text}")

    # 4. SOS Panic Button
    print("\nTesting SOS Panic Button...")
    sos_data = {
        "rider_id": "current_user",
        "location": {"latitude": 11.0168, "longitude": 76.9558},
        "delivery_id": "test_delivery_123"
    }
    sos_resp = requests.post(f"http://127.0.0.1:8000/api/v1/safety/panic-button", json=sos_data, headers=headers)
    if sos_resp.status_code == 200:
        print(f"SOS Alert Sent: ID {sos_resp.json().get('alert_id')}")
    else:
        print(f"SOS Failed: {sos_resp.text}")

    # 5. AI Report (Mock Check)
    print("\nTesting AI Report (should use mock if key is missing)...")
    report_data = {
        "total_users": 100,
        "new_users": 10
    }
    report_resp = requests.post(f"http://127.0.0.1:8000/api/v1/ai/reports/user-summary", json=report_data, headers=headers)
    if report_resp.status_code == 200:
        content = report_resp.json().get("summary", "")
        is_mock = "[MOCK]" in content
        print(f"AI Report: {'MOCK' if is_mock else 'REAL'} content received")
    else:
        print(f"AI Report failed: {report_resp.text}")

    print("\n--- CORE FLOW VALIDATION COMPLETE ---")

if __name__ == "__main__":
    test_workflow()
