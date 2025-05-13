import cv2
import numpy as np
import pyautogui
import keyboard

# Define color ranges in HSV for red, yellow, purple
color_ranges = {
    "red": [(0, 120, 70), (10, 255, 255), (170, 120, 70), (180, 255, 255)],
    "yellow": [(20, 100, 100), (30, 255, 255)],
    "purple": [(130, 50, 50), (160, 255, 255)]
}

# Settings
tracking_enabled = False
toggle_key = "f"  # Key to toggle tracking

def toggle_tracking():
    global tracking_enabled
    tracking_enabled = not tracking_enabled
    print(f"Tracking {'enabled' if tracking_enabled else 'disabled'}")

keyboard.add_hotkey(toggle_key, toggle_tracking)

def find_color_center(mask):
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > 500:
            M = cv2.moments(largest)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return cx, cy
    return None

def main():
    cap = cv2.VideoCapture(0)
    screen_width, screen_height = pyautogui.size()

    print(f"Press '{toggle_key}' to toggle tracking on/off.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if tracking_enabled:
            for color, ranges in color_ranges.items():
                if color == "red":
                    lower1 = np.array(ranges[0])
                    upper1 = np.array(ranges[1])
                    lower2 = np.array(ranges[2])
                    upper2 = np.array(ranges[3])
                    mask1 = cv2.inRange(hsv, lower1, upper1)
                    mask2 = cv2.inRange(hsv, lower2, upper2)
                    mask = mask1 + mask2
                else:
                    lower = np.array(ranges[0])
                    upper = np.array(ranges[1])
                    mask = cv2.inRange(hsv, lower, upper)

                center = find_color_center(mask)
                if center:
                    cx, cy = center
                    cv2.circle(frame, (cx, cy), 10, (0, 255, 0), 2)
                    # Move mouse to center of detected color (scaled to screen)
                    screen_x = int(cx * screen_width / frame.shape[1])
                    screen_y = int(cy * screen_height / frame.shape[0])
                    pyautogui.moveTo(screen_x, screen_y, duration=0.1)
                    break  # Track only one color at a time

        cv2.imshow("AimColor", frame)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC to quit
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
