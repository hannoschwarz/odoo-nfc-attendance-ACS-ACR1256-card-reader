# Odoo NFC Attendance Kiosk 🚀

**Turn your Raspberry Pi into a professional, plug-and-play attendance terminal for Odoo.**

This project provides a robust, real-time interface for Odoo's Attendance module. It uses a **ACS ACR1256** usb card reader to read employee badges and sends the data to Odoo via Webhooks.

---

## ✨ Features

* **Real-time Feedback**: Instant visual and audio cues on scan.
* **Double-Tap Protection**: Prevents accidental double-scans within a 5-second window.
* **Auto-Kiosk Mode**: Boots directly into a full-screen, mouse-less browser.
* **Hardened Security**: Includes options to disable Wi-Fi/Bluetooth and uses `.env` for secrets.
* **Self-Healing**: Systemd services automatically restart the app if it crashes.

---

## 🛠️ Hardware Requirements

1. **Raspberry Pi** (3, 4, or 5).
2. **ACS ACR 1256 usb nfc reader**.
3. **MicroSD Card** (8GB+ with Raspberry Pi OS Bookworm).
4. **Ethernet Connection** (Recommended for stability).

---

## 🚀 Quick Start (Automated Install)

### 1. Preparation

Ensure your Pi is running the latest OS and you have SSH access or a keyboard/monitor connected.

### 2. Clone & Install

Run these commands in your terminal:

```bash
git clone https://github.com/alanschwarz/odoo-nfc-attendance.git
cd odoo-nfc-attendance
chmod +x setup_attendance.sh
./setup_attendance.sh

```

### 3. Configure Odoo

The script creates a directory at `~/attendance`. You must configure your Webhook:

1. In **Odoo**, create an **Automation Rule** for the "Attendance" model.
2. Set the trigger to **On Webhook**.
3. Copy the Webhook URL.
4. On the Pi, edit the config: `nano ~/attendance/.env`
5. Paste your URL into `ODOO_WEBHOOK_URL`.

---

## 📂 Project Structure

* `app.py`: The Flask backend that listens to the NFC hardware.
* `setup_attendance.sh`: The "bulletproof" installer for hardware drivers and services.
* `libasccid1_1.1.12-1~bpo12+1arm64.deb`: The low-level hardware driver (installed automatically from ACS.com.hk sources).
* `templates/`: The HTML/JS frontend for the kiosk display.
* `.env`: (Private) Stores your Odoo URL and Flask secret keys.

---

## 🔧 Technical Details

### Disabling Wireless for Security

The installation script offers an option to disable Wi-Fi and Bluetooth. This is highly recommended for physical terminals to prevent unauthorized access. If you need to re-enable them later, edit `/boot/firmware/config.txt`.

### Service Management

The app runs as two systemd services:

* `attendance_app.service`: Manages the Python hardware listener.
* `attendance_kiosk.service`: Manages the Chromium browser window.

**Commands to check status or logs:**

```bash
sudo systemctl status attendance_app
journalctl -u attendance_app.service -f

sudo systemctl status attendance_kiosk
journalctl -u attendance_kiosk.service -f
```

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have a feature request (like support for I2C instead of SPI), please open an issue or submit a pull request.

---

## ⚖️ License

**MIT License**

Copyright (c) 2026 Alan Schwarz

Permission is hereby granted, free of charge, to any person obtaining a copy of this software... (See the [LICENSE](https://www.google.com/search?q=LICENSE) file for the full text).

**Disclaimer**: This software is provided "as is", without warranty of any kind. The author is not responsible for any hardware damage or data loss.


    
