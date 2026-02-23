import time
import threading
import requests
import sys

from flask import Flask, render_template
from flask_socketio import SocketIO
import os
from dotenv import load_dotenv

from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException

# Load configuration from .env file
load_dotenv()

# Configuration from Environment Variables
ODOO_WEBHOOK_URL = os.getenv("ODOO_WEBHOOK_URL")
APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "default_secret_for_dev")

# Initialize Flask with the secret
app = Flask(__name__)
app.config['SECRET_KEY'] = APP_SECRET_KEY


# Get the directory where app.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
app.config['SECRET_KEY'] = 'odoo_nfc_kiosk_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading', logger=True, engineio_logger=True)


def init_hardware():
  # USB readers are Plug-and-Play. We just check if it's plugged in.
    available_readers = readers()
    if not available_readers:
        print("❌ No USB NFC Reader found!")
        return False
    print(f"✅ Found USB Reader: {available_readers[0]}")
    return True
    

def trigger_odoo(card_id):
    try:
        payload = {"card_id": card_id}
        # We send the request and wait for Odoo's response
        r = requests.post(ODOO_WEBHOOK_URL, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Odoo Connection Error: {e}")
        return False

def nfc_worker():
    print("🚀 USB NFC listener started...")
    while True:
        socketio.sleep(0.5)
        try:
           r = readers()
            if not r: continue
            
            connection = r[0].createConnection()
            connection.connect()
            
            # Command to get the Card UID (Standard ACR122U/1252U APDU command)
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(GET_UID)
            
            if sw1 == 0x90: # Success code
                card_id = toHexString(data).replace(" ", "")
                print(f"🔍 USB Card Scanned: {card_id}")
                
                success = trigger_odoo(card_id)
                socketio.emit('scan_result', {
                    'status': 'success' if success else 'error',
                    'card_id': card_id
                })
                socketio.sleep(3) # Cooldown to prevent double-scans
        except NoCardException:
            continue # No card on the reader, keep looking
        except Exception as e:
            # Most common error is the reader being unplugged or "Card Not Found"
            pass

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    try:
        if init_hardware():
            # Start background thread
            socketio.start_background_task(nfc_worker)
            socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print("\nStopping...")
    
