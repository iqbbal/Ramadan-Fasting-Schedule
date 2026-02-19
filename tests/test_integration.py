"""Quick integration test for all modules."""
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test all imports
from src.config.manager import load_config, save_config, CALCULATION_METHODS, INDONESIAN_CITIES, get_all_cities
print('1. src.config.manager        OK')

from src.services.location import get_current_location, get_location_by_ip, get_location_by_city
print('2. src.services.location     OK')

from src.services.prayer_times import get_fasting_times, get_time_remaining, format_countdown, PRAYER_LABELS, PRAYER_KEYS
print('3. src.services.prayer_times OK')

from src.services.notification import NotificationScheduler, show_notification
print('4. src.services.notification OK')

from src.ui.icon import create_moon_icon, create_countdown_icon, create_text_icon
print('5. src.ui.icon               OK')

from src.ui.menu import DarkPopupMenu, build_dark_menu
print('6. src.ui.menu               OK')

# Test icon generation
icon = create_moon_icon(64)
print(f'   Moon icon created: {icon.size}')

cd_icon = create_countdown_icon(3, 45)
print(f'   Countdown icon created: {cd_icon.size}')

# Test config
config = load_config()
loc_mode = config["location_mode"]
method = config["calculation_method"]
print(f'7. Config loaded: mode={loc_mode}, method={method}')

# Test city database
cities = get_all_cities()
print(f'8. Cities available: {len(cities)} total')

# Test countdown formatting
print(f'9. format_countdown(3, 45, 12) = {format_countdown(3, 45, 12)}')
print(f'   format_countdown(0, 5, 30) = {format_countdown(0, 5, 30)}')

# Test city lookup
loc = get_location_by_city("Jakarta")
print(f'10. Jakarta coords: lat={loc["latitude"]}, lng={loc["longitude"]}')

print()
print('ALL TESTS PASSED! ✅')
