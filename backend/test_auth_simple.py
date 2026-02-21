import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_auth():
    print("Testing Auth...")
    login_data = {
        "username": "admin@smartshield.com",
        "password": "Admin@123",
        "role": "admin"
    }
    
    try:
        # Login
        resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"Login Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Login Failed: {resp.text}")
            return
            
        token = resp.json().get("access_token")
        print(f"Token obtained (starts with): {token[:20]}...")
        
        # Call admin endpoint
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/admin/riders-status", headers=headers)
        print(f"Riders Status: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Riders Fetch Failed: {resp.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_auth()
