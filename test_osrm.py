import asyncio
import httpx
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_osrm():
    orig = (10.9965, 76.9631)
    dest = (10.9987, 76.9591)
    
    # Build coordinates string: lng,lat;lng,lat
    coords = f"{orig[1]},{orig[0]};{dest[1]},{dest[0]}"
    
    url = f"https://router.project-osrm.org/route/v1/driving/{coords}"
    params = {
        'overview': 'full',
        'geometries': 'polyline',
        'steps': 'true',
        'alternatives': 'true'
    }
    
    print(f"Testing OSRM for Coimbatore points: {orig} to {dest}")
    print(f"URL: {url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            print(f"Status: {response.status_code}")
            data = response.json()
            print(f"Response Code: {data.get('code')}")
            if data.get('code') == 'Ok':
                print(f"Routes found: {len(data.get('routes', []))}")
            else:
                print(f"Error Message: {data.get('message')}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_osrm())
