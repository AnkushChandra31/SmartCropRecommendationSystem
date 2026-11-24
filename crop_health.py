
from crop_recommender import FEATURES

DISPLAY_NAMES = {
    "N": "Nitrogen", "P": "Phosphorus", "K": "Potassium",
    "temperature": "Temperature", "humidity": "Humidity",
    "ph": "Soil pH", "rainfall": "Rainfall",
}


def get_crop_health(model, crop_name, values):
    profile = getattr(model, "crop_profiles", {}).get(crop_name)
    if not profile:
        return {"status": "Unknown", "score": 0, "good": [], "attention": []}

    good, attention = [], []
    for feature in FEATURES:
        value = float(values[feature])
        low = profile[feature]["low"]
        high = profile[feature]["high"]
        name = DISPLAY_NAMES[feature]

        if low <= value <= high:
            good.append(name)
        elif value < low:
            attention.append(f"{name} is low (ideal: {low:.1f} to {high:.1f})")
        else:
            attention.append(f"{name} is high (ideal: {low:.1f} to {high:.1f})")

    score = len(good)
    if score >= 6:
        status = "Healthy"
    elif score >= 4:
        status = "Moderate - needs monitoring"
    else:
        status = "Needs attention"

    return {"status": status, "score": score, "good": good, "attention": attention}


def get_future_advice(health, forecast):
    total_rain = sum(day["rainfall"] for day in forecast)
    rainy_days = sum(1 for day in forecast if day["rainfall"] > 0.5)

    if total_rain < 10:
        rain_advice = "Low rainfall expected. Plan light irrigation and check soil moisture daily."
    elif total_rain > 80:
        rain_advice = "Heavy rainfall expected. Keep drainage channels clear and avoid over-watering."
    else:
        rain_advice = "Moderate rainfall expected. Monitor soil moisture before irrigating."

    if health["status"] == "Healthy":
        health_advice = "Current conditions are suitable. Continue regular pest and leaf checks."
    elif health["status"] == "Moderate - needs monitoring":
        health_advice = "Check the listed values within the next few days and make small corrections."
    else:
        health_advice = "Correct the listed soil or weather issues before making major planting decisions."

    return {
        "total_rain": round(total_rain, 1),
        "rainy_days": rainy_days,
        "rain_advice": rain_advice,
        "health_advice": health_advice,
    }
