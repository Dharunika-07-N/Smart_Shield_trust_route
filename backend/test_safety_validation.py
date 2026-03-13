"""Test script to identify validation errors in safety scorer output."""
import sys
sys.path.insert(0, '.')

import numpy as np
from api.models.safety_scorer import SafetyScorer
from api.schemas.delivery import Coordinate
from api.schemas.safety import SafetyScoreResponse, LocationSafetyScore, SafetyFactor

scorer = SafetyScorer()
coords = [
    Coordinate(latitude=11.0168, longitude=76.9558),
    Coordinate(latitude=11.0200, longitude=76.9600),
    # Test night conditions
    Coordinate(latitude=10.7905, longitude=78.7047),  # High crime area
]

result = scorer.score_route(coords, time_of_day='night', rider_info={'gender': 'female'})
seg_scores = result.get('segment_scores', [])

print("=== Checking Factor Validation ===")
errors_found = []
for i, seg in enumerate(seg_scores):
    print(f"\nSegment {i}: overall_score={float(seg['overall_score']):.2f}, risk_level={seg['risk_level']}")
    for f in seg['factors']:
        score_val = float(f['score'])
        weight_val = float(f['weight'])
        score_ok = 0 <= score_val <= 100
        weight_ok = 0 <= weight_val <= 1
        status = "OK" if (score_ok and weight_ok) else "INVALID"
        if not score_ok or not weight_ok:
            errors_found.append(f"  Segment {i}, factor={f['factor']}: score={score_val} (ok={score_ok}), weight={weight_val} (ok={weight_ok})")
        print(f"  [{status}] factor={f['factor']} score={score_val:.2f} weight={weight_val:.2f}")

if errors_found:
    print("\n=== ERRORS FOUND ===")
    for err in errors_found:
        print(err)
else:
    print("\n=== All factors valid ===")

# Now test full Pydantic serialization
print("\n=== Testing Pydantic SafetyScoreResponse ===")
try:
    resp = SafetyScoreResponse(
        route_safety_score=result.get('route_safety_score', 0),
        average_score=result.get('average_score', 0),
        segment_scores=seg_scores,
        improvement_suggestions=result.get('improvement_suggestions', [])
    )
    print("SUCCESS: SafetyScoreResponse created OK")
    print(f"Route safety score: {resp.route_safety_score:.2f}")
except Exception as e:
    print(f"FAIL: {e}")
    import traceback
    traceback.print_exc()
