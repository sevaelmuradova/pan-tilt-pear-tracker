"""
Hand-tracked pan-tilt camera — full integration.
Webcam tracks the green pear; Arduino moves both servos to follow it.
"""
import cv2
import numpy as np
import serial
import time

PORT = "/dev/cu.usbserial-A5069RR4"
BAUD = 9600
arduino = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)
print("connected to arduino")

def send_angles(pan, tilt):
    arduino.write(f"{int(pan)},{int(tilt)}\n".encode())

LOWER_GREEN = np.array([35, 80, 50])
UPPER_GREEN = np.array([85, 255, 255])
MIN_BLOB_AREA = 1500
ALPHA = 0.2
smooth_pan = 90.0
smooth_tilt = 90.0

log_raw, log_smooth = [], []

cap = cv2.VideoCapture(0)
print("tracker running. press q to quit.")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, LOWER_GREEN, UPPER_GREEN)

    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        biggest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(biggest)
        if area > MIN_BLOB_AREA:
            M = cv2.moments(biggest)
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            raw_pan = (cx / w) * 180
            raw_tilt = (cy / h) * 180

            smooth_pan = ALPHA * raw_pan + (1 - ALPHA) * smooth_pan
            smooth_tilt = ALPHA * raw_tilt + (1 - ALPHA) * smooth_tilt

            log_raw.append(raw_pan)
            log_smooth.append(smooth_pan)

            send_angles(smooth_pan, smooth_tilt)

            radius = int(np.sqrt(area / np.pi))
            cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)
            cv2.drawMarker(frame, (cx, cy), (0, 0, 255),
                           markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
            cv2.putText(frame, f"pan={int(smooth_pan)} tilt={int(smooth_tilt)}",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("pear tracker", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
arduino.close()

try:
    import matplotlib.pyplot as plt
    plt.figure(figsize=(10, 4))
    plt.plot(log_raw, label="raw pan angle", alpha=0.5)
    plt.plot(log_smooth, label="smoothed pan angle", linewidth=2)
    plt.xlabel("frame"); plt.ylabel("angle (degrees)")
    plt.title("Pear tracker: raw vs smoothed servo command")
    plt.legend(); plt.tight_layout()
    plt.savefig("signal_chart.png", dpi=120)
    print("saved signal_chart.png")
except ImportError:
    print("for signal chart: pip3 install matplotlib")
