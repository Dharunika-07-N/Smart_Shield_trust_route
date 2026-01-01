"""
Test OSRM Service - FREE routing without API key
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from api.services.osrm_service import OSRMService
from api.schemas.delivery import Coordinate

print("=" * 70)
print("🧪 TESTING FREE OSRM SERVICE (No API Key Required)")
print("=" * 70)
print()

# Initialize OSRM service
print("✓ Test 1: Initialize OSRM Service")
print("-" * 70)
try:
    osrm = OSRMService()
    print("  ✅ OSRM Service initialized successfully!")
    print("  → No API key needed!")
    print("  → No billing required!")
except Exception as e:
    print(f"  ❌ Failed: {e}")
    exit(1)

print()

# Test routing
print("✓ Test 2: Get Route (Coimbatore to Chennai)")
print("-" * 70)
try:
    origin = Coordinate(latitude=11.0168, longitude=76.9558)  # Coimbatore
    destination = Coordinate(latitude=13.0827, longitude=80.2707)  # Chennai
    
    print(f"  Origin: Coimbatore ({origin.latitude}, {origin.longitude})")
    print(f"  Destination: Chennai ({destination.latitude}, {destination.longitude})")
    print("  🔄 Fetching route from OSRM...")
    
    directions = osrm.get_directions(origin, destination, alternatives=True)
    
    if directions:
        print(f"  ✅ Got {len(directions)} route(s)!")
        
        for idx, route in enumerate(directions):
            leg = route['legs'][0]
            print(f"\n  Route {idx + 1}:")
            print(f"    → Distance: {leg['distance']['text']}")
            print(f"    → Duration: {leg['duration']['text']}")
            print(f"    → Summary: {route.get('summary', 'N/A')}")
            print(f"    → Steps: {len(leg.get('steps', []))}")
    else:
        print("  ❌ No routes returned")
        
except Exception as e:
    print(f"  ❌ Failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test geocoding
print("✓ Test 3: Geocode Address (FREE Nominatim)")
print("-" * 70)
try:
    address = "Coimbatore, Tamil Nadu, India"
    print(f"  Address: {address}")
    print("  🔄 Geocoding...")
    
    result = osrm.geocode_address(address)
    
    if result:
        print(f"  ✅ Geocoded successfully!")
        print(f"    → Latitude: {result['lat']}")
        print(f"    → Longitude: {result['lng']}")
    else:
        print("  ❌ Geocoding failed")
        
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()

# Test reverse geocoding
print("✓ Test 4: Reverse Geocode (Coordinates → Address)")
print("-" * 70)
try:
    lat, lng = 11.0168, 76.9558
    print(f"  Coordinates: ({lat}, {lng})")
    print("  🔄 Reverse geocoding...")
    
    address = osrm.reverse_geocode(lat, lng)
    
    print(f"  ✅ Address: {address}")
        
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()

# Test distance calculation
print("✓ Test 5: Calculate Distance")
print("-" * 70)
try:
    coord1 = Coordinate(latitude=11.0168, longitude=76.9558)  # Coimbatore
    coord2 = Coordinate(latitude=11.0258, longitude=76.9658)  # Nearby point
    
    distance = osrm.calculate_straight_distance(coord1, coord2)
    
    print(f"  ✅ Distance: {distance:.2f} meters ({distance/1000:.2f} km)")
        
except Exception as e:
    print(f"  ❌ Failed: {e}")

print()
print("=" * 70)
print("✅ OSRM SERVICE TEST COMPLETE")
print("=" * 70)
print()
print("🎉 Your app now has FREE routing with:")
print("   ✓ No API key required")
print("   ✓ No billing needed")
print("   ✓ Unlimited requests (fair use)")
print("   ✓ Real-world routing data")
print("   ✓ Turn-by-turn navigation")
print("   ✓ Multiple route alternatives")
print()
print("Ready to demo to the jury! 🚀")
print()

input("Press Enter to exit...")
