import pytest
import asyncio
from unittest.mock import MagicMock, patch
from api.services.sms import SMSService
from api.services.weather import WeatherService
from api.services.traffic import TrafficService
from api.schemas.delivery import Coordinate

@pytest.mark.asyncio
async def test_sms_service_emergency_alert():
    # Patch settings BEFORE creating the service
    with patch('config.config.settings.TWILIO_ACCOUNT_SID', 'AC123'), \
         patch('config.config.settings.TWILIO_AUTH_TOKEN', 'token'), \
         patch('config.config.settings.TWILIO_PHONE_NUMBER', '+1234'), \
         patch('config.config.settings.EMERGENCY_PHONE', '+5678'):
        
        # Patch the Client inside the module
        with patch('api.services.sms.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            mock_messages = MagicMock()
            mock_client.messages = mock_messages
            
            mock_msg_instance = MagicMock()
            mock_msg_instance.sid = "SM123"
            mock_messages.create.return_value = mock_msg_instance
            
            service = SMSService()
            assert service.enabled is True
            
            success = await service.send_emergency_alert("Test Rider", "13.0, 80.0")
            assert success is True
            assert mock_messages.create.called

@pytest.mark.asyncio
async def test_weather_service_impact():
    service = WeatherService()
    # Force API key to be set so it doesn't use mock
    service.api_key = "fake_weather_key"
    coord = Coordinate(latitude=13.0827, longitude=80.2707)
    
    # Mock httpx.AsyncClient.get
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "weather": [{"main": "Rain", "description": "heavy rain"}],
            "main": {"temp": 30, "humidity": 80},
            "rain": {"1h": 10},
            "visibility": 2000,
            "wind": {"speed": 12}
        }
        mock_get.return_value = mock_response
        
        weather_info = await service.get_weather(coord)
        assert weather_info['hazard_score'] > 0
        assert any("Rain" in c for c in weather_info['hazard_conditions'])

@pytest.mark.asyncio
async def test_traffic_service_levels():
    service = TrafficService()
    coord1 = Coordinate(latitude=13.0, longitude=80.0)
    coord2 = Coordinate(latitude=13.1, longitude=80.1)
    
    with patch('api.services.traffic.aggregator.get_traffic_data') as mock_agg:
        mock_segment = MagicMock()
        # Mocking the Enum-like structure
        mock_segment.traffic_level.value = 4 # HEAVY
        mock_segment.traffic_level.name = "HEAVY"
        mock_agg.return_value = [mock_segment]
        
        traffic_level, _, duration = await service.get_traffic_level(coord1, coord2)
        assert traffic_level == "high" 
        assert duration > 0
