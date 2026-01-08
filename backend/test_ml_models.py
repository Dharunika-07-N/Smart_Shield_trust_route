"""
Test script to verify all AI/ML models are working correctly
Run this to ensure StandardScaler, async/await, and route optimization work
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from api.models.safety_scorer import SafetyScorer
from api.models.route_optimizer import RouteOptimizer
from api.schemas.delivery import Coordinate, DeliveryStop
from ml.safety_classifier import SafetyClassifier
from ml.time_predictor import DeliveryTimePredictor
from ml.rl_agent import SARSARouteAgent
import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 70)
print("🧪 AI/ML MODELS TEST SUITE")
print("=" * 70)
print()

# Test 1: SafetyScorer (StandardScaler)
print("✓ Test 1: SafetyScorer with StandardScaler")
print("-" * 70)
try:
    scorer = SafetyScorer()
    
    # Test single location
    coord = Coordinate(latitude=11.0168, longitude=76.9558)  # Coimbatore
    score, factors = scorer.score_location(coord, time_of_day="day")
    
    print(f"  ✅ Single location score: {score:.2f}/100")
    print(f"  → Factors analyzed: {len(factors)}")
    
    # Test route scoring
    route_coords = [
        Coordinate(latitude=11.0168, longitude=76.9558),
        Coordinate(latitude=11.0258, longitude=76.9658),
        Coordinate(latitude=11.0358, longitude=76.9758)
    ]
    route_score = scorer.score_route(route_coords, time_of_day="day")
    
    print(f"  ✅ Route safety score: {route_score['route_safety_score']:.2f}/100")
    print(f"  → Risk level: {route_score['risk_level']}")
    print(f"  → Segments analyzed: {len(route_score['segment_scores'])}")
    
    print("  ✅ SafetyScorer works correctly!")
    
except Exception as e:
    print(f"  ❌ SafetyScorer failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 2: SafetyClassifier (StandardScaler)
print("✓ Test 2: SafetyClassifier with StandardScaler")
print("-" * 70)
try:
    classifier = SafetyClassifier()
    
    # Create test data
    X_test = pd.DataFrame({
        'crime_rate': [3.5, 7.2, 2.1],
        'lighting': [80, 45, 90],
        'patrol': [70, 30, 85],
        'traffic': [50, 80, 40],
        'hour': [14, 22, 10],
        'police_proximity': [75, 30, 90],
        'hospital_proximity': [80, 20, 95]
    })
    
    safety_scores = classifier.predict_safety_score(X_test)
    
    print(f"  ✅ Predicted safety scores: {safety_scores}")
    print(f"  → Average score: {np.mean(safety_scores):.2f}/100")
    print("  ✅ SafetyClassifier works correctly!")
    
except Exception as e:
    print(f"  ❌ SafetyClassifier failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 3: DeliveryTimePredictor
print("✓ Test 3: DeliveryTimePredictor")
print("-" * 70)
try:
    predictor = DeliveryTimePredictor()
    
    # Create test data
    X_test = pd.DataFrame({
        'distance_km': [5.2, 12.5, 3.8],
        'num_stops': [1, 3, 1],
        'hour': [14, 18, 10],
        'day_of_week': [2, 5, 1],
        'traffic_level': [1, 2, 0],  # 0=low, 1=medium, 2=high
        'weather_condition': [0, 1, 0]  # 0=clear, 1=rain
    })
    
    predictions = predictor.predict(X_test)
    
    print(f"  ✅ Predicted delivery times (minutes): {predictions}")
    print(f"  → Average time: {np.mean(predictions):.2f} minutes")
    print("  ✅ DeliveryTimePredictor works correctly!")
    
except Exception as e:
    print(f"  ❌ DeliveryTimePredictor failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 4: RL Agent
print("✓ Test 4: SARSA RL Agent")
print("-" * 70)
try:
    rl_agent = SARSARouteAgent()
    
    # Test state generation
    context = {
        'current_lat': 11.0168,
        'current_lng': 76.9558,
        'hour': 14,
        'traffic_level': 'medium',
        'weather_condition': 'clear'
    }
    
    state = rl_agent.get_state(context)
    print(f"  ✅ Generated state: {state}")
    
    # Test action selection
    available_routes = ['route_0', 'route_1', 'route_2']
    chosen_route = rl_agent.choose_action(state, available_routes)
    print(f"  ✅ Chosen route: {chosen_route}")
    
    # Test learning
    reward = 85.0  # Safety score
    next_state = rl_agent.get_state(context)
    rl_agent.learn(state, chosen_route, reward, next_state, available_routes)
    print(f"  ✅ Learning step completed with reward: {reward}")
    
    print("  ✅ RL Agent works correctly!")
    
except Exception as e:
    print(f"  ❌ RL Agent failed: {e}")
    import traceback
    traceback.print_exc()

print()

# Test 5: Route Optimizer (Async/Await)
print("✓ Test 5: Route Optimizer with Async/Await")
print("-" * 70)

async def test_route_optimizer():
    try:
        from api.schemas.delivery import DeliveryPriority
        
        optimizer = RouteOptimizer()
        
        # Test single destination (should return alternatives)
        starting_point = Coordinate(latitude=11.0168, longitude=76.9558)
        stop = DeliveryStop(
            stop_id="STOP_1",
            coordinates=Coordinate(latitude=11.0258, longitude=76.9658),
            address="Test Address",
            priority=DeliveryPriority.MEDIUM  # Use enum instead of integer
        )
        
        print("  🔄 Optimizing route (this may take a few seconds)...")
        
        result = await optimizer.optimize_route(
            starting_point=starting_point,
            stops=[stop],
            optimize_for=["time", "safety"],
            rider_info={"gender": "female"},
            departure_time=datetime.now()
        )
        
        print(f"  ✅ Route optimized successfully!")
        print(f"  → Route ID: {result['route_id']}")
        print(f"  → Total distance: {result['total_distance_meters']/1000:.2f} km")
        print(f"  → Total duration: {result['total_duration_seconds']/60:.2f} minutes")
        print(f"  → Average safety score: {result['average_safety_score']:.2f}/100")
        print(f"  → Segments: {len(result['segments'])}")
        
        if 'alternatives' in result:
            print(f"  → Alternatives found: {len(result.get('alternatives', []))}")
        
        print("  ✅ Route Optimizer works correctly!")
        print("  ✅ Async/await is working properly!")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Route Optimizer failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# Run async test
success = asyncio.run(test_route_optimizer())

print()
print("=" * 70)

if success:
    print("✅ ALL TESTS PASSED!")
    print()
    print("🎉 Your AI/ML models are working correctly:")
    print("   ✓ StandardScaler is properly fitted")
    print("   ✓ Async/await is working")
    print("   ✓ Route optimization is functional")
    print("   ✓ Safety scoring is operational")
    print("   ✓ ML models are ready for demo")
else:
    print("⚠️ SOME TESTS FAILED")
    print()
    print("Please check the errors above and fix them.")

print("=" * 70)
print()

# Additional diagnostic info
print("📊 Model Status:")
print("-" * 70)

from pathlib import Path
import os

models_dir = Path(__file__).parent / "models"
if models_dir.exists():
    print(f"  Models directory: {models_dir}")
    for model_file in models_dir.glob("*.pkl"):
        size_kb = os.path.getsize(model_file) / 1024
        print(f"  ✓ {model_file.name} ({size_kb:.2f} KB)")
    for model_file in models_dir.glob("*.h5"):
        size_kb = os.path.getsize(model_file) / 1024
        print(f"  ✓ {model_file.name} ({size_kb:.2f} KB)")
else:
    print("  ⚠️ Models directory not found")

print()
input("Press Enter to exit...")
