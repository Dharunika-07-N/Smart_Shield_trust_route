import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def test_full_flow():
    # 1. Login as Admin
    print("Step 1: Login users")
    admin_login = {"username": "admin@smartshield.com", "password": "Admin@123", "role": "admin"}
    admin_resp = requests.post(f"{BASE_URL}/auth/login", json=admin_login).json()
    admin_headers = {"Authorization": f"Bearer {admin_resp['access_token']}"}
    print("✅ Admin logged in")

    dispatcher_login = {"username": "dispatcher@smartshield.com", "password": "Dispatch@123", "role": "dispatcher"}
    dispatcher_resp = requests.post(f"{BASE_URL}/auth/login", json=dispatcher_login).json()
    dispatcher_headers = {"Authorization": f"Bearer {dispatcher_resp['access_token']}"}
    print("✅ Dispatcher logged in")

    rider_login = {"username": "rider@smartshield.com", "password": "Rider@123", "role": "rider"}
    rider_resp = requests.post(f"{BASE_URL}/auth/login", json=rider_login).json()
    rider_headers = {"Authorization": f"Bearer {rider_resp['access_token']}"}
    rider_id = rider_resp['user_id']
    print(f"✅ Rider logged in (ID: {rider_id})")

    # 2. Create Delivery
    print("\nStep 2: Admin creates delivery order")
    delivery_data = {
        "order_id": f"ORD-{int(time.time())}",
        "customer_id": "CUST-001",
        "pickup_location": {"latitude": 11.0168, "longitude": 76.9558, "address": "RS Puram, Coimbatore"},
        "dropoff_location": {"latitude": 11.0183, "longitude": 76.9740, "address": "Gandhipuram, Coimbatore"}
    }
    resp = requests.post(f"{BASE_URL}/deliveries/", json=delivery_data, headers=admin_headers)
    if resp.status_code != 200:
        print(f"FAILED Delivery creation: {resp.text}")
        return
    delivery_id = resp.json()["id"]
    print(f"✅ Delivery created: {delivery_id}")

    # 3. Manually Assign to Rider
    print("\nStep 3: Dispatcher manually assigns to rider")
    assign_data = {"rider_id": rider_id}
    resp = requests.patch(f"{BASE_URL}/deliveries/{delivery_id}/assign", json=assign_data, headers=dispatcher_headers)
    if resp.status_code != 200:
        print(f"FAILED Assignment: {resp.text}")
        return
    print(f"✅ Assigned successfully: {resp.json()}")

    # 4. Driver Flow
    print("\nStep 4: Driver Flow (Pick up -> In Transit -> Delivered)")
    statuses = ["picked_up", "in_transit"]
    for status in statuses:
        print(f"Updating status to: {status}")
        resp = requests.put(f"{BASE_URL}/deliveries/{delivery_id}/status", 
                          json={"status": status}, headers=rider_headers)
        if resp.status_code != 200:
             print(f"FAILED Status update to {status}: {resp.text}")
             return
        time.sleep(1)

    # 5. Live Tracking Update
    print("\nStep 5: Live tracking update")
    loc_update = {
        "delivery_id": delivery_id,
        "latitude": 11.0175,
        "longitude": 76.9600,
        "status": "in_transit"
    }
    resp = requests.post(f"{BASE_URL}/tracking/location", json=loc_update, headers=rider_headers)
    if resp.status_code != 200:
        print(f"FAILED Location update: {resp.text}")
    else:
        print(f"✅ Location update response: {resp.status_code}")

    # 6. Final Delivery
    print("\nStep 6: Mark as Delivered")
    resp = requests.put(f"{BASE_URL}/deliveries/{delivery_id}/status", 
                      json={"status": "delivered"}, headers=rider_headers)
    if resp.status_code != 200:
        print(f"FAILED Final status update: {resp.text}")
    else:
        print(f"✅ Final status update response: {resp.status_code}")

    # 7. Check Admin Stats
    print("\nStep 7: Verify Admin Stats")
    resp = requests.get(f"{BASE_URL}/admin/summary", headers=admin_headers)
    if resp.status_code != 200:
        print(f"FAILED Admin summary: {resp.text}")
    else:
        print(f"✅ Admin summary: {json.dumps(resp.json(), indent=2)}")

if __name__ == "__main__":
    test_full_flow()
