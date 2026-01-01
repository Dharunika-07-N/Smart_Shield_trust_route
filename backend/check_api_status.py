"""
Diagnostic script to check Google Maps API status
Run this to diagnose why route optimization is failing
"""
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def check_api_key():
    """Check if API key is configured"""
    api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
    
    print("=" * 60)
    print("🔍 GOOGLE MAPS API DIAGNOSTICS")
    print("=" * 60)
    print()
    
    # Check 1: API Key Exists
    print("✓ Check 1: API Key Configuration")
    if not api_key:
        print("  ❌ GOOGLE_MAPS_API_KEY is NOT set in .env file")
        print("  → Solution: Add your API key to backend/.env")
        print("     GOOGLE_MAPS_API_KEY=your_key_here")
        return False
    elif api_key == "YOUR_API_KEY_HERE" or api_key == "your_key_here":
        print("  ❌ GOOGLE_MAPS_API_KEY is set to placeholder value")
        print("  → Solution: Replace with actual Google Maps API key")
        return False
    else:
        print(f"  ✅ API Key is set (length: {len(api_key)} characters)")
        print(f"  → Key starts with: {api_key[:10]}...")
    
    print()
    
    # Check 2: Test Geocoding API (simplest API)
    print("✓ Check 2: Testing Geocoding API")
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            'address': 'Chennai, India',
            'key': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') == 'OK':
            print("  ✅ Geocoding API works!")
            print(f"  → Found: {data['results'][0]['formatted_address']}")
        else:
            print(f"  ❌ Geocoding API failed")
            print(f"  → Status: {data.get('status')}")
            print(f"  → Error: {data.get('error_message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ❌ Request failed: {str(e)}")
        return False
    
    print()
    
    # Check 3: Test Directions API (the one that's failing)
    print("✓ Check 3: Testing Directions API (THE CRITICAL ONE)")
    try:
        url = "https://maps.googleapis.com/maps/api/directions/json"
        params = {
            'origin': 'Chennai, India',
            'destination': 'Coimbatore, India',
            'mode': 'driving',
            'key': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') == 'OK':
            print("  ✅ Directions API works!")
            route = data['routes'][0]
            leg = route['legs'][0]
            print(f"  → Distance: {leg['distance']['text']}")
            print(f"  → Duration: {leg['duration']['text']}")
            print("  → This means your route optimization SHOULD work!")
        elif data.get('status') == 'REQUEST_DENIED':
            print("  ❌ Directions API: REQUEST DENIED")
            print(f"  → Error: {data.get('error_message', 'No error message')}")
            print()
            print("  🔧 Common causes:")
            print("     1. Directions API not enabled in Google Cloud Console")
            print("     2. API key has restrictions blocking this API")
            print("     3. Billing not enabled on Google Cloud account")
            print()
            print("  📋 Solutions:")
            print("     1. Go to: https://console.cloud.google.com/apis/library/directions-backend.googleapis.com")
            print("     2. Click 'ENABLE' on Directions API")
            print("     3. Enable billing: https://console.cloud.google.com/billing")
            return False
        elif data.get('status') == 'OVER_QUERY_LIMIT':
            print("  ❌ Directions API: QUOTA EXCEEDED")
            print("  → You've hit your daily/monthly limit")
            print("  → Wait 24 hours or upgrade your quota")
            return False
        else:
            print(f"  ❌ Directions API failed")
            print(f"  → Status: {data.get('status')}")
            print(f"  → Error: {data.get('error_message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"  ❌ Request failed: {str(e)}")
        return False
    
    print()
    
    # Check 4: Test Distance Matrix API
    print("✓ Check 4: Testing Distance Matrix API")
    try:
        url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        params = {
            'origins': 'Chennai, India',
            'destinations': 'Coimbatore, India',
            'mode': 'driving',
            'key': api_key
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if response.status_code == 200 and data.get('status') == 'OK':
            print("  ✅ Distance Matrix API works!")
        else:
            print(f"  ⚠️  Distance Matrix API issue: {data.get('status')}")
    except Exception as e:
        print(f"  ⚠️  Request failed: {str(e)}")
    
    print()
    print("=" * 60)
    print("✅ DIAGNOSIS COMPLETE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = check_api_key()
    
    if success:
        print()
        print("🎉 All checks passed! Your API should work.")
        print("   If route optimization still fails, check:")
        print("   1. Backend logs for detailed errors")
        print("   2. Network connectivity")
        print("   3. Firewall settings")
    else:
        print()
        print("❌ Issues found. Please fix the problems above.")
        print("   Need help? Share the output with your developer.")
    
    print()
    input("Press Enter to exit...")
