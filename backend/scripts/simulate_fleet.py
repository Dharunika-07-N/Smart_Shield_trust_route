
import requests
import concurrent.futures

BASE_URL = "http://127.0.0.1:8000/api/v1"

SIM_DATA = [
    ("588e44c1-712f-4431-918e-b022c2a703c0", "panic_rider"),
    ("2b12a759-be82-458e-8538-ebd401c6c991", "r1"),
    ("d8dda299-22d7-495b-9b1f-9c3e91d20732", "r2"),
    ("a4edcb0f-9565-4757-9534-ea9bb0f9226f", "checker"),
    ("0ace53bf-174d-4878-845b-2e6ccb267214", "test@example.com"),
    ("959ab931-1375-48c2-9e90-83ed6af64bc5", "dharunikaktm@gmail.com"),
    ("7573762b-609b-4259-a985-9cba34c5ecd7", "rider@smartshield.com"),
    ("d973853a-3e7a-4060-97c0-b4d54a680abb", "rajesh@fleet.com"),
    ("fc1ee680-c440-4df4-886c-f2d925503881", "ananya@fleet.com"),
    ("be1fba9f-7e15-420b-bfd2-ccb57d7dc9de", "vikram@fleet.com")
]

def trigger_sim(d_id, username):
    try:
        # Login
        login_resp = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": "Rider@123", "role": "rider"}, timeout=10)
        if login_resp.status_code != 200:
            return f"Login failed for {username} (Status: {login_resp.status_code}): {login_resp.text}"
        
        token = login_resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        
        # Trigger simulation
        sim_resp = requests.post(f"{BASE_URL}/tracking/simulate/{d_id}", headers=headers, timeout=10)
        if sim_resp.status_code == 200:
            return f"Success for {username}"
        else:
            return f"Sim failed for {username}: {sim_resp.text}"
    except Exception as e:
        return f"Error for {username}: {str(e)}"

def main():
    import time
    print(f"Triggering simulation for {len(SIM_DATA)} riders...")
    success_count = 0
    for d_id, username in SIM_DATA:
        res = trigger_sim(d_id, username)
        print(res)
        if "Success" in res:
            success_count += 1
        time.sleep(2)
    print(f"Summary: {success_count}/{len(SIM_DATA)} simulations started.")

if __name__ == "__main__":
    main()
