import sys
sys.path.append('backend')

from api.services.maps import MapsService

ms = MapsService()
origin = (13.0827, 80.2707)
dest = (13.0400, 80.2400)

print("Calling get_directions...")
routes = ms.get_directions(origin, dest)
print(f"Routes returned: {len(routes)}")

if routes:
    r = routes[0]
    has_rc = "route_coordinates" in r
    rc = r.get("route_coordinates")
    has_op = "overview_polyline" in r
    op = r.get("overview_polyline", {})
    
    print(f"Has route_coordinates: {has_rc}")
    print(f"route_coordinates value (first 2): {rc[:2] if rc else None}")
    print(f"Has overview_polyline: {has_op}")
    print(f"overview_polyline points (first 20 chars): {str(op.get('points', ''))[:20]}")
    print(f"Summary: {r.get('summary')}")
    
    # Test polyline decode
    if op.get('points'):
        import polyline
        decoded = polyline.decode(op['points'])
        print(f"Polyline decoded: {len(decoded)} points, first: {decoded[0] if decoded else None}")
