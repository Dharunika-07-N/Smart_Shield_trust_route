
import httpx
import json
import asyncio
import sys
from pathlib import Path

async def test_full_optimization():
    url = "http://localhost:8000/api/v1/delivery/optimize"
    
    payload = {
        "starting_point": {"latitude": 11.0168, "longitude": 76.9558},
        "stops": [
            {
                "stop_id": "STOP_1",
                "address": "Saravanampatti",
                "coordinates": {"latitude": 11.0850, "longitude": 77.0100},
                "priority": "high"
            }
        ],
        "optimize_for": ["safety", "time"],
        "vehicle_type": "motorcycle",
        "rider_info": {"gender": "female", "experience_years": 2}
    }
    
    # Try multiple times in case server is starting
    for i in range(5):
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"Attempt {i+1}: Sending optimization request...")
                response = await client.post(url, json=payload)
                
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print("Optimization Success!")
                    print(f"Route ID: {data['data']['route_id']}")
                    print(f"Average Safety Score: {data['data'].get('average_safety_score')}")
                    print(f"Total Distance: {data['data']['total_distance_meters']}m")
                    print(f"Provider used: {data['data']['segments'][0].get('provider', 'unknown')}")
                    
                    # Print segment safety score
                    if data['data']['segments']:
                        print(f"Segment Safety Score: {data['data']['segments'][0].get('safety_score')}")
                        
                    return
                else:
                    print(f"Error: {response.text}")
        except Exception as e:
            print(f"Connection failed: {e}")
            await asyncio.sleep(2)
    
    print("Full optimization test FAILED - Is the server running?")

if __name__ == "__main__":
    asyncio.run(test_full_optimization())
