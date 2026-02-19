"""
Prayer times service for the Ramadan Fasting Schedule app.
Fetches prayer times from the Aladhan API.
"""
import requests
from datetime import datetime, date
from src.config.manager import load_config


# Prayer time labels in Indonesian
PRAYER_LABELS = {
    "Imsak": "Imsak (Sahur)",
    "Fajr": "Subuh",
    "Sunrise": "Syuruq",
    "Dhuhr": "Dzuhur",
    "Asr": "Ashar",
    "Maghrib": "Maghrib (Berbuka)",
    "Isha": "Isya",
}

# Keys we want from the API response
PRAYER_KEYS = ["Imsak", "Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]


def fetch_prayer_times(latitude, longitude, date_obj=None, method=20):
    """
    Fetch prayer times from Aladhan API for a given location and date.

    Args:
        latitude: float
        longitude: float
        date_obj: date object (defaults to today)
        method: calculation method ID (default: 20 = KEMENAG Indonesia)

    Returns:
        dict with prayer times or None on failure
    """
    if date_obj is None:
        date_obj = date.today()

    try:
        url = "https://api.aladhan.com/v1/timings"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "method": method,
            "date": date_obj.strftime("%d-%m-%Y"),
        }

        response = requests.get(url, params=params, timeout=15)
        data = response.json()

        if data.get("code") == 200:
            timings = data["data"]["timings"]
            hijri = data["data"]["date"]["hijri"]
            gregorian = data["data"]["date"]["gregorian"]

            result = {
                "timings": {},
                "hijri_date": f"{hijri['day']} {hijri['month']['en']} {hijri['year']}",
                "hijri_date_ar": f"{hijri['day']} {hijri['month']['ar']} {hijri['year']}",
                "hijri_month": hijri['month']['en'],
                "hijri_day": int(hijri['day']),
                "gregorian_date": f"{gregorian['day']} {gregorian['month']['en']} {gregorian['year']}",
                "is_ramadan": hijri['month']['number'] == 9,
            }

            for key in PRAYER_KEYS:
                if key in timings:
                    # Remove timezone offset like "(WIB)" from the time
                    time_str = timings[key].split(" ")[0]
                    result["timings"][key] = time_str

            return result
        else:
            print(f"Aladhan API error: {data}")
            return None

    except requests.RequestException as e:
        print(f"Prayer times request error: {e}")
        return None


def get_fasting_times(latitude, longitude, date_obj=None, method=None):
    """
    Get the fasting-relevant times (Imsak/Sahur and Maghrib/Iftar).

    Returns:
        dict with 'imsak', 'fajr', 'maghrib' times and metadata, or None
    """
    if method is None:
        config = load_config()
        method = config.get("calculation_method", 20)

    prayer_data = fetch_prayer_times(latitude, longitude, date_obj, method)

    if prayer_data is None:
        return None

    timings = prayer_data["timings"]

    return {
        "imsak": timings.get("Imsak", "--:--"),
        "fajr": timings.get("Fajr", "--:--"),
        "maghrib": timings.get("Maghrib", "--:--"),
        "all_timings": timings,
        "hijri_date": prayer_data["hijri_date"],
        "hijri_date_ar": prayer_data.get("hijri_date_ar", ""),
        "hijri_month": prayer_data["hijri_month"],
        "hijri_day": prayer_data["hijri_day"],
        "gregorian_date": prayer_data["gregorian_date"],
        "is_ramadan": prayer_data["is_ramadan"],
    }


def get_time_remaining(target_time_str):
    """
    Calculate remaining time until a given target time (HH:MM format).
    Returns a tuple (hours, minutes, seconds, is_past).
    """
    now = datetime.now()
    try:
        parts = target_time_str.split(":")
        target = now.replace(
            hour=int(parts[0]),
            minute=int(parts[1]),
            second=0,
            microsecond=0,
        )

        if target < now:
            return (0, 0, 0, True)

        diff = target - now
        total_seconds = int(diff.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return (hours, minutes, seconds, False)
    except (ValueError, IndexError):
        return (0, 0, 0, True)


def format_countdown(hours, minutes, seconds):
    """Format countdown as human-readable string."""
    if hours > 0:
        return f"{hours}j {minutes}m {seconds}d"
    elif minutes > 0:
        return f"{minutes}m {seconds}d"
    else:
        return f"{seconds}d"
