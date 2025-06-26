import requests
import webbrowser
import time

# This simulates the UID being read — replace with your actual UID reading code
def simulate_rfid_read():
    uid = input("Scan RFID card (enter UID): ")
    return uid

BASE_URL = "http://127.0.0.1:5000"

while True:
    uid = simulate_rfid_read()

    try:
        # Ask Flask app if UID is registered
        response = requests.get(f"{BASE_URL}/api/check_uid/{uid}")
        if response.status_code == 200 and response.json().get("registered"):
            webbrowser.open(f"{BASE_URL}/patient-info?uid={uid}")
            print("Opening existing patient profile...")
        else:
            webbrowser.open(f"{BASE_URL}/register-patient?uid={uid}")
            print("Opening registration form for new patient...")
    except Exception as e:
        print("Error:", e)

    time.sleep(5)
