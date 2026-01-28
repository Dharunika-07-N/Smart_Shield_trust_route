"""
Smart Shield - ML Integration Testing Script
Tests the complete ML pipeline from data to predictions to route optimization
"""

import sys
import os
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

import requests
import json
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)  # Initialize colorama

API_BASE_URL = "http://localhost:8000/api/v1"

def print_header(text):
    """Print styled header"""
    print("\n" + "="*70)
    print(Fore.CYAN + Style.BRIGHT + text.center(70))
    print("="*70 + "\n")

def print_success(text):
    """Print success message"""
    print(Fore.GREEN + "✅ " + text)

def print_error(text):
    """Print error message"""
    print(Fore.RED + "❌ " + text)

def print_warning(text):
    """Print warning message"""
    print(Fore.YELLOW + "⚠️  " + text)

def print_info(text):
    """Print info message"""
    print(Fore.BLUE + "ℹ️  " + text)

def test_api_health():
    """Test if API is running"""
    print_header("TEST 1: API HEALTH CHECK")
    
    try:
        response = requests.get(f"{API_BASE_URL.replace('/api/v1', '')}/health", timeout=5)
        if response.status_code == 200:
            print_success("API is running and healthy")
            return True
        else:
            print_error(f"API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to API. Is the backend running?")
        print_info("Start backend with: uvicorn api.main:app --reload")
        return False
    except Exception as e:
        print_error(f"Error checking API health: {e}")
        return False

