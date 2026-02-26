
import asyncio
from api.services.maps import MapsService

async def test_route():
    maps = MapsService()
    origin = (11.0168, 76.9558)  # RS Puram
    dest = (11.0400, 76.9930)    # Ukkadam
    
    print(f"Fetching route from {origin} to {dest}...")
    routes = maps.get_directions(origin, dest)
    
    if routes and 'route_coordinates' in routes[0]:
        coords = routes[0]['route_coordinates']
        print(f"Found {len(coords)} points!")
        print(f"First 5: {coords[:5]}")
        print(f"Provider: {routes[0].get('provider')}")
    else:
        print("No route found or no coordinates returned.")

if __name__ == "__main__":
    asyncio.run(test_route())
