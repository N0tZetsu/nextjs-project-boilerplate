import sys
import cv2
import numpy as np
import pyautogui
import keyboard
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QComboBox, QCheckBox, QVBoxLayout, QHBoxLayout, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer

class AimColorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("007 AimColor")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: black; color: white; font-family: Arial;")

        self.tracking_enabled = False
        self.menu_fixed = False
        self.toggle_key = "F"
        self.selected_color = "red"

        self.color_ranges = {
            "red": [(0, 70, 50), (10, 255, 255), (170, 70, 50), (180, 255, 255)],
            "yellow": [(15, 100, 100), (35, 255, 255)],
            "purple": [(125, 50, 50), (155, 255, 255)]
        }

        self.init_ui()
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.process_frame)
        self.timer.start(30)

        keyboard.add_hotkey(self.toggle_key.lower(), self.toggle_tracking)
        keyboard.add_hotkey('m', self.toggle_menu_fix)

    def init_ui(self):
        layout = QVBoxLayout()

        brand_label = QLabel("007")
        brand_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")
        layout.addWidget(brand_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Enable checkbox
        self.enable_checkbox = QCheckBox("Enable AimColor")
        self.enable_checkbox.stateChanged.connect(self.enable_changed)
        layout.addWidget(self.enable_checkbox)

        # Color selection
        color_layout = QHBoxLayout()
        color_label = QLabel("Select Color:")
        self.color_combo = QComboBox()
        self.color_combo.addItems(["red", "yellow", "purple"])
        self.color_combo.currentTextChanged.connect(self.color_changed)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_combo)
        layout.addLayout(color_layout)

        # Toggle key selection
        key_layout = QHBoxLayout()
        key_label = QLabel("Toggle Key:")
        self.key_input = QLineEdit(self.toggle_key)
        self.key_input.setMaxLength(1)
        self.key_input.setFixedWidth(40)
        self.key_input.textChanged.connect(self.key_changed)
        key_layout.addWidget(key_label)
        key_layout.addWidget(self.key_input)
        layout.addLayout(key_layout)

        # Menu fix info
        fix_label = QLabel("Press 'M' to fix/unfix menu")
        fix_label.setStyleSheet("color: gray; font-size: 10px;")
        layout.addWidget(fix_label, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout)

    def enable_changed(self, state):
        self.tracking_enabled = state == Qt.CheckState.Checked

    def color_changed(self, text):
        self.selected_color = text

    def key_changed(self, text):
        if text:
            keyboard.remove_hotkey(self.toggle_key.lower())
            self.toggle_key = text.upper()
            keyboard.add_hotkey(self.toggle_key.lower(), self.toggle_tracking)

    def toggle_tracking(self):
        self.tracking_enabled = not self.tracking_enabled
        self.enable_checkbox.setChecked(self.tracking_enabled)
        print(f"Tracking {'enabled' if self.tracking_enabled else 'disabled'}")

    def toggle_menu_fix(self):
        self.menu_fixed = not self.menu_fixed
        if self.menu_fixed:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        self.show()

    def find_color_center(self, mask):
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

    def process_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return

        frame = cv2.flip(frame, 1)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if self.tracking_enabled:
            ranges = self.color_ranges[self.selected_color]
            if self.selected_color == "red":
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

            center = self.find_color_center(mask)
            if center:
                cx, cy = center
                screen_width, screen_height = pyautogui.size()
                screen_x = int(cx * screen_width / frame.shape[1])
                screen_y = int(cy * screen_height / frame.shape[0])
                pyautogui.moveTo(screen_x, screen_y, duration=0.1)

    def closeEvent(self, event):
        self.cap.release()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AimColorApp()
    window.show()
    sys.exit(app.exec())
