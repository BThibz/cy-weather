import math
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock

from fastapi import FastAPI
from src.resources.weather_resource import router
from src.services.weather_service import WeatherService
from src.models.Weather import (
    WeatherResponse, 
    ForecastResponse, 
    CurrentWeatherData, 
    DailyForecastData
)

# Création d'une app FastAPI pour les tests
app = FastAPI()
app.include_router(router)

client = TestClient(app)

# --- Fixture pour mocker le service ---
@pytest.fixture
def mock_weather_service(mocker):
    mock_service = mocker.patch(
        "src.resources.weather_resource.weather_service",
        autospec=True
    )
    return mock_service

# ======================================================
# Tests endpoint /weather/current
# ======================================================

def test_get_current_weather_success(mock_weather_service):
    # Mock de la fonction async get_current_weather
    mock_weather_service.get_current_weather = AsyncMock(
        return_value=WeatherResponse(
            city="Paris",
            country="FR",
            timestamp="2026-01-10T12:00",
            weather=CurrentWeatherData(
                temperature=20.0,
                feels_like=21.0,
                humidity=60,
                pressure=1013,
                wind_speed=3.5,
                description="Ciel dégagé",
                icon="01d"
            )
        )
    )

    response = client.get("/weather/current?city=Paris&country_code=FR")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert math.isclose(data["weather"]["temperature"], 20.0, rel_tol=1e-9)
    assert data["weather"]["description"] == "Ciel dégagé"

def test_get_current_weather_404(mock_weather_service):
    from httpx import HTTPStatusError
    # Simuler une ville non trouvée
    mock_weather_service.get_current_weather = AsyncMock(side_effect=HTTPStatusError(
        "Not found",
        request=None,
        response=type("obj", (), {"status_code": 404})()
    ))

    response = client.get("/weather/current?city=UnknownCity")
    assert response.status_code == 404
    assert "non trouvée" in response.json()["detail"]

# ======================================================
# Tests endpoint /weather/forecast
# ======================================================

def test_get_forecast_success(mock_weather_service):
    mock_weather_service.get_forecast = AsyncMock(
        return_value=ForecastResponse(
            city="Paris",
            country="FR",
            forecast=[
                DailyForecastData(
                    date="2026-01-10",
                    temp_min=5,
                    temp_max=12,
                    temp_day=10,
                    temp_night=6,
                    humidity=60,
                    wind_speed=3.5,
                    description="Ciel dégagé",
                    icon="01d",
                    precipitation_probability=10
                )
            ]
        )
    )

    response = client.get("/weather/forecast?city=Paris&country_code=FR")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Paris"
    assert len(data["forecast"]) == 1
    assert data["forecast"][0]["description"] == "Ciel dégagé"

def test_get_forecast_404(mock_weather_service):
    from httpx import HTTPStatusError
    mock_weather_service.get_forecast = AsyncMock(side_effect=HTTPStatusError(
        "Not found",
        request=None,
        response=type("obj", (), {"status_code": 404})()
    ))

    response = client.get("/weather/forecast?city=UnknownCity")
    assert response.status_code == 404
    assert "non trouvée" in response.json()["detail"]
