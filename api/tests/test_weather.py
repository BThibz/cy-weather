import math
import pytest
from datetime import datetime
from pydantic import ValidationError
from datetime import datetime, timezone

from src.models.Weather import (
    WeatherRequest,
    CurrentWeatherData,
    WeatherResponse,
    DailyForecastData,
    ForecastResponse,
)

# ======================================================
# Tests pour WeatherRequest
# ======================================================

def test_weather_request_valid():
    req = WeatherRequest(city="Paris", country_code="FR")
    assert req.city == "Paris"
    assert req.country_code == "FR"


def test_weather_request_without_country_code():
    req = WeatherRequest(city="Paris")
    assert req.city == "Paris"
    assert req.country_code is None


def test_weather_request_city_required():
    with pytest.raises(ValidationError):
        WeatherRequest()


def test_weather_request_city_empty():
    with pytest.raises(ValidationError):
        WeatherRequest(city="")


# ======================================================
# Tests pour CurrentWeatherData
# ======================================================

def test_current_weather_data_valid():
    data = CurrentWeatherData(
        temperature=20.5,
        feels_like=21.0,
        humidity=60,
        pressure=1013,
        wind_speed=3.5,
        description="clear sky",
        icon="01d",
    )

    assert math.isclose(data.temperature, 20.5, rel_tol=1e-9)
    assert math.isclose(data.feels_like, 21.0, rel_tol=1e-9)
    assert data.humidity == 60
    assert data.description == "clear sky"


def test_current_weather_data_invalid_type():
    with pytest.raises(ValidationError):
        CurrentWeatherData(
            temperature="hot",
            feels_like=21.0,
            humidity=60,
            pressure=1013,
            wind_speed=3.5,
            description="sunny",
            icon="01d",
        )


# ======================================================
# Tests pour WeatherResponse (modèle imbriqué)
# ======================================================

def test_weather_response_valid():
    weather = CurrentWeatherData(
        temperature=18.0,
        feels_like=17.0,
        humidity=70,
        pressure=1012,
        wind_speed=4.0,
        description="cloudy",
        icon="03d",
    )

    response = WeatherResponse(
        city="Lyon",
        country="FR",
        timestamp = datetime.now(timezone.utc),
        weather=weather,
    )

    assert response.city == "Lyon"
    assert response.country == "FR"
    assert math.isclose(response.weather.temperature, 18.0, rel_tol=1e-9)


def test_weather_response_missing_weather():
    with pytest.raises(ValidationError):
        WeatherResponse(
            city="Lyon",
            country="FR",
            timestamp = datetime.now(timezone.utc),
        )


# ======================================================
# Tests pour DailyForecastData
# ======================================================

def test_daily_forecast_with_precipitation():
    forecast = DailyForecastData(
        date="2026-01-10",
        temp_min=5.0,
        temp_max=12.0,
        temp_day=10.0,
        temp_night=6.0,
        humidity=65,
        wind_speed=3.0,
        description="rainy",
        icon="09d",
        precipitation_probability=80.0,
    )

    assert math.isclose(forecast.precipitation_probability, 80.0, rel_tol=1e-9)


def test_daily_forecast_without_precipitation():
    forecast = DailyForecastData(
        date="2026-01-11",
        temp_min=4.0,
        temp_max=11.0,
        temp_day=9.0,
        temp_night=5.0,
        humidity=60,
        wind_speed=2.0,
        description="clear",
        icon="01d",
    )

    assert forecast.precipitation_probability is None


def test_daily_forecast_invalid_type():
    with pytest.raises(ValidationError):
        DailyForecastData(
            date="2026-01-12",
            temp_min="cold",
            temp_max=10.0,
            temp_day=8.0,
            temp_night=4.0,
            humidity=55,
            wind_speed=2.5,
            description="cloudy",
            icon="03d",
        )


# ======================================================
# Tests pour ForecastResponse
# ======================================================

def test_forecast_response_valid():
    forecast = [
        DailyForecastData(
            date="2026-01-10",
            temp_min=5.0,
            temp_max=12.0,
            temp_day=10.0,
            temp_night=6.0,
            humidity=65,
            wind_speed=3.0,
            description="rainy",
            icon="09d",
        ),
        DailyForecastData(
            date="2026-01-11",
            temp_min=4.0,
            temp_max=11.0,
            temp_day=9.0,
            temp_night=5.0,
            humidity=60,
            wind_speed=2.0,
            description="clear",
            icon="01d",
        ),
    ]

    response = ForecastResponse(
        city="Marseille",
        country="FR",
        forecast=forecast,
    )

    assert response.city == "Marseille"
    assert response.country == "FR"
    assert len(response.forecast) == 2
    assert response.forecast[0].date == "2026-01-10"


def test_forecast_response_empty_forecast():
    with pytest.raises(ValidationError):
        ForecastResponse(
            city="Nice",
            country="FR",
            forecast=None,
        )
