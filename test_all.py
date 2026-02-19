"""Quick integration test for all modules."""
import sys
sys.path.insert(0, r'l:\ramadhan-windows-taskbar')

# Test all imports
from config_manager import load_config, save_config, CALCULATION_METHODS, INDONESIAN_CITIES, get_all_cities
print('1. config_manager      OK')

from location_service import get_current_location, get_location_by_ip, get_location_by_city
print('2. location_service    OK')

from prayer_times_service import get_fasting_times, get_time_remaining, format_countdown, PRAYER_LABELS, PRAYER_KEYS
print('3. prayer_times_service OK')

from notification_service import NotificationScheduler, show_notification
print('4. notification_service OK')

from icon_generator import create_moon_icon, create_countdown_icon, create_text_icon
print('5. icon_generator      OK')

# Test icon generation
icon = create_moon_icon(64)
print(f'   Moon icon created: {icon.size}')

cd_icon = create_countdown_icon(3, 45)
print(f'   Countdown icon created: {cd_icon.size}')

# Test config
config = load_config()
loc_mode = config["location_mode"]
method = config["calculation_method"]
print(f'6. Config loaded: mode={loc_mode}, method={method}')

# Test city database
cities = get_all_cities()
print(f'7. Cities available: {len(cities)} total')

# Test countdown formatting
print(f'8. format_countdown(3, 45, 12) = {format_countdown(3, 45, 12)}')
print(f'   format_countdown(0, 5, 30) = {format_countdown(0, 5, 30)}')

# Test city lookup
loc = get_location_by_city("Jakarta")
print(f'9. Jakarta coords: lat={loc["latitude"]}, lng={loc["longitude"]}')

print()
print('ALL TESTS PASSED!')
