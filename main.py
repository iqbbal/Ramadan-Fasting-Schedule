"""
Ramadan Fasting Schedule - Windows System Tray App
===================================================
Entry point. Run this file to start the application.

Features:
  - System tray icon with crescent moon & countdown
  - Right-click menu showing all prayer times
  - Custom dark popup menu on left-click
  - IP-based auto location detection
  - Manual city selection settings
  - Desktop notifications for Imsak & Iftar
  - Aladhan API + KEMENAG calculation method
"""
import sys
import atexit

from src.app import (
    RamadhanTrayApp,
    kill_existing_instance,
    write_pid_file,
    cleanup_pid_file,
)


def main():
    """Main entry point."""
    print("=" * 50)
    print("🌙 Jadwal Puasa Ramadhan - System Tray App")
    print("=" * 50)
    print()

    # Kill any existing instance before starting
    kill_existing_instance()

    # Write our PID and register cleanup
    write_pid_file()
    atexit.register(cleanup_pid_file)

    app = RamadhanTrayApp()

    try:
        app.start()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted!")
        app.stop()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        app.stop()
        sys.exit(1)


if __name__ == "__main__":
    main()
