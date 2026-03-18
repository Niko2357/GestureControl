import base64
import eel
import cv2
import mediapipe as mp
import time
from Features.CustomGestures import CustomGestures
from Features.PresentationMode import PresentationMode
from Features.VolumeControl import VolumeControl
from Features.MouseControl import MouseControl


class CoreEngine:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=2, min_detection_confidence=0.7)

        # --- TADY CHYBĚL TENTO ŘÁDEK ---
        self.macro_module = CustomGestures()

        self.volume_module = VolumeControl()
        self.mouse_module = MouseControl()
        self.presentation_module = PresentationMode()

        # Dashboard Toggles
        self.volume_active = False
        self.mouse_active = False
        self.smartwatch_active = False
        self.camera_view_active = False
        self.presentation_active = False
        self.macro_active = False

        self.is_running = False
        self.camera_active = False

    def run(self):
        self.is_running = True
        self.camera_active = False
        cap = None

        def pripoj_kameru():
            for i in range(2):
                temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
                if temp_cap.isOpened():
                    temp_cap.set(3, 640)
                    temp_cap.set(4, 480)
                    return temp_cap
            return None

        while self.is_running:
            if cap is None:
                cap = pripoj_kameru()
                if cap is None:
                    time.sleep(1)
                    continue

            success, img = cap.read()

            if not success or not self.is_running:
                if cap is not None:
                    cap.release()
                    cap = None
                self.camera_active = False
                break

            self.camera_active = True

            if not (self.volume_active or self.mouse_active or self.camera_view_active or
                    getattr(self, 'smartwatch_active', False) or getattr(self, 'presentation_active', False) or getattr(
                        self, 'macro_active', False)):
                time.sleep(0.05)
                continue

            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            if getattr(self, 'smartwatch_active', False):
                from Features.SmartWatch import SmartWatch
                SmartWatch.check_time(img, results)

            if self.volume_active:
                self.volume_module.process_frame(img, results)

            if self.mouse_active:
                self.mouse_module.process_frame(img, results)

            if self.camera_view_active:
                small_cam = cv2.resize(img, (640, 360))
                _, buffer = cv2.imencode('.jpg', small_cam, [cv2.IMWRITE_JPEG_QUALITY, 60])
                b64_str = base64.b64encode(buffer).decode('utf-8')
                try:
                    eel.update_camera_frame(b64_str)()
                except Exception as e:
                    print("EEL ERROR", e)

            cv2.waitKey(1)

        if cap is not None:
            cap.release()
            cap = None
        self.camera_active = False
        print("--- CORE ENGINE IS OFFLINE ---")
