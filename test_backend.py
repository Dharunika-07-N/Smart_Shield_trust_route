#!/usr/bin/env python3
"""Test script to verify backend connection"""
import requests
import json
import sys

def test_health():
    """Test the health endpoint"""
    print("Testing backend health endpoint...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"OK: Health check: Status {response.status_code}")
        print(f"  Response: {json.dumps(response.json(), indent=2)}")
        return True
    except requests.exceptions.ConnectionError:
        print("FAIL: Backend is not running on http://localhost:8000")
        print("  Start it with: cd backend && python -m uvicorn api.main:app --reload")
        return False
    except Exception as e:
        print(f"FAIL: Error: {e}")
        return False

def test_route_optimization():
    """Test the route optimization endpoint"""
    print("\nTesting route optimization endpoint...")
    test_data = {
        "starting_point": {"latitude": 10.9894, "longitude": 76.9598},
        "stops": [{
            "stop_id": "DEST_1",
            "address": "Test Destination",
            "coordinates": {"latitude": 10.9669, "longitude": 76.9543},
            "priority": "high"
        }],
        "optimize_for": ["time", "distance"]
    }
    
    try:
        response = requests.post(
            'http://localhost:8000/api/v1/delivery/optimize',
            json=test_data,
            timeout=30
        )
        print(f"OK: Route optimization: Status {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print(f"  Route ID: {result.get('data', {}).get('route_id', 'N/A')}")
                print(f"  Distance: {result.get('data', {}).get('total_distance_meters', 0) / 1000:.2f} km")
                print(f"  Duration: {result.get('data', {}).get('total_duration_seconds', 0) / 60:.1f} min")
            else:
                print(f"  Error: {result.get('message', 'Unknown error')}")
        else:
            print(f"  Error response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("FAIL: Cannot connect to backend")
        return False
    except Exception as e:
        print(f"FAIL: Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Backend Connection Test")
    print("=" * 60)
    
    health_ok = test_health()
    
    if health_ok:
        test_route_optimization()
    else:
        print("\n⚠ Backend must be running before testing route optimization")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
