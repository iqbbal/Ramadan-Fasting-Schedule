# 🌙 Jadwal Puasa Ramadhan - Windows Taskbar App

Aplikasi system tray (taskbar) Windows untuk menampilkan jadwal puasa Ramadhan berdasarkan geolokasi IP atau pilihan kota manual.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Fitur

- 🕐 **System Tray Icon** - Ikon bulan sabit di taskbar dengan countdown
- 📋 **Menu Jadwal** - Klik kanan untuk melihat semua waktu shalat
- 🌍 **Auto Geolokasi** - Deteksi lokasi otomatis via IP
- 📍 **Pilih Kota** - 20+ kota Indonesia & internasional
- 🔔 **Notifikasi Desktop** - Alert sebelum Imsak & saat Berbuka
- ⏰ **Countdown** - Hitung mundur ke Imsak/Iftar
- 🕌 **Metode KEMENAG** - Perhitungan resmi Kementerian Agama RI
- 🌙 **Hijriyah** - Menampilkan tanggal Hijriyah

## 🚀 Quick Start

### Prerequisites

- Python 3.8 atau lebih baru
- Windows 10/11

### Instalasi

```bash
# Clone atau download project
cd ramadhan-windows-taskbar

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python main.py
```

## 📁 Struktur Project

```
ramadhan-windows-taskbar/
├── main.py                 # Entry point - System tray app
├── config_manager.py       # Manajemen konfigurasi & database kota
├── location_service.py     # Geolokasi IP & koordinat kota
├── prayer_times_service.py # API Aladhan untuk jadwal shalat
├── notification_service.py # Notifikasi desktop Windows
├── icon_generator.py       # Generator ikon dynamic untuk tray
├── settings_window.py      # UI pengaturan (Tkinter)
├── config.json             # File konfigurasi user
├── requirements.txt        # Python dependencies
└── README.md               # Dokumentasi
```

## 🛠️ Tech Stack

| Komponen | Teknologi | Alasan |
|----------|-----------|--------|
| **Language** | Python 3 | Mudah di-maintain, rich ecosystem |
| **System Tray** | pystray | Cross-platform, ringan |
| **Icon Generation** | Pillow (PIL) | Dynamic icon creation |
| **Settings UI** | Tkinter | Built-in Python, zero dependency |
| **Prayer Times API** | [Aladhan API](https://aladhan.com/prayer-times-api) | Gratis, tanpa API key, akurat |
| **Geolokasi** | ip-api.com | Gratis, tanpa registrasi |
| **Notifications** | win10toast | Native Windows 10/11 toast |

## ⚙️ Konfigurasi

### Mode Lokasi

1. **Otomatis (IP)** - Aplikasi mendeteksi lokasi dari IP address
2. **Manual (Kota)** - Pilih dari 20+ kota tersedia

### Kota Tersedia

**Indonesia:** Jakarta, Surabaya, Bandung, Medan, Semarang, Makassar, Yogyakarta, Palembang, Denpasar, Balikpapan, Banjarmasin, Pontianak, Aceh, Padang, Pekanbaru, Manado, Malang, Solo, Mataram, Jayapura

**Internasional:** Makkah, Madinah, Kuala Lumpur, Singapore, Istanbul, Dubai, London, Tokyo, Sydney, New York

### Metode Perhitungan

Default: **Kementerian Agama RI (KEMENAG)**

Tersedia 15+ metode perhitungan lainnya termasuk MWL, ISNA, Umm Al-Qura, dll.

## 📸 Cara Penggunaan

1. **Jalankan** `python main.py`
2. Ikon 🌙 akan muncul di system tray (taskbar)
3. **Klik kanan** pada ikon untuk melihat jadwal
4. Pilih **⚙️ Pengaturan** untuk konfigurasi
5. Aplikasi akan mengirim **notifikasi** otomatis

## 🔔 Notifikasi

- **Sebelum Imsak**: Notifikasi X menit sebelum waktu Imsak (configurable)
- **Saat Berbuka**: Notifikasi saat waktu Maghrib tiba
- Notifikasi menggunakan Windows 10/11 native toast

## 📝 API yang Digunakan

### Aladhan API (Prayer Times)
- **URL**: `https://api.aladhan.com/v1/timings`
- **Limit**: Unlimited (fair use)
- **Auth**: Tidak perlu API key
- **Docs**: https://aladhan.com/prayer-times-api

### ip-api.com (Geolocation)
- **URL**: `http://ip-api.com/json/`
- **Limit**: 45 requests/menit
- **Auth**: Tidak perlu registrasi

## 🏗️ Development

### Menambah Kota Baru

Edit `config_manager.py`, tambahkan ke `INDONESIAN_CITIES` atau `INTERNATIONAL_CITIES`:

```python
INDONESIAN_CITIES = {
    ...
    "Kota Baru": {"lat": -X.XXXX, "lng": XXX.XXXX, "country": "Indonesia"},
}
```

### Build Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name="JadwalPuasa" main.py
```

## 📄 License

MIT License - Silakan gunakan dan modifikasi sesuai kebutuhan.

## 🤲 Doa

> *"Allahumma laka sumtu wa 'ala rizqika aftartu"*
> 
> Ya Allah, untuk-Mu aku berpuasa dan dengan rezeki-Mu aku berbuka.
