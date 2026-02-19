"""
Configuration manager for the Ramadan Fasting Schedule app.
Handles loading, saving, and validating user settings.
"""
import json
import os
import sys

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "location_mode": "auto",       # "auto" (IP geolocation) or "manual"
    "city": "",
    "country": "",
    "latitude": None,
    "longitude": None,
    "calculation_method": 20,       # 20 = Kementerian Agama RI (KEMENAG)
    "notification_before_imsak_minutes": 10,
    "notification_at_iftar": True,
    "theme": "dark",
    "auto_start": False,
}

# Metode perhitungan waktu shalat dari Aladhan API
CALCULATION_METHODS = {
    0: "Shia Ithna-Ashari (Jafari)",
    1: "University of Islamic Sciences, Karachi",
    2: "Islamic Society of North America (ISNA)",
    3: "Muslim World League (MWL)",
    4: "Umm Al-Qura University, Makkah",
    5: "Egyptian General Authority of Survey",
    7: "Institute of Geophysics, University of Tehran",
    8: "Gulf Region",
    9: "Kuwait",
    10: "Qatar",
    11: "Majlis Ugama Islam Singapura",
    12: "UOIF (France)",
    13: "Diyanet İşleri Başkanlığı (Turkey)",
    14: "Spiritual Administration of Muslims of Russia",
    15: "Moonsighting Committee Worldwide",
    16: "Dubai (unofficial)",
    20: "Kementerian Agama Republik Indonesia (KEMENAG)",
}

# Daftar kota populer di Indonesia
INDONESIAN_CITIES = {
    "Jakarta": {"lat": -6.2088, "lng": 106.8456, "country": "Indonesia"},
    "Surabaya": {"lat": -7.2575, "lng": 112.7521, "country": "Indonesia"},
    "Bandung": {"lat": -6.9175, "lng": 107.6191, "country": "Indonesia"},
    "Medan": {"lat": 3.5952, "lng": 98.6722, "country": "Indonesia"},
    "Semarang": {"lat": -6.9666, "lng": 110.4196, "country": "Indonesia"},
    "Makassar": {"lat": -5.1477, "lng": 119.4327, "country": "Indonesia"},
    "Yogyakarta": {"lat": -7.7956, "lng": 110.3695, "country": "Indonesia"},
    "Palembang": {"lat": -2.9761, "lng": 104.7754, "country": "Indonesia"},
    "Denpasar": {"lat": -8.6500, "lng": 115.2167, "country": "Indonesia"},
    "Balikpapan": {"lat": -1.2654, "lng": 116.8311, "country": "Indonesia"},
    "Banjarmasin": {"lat": -3.3167, "lng": 114.5900, "country": "Indonesia"},
    "Pontianak": {"lat": -0.0263, "lng": 109.3425, "country": "Indonesia"},
    "Aceh (Banda Aceh)": {"lat": 5.5483, "lng": 95.3238, "country": "Indonesia"},
    "Padang": {"lat": -0.9471, "lng": 100.4172, "country": "Indonesia"},
    "Pekanbaru": {"lat": 0.5071, "lng": 101.4478, "country": "Indonesia"},
    "Manado": {"lat": 1.4748, "lng": 124.8421, "country": "Indonesia"},
    "Malang": {"lat": -7.9666, "lng": 112.6326, "country": "Indonesia"},
    "Solo (Surakarta)": {"lat": -7.5755, "lng": 110.8243, "country": "Indonesia"},
    "Mataram": {"lat": -8.5833, "lng": 116.1167, "country": "Indonesia"},
    "Jayapura": {"lat": -2.5333, "lng": 140.7167, "country": "Indonesia"},
}

# Kota-kota internasional (untuk pilihan manual)
INTERNATIONAL_CITIES = {
    "Makkah": {"lat": 21.3891, "lng": 39.8579, "country": "Saudi Arabia"},
    "Madinah": {"lat": 24.4672, "lng": 39.6024, "country": "Saudi Arabia"},
    "Kuala Lumpur": {"lat": 3.1390, "lng": 101.6869, "country": "Malaysia"},
    "Singapore": {"lat": 1.3521, "lng": 103.8198, "country": "Singapore"},
    "Istanbul": {"lat": 41.0082, "lng": 28.9784, "country": "Turkey"},
    "Dubai": {"lat": 25.2048, "lng": 55.2708, "country": "UAE"},
    "London": {"lat": 51.5074, "lng": -0.1278, "country": "UK"},
    "Tokyo": {"lat": 35.6762, "lng": 139.6503, "country": "Japan"},
    "Sydney": {"lat": -33.8688, "lng": 151.2093, "country": "Australia"},
    "New York": {"lat": 40.7128, "lng": -74.0060, "country": "USA"},
}


def _get_project_root():
    """Get the project root directory."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Go up from src/config/manager.py to project root
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_config_path():
    """Get the absolute path to the config file."""
    return os.path.join(_get_project_root(), CONFIG_FILE)


def load_config():
    """Load configuration from file, creating default if not exists."""
    config_path = get_config_path()
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Merge with defaults for any missing keys
            merged = {**DEFAULT_CONFIG, **config}
            return merged
        else:
            save_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()


def save_config(config):
    """Save configuration to file."""
    config_path = get_config_path()
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


def get_all_cities():
    """Return all available cities (Indonesian + International)."""
    all_cities = {}
    all_cities.update(INDONESIAN_CITIES)
    all_cities.update(INTERNATIONAL_CITIES)
    return all_cities
