"""
Ramadan Fasting Schedule - Main Application Module.
Contains the RamadhanTrayApp class and single-instance management.
"""
import sys
import os
import time
import threading
import atexit
from datetime import datetime, date

import pystray
from pystray import MenuItem as Item, Menu

from src.config.manager import load_config, save_config
from src.services.location import get_current_location
from src.services.prayer_times import (
    get_fasting_times,
    get_time_remaining,
    format_countdown,
    PRAYER_LABELS,
    PRAYER_KEYS,
)
from src.ui.icon import create_moon_icon, create_countdown_icon, create_text_icon
from src.services.notification import NotificationScheduler
from src.ui.menu import build_dark_menu


# ─── Single Instance Management ───
LOCK_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".ramadhan_tray.pid")


def kill_existing_instance():
    """Check for and kill any existing instance of this app."""
    if not os.path.exists(LOCK_FILE):
        return

    try:
        with open(LOCK_FILE, "r") as f:
            old_pid = int(f.read().strip())

        # Don't kill ourselves
        if old_pid == os.getpid():
            return

        # Check if process is still running and kill it
        import psutil
        try:
            proc = psutil.Process(old_pid)
            if "python" in proc.name().lower():
                print(f"⚠️ Instance lama ditemukan (PID {old_pid}), menutup...")
                proc.terminate()
                proc.wait(timeout=5)
                print(f"✅ Instance lama (PID {old_pid}) berhasil ditutup")
        except psutil.NoSuchProcess:
            pass  # Already dead
        except psutil.TimeoutExpired:
            proc.kill()  # Force kill
        except Exception as e:
            print(f"⚠️ Gagal menutup instance lama: {e}")
    except (ValueError, FileNotFoundError, ImportError):
        # psutil not installed — fallback to taskkill
        try:
            with open(LOCK_FILE, "r") as f:
                old_pid = int(f.read().strip())
            if old_pid != os.getpid():
                os.system(f'taskkill /PID {old_pid} /F >nul 2>&1')
                print(f"✅ Instance lama (PID {old_pid}) ditutup via taskkill")
        except Exception:
            pass

    # Clean up stale lock file
    try:
        os.remove(LOCK_FILE)
    except OSError:
        pass


def write_pid_file():
    """Write current PID to lock file."""
    try:
        with open(LOCK_FILE, "w") as f:
            f.write(str(os.getpid()))
    except OSError as e:
        print(f"⚠️ Gagal menulis PID file: {e}")


def cleanup_pid_file():
    """Remove PID lock file on exit."""
    try:
        if os.path.exists(LOCK_FILE):
            with open(LOCK_FILE, "r") as f:
                pid = int(f.read().strip())
            # Only remove if it's our PID
            if pid == os.getpid():
                os.remove(LOCK_FILE)
    except Exception:
        pass


