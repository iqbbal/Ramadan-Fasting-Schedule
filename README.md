# 🌙 Ramadan Fasting Schedule — Windows Taskbar App

A Windows system tray application that displays the Ramadan fasting schedule in real-time based on your location.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Windows](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

<p align="center">
  <img src="images/ramadan_tray_active.png" alt="Tray Active" width="350"/>
  &nbsp;&nbsp;
  <img src="images/ramadan_tray_idle.png" alt="Tray Idle" width="350"/>
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🌙 **System Tray Icon** | Crescent moon icon with dynamic countdown |
| 📋 **Dark Menu** | Left-click → modern dark-themed popup menu |
| 📋 **Native Menu** | Right-click → native Windows menu with full schedule |
| 📍 **Auto Location** | Automatic location detection via IP geolocation |
| 🏙️ **City Selection** | 20+ Indonesian cities & 10 international cities |
| 🔔 **Notifications** | Desktop notifications for Imsak & Iftar |
| ⏰ **Countdown** | Countdown timer to next Imsak / Iftar |
| 🕌 **Full Schedule** | 7 prayer times (Imsak, Fajr, Sunrise, Dhuhr, Asr, Maghrib, Isha) |
| 🔄 **Auto Refresh** | Automatic update every 30 seconds |
| 🔒 **Single Instance** | Only 1 instance runs at a time, automatically closes the old one |

---

## 📁 Project Structure

```
ramadhan-windows-taskbar/
├── main.py                          # Entry point
├── config.json                      # User configuration
├── requirements.txt                 # Python dependencies
├── README.md
├── .gitignore
│
├── src/                             # Source code
│   ├── __init__.py
│   ├── app.py                       # RamadhanTrayApp class & single instance
│   │
│   ├── config/                      # Configuration
│   │   ├── __init__.py
│   │   └── manager.py              # Config load/save, city database
│   │
│   ├── services/                    # Business logic
│   │   ├── __init__.py
│   │   ├── location.py             # IP geolocation & city lookup
│   │   ├── prayer_times.py         # Aladhan API integration
│   │   └── notification.py         # Desktop notifications
│   │
│   └── ui/                          # User interface
│       ├── __init__.py
│       ├── icon.py                  # Dynamic tray icon generator
│       ├── menu.py                  # Custom dark popup menu
│       └── settings.py             # Settings window (Tkinter)
│
└── tests/                           # Test suite
    ├── __init__.py
    └── test_integration.py          # Integration tests
```

---

## 🚀 Installation & Running

### Prerequisites

- **Python 3.10+**
- **Windows 10/11**

### Setup

```bash
# Clone the repository
git clone https://github.com/iqbbal/Ramadan-Fasting-Schedule.git
cd Ramadan-Fasting-Schedule

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running

```bash
python main.py
```

The app will appear as a 🌙 icon in the system tray (bottom-right corner of the taskbar).

---

## 🖱️ Usage

| Action | Function |
|--------|----------|
| **Hover** over icon | View tooltip with schedule & countdown |
| **Left-click** icon | Open dark popup menu |
| **Right-click** icon | Open native menu with full schedule |

---

## ⚙️ Configuration

Settings are stored in `config.json`:

```json
{
    "location_mode": "auto",
    "city": "",
    "calculation_method": 20,
    "notification_before_imsak_minutes": 10,
    "notification_at_iftar": true
}
```

| Parameter | Description |
|-----------|-------------|
| `location_mode` | `"auto"` (IP-based) or `"manual"` (select city) |
| `calculation_method` | `20` = Ministry of Religious Affairs of Indonesia (KEMENAG) |
| `notification_before_imsak_minutes` | Notify N minutes before Imsak |
| `notification_at_iftar` | Notify when it's time to break the fast |

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `pystray` | System tray icon |
| `Pillow` | Dynamic icon generation |
| `requests` | HTTP API calls |
| `win10toast` | Desktop notifications |
| `psutil` | Single-instance management |
| `schedule` | Task scheduling |

---

## 🕌 API

Uses the [Aladhan Prayer Times API](https://aladhan.com/prayer-times-api) (free, no API key required).

Default calculation method: **Ministry of Religious Affairs of Indonesia (KEMENAG)**.

---

## 🏗️ Development

### Adding a New City

Edit `src/config/manager.py`, add to `INDONESIAN_CITIES` or `INTERNATIONAL_CITIES`:

```python
INDONESIAN_CITIES = {
    ...
    "New City": {"lat": -X.XXXX, "lng": XXX.XXXX, "country": "Indonesia"},
}
```

### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name="RamadanSchedule" main.py
```

The executable will be generated in the `dist/` folder.

---

## 🤲 Dua for Breaking the Fast

<div align="center">

### ذَهَبَ الظَّمَأُ وَابْتَلَّتِ الْعُرُوقُ وَثَبَتَ الأَجْرُ إِنْ شَاءَ اللهُ

*"Dzahabazh-zhama'u wabtallatil-'uruuqu wa tsabatal-ajru insyaa-Allah"*

**"The thirst has gone, the veins are moistened, and the reward is confirmed, if Allah wills."**

*(HR. Abu Dawud no. 2357)*

</div>

---