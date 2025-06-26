import serial
import time
import requests

def find_arduino_port():
    import serial.tools.list_ports
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "CH340" in port.description:
            return port.device
    return None

arduino_port = find_arduino_port()
if not arduino_port:
    print("Arduino not found.")
    exit()

ser = serial.Serial(arduino_port, 9600, timeout=1)
print(f"Listening on {arduino_port}...")

while True:
    if ser.in_waiting:
        uid = ser.readline().decode().strip()
        if uid:
            print(f"UID Received: {uid}")
            try:
                response = requests.post('http://localhost:8000/auth/api/receive_uid', json={'uid': uid})


                print("Sent to Flask:", response.status_code)
            except Exception as e:
                print("Error sending UID:", e)
    time.sleep(1)
