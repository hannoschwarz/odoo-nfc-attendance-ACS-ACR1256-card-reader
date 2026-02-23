import os
import requests
from flask import Flask, render_template
from flask_socketio import SocketIO
from smartcard.System import readers
from smartcard.util import toHexString
from smartcard.Exceptions import NoCardException
from gpiozero import LED # Modern RPi GPIO library
from time import sleep

# --- Configuration ---
ODOO_WEBHOOK_URL = "YOUR_ODOO_WEBHOOK_URL"
GREEN_LED_PIN = 26
RED_LED_PIN = 19

# Initialize Hardware LEDs
green_led = LED(GREEN_LED_PIN)
red_led = LED(RED_LED_PIN)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'odoo_nfc_kiosk_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

def init_hardware():
    available_readers = readers()
    if not available_readers:
        print("❌ No USB NFC Reader found!")
        # Blink red rapidly to show error
        red_led.blink(on_time=0.1, off_time=0.1, n=5)
        return False
    print(f"✅ Found USB Reader: {available_readers[0]}")
    return True

def trigger_odoo(card_id):
    # Stop Green blink, Start Red blink to show "Processing"
    green_led.off()
    red_led.blink(on_time=0.2, off_time=0.2)
    
    try:
        payload = {"card_id": card_id}
        r = requests.post(ODOO_WEBHOOK_URL, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print(f"Odoo Connection Error: {e}")
        return False

def nfc_worker():
    print("🚀 USB NFC listener started...")
    
    while True:
        # State: Waiting for Card (Green Blinking)
        if not green_led.is_lit:
            green_led.blink(on_time=1, off_time=1)
        
        socketio.sleep(0.5)
        try:
            r = readers()
            if not r: continue
            
            connection = r[0].createConnection()
            connection.connect()
            
            GET_UID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            data, sw1, sw2 = connection.transmit(GET_UID)
            
            if sw1 == 0x90:
                card_id = toHexString(data).replace(" ", "")
                print(f"🔍 USB Card Scanned: {card_id}")
                
                # Communicate with Odoo
                success = trigger_odoo(card_id)
                
                # Handle Response Logic
                red_led.off() # Stop the "Processing" blink
                
                if success:
                    green_led.on() # Steady Green
                    red_led.off()
                else:
                    green_led.off()
                    red_led.on()  # Steady Red
                
                # Show result for 3 seconds
                socketio.sleep(3)
                
                # Reset for next scan
                green_led.off()
                red_led.off()

        except NoCardException:
            continue 
        except Exception as e:
            pass

if __name__ == '__main__':
    try:
        if init_hardware():
            socketio.start_background_task(target=nfc_worker)
            # Port 5000 remains open if you still want to check the logs via browser
            socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        green_led.off()
        red_led.off()
        print("\nStopping...")
