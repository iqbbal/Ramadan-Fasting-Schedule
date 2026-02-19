"""
Location service for the Ramadan Fasting Schedule app.
Handles IP-based geolocation and manual city coordinates.
"""
import requests
from src.config.manager import load_config, INDONESIAN_CITIES, INTERNATIONAL_CITIES


def get_location_by_ip():
    """
    Get user's location based on their IP address.
    Uses ip-api.com (free, no API key required, 45 req/min limit).
    Returns dict with lat, lng, city, country or None on failure.
    """
    try:
        response = requests.get(
            "http://ip-api.com/json/?fields=status,city,country,lat,lon,timezone",
            timeout=10
        )
        data = response.json()

        if data.get("status") == "success":
            return {
                "latitude": data["lat"],
                "longitude": data["lon"],
                "city": data.get("city", "Unknown"),
                "country": data.get("country", "Unknown"),
                "timezone": data.get("timezone", ""),
            }
        else:
            print(f"IP geolocation failed: {data}")
            return None
    except requests.RequestException as e:
        print(f"IP geolocation request error: {e}")
        return None


def get_location_by_city(city_name):
    """
    Get coordinates for a predefined city.
    Returns dict with lat, lng, city, country or None if city not found.
    """
    all_cities = {**INDONESIAN_CITIES, **INTERNATIONAL_CITIES}

    if city_name in all_cities:
        city_data = all_cities[city_name]
        return {
            "latitude": city_data["lat"],
            "longitude": city_data["lng"],
            "city": city_name,
            "country": city_data["country"],
        }
    return None


def get_current_location():
    """
    Get the current location based on the user's settings.
    If mode is 'auto', uses IP geolocation.
    If mode is 'manual', uses the saved city coordinates.
    Falls back to Jakarta if all else fails.
    """
    config = load_config()
    location_mode = config.get("location_mode", "auto")

    if location_mode == "manual":
        city = config.get("city", "")
        if city:
            loc = get_location_by_city(city)
            if loc:
                return loc

        # If manual but has lat/lng directly
        lat = config.get("latitude")
        lng = config.get("longitude")
        if lat is not None and lng is not None:
            return {
                "latitude": lat,
                "longitude": lng,
                "city": config.get("city", "Custom"),
                "country": config.get("country", ""),
            }

    # Auto mode or fallback
    loc = get_location_by_ip()
    if loc:
        return loc

    # Ultimate fallback: Jakarta
    print("Using fallback location: Jakarta")
    return {
        "latitude": -6.2088,
        "longitude": 106.8456,
        "city": "Jakarta",
        "country": "Indonesia",
    }
