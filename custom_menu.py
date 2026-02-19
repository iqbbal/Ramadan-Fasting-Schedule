"""
Custom dark-themed popup menu for the Ramadan Fasting Schedule app.
Replaces the native Windows context menu with a styled Tkinter popup.

Fixed: Tkinter runs on its own dedicated thread. All Tk calls happen
on that thread to avoid Tcl_AsyncDelete threading errors.
"""
import tkinter as tk
import threading


class DarkPopupMenu:
    """
    A custom dark popup menu window using Tkinter.
    Provides full control over colors, fonts, and layout.
    All Tkinter operations run on the same thread to avoid Tcl errors.
    """

    # Color scheme
    BG_COLOR = "#1f1f1f"
    BG_HOVER = "#16213e"
    TEXT_COLOR = "#e0e0e0"
    TEXT_MUTED = "#8a8a9a"
    TEXT_ACCENT = "#ffd700"
    TEXT_GREEN = "#2ecc71"
    TEXT_BLUE = "#87ceeb"
    SEPARATOR_COLOR = "#2a2a4a"
    BORDER_COLOR = "#2a2a4a"

    def __init__(self):
        self.root = None
        self._items = []
        self._action_callbacks = {}

    def add_label(self, text, color=None, bold=False, icon=""):
        """Add a non-clickable label item."""
        self._items.append({
            "type": "label",
            "text": text,
            "color": color or self.TEXT_COLOR,
            "bold": bold,
        })

    def add_info(self, label, value, icon=""):
        """Add an info row with label and value."""
        self._items.append({
            "type": "info",
            "label": label,
            "value": value,
        })

    def add_separator(self):
        """Add a horizontal separator."""
        self._items.append({"type": "separator"})

    def add_action(self, text, callback, icon=""):
        """Add a clickable action button."""
        self._items.append({
            "type": "action",
            "text": text,
            "callback": callback,
        })

    def clear(self):
        """Remove all menu items."""
        self._items.clear()

    def show(self, x=None, y=None):
        """Show the popup menu. Creates a new Tk instance on a fresh thread."""
        thread = threading.Thread(
            target=self._run_popup, args=(x, y), daemon=True
        )
        thread.start()

    def _run_popup(self, x=None, y=None):
        """Create and run the popup window — everything on this thread."""
        try:
            root = tk.Tk()
            self.root = root

            # Remove window decorations
            root.overrideredirect(True)
            root.configure(
                bg=self.BG_COLOR,
                highlightthickness=1,
                highlightbackground=self.BORDER_COLOR,
            )
            root.attributes("-topmost", True)

            try:
                root.attributes("-alpha", 0.97)
            except Exception:
                pass

            # Main container
            container = tk.Frame(root, bg=self.BG_COLOR, padx=6, pady=6)
            container.pack(fill=tk.BOTH, expand=True)

            # Build menu items
            for item in self._items:
                self._build_item(container, item, root)

            # Calculate size and position
            root.update_idletasks()
            w = root.winfo_reqwidth()
            h = root.winfo_reqheight()

            if x is None or y is None:
                px = root.winfo_pointerx()
                py = root.winfo_pointery()
            else:
                px, py = x, y

            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()

            # Keep on screen
            if px + w > screen_w:
                px = screen_w - w - 10
            if py + h > screen_h:
                py = py - h - 10
            if py < 0:
                py = 10

            root.geometry(f"{w}x{h}+{px}+{py}")

            # Close on Escape or focus loss
            root.bind("<Escape>", lambda e: root.destroy())
            root.bind("<FocusOut>", lambda e: self._schedule_close(root))

            # Click anywhere outside closes the popup
            root.after(300, lambda: self._start_focus_check(root))

            root.focus_force()
            root.mainloop()

        except Exception as e:
            print(f"Menu error: {e}")
        finally:
            self.root = None

    def _build_item(self, container, item, root):
        """Build a single menu item widget."""
        item_type = item["type"]

        if item_type == "separator":
            sep = tk.Frame(container, bg=self.SEPARATOR_COLOR, height=1)
            sep.pack(fill=tk.X, pady=5, padx=4)

        elif item_type == "label":
            text = item["text"]
            color = item["color"]
            is_bold = item["bold"]
            weight = "bold" if is_bold else "normal"
            size = 11 if is_bold else 10

            lbl = tk.Label(
                container,
                text=text,
                bg=self.BG_COLOR,
                fg=color,
                font=("Segoe UI", size, weight),
                anchor="w",
                padx=8,
                pady=2,
            )
            lbl.pack(fill=tk.X)

        elif item_type == "info":
            row = tk.Frame(container, bg=self.BG_COLOR)
            row.pack(fill=tk.X, padx=8, pady=1)

            lbl = tk.Label(
                row,
                text=item["label"],
                bg=self.BG_COLOR,
                fg=self.TEXT_MUTED,
                font=("Segoe UI", 10),
                anchor="w",
                width=22,
            )
            lbl.pack(side=tk.LEFT)

            val = tk.Label(
                row,
                text=item["value"],
                bg=self.BG_COLOR,
                fg=self.TEXT_COLOR,
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            )
            val.pack(side=tk.LEFT)

        elif item_type == "action":
            callback = item["callback"]

            btn = tk.Label(
                container,
                text=item["text"],
                bg=self.BG_COLOR,
                fg=self.TEXT_COLOR,
                font=("Segoe UI", 10),
                anchor="w",
                padx=8,
                pady=4,
                cursor="hand2",
            )
            btn.pack(fill=tk.X)

            # Hover effects
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.BG_HOVER))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.BG_COLOR))

            # Click: close menu first, then run callback
            def on_click(e, cb=callback, r=root):
                r.destroy()
                if cb:
                    t = threading.Thread(target=cb, daemon=True)
                    t.start()

            btn.bind("<Button-1>", on_click)

    def _schedule_close(self, root):
        """Schedule a close check — only close if truly lost focus."""
        try:
            root.after(150, lambda: self._check_and_close(root))
        except Exception:
            pass

    def _check_and_close(self, root):
        """Close if the window no longer has focus."""
        try:
            if not root.focus_get():
                root.destroy()
        except Exception:
            pass

    def _start_focus_check(self, root):
        """Periodically check if the popup still has focus."""
        def check():
            try:
                if not root.focus_get():
                    root.destroy()
                else:
                    root.after(300, check)
            except Exception:
                pass
        check()