class RamadhanTrayApp:
    """
    Main application class for the Ramadhan Fasting Schedule system tray app.
    """

    def __init__(self):
        self.icon = None
        self.running = False
        self.fasting_data = None
        self.location_info = None
        self.last_fetch_date = None
        self.notification_scheduler = NotificationScheduler()
        self.config = load_config()

        # Update interval (seconds)
        self.update_interval = 30  # Update tooltip every 30 seconds
        self.fetch_interval = 3600  # Re-fetch prayer times every hour

    def start(self):
        """Start the system tray application."""
        print("🌙 Memulai Jadwal Puasa Ramadhan...")

        # Create initial icon
        icon_image = create_moon_icon(64)

        # Create system tray icon with full native menu
        self.icon = pystray.Icon(
            name="RamadhanSchedule",
            icon=icon_image,
            title="Jadwal Puasa Ramadhan\nMemuat...",
            menu=self._build_native_menu(),
        )

        self.running = True

        # Start background update thread
        update_thread = threading.Thread(target=self._update_loop, daemon=True)
        update_thread.start()

        # Run the system tray icon (this blocks)
        print("✅ Aplikasi berjalan di system tray")
        self.icon.run()

    def stop(self):
        """Stop the application."""
        self.running = False
        if self.icon:
            self.icon.stop()
        print("👋 Aplikasi ditutup")

    def _build_native_menu(self):
        """Build the native right-click context menu with full jadwal data."""
        menu_items = []

        # Hidden default item: left-click/double-click opens dark popup
        menu_items.append(
            Item("Buka Jadwal", self._on_left_click, default=True, visible=False)
        )

        # ─── Header ───
        if self.fasting_data:
            hijri = self.fasting_data.get("hijri_date", "")
            gregorian = self.fasting_data.get("gregorian_date", "")
            is_ramadan = self.fasting_data.get("is_ramadan", False)

            header = f"🌙 {'RAMADHAN' if is_ramadan else 'Jadwal Shalat'}"
            menu_items.append(Item(header, None, enabled=False))
            menu_items.append(Item(f"📅 {gregorian} | {hijri}", None, enabled=False))
        else:
            menu_items.append(Item("🌙 Jadwal Puasa Ramadhan", None, enabled=False))

        # Location info
        if self.location_info:
            city = self.location_info.get("city", "Unknown")
            country = self.location_info.get("country", "")
            loc = f"📍 {city}, {country}" if country else f"📍 {city}"
            menu_items.append(Item(loc, None, enabled=False))

        menu_items.append(Menu.SEPARATOR)

        # ─── Fasting Times ───
        if self.fasting_data:
            imsak = self.fasting_data.get("imsak", "--:--")
            maghrib = self.fasting_data.get("maghrib", "--:--")

            imsak_h, imsak_m, imsak_s, imsak_past = get_time_remaining(imsak)
            maghrib_h, maghrib_m, maghrib_s, maghrib_past = get_time_remaining(maghrib)

            imsak_cd = ""
            if not imsak_past:
                imsak_cd = f" ({format_countdown(imsak_h, imsak_m, imsak_s)} lagi)"
            maghrib_cd = ""
            if not maghrib_past:
                maghrib_cd = f" ({format_countdown(maghrib_h, maghrib_m, maghrib_s)} lagi)"

            menu_items.append(Item(f"🍽️ Imsak (Sahur) : {imsak}{imsak_cd}", None, enabled=False))
            menu_items.append(Item(f"🌅 Berbuka (Maghrib) : {maghrib}{maghrib_cd}", None, enabled=False))

            menu_items.append(Menu.SEPARATOR)

            # ─── All Prayer Times ───
            menu_items.append(Item("🕌 Jadwal Shalat Lengkap", None, enabled=False))

            all_timings = self.fasting_data.get("all_timings", {})
            for key in PRAYER_KEYS:
                if key in all_timings:
                    label = PRAYER_LABELS.get(key, key)
                    time_str = all_timings[key]
                    menu_items.append(Item(f"{label} : {time_str}", None, enabled=False))
        else:
            menu_items.append(Item("⏳ Memuat jadwal...", None, enabled=False))

        menu_items.append(Menu.SEPARATOR)

        # ─── Actions ───
        menu_items.append(Item("🔄 Refresh", self._on_refresh))
        menu_items.append(Item("⚙️ Pengaturan", self._on_settings))
        menu_items.append(Menu.SEPARATOR)
        menu_items.append(Item("❌ Keluar", self._on_quit))

        return Menu(*menu_items)

    def _on_left_click(self, icon=None, item=None):
        """Handle left-click/double-click — show custom dark popup menu."""
        self._show_dark_menu()

    def _show_dark_menu(self):
        """Show the custom dark popup menu."""
        try:
            menu = build_dark_menu(self)
            menu.show()
        except Exception as e:
            print(f"Error showing dark menu: {e}")

    def _update_tooltip(self):
        """Update the system tray tooltip text."""
        if not self.fasting_data or not self.icon:
            return

        imsak = self.fasting_data.get("imsak", "--:--")
        maghrib = self.fasting_data.get("maghrib", "--:--")
        city = self.location_info.get("city", "?") if self.location_info else "?"
        hijri = self.fasting_data.get("hijri_date", "")
        gregorian = self.fasting_data.get("gregorian_date", "")

        # Determine what to show in countdown
        imsak_h, imsak_m, imsak_s, imsak_past = get_time_remaining(imsak)
        maghrib_h, maghrib_m, maghrib_s, maghrib_past = get_time_remaining(maghrib)

        lines = [f"🌙 Jadwal Puasa - {city}"]
        lines.append(f"📅 {gregorian} | {hijri}")
        lines.append(f"🍽️ Imsak: {imsak}")
        lines.append(f"🌅 Berbuka: {maghrib}")

        if not imsak_past:
            cd = format_countdown(imsak_h, imsak_m, imsak_s)
            lines.append(f"⏰ Imsak dalam {cd}")
        elif not maghrib_past:
            cd = format_countdown(maghrib_h, maghrib_m, maghrib_s)
            lines.append(f"⏰ Berbuka dalam {cd}")
        else:
            lines.append("✅ Waktu berbuka telah lewat")

        # Windows tooltip max 128 chars
        tooltip = "\n".join(lines)
        if len(tooltip) > 127:
            tooltip = tooltip[:124] + "..."

        try:
            self.icon.title = tooltip
        except Exception:
            pass

    def _update_icon(self):
        """Update the system tray icon based on current state."""
        if not self.fasting_data or not self.icon:
            return

        try:
            imsak = self.fasting_data.get("imsak", "--:--")
            maghrib = self.fasting_data.get("maghrib", "--:--")

            imsak_h, imsak_m, _, imsak_past = get_time_remaining(imsak)
            maghrib_h, maghrib_m, _, maghrib_past = get_time_remaining(maghrib)

            if not imsak_past:
                new_icon = create_countdown_icon(imsak_h, imsak_m)
            elif not maghrib_past:
                new_icon = create_countdown_icon(maghrib_h, maghrib_m)
            else:
                new_icon = create_moon_icon(64)

            self.icon.icon = new_icon
        except Exception as e:
            print(f"Error updating icon: {e}")

    def _fetch_data(self):
        """Fetch prayer times and location data."""
        try:
            print("📡 Mengambil data lokasi dan jadwal shalat...")

            self.location_info = get_current_location()
            lat = self.location_info["latitude"]
            lng = self.location_info["longitude"]
            city = self.location_info.get("city", "Unknown")

            print(f"📍 Lokasi: {city} ({lat:.4f}, {lng:.4f})")

            self.config = load_config()
            method = self.config.get("calculation_method", 20)

            self.fasting_data = get_fasting_times(lat, lng, method=method)

            if self.fasting_data:
                imsak = self.fasting_data.get("imsak", "--:--")
                maghrib = self.fasting_data.get("maghrib", "--:--")
                hijri = self.fasting_data.get("hijri_date", "")
                print(f"✅ Jadwal berhasil dimuat!")
                print(f"   📅 {hijri}")
                print(f"   🍽️ Imsak: {imsak}")
                print(f"   🌅 Berbuka: {maghrib}")
            else:
                print("❌ Gagal mengambil jadwal shalat")

            self.last_fetch_date = date.today()

        except Exception as e:
            print(f"❌ Error fetching data: {e}")

    def _update_loop(self):
        """Background loop to update data and UI."""
        # Initial fetch
        self._fetch_data()

        while self.running:
            try:
                # Refresh data if new day
                today = date.today()
                if self.last_fetch_date != today:
                    print("🌅 Hari baru - memperbarui jadwal...")
                    self._fetch_data()

                # Update tooltip and icon
                self._update_tooltip()
                self._update_icon()

                # Rebuild native menu with fresh data
                if self.icon:
                    self.icon.menu = self._build_native_menu()

                # Check notifications
                if self.fasting_data:
                    self.notification_scheduler.check_and_notify(
                        self.fasting_data, self.config
                    )

                time.sleep(self.update_interval)

            except Exception as e:
                print(f"Update loop error: {e}")
                time.sleep(5)

    def _on_refresh(self, icon=None, item=None):
        """Handle refresh action from menu."""
        print("🔄 Refresh...")
        thread = threading.Thread(target=self._fetch_data, daemon=True)
        thread.start()

    def _on_settings(self, icon=None, item=None):
        """Handle settings action from menu."""
        from src.ui.settings import SettingsWindow

        def on_save():
            """Callback when settings are saved."""
            self.config = load_config()
            thread = threading.Thread(target=self._fetch_data, daemon=True)
            thread.start()

        settings = SettingsWindow(on_save_callback=on_save)
        thread = threading.Thread(target=settings.show, daemon=True)
        thread.start()

    def _on_quit(self, icon=None, item=None):
        """Handle quit action from menu."""
        self.stop()
