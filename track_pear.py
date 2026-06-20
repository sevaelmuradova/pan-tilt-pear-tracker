"""
Green pear color tracker — standalone Python demo.
Webcam finds the biggest green blob, draws a circle around it,
prints its position.

Run:    python3 track_pear.py
Quit:   press 'q' in the video window
Toggle mask view: press 'h'
"""

import cv2
import numpy as np

LOWER_GREEN = np.array([35, 80, 50])
UPPER_GREEN = np.array([85, 255, 255])
MIN_BLOB_AREA = 1500
SMOOTHING = 0.6


def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: cannot open webcam. Check macOS camera permissions.")
        return

    smooth_x, smooth_y = None, None
    show_mask = False

    print("Tracker running. Press 'q' to quit, 'h' to toggle mask view.")

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
                if smooth_x is None:
                    smooth_x, smooth_y = cx, cy
                else:
                    smooth_x = int(SMOOTHING * smooth_x + (1 - SMOOTHING) * cx)
                    smooth_y = int(SMOOTHING * smooth_y + (1 - SMOOTHING) * cy)

                radius = int(np.sqrt(area / np.pi))
                cv2.circle(frame, (cx, cy), radius, (0, 255, 0), 2)
                cv2.drawMarker(frame, (smooth_x, smooth_y), (0, 0, 255),
                               markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

                norm_x = smooth_x / w
                norm_y = smooth_y / h
                cv2.putText(frame, f"pear: x={norm_x:.2f} y={norm_y:.2f}",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "green blob too small",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            cv2.putText(frame, "no green detected",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow("pear tracker", frame)
        if show_mask:
            cv2.imshow("mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("h"):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("mask")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