def build_dark_menu(app):
    """
    Build a dark popup menu with the app's current data.

    Args:
        app: RamadhanTrayApp instance

    Returns:
        DarkPopupMenu instance ready to show
    """
    from prayer_times_service import (
        PRAYER_LABELS, PRAYER_KEYS, get_time_remaining, format_countdown,
    )

    menu = DarkPopupMenu()

    # ─── Header ───
    if app.fasting_data:
        hijri = app.fasting_data.get("hijri_date", "")
        gregorian = app.fasting_data.get("gregorian_date", "")
        is_ramadan = app.fasting_data.get("is_ramadan", False)

        title = "RAMADHAN" if is_ramadan else "Jadwal Shalat"
        menu.add_label(f"🌙 {title}", color=DarkPopupMenu.TEXT_ACCENT, bold=True)
        menu.add_label(f"📅 {gregorian}  |  {hijri}", color=DarkPopupMenu.TEXT_BLUE)
    else:
        menu.add_label("🌙 Jadwal Puasa Ramadhan", color=DarkPopupMenu.TEXT_ACCENT, bold=True)

    # Location info
    if app.location_info:
        city = app.location_info.get("city", "Unknown")
        country = app.location_info.get("country", "")
        loc = f"📍 {city}, {country}" if country else f"📍 {city}"
        menu.add_label(loc, color=DarkPopupMenu.TEXT_MUTED)

    menu.add_separator()

    # ─── Fasting Times ───
    if app.fasting_data:
        imsak = app.fasting_data.get("imsak", "--:--")
        maghrib = app.fasting_data.get("maghrib", "--:--")

        imsak_h, imsak_m, imsak_s, imsak_past = get_time_remaining(imsak)
        maghrib_h, maghrib_m, maghrib_s, maghrib_past = get_time_remaining(maghrib)

        imsak_cd = ""
        if not imsak_past:
            imsak_cd = f"  ({format_countdown(imsak_h, imsak_m, imsak_s)} lagi)"

        maghrib_cd = ""
        if not maghrib_past:
            maghrib_cd = f"  ({format_countdown(maghrib_h, maghrib_m, maghrib_s)} lagi)"

        menu.add_label(f"🍽️  Imsak (Sahur) : {imsak}{imsak_cd}", color=DarkPopupMenu.TEXT_COLOR)
        menu.add_label(f"🌅  Berbuka (Maghrib) : {maghrib}{maghrib_cd}", color=DarkPopupMenu.TEXT_GREEN)

        menu.add_separator()

        # ─── All Prayer Times ───
        menu.add_label("🕌 Jadwal Shalat Lengkap", color=DarkPopupMenu.TEXT_BLUE, bold=True)

        all_timings = app.fasting_data.get("all_timings", {})
        for key in PRAYER_KEYS:
            if key in all_timings:
                label = PRAYER_LABELS.get(key, key)
                time_str = all_timings[key]
                menu.add_info(f"{label}", time_str)
    else:
        menu.add_label("⏳ Memuat jadwal...", color=DarkPopupMenu.TEXT_MUTED)

    menu.add_separator()

    # ─── Actions ───
    menu.add_action("🔄  Refresh", lambda: app._on_refresh())
    # menu.add_action("⚙️  Pengaturan", lambda: app._on_settings())
    menu.add_separator()
    menu.add_action("❌  Keluar", lambda: app._on_quit())

    return menu
