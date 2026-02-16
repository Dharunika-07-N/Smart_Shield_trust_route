import pytest
import time
from api.services.crime_data import CrimeDataService
from api.services.maps import MapsService
from api.schemas.delivery import Coordinate

def test_crime_data_caching():
    service = CrimeDataService()
    coord = Coordinate(latitude=13.0827, longitude=80.2707)
    
    # First call - should calculate
    start_time = time.time()
    score1 = service.get_crime_score(coord)
    first_duration = time.time() - start_time
    
    # Second call - should be cached
    start_time = time.time()
    score2 = service.get_crime_score(coord)
    second_duration = time.time() - start_time
    
    assert score1 == score2
    # Cached call should be significantly faster
    # On most systems, math/geometric calc takes much longer than LRU lookup
    assert second_duration < first_duration or second_duration < 0.001
    print(f"Crime Score - First: {first_duration:.6f}s, Cached: {second_duration:.6f}s")

def test_crime_data_coordinate_rounding():
    service = CrimeDataService()
    # Coordinates that round to the same value (2 decimal places)
    coord1 = Coordinate(latitude=13.08271, longitude=80.27071)
    coord2 = Coordinate(latitude=13.08274, longitude=80.27074)
    
    score1 = service.get_crime_score(coord1)
    
    start_time = time.time()
    score2 = service.get_crime_score(coord2)
    duration = time.time() - start_time
    
    assert score1 == score2
    assert duration < 0.001 # Should hit cache

def test_maps_service_caching():
    # Mocking MapsService as it requires API key for real geocoding
    # But we can test the logic if we mock the gmaps client
    from unittest.mock import MagicMock
    # googlemaps.Client validates key starts with AIza
    service = MapsService(api_key="AIza_fake_key")
    service.gmaps = MagicMock()
    service.gmaps.geocode.return_value = [{'geometry': {'location': {'lat': 10.0, 'lng': 20.0}}}]
    
    # First call
    res1 = service.geocode_address("Test Address")
    assert service.gmaps.geocode.call_count == 1
    
    # Second call - should be cached
    res2 = service.geocode_address("Test Address")
    assert res1 == res2
    assert service.gmaps.geocode.call_count == 1 # Still 1
