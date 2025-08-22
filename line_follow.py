import cv2
import numpy as np

def detect_parallel_lines(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower_black = np.array([0, 0, 0])
    upper_black = np.array([180, 255, 50])
    mask = cv2.inRange(hsv, lower_black, upper_black)

    height, width = mask.shape
    mask[0:int(height * 0.5), :] = 0

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    line_positions = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            line_positions.append(cx)
            cv2.line(frame, (cx, y), (cx, y + h), (0, 255, 0), 3)

    line_positions = sorted(line_positions)

    direction = "STOP"
    if len(line_positions) >= 2:
        left = line_positions[0]
        right = line_positions[-1]
        center = (left + right) // 2
        cv2.line(frame, (center, int(height * 0.6)), (center, height), (0, 0, 255), 2)

        if center < width // 2 - 20:
            direction = "Turn Left"
        elif center > width // 2 + 20:
            direction = "Turn Right"
        else:
            direction = "Forward"

    cv2.putText(frame, direction, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

    return frame, direction
