"""
Test: send a few commands to make the servos visibly move.
Confirms Python -> Arduino -> servo wiring is all working.
"""
import serial
import time

PORT = "/dev/cu.usbserial-A5069RR4"
BAUD = 9600

print("Opening serial port...")
arduino = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # Arduino auto-resets when serial opens; wait for boot
print("Connected.")

def send(pan, tilt):
    msg = f"{pan},{tilt}\n"
    arduino.write(msg.encode())
    print(f"sent: pan={pan}, tilt={tilt}")

print("\n--- Centering both servos ---")
send(90, 90)
time.sleep(1.5)

print("\n--- Pan LEFT (servo on pin 9 should move) ---")
send(30, 90)
time.sleep(1.5)

print("\n--- Pan RIGHT ---")
send(150, 90)
time.sleep(1.5)

print("\n--- Pan CENTER ---")
send(90, 90)
time.sleep(1.5)

print("\n--- Tilt DOWN (servo on pin 10 should move) ---")
send(90, 30)
time.sleep(1.5)

print("\n--- Tilt UP ---")
send(90, 150)
time.sleep(1.5)

print("\n--- Both center ---")
send(90, 90)
time.sleep(1.5)

print("\nDone.")
arduino.close()