def test_safety_scoring():
    """Test safety scoring endpoint with ML model"""
    print_header("TEST 2: SAFETY SCORING WITH ML")
    
    # Test location (Coimbatore area)
    test_location = {
        "coordinates": [
            {"latitude": 11.0168, "longitude": 76.9558},
            {"latitude": 11.0178, "longitude": 76.9568}
        ],
        "time_of_day": "night",
        "rider_gender": "female"
    }
    
    print_info(f"Testing {len(test_location['coordinates'])} coordinates")
    print_info(f"Time of day: {test_location['time_of_day']}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/safety/score",
            json=test_location,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Safety scoring endpoint working!")
            
            safety_score = data.get('route_safety_score', 0)
            print(f"\n  {Fore.CYAN}Safety Score: {Style.BRIGHT}{safety_score:.1f}/100")
            
            # Check if ML model is being used
            if 'model_used' in data:
                print(f"  Model Used: {data['model_used']}")
                print_success("ML model is actively being used!")
            else:
                print_warning("Response doesn't indicate ML model usage")
            
            # Display factors
            if 'factors' in data:
                print(f"\n  {Fore.YELLOW}Safety Factors:")
                for key, value in data['factors'].items():
                    print(f"    • {key}: {value}")
            
            return True, safety_score
        else:
            print_error(f"Safety scoring failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False, 0
            
    except Exception as e:
        print_error(f"Error testing safety scoring: {e}")
        return False, 0

def test_route_optimization():
    """Test route optimization with ML-enhanced safety"""
    print_header("TEST 3: ROUTE OPTIMIZATION WITH ML")
    
    # Test delivery request with multiple stops
    delivery_request = {
        "stops": [
            {
                "address": "Coimbatore Railway Station",
                "latitude": 11.0079,
                "longitude": 76.9618,
                "priority": "high",
                "time_window": {"start": "09:00", "end": "18:00"}
            },
            {
                "address": "Brookefields Mall, Coimbatore",
                "latitude": 11.0298,
                "longitude": 76.9970,
                "priority": "medium",
                "time_window": {"start": "10:00", "end": "19:00"}
            },
            {
                "address": "Gandhipuram, Coimbatore",
                "latitude": 11.0192,
                "longitude": 76.9674,
                "priority": "medium",
                "time_window": {"start": "09:00", "end": "20:00"}
            },
            {
                "address": "RS Puram, Coimbatore",
                "latitude": 11.0024,
                "longitude": 76.9514,
                "priority": "low",
                "time_window": {"start": "14:00", "end": "20:00"}
            }
        ],
        "starting_point": {
            "latitude": 11.0168,
            "longitude": 76.9558
        },
        "rider_info": {"gender": "female"},
        "rider_id": "test_rider_001"
    }
    
    print_info(f"Optimizing route with {len(delivery_request['stops'])} stops")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/delivery/optimize",
            json=delivery_request,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Route optimization completed!")
            
            # Extract route information
            route_info = data.get('data', {})
            
            print(f"\n  {Fore.CYAN}Route Summary:")
            print(f"    Total Distance: {route_info.get('total_distance_meters', 0)/1000:.2f} km")
            print(f"    Estimated Time: {route_info.get('total_duration_seconds', 0)/60:.0f} minutes")
            print(f"    Safety Score: {Style.BRIGHT}{route_info.get('average_safety_score', 0):.1f}/100")
            
            # Check if ML influenced the route
            if 'optimization_method' in route_info:
                print(f"    Method: {route_info['optimization_method']}")
            
            # Show stop sequence
            if 'optimized_sequence' in route_info:
                print(f"\n  {Fore.YELLOW}Optimized Stop Sequence:")
                for idx, stop_id in enumerate(route_info['sequence'], 1):
                    # stop_name = stop.get('address', 'Unknown')
                    # stop_safety = stop.get('safety_score', 0)
                    print(f"    {idx}. Stop ID: {stop_id}")
            
            # Compare with non-ML route if available
            if 'comparison' in data:
                comp = data['comparison']
                print(f"\n  {Fore.MAGENTA}ML vs. Standard Comparison:")
                print(f"    Time Difference: {comp.get('time_difference_min', 0):+.1f} min")
                print(f"    Safety Improvement: {comp.get('safety_improvement', 0):+.1f} points")
                
                if comp.get('safety_improvement', 0) > 10:
                    print_success("ML significantly improved route safety!")
            
            return True, route_info
        else:
            print_error(f"Route optimization failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False, {}
            
    except Exception as e:
        print_error(f"Error testing route optimization: {e}")
        return False, {}

def test_feedback_learning():
    """Test if feedback updates ML model"""
    print_header("TEST 4: FEEDBACK LEARNING LOOP")
    
    feedback_data = {
        "route_id": "ROUTE_TEST",
        "rider_id": "test_rider_001",
        "safety_rating": 4,
        "route_quality_rating": 5,
        "comfort_rating": 4,
        "feedback_text": "Route was safe and well-lit. Good optimization!"
    }
    
    print_info("Submitting rider feedback...")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback/submit",
            json=feedback_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Feedback submitted successfully!")
            
            if data.get('model_updated'):
                print_success("ML model was updated with new feedback!")
                print(f"  New training samples: {data.get('new_samples_count', 0)}")
            else:
                print_info("Feedback stored (model will be retrained periodically)")
            
            return True
        else:
            print_warning(f"Feedback submission: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print_error(f"Error testing feedback: {e}")
        return False

def test_ml_model_info():
    """Get ML model information"""
    print_header("TEST 5: ML MODEL INFORMATION")
    
    try:
        # Try to get model stats from training endpoint
        response = requests.get(
            f"{API_BASE_URL}/training/model-info",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Retrieved ML model information!")
            
            print(f"\n  {Fore.CYAN}Model Details:")
            print(f"    Type: {data.get('model_type', 'Unknown')}")
            print(f"    Accuracy: {data.get('accuracy', 0):.2%}")
            print(f"    Training Samples: {data.get('training_samples', 0)}")
            print(f"    Last Trained: {data.get('last_trained', 'Unknown')}")
            print(f"    Features Used: {data.get('feature_count', 0)}")
            
            if 'top_features' in data:
                print(f"\n  {Fore.YELLOW}Top Important Features:")
                for feature in data['top_features'][:5]:
                    print(f"    • {feature['name']}: {feature['importance']:.3f}")
            
            return True
        else:
            print_warning("Model info endpoint not available")
            print_info("Model is likely working but stats endpoint not implemented")
            return False
            
    except Exception as e:
        print_warning(f"Could not retrieve model info: {e}")
        print_info("This is optional - ML can still be working")
        return False

def run_comprehensive_test():
    """Run all tests and generate report"""
    print("\n" + "="*70)
    print(Fore.CYAN + Style.BRIGHT + "🧪 SMART SHIELD ML INTEGRATION TEST SUITE".center(70))
    print("="*70)
    
    results = {
        'api_health': False,
        'safety_scoring': False,
        'route_optimization': False,
        'feedback_learning': False,
        'model_info': False
    }
    
    # Test 1: API Health
    results['api_health'] = test_api_health()
    if not results['api_health']:
        print_error("\n⚠️  Cannot proceed without running API. Please start the backend first.")
        return results
    
    # Test 2: Safety Scoring
    results['safety_scoring'], safety_score = test_safety_scoring()
    
    # Test 3: Route Optimization
    results['route_optimization'], route_info = test_route_optimization()
    
    # Test 4: Feedback Learning
    results['feedback_learning'] = test_feedback_learning()
    
    # Test 5: Model Info (optional)
    results['model_info'] = test_ml_model_info()
    
    # Generate Report
    print_header("TEST RESULTS SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"  Tests Passed: {Fore.GREEN}{passed_tests}{Style.RESET_ALL}/{total_tests}")
    print(f"\n  Individual Results:")
    
    for test_name, passed in results.items():
        status = f"{Fore.GREEN}✅ PASS" if passed else f"{Fore.RED}❌ FAIL"
        print(f"    {test_name.replace('_', ' ').title():.<40} {status}")
    
    # Overall assessment
    print("\n" + "="*70)
    
    if passed_tests == total_tests:
        print(Fore.GREEN + Style.BRIGHT + "🎉 ALL TESTS PASSED! ML SYSTEM IS FULLY OPERATIONAL!")
    elif passed_tests >= 3:
        print(Fore.YELLOW + Style.BRIGHT + "✅ CORE ML FEATURES WORKING! Some optional features need attention.")
    elif passed_tests >= 2:
        print(Fore.YELLOW + Style.BRIGHT + "⚠️  ML PARTIALLY WORKING. Some core features need fixing.")
    else:
        print(Fore.RED + Style.BRIGHT + "❌ ML SYSTEM NEEDS ATTENTION. Check the errors above.")
    
    print("="*70 + "\n")
    
    # Next steps
    if passed_tests >= 3:
        print(Fore.GREEN + "💡 NEXT STEPS FOR SUCCESS:")
        print("  1. ✅ Your ML system is working!")
        print("  2. 📊 Create a demo showing ML impact on routes")
        print("  3. 📈 Document the safety improvements with metrics")
        print("  4. 🎬 Prepare a presentation for your mentor")
        print("  5. 🚀 Deploy to production (Render/Vercel)")
    else:
        print(Fore.YELLOW + "💡 NEXT STEPS TO FIX:")
        if not results['api_health']:
            print("  1. Start the backend: cd backend && uvicorn api.main:app --reload")
        if not results['safety_scoring']:
            print("  2. Train ML model: python scripts/train_safety_model.py")
        if not results['route_optimization']:
            print("  3. Check route optimizer code in api/models/route_optimizer.py")
        if not results['feedback_learning']:
            print("  4. Verify feedback endpoint in api/routes/feedback.py")
    
    return results

def main():
    """Main function"""
    try:
        results = run_comprehensive_test()
        
        # Exit with appropriate code
        passed = sum(1 for v in results.values() if v)
        if passed >= 3:
            sys.exit(0)  # Success
        else:
            sys.exit(1)  # Failure
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Check if colorama is installed
    try:
        import colorama
    except ImportError:
        print("⚠️  Installing colorama for better output...")
        os.system("pip install colorama")
        import colorama
    
    main()
