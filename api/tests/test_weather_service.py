import math
import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from src.services.weather_service import WeatherService
from src.models.Weather import WeatherResponse, ForecastResponse


@pytest.fixture
def service():
    return WeatherService()


# ======================================================
# Tests méthodes internes
# ======================================================

def test_get_weather_description(service):
    assert service._get_weather_description(0) == "Ciel dégagé"
    assert service._get_weather_description(999) == "Conditions inconnues"


def test_wmo_to_icon(service):
    assert service._wmo_to_icon(0) == "01d"
    assert service._wmo_to_icon(95) == "11d"
    assert service._wmo_to_icon(999) == "01d"


# ======================================================
# Test get_current_weather (ASYNC + MOCK)
# ======================================================

@pytest.mark.asyncio
async def test_get_current_weather(service, mocker):
    # --- Mock coordonnées ---
    mocker.patch.object(
        service,
        "_get_coordinates",
        AsyncMock(return_value=(48.85, 2.35, "Paris", "FR")),
    )

    # --- Mock réponse API météo ---
    mock_response = {
        "current": {
            "temperature_2m": 20.0,
            "apparent_temperature": 21.0,
            "relative_humidity_2m": 60,
            "pressure_msl": 1013,
            "wind_speed_10m": 3.5,
            "weather_code": 0,
            "time": "2026-01-10T12:00",
        }
    }

    
    mock_resp = AsyncMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = mock_response

    # Patch httpx.AsyncClient.get pour retourner la réponse mockée
    mocker.patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp))

    result = service.get_current_weather("Paris")

    assert isinstance(result, WeatherResponse)
    assert result.city == "Paris"
    assert math.isclose(result.weather.temperature, 20.0, rel_tol=1e-9)
    assert result.weather.description == "Ciel dégagé"


# ======================================================
# Test get_forecast (ASYNC + MOCK)
# ======================================================

@pytest.mark.asyncio
async def test_get_forecast(service, mocker):
    # --- Mock coordonnées ---
    mocker.patch.object(
        service,
        "_get_coordinates",
        AsyncMock(return_value=(43.3, 5.4, "Marseille", "FR")),
    )

    mock_response = {
        "daily": {
            "time": ["2026-01-10", "2026-01-11"],
            "weather_code": [1, 3],
            "temperature_2m_max": [15, 14],
            "temperature_2m_min": [7, 6],
            "apparent_temperature_max": [14, 13],
            "apparent_temperature_min": [6, 5],
            "precipitation_probability_max": [10, 20],
            "wind_speed_10m_max": [4.0, 5.0],
        }
    }

    
    mock_resp = AsyncMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = mock_response

    # Patch httpx.AsyncClient.get pour retourner la réponse mockée
    mocker.patch("httpx.AsyncClient.get", new=AsyncMock(return_value=mock_resp))

    result = service.get_forecast("Marseille")

    assert isinstance(result, ForecastResponse)
    assert len(result.forecast) == 2
    assert result.forecast[0].description == "Principalement dégagé"
