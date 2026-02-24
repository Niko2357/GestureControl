import cv2
import mediapipe as mp
import base64
import eel
import time
from Features.VolumeControl import VolumeControl
from Features.MouseControl import MouseControl
from Features.SmartWatch import SmartWatch
from Features.PresentationMode import PresentationMode
from Features.CustomGestures import CustomGestures


class CoreEngine:
    def __init__(self):
        # Initialize MediaPipe once for all modules
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7)

        # Initialize modules
        self.volume_module = VolumeControl()
        self.mouse_module = MouseControl()

        # Dashboard Toggles (All OFF by default)
        self.volume_active = False
        self.mouse_active = False
        self.smartwatch_active = False
        self.camera_view_active = False
        self.presentation_module = PresentationMode()
        self.presentation_active = False
        self.macro_module = CustomGestures()
        self.macro_active = False

        self.is_running = False

    def run(self):
        self.is_running = True
        cap = None

        # Smart camera search
        for i in range(5):
            temp_cap = cv2.VideoCapture(i)
            if temp_cap.isOpened():
                success, _ = temp_cap.read()
                if success:
                    cap = temp_cap
                    break
                else:
                    temp_cap.release()

        if cap is None:
            print("CRITICAL: Camera not found!")
            return

        # Lower resolution for fast and smooth background processing
        cap.set(3, 640)
        cap.set(4, 480)
        print("--- CORE ENGINE IS ONLINE ---")

        while self.is_running:
            # Idle mode: If nothing is active, sleep to save CPU power
            if not (self.volume_active or self.mouse_active or self.camera_view_active or self.smartwatch_active):
                time.sleep(0.1)
                continue

            success, img = cap.read()
            if not success:
                continue

            # Mirror flip is crucial for intuitive control
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Process hands ONCE per frame
            results = self.hands.process(imgRGB)

            # --- 1. SMART WATCH ---
            if self.smartwatch_active:
                # Draws the watch directly onto the camera frame
                SmartWatch.check_time(img, results)

            # --- 2. VOLUME CONTROL ---
            if self.volume_active:
                self.volume_module.process_frame(img, results)

            # --- 3. MOUSE CONTROL ---
            if self.mouse_active:
                self.mouse_module.process_frame(img, results)

            # --- 4. PRESENTATION MODE ---
            if self.presentation_active:
                self.presentation_module.process_frame(img, results)

            # --- 5. MACRO GESTURES ---
            if self.macro_active:
                self.macro_module.process_frame(img, results)

            # --- 6. CAMERA VIEW (Web Stream) ---
            if self.camera_view_active:
                cx, cy = 320, 240
                # Draw Crosshair
                cv2.line(img, (cx, cy - 30), (cx, cy + 30), (0, 255, 0), 2)
                cv2.line(img, (cx - 30, cy), (cx + 30, cy), (0, 255, 0), 2)

                # Compress and send to JavaScript
                _, buffer = cv2.imencode('.jpg', img)
                b64_str = base64.b64encode(buffer).decode('utf-8')
                try:
                    eel.update_camera_frame(b64_str)()
                except Exception:
                    pass  # Ignore errors if web page is refreshing

            cv2.waitKey(1)

        cap.release()
        print("--- CORE ENGINE IS OFFLINE ---")
