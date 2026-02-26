
import requests
BASE_URL = "http://127.0.0.1:8000/api/v1"
emails = ["baileyjustin@example.net", "rider@smartshield.com"]
passwords = ["password123", "Rider@123"]

for e in emails:
    for p in passwords:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"username": e, "password": p})
        print(f"Email: {e}, Password: {p}, Status: {resp.status_code}")
