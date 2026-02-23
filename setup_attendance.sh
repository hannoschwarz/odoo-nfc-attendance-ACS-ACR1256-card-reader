#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Use absolute path for reliability
PROJECT_DIR="/home/$USER/attendance"

echo "🚀 Starting Odoo NFC Kiosk Installation..."

# --- 1. SYSTEM UPDATES & BUILD TOOLS ---
echo "⚙️ Installing System Dependencies..."
sudo apt update
sudo apt install -y python3-pip python3-venv git unclutter chromium \
     netcat-openbsd swig python3-dev liblgpio-dev build-essential p7zip-full \
     wget libpcsclite-dev  gcc libccid pcscd pcsc-tools
sudo apt install python3-rpi.gpio python3-gpiozero -y     

# --- 0. FIX LOCALES (Hard Reset) ---
echo "🌐 Fixing Locales..."
sudo apt-get install -y locales
sudo locale-gen en_GB.UTF-8
# Set them for the current session to stop the Perl/Bash warnings
export LANG=en_GB.UTF-8
export LANGUAGE=en_GB.UTF-8
export LC_ALL=en_GB.UTF-8



# Return to repo
cd /home/$USER/odoo-nfc-attendance-ACS-ACR1256-card-reader

# install the driver for the NFC reader
sudo dpkg libasccid1_1.1.12-1~bpo12+1arm64.deb

# --- 5. PYTHON VIRTUAL ENVIRONMENT ---
echo "🐍 Setting up Python Environment..."
cd "$PROJECT_DIR"
python3 -m venv env
source env/bin/activate
pip install flask flask-socketio requests eventlet python-dotenv pyscard
deactivate

# --- 6. CONFIGURATION (DOTENV) ---
echo "📄 Setting up Configuration template..."
if [ ! -f .env ]; then
    cat <<EOF > .env
# Odoo Webhook URL
ODOO_WEBHOOK_URL=https://your-odoo-domain.com/web/hook/xxxx

# Flask Security
APP_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(16))')
EOF
fi


# --- 8. SYSTEMD SERVICES ---
echo "🖥️ Configuring System Services..."

# Backend Service
sudo bash -c "cat <<EOF > /etc/systemd/system/attendance_app.service
[Unit]
Description=Odoo NFC Backend
After=network.target

[Service]
User=$USER
WorkingDirectory=$PROJECT_DIR
ExecStart=$PROJECT_DIR/env/bin/python $PROJECT_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"


sudo systemctl daemon-reload
sudo systemctl enable attendance_app.service 

echo "-------------------------------------------------------"
echo "✅ INSTALLATION COMPLETE!"
echo "-------------------------------------------------------"
echo "1. Put your app.py and templates/index.html in: $PROJECT_DIR"
echo "2. Edit your Odoo URL in: $PROJECT_DIR/.env"
echo "3. Run: sudo systemctl restart attendance_app.service"
echo "-------------------------------------------------------"
