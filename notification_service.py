"""
Notification service for the Ramadan Fasting Schedule app.
Handles Windows desktop notifications for prayer times.
"""
import threading
from datetime import datetime


def show_notification(title, message, duration=10):
    """
    Show a Windows desktop notification.

    Args:
        title: Notification title
        message: Notification body text
        duration: How long to show (seconds)
    """
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        # Run in a thread to avoid blocking
        thread = threading.Thread(
            target=toaster.show_toast,
            args=(title, message),
            kwargs={"duration": duration, "threaded": False},
        )
        thread.daemon = True
        thread.start()
    except ImportError:
        # Fallback: just print to console
        print(f"[NOTIFICATION] {title}: {message}")
    except Exception as e:
        print(f"Notification error: {e}")


def notify_imsak_approaching(minutes_left, imsak_time):
    """Send notification that Imsak is approaching."""
    show_notification(
        "🌙 Imsak Segera!",
        f"Waktu Imsak ({imsak_time}) dalam {minutes_left} menit lagi.\n"
        f"Segera selesaikan sahur Anda.",
        duration=15,
    )


def notify_iftar_time(maghrib_time):
    """Send notification that it's Iftar (breaking fast) time."""
    show_notification(
        "🌅 Waktunya Berbuka!",
        f"Waktu Maghrib telah tiba ({maghrib_time}).\n"
        f"Allahumma laka sumtu wa 'ala rizqika aftartu.",
        duration=15,
    )


def notify_fajr_time(fajr_time):
    """Send notification for Fajr prayer."""
    show_notification(
        "🕌 Waktu Subuh",
        f"Waktu shalat Subuh telah tiba ({fajr_time}).",
        duration=10,
    )


class NotificationScheduler:
    """
    Manages scheduling of notifications for prayer times.
    Keeps track of which notifications have been sent today.
    """

    def __init__(self):
        self.sent_today = set()
        self.last_reset_date = datetime.now().date()

    def reset_if_new_day(self):
        """Reset sent notifications if it's a new day."""
        today = datetime.now().date()
        if today != self.last_reset_date:
            self.sent_today.clear()
            self.last_reset_date = today

    def check_and_notify(self, fasting_data, config):
        """
        Check if any notifications should be sent based on current time.

        Args:
            fasting_data: dict with prayer times
            config: app configuration
        """
        self.reset_if_new_day()
        now = datetime.now()

        if fasting_data is None:
            return

        # Check Imsak approaching notification
        imsak_str = fasting_data.get("imsak", "")
        if imsak_str and "imsak_approaching" not in self.sent_today:
            try:
                parts = imsak_str.split(":")
                imsak_hour, imsak_min = int(parts[0]), int(parts[1])
                imsak_time = now.replace(hour=imsak_hour, minute=imsak_min, second=0)
                minutes_before = config.get("notification_before_imsak_minutes", 10)
                diff = (imsak_time - now).total_seconds() / 60

                if 0 < diff <= minutes_before:
                    notify_imsak_approaching(int(diff), imsak_str)
                    self.sent_today.add("imsak_approaching")
            except (ValueError, IndexError):
                pass

        # Check Maghrib/Iftar notification
        maghrib_str = fasting_data.get("maghrib", "")
        if maghrib_str and "iftar" not in self.sent_today:
            try:
                parts = maghrib_str.split(":")
                maghrib_hour, maghrib_min = int(parts[0]), int(parts[1])
                maghrib_time = now.replace(hour=maghrib_hour, minute=maghrib_min, second=0)
                diff = (maghrib_time - now).total_seconds() / 60

                if -2 <= diff <= 0:  # Within 2 minutes after maghrib
                    if config.get("notification_at_iftar", True):
                        notify_iftar_time(maghrib_str)
                        self.sent_today.add("iftar")
            except (ValueError, IndexError):
                pass
