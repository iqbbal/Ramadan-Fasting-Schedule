"""
Settings window (GUI) for the Ramadan Fasting Schedule app.
Built with Tkinter for a lightweight, native-feeling UI.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading

from config_manager import (
    load_config,
    save_config,
    CALCULATION_METHODS,
    INDONESIAN_CITIES,
    INTERNATIONAL_CITIES,
    get_all_cities,
)
from location_service import get_location_by_ip


class SettingsWindow:
    """Settings window for configuring location and preferences."""

    def __init__(self, on_save_callback=None):
        self.on_save_callback = on_save_callback
        self.window = None

    def show(self):
        """Show the settings window. If already open, bring to front."""
        if self.window is not None:
            try:
                self.window.lift()
                self.window.focus_force()
                return
            except tk.TclError:
                self.window = None

        self.config = load_config()
        self._create_window()

    def _create_window(self):
        """Create the settings window."""
        self.window = tk.Tk()
        self.window.title("⚙️ Pengaturan - Jadwal Puasa Ramadhan")
        self.window.geometry("520x650")
        self.window.resizable(False, False)
        self.window.configure(bg="#1a1a2e")

        # Try to set icon
        try:
            from icon_generator import create_moon_icon
            import tempfile, os
            icon = create_moon_icon(32)
            icon_path = os.path.join(tempfile.gettempdir(), "ramadan_settings_icon.ico")
            icon.save(icon_path, format="ICO")
            self.window.iconbitmap(icon_path)
        except Exception:
            pass

        # Style configuration
        style = ttk.Style()
        style.theme_use("clam")

        # Custom styles
        style.configure("Dark.TFrame", background="#1a1a2e")
        style.configure("Dark.TLabel", background="#1a1a2e", foreground="#e0e0e0",
                        font=("Segoe UI", 10))
        style.configure("Header.TLabel", background="#1a1a2e", foreground="#ffd700",
                        font=("Segoe UI", 14, "bold"))
        style.configure("SubHeader.TLabel", background="#1a1a2e", foreground="#87ceeb",
                        font=("Segoe UI", 11, "bold"))
        style.configure("Dark.TRadiobutton", background="#1a1a2e", foreground="#e0e0e0",
                        font=("Segoe UI", 10))
        style.configure("Dark.TCheckbutton", background="#1a1a2e", foreground="#e0e0e0",
                        font=("Segoe UI", 10))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

        # Main container
        main_frame = ttk.Frame(self.window, style="Dark.TFrame", padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ─── Header ───
        ttk.Label(
            main_frame, text="🌙 Pengaturan Jadwal Puasa",
            style="Header.TLabel"
        ).pack(anchor=tk.W, pady=(0, 15))

        # ─── Location Section ───
        ttk.Label(main_frame, text="📍 Lokasi", style="SubHeader.TLabel").pack(
            anchor=tk.W, pady=(0, 8)
        )

        self.location_mode = tk.StringVar(value=self.config.get("location_mode", "auto"))

        loc_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        loc_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Radiobutton(
            loc_frame, text="🌐 Otomatis (Geolokasi IP)",
            variable=self.location_mode, value="auto",
            style="Dark.TRadiobutton",
            command=self._on_mode_change,
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            loc_frame, text="📝 Pilih Kota Manual",
            variable=self.location_mode, value="manual",
            style="Dark.TRadiobutton",
            command=self._on_mode_change,
        ).pack(anchor=tk.W, pady=(3, 0))

        # Auto-detect info
        self.auto_info_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        self.auto_info_frame.pack(fill=tk.X, pady=(5, 5))

        self.auto_info_label = ttk.Label(
            self.auto_info_frame,
            text="Mendeteksi lokasi...",
            style="Dark.TLabel",
        )
        self.auto_info_label.pack(anchor=tk.W)

        detect_btn = ttk.Button(
            self.auto_info_frame,
            text="🔄 Deteksi Ulang",
            command=self._detect_location,
            style="Accent.TButton",
        )
        detect_btn.pack(anchor=tk.W, pady=(5, 0))

        # City selection (for manual mode)
        self.city_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        self.city_frame.pack(fill=tk.X, pady=(5, 5))

        ttk.Label(self.city_frame, text="Kota Indonesia:", style="Dark.TLabel").pack(
            anchor=tk.W
        )

        self.city_var = tk.StringVar(value=self.config.get("city", ""))

        # Indonesian cities combobox
        indo_cities = sorted(INDONESIAN_CITIES.keys())
        self.indo_combo = ttk.Combobox(
            self.city_frame,
            textvariable=self.city_var,
            values=indo_cities,
            state="readonly",
            width=40,
            font=("Segoe UI", 10),
        )
        self.indo_combo.pack(anchor=tk.W, pady=(3, 8))

        ttk.Label(self.city_frame, text="Kota Internasional:", style="Dark.TLabel").pack(
            anchor=tk.W
        )

        self.intl_city_var = tk.StringVar()
        intl_cities = sorted(INTERNATIONAL_CITIES.keys())
        self.intl_combo = ttk.Combobox(
            self.city_frame,
            textvariable=self.intl_city_var,
            values=intl_cities,
            state="readonly",
            width=40,
            font=("Segoe UI", 10),
        )
        self.intl_combo.pack(anchor=tk.W, pady=(3, 5))

        # Bind combo selections
        self.indo_combo.bind("<<ComboboxSelected>>", self._on_indo_city_selected)
        self.intl_combo.bind("<<ComboboxSelected>>", self._on_intl_city_selected)

        # Set initial city value
        if self.config.get("city") in INDONESIAN_CITIES:
            self.city_var.set(self.config.get("city"))
        elif self.config.get("city") in INTERNATIONAL_CITIES:
            self.intl_city_var.set(self.config.get("city"))

        # ─── Separator ───
        ttk.Separator(main_frame).pack(fill=tk.X, pady=12)

        # ─── Calculation Method ───
        ttk.Label(
            main_frame, text="🕌 Metode Perhitungan", style="SubHeader.TLabel"
        ).pack(anchor=tk.W, pady=(0, 8))

        self.method_var = tk.IntVar(value=self.config.get("calculation_method", 20))
        method_names = [f"{k}: {v}" for k, v in sorted(CALCULATION_METHODS.items())]

        self.method_combo = ttk.Combobox(
            main_frame,
            values=method_names,
            state="readonly",
            width=50,
            font=("Segoe UI", 9),
        )
        # Set current value
        current_method = self.config.get("calculation_method", 20)
        if current_method in CALCULATION_METHODS:
            idx = list(sorted(CALCULATION_METHODS.keys())).index(current_method)
            self.method_combo.current(idx)
        self.method_combo.pack(anchor=tk.W, pady=(0, 5))

        # ─── Separator ───
        ttk.Separator(main_frame).pack(fill=tk.X, pady=12)

        # ─── Notifications ───
        ttk.Label(
            main_frame, text="🔔 Notifikasi", style="SubHeader.TLabel"
        ).pack(anchor=tk.W, pady=(0, 8))

        notif_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        notif_frame.pack(fill=tk.X)

        # Minutes before Imsak
        imsak_frame = ttk.Frame(notif_frame, style="Dark.TFrame")
        imsak_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(imsak_frame, text="Notifikasi sebelum Imsak (menit):",
                  style="Dark.TLabel").pack(side=tk.LEFT)

        self.imsak_minutes = tk.IntVar(
            value=self.config.get("notification_before_imsak_minutes", 10)
        )
        imsak_spin = ttk.Spinbox(
            imsak_frame, from_=1, to=60,
            textvariable=self.imsak_minutes, width=5,
            font=("Segoe UI", 10),
        )
        imsak_spin.pack(side=tk.LEFT, padx=(8, 0))

        # Iftar notification
        self.iftar_notif = tk.BooleanVar(
            value=self.config.get("notification_at_iftar", True)
        )
        ttk.Checkbutton(
            notif_frame, text="Notifikasi saat waktu berbuka (Maghrib)",
            variable=self.iftar_notif,
            style="Dark.TCheckbutton",
        ).pack(anchor=tk.W, pady=(3, 0))

        # ─── Buttons ───
        btn_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        save_btn = tk.Button(
            btn_frame,
            text="💾 Simpan",
            command=self._save,
            bg="#2ecc71",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))

        cancel_btn = tk.Button(
            btn_frame,
            text="❌ Batal",
            command=self._close,
            bg="#e74c3c",
            fg="white",
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
        )
        cancel_btn.pack(side=tk.RIGHT)

        # Initial state
        self._on_mode_change()

        # Auto-detect location on open
        if self.location_mode.get() == "auto":
            self._detect_location()

        self.window.protocol("WM_DELETE_WINDOW", self._close)
        self.window.mainloop()

    def _on_mode_change(self):
        """Handle location mode change."""
        mode = self.location_mode.get()
        if mode == "auto":
            for child in self.auto_info_frame.winfo_children():
                child.pack_configure()
            # Show auto info, hide city selection
            self.auto_info_frame.pack(fill=tk.X, pady=(5, 5))
            self.city_frame.pack_forget()
        else:
            # Hide auto info, show city selection
            self.auto_info_frame.pack_forget()
            self.city_frame.pack(fill=tk.X, pady=(5, 5))

    def _detect_location(self):
        """Detect location via IP in a background thread."""
        self.auto_info_label.config(text="🔄 Mendeteksi lokasi...")

        def detect():
            loc = get_location_by_ip()
            if loc:
                text = f"✅ Terdeteksi: {loc['city']}, {loc['country']}\n" \
                       f"   Koordinat: {loc['latitude']:.4f}, {loc['longitude']:.4f}"
            else:
                text = "❌ Gagal mendeteksi lokasi. Periksa koneksi internet."

            try:
                self.auto_info_label.config(text=text)
            except tk.TclError:
                pass  # Window was closed

        thread = threading.Thread(target=detect, daemon=True)
        thread.start()

    def _on_indo_city_selected(self, event):
        """When Indonesian city is selected, clear international."""
        self.intl_city_var.set("")

    def _on_intl_city_selected(self, event):
        """When international city is selected, clear Indonesian."""
        self.city_var.set("")

    def _save(self):
        """Save settings and close."""
        mode = self.location_mode.get()

        # Get selected city
        city = self.city_var.get() or self.intl_city_var.get()
        all_cities = get_all_cities()

        # Get calculation method
        method_str = self.method_combo.get()
        try:
            method_id = int(method_str.split(":")[0])
        except (ValueError, IndexError):
            method_id = 20

        # Build config
        new_config = {
            "location_mode": mode,
            "city": city if mode == "manual" else "",
            "country": all_cities.get(city, {}).get("country", "") if city else "",
            "latitude": all_cities.get(city, {}).get("lat") if city and mode == "manual" else None,
            "longitude": all_cities.get(city, {}).get("lng") if city and mode == "manual" else None,
            "calculation_method": method_id,
            "notification_before_imsak_minutes": self.imsak_minutes.get(),
            "notification_at_iftar": self.iftar_notif.get(),
        }

        if mode == "manual" and not city:
            messagebox.showwarning(
                "Peringatan",
                "Silakan pilih kota terlebih dahulu.",
                parent=self.window,
            )
            return

        if save_config(new_config):
            messagebox.showinfo(
                "Berhasil",
                "Pengaturan berhasil disimpan! ✅\n"
                "Jadwal akan diperbarui.",
                parent=self.window,
            )
            if self.on_save_callback:
                self.on_save_callback()
            self._close()
        else:
            messagebox.showerror(
                "Error",
                "Gagal menyimpan pengaturan.",
                parent=self.window,
            )

    def _close(self):
        """Close the settings window."""
        if self.window:
            self.window.destroy()
            self.window = None
