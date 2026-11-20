

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
            "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,weather_code",
            "past_days": 30,      
            "forecast_days": 7,
            "timezone": "auto"
        },
        timeout=10
    )
    response.raise_for_status()
    data = response.json()


    daily = data["daily"]
    daily_rain = daily["precipitation_sum"]
    total_rain = sum(r for r in daily_rain if r is not None)

    # The API returns past days plus future days. Select today and the next
    # seven days to provide a simple rainfall prediction for the user.
    today = data["current"]["time"][:10]
    forecast = []
    for index, date in enumerate(daily["time"]):
        if date >= today and len(forecast) < 7:
            forecast.append({
                "date": date,
                "rainfall": round(float(daily["precipitation_sum"][index] or 0), 1),
                "min_temp": round(float(daily["temperature_2m_min"][index]), 1),
                "max_temp": round(float(daily["temperature_2m_max"][index]), 1),
            })

    return {
        "city": city.title(),
        "temperature": data["current"]["temperature_2m"],
        "humidity": data["current"]["relative_humidity_2m"],
        "rainfall": round(total_rain, 1),
        "rain_forecast": forecast,
    }
