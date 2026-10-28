

import requests

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city):
    response = requests.get(
        GEOCODING_URL,
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=10
    )
    response.raise_for_status()

    results = response.json().get("results")
    if not results:
        raise ValueError(f"City '{city}' was not found.")

    return results[0]["latitude"], results[0]["longitude"]


def get_weather(city):
    latitude, longitude = get_coordinates(city)

    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m",
            "daily": "precipitation_sum",
            "past_days": 30,      
            "forecast_days": 1,
            "timezone": "auto"
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()


    daily_rain = data["daily"]["precipitation_sum"]
    total_rain = sum(r for r in daily_rain if r is not None)

    return {
        "temperature": data["current"]["temperature_2m"],
        "humidity": data["current"]["relative_humidity_2m"],
        "rainfall": round(total_rain, 1)
    }