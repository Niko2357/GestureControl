import base64
import eel
import cv2
import mediapipe as mp
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
        self.camera_active = False

    def run(self):
        self.is_running = True
        self.camera_active = False
        cap = None

        # Funkce pro bezpečné nalezení a spuštění kamery
        def pripoj_kameru():
            for i in range(5):
                temp_cap = cv2.VideoCapture(i)
                if temp_cap.isOpened():
                    success, _ = temp_cap.read()
                    if success:
                        temp_cap.set(3, 640)
                        temp_cap.set(4, 480)
                        return temp_cap
                    else:
                        temp_cap.release()
            return None

        print("--- CORE ENGINE STARTING ---")

        while self.is_running:
            # Pokud kameru nemáme (nebo byla vytržena), zkusíme ji najít
            if cap is None:
                self.camera_active = False
                cap = pripoj_kameru()
                if cap is None:
                    time.sleep(1)  # Počkáme vteřinu a zkusíme znovu (kabel je odpojen)
                    continue
                else:
                    print("--- CAMERA CONNECTED ---")

            # 1. Přečtení obrazu z existující kamery
            success, img = cap.read()
            self.camera_active = success

            # 2. Reakce na fyzické odpojení (vytržení USB kabelu)
            if not success:
                print("--- CAMERA DISCONNECTED ---")
                cap.release()  # Zahodíme rozbité spojení
                cap = None  # V dalším kole se spustí hledání
                time.sleep(0.5)
                continue

            # 3. IDLE MODE (Režim spánku)
            if not (self.volume_active or self.mouse_active or self.camera_view_active or
                    getattr(self, 'smartwatch_active', False) or getattr(self, 'presentation_active', False) or getattr(
                        self, 'macro_active', False)):
                time.sleep(0.05)
                continue

            # Mirror flip
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Process hands
            results = self.hands.process(imgRGB)

            # --- 1. SMART WATCH ---
            if getattr(self, 'smartwatch_active', False):
                from Features.SmartWatch import SmartWatch
                SmartWatch.check_time(img, results)

            # --- 2. VOLUME CONTROL ---
            if self.volume_active:
                self.volume_module.process_frame(img, results)

            # --- 3. MOUSE CONTROL ---
            if self.mouse_active:
                self.mouse_module.process_frame(img, results)

            # --- 4. PRESENTATION MODE ---
            if getattr(self, 'presentation_active', False):
                self.presentation_module.process_frame(img, results)

            # --- 5. MACRO GESTURES ---
            if getattr(self, 'macro_active', False):
                self.macro_module.process_frame(img, results)

            # --- 6. CAMERA VIEW (Web Stream) ---
            if self.camera_view_active:
                cx, cy = 320, 240
                cv2.line(img, (cx, cy - 30), (cx, cy + 30), (0, 255, 0), 2)
                cv2.line(img, (cx - 30, cy), (cx + 30, cy), (0, 255, 0), 2)

                # --- OPTIMALIZACE OBRAZU ZDE ---
                # 1. Zmenšíme obraz pro rychlý přenos do webu
                small_cam = cv2.resize(img, (640, 360))
                # 2. Zkomprimujeme JPEG na 60 %
                _, buffer = cv2.imencode('.jpg', small_cam, [cv2.IMWRITE_JPEG_QUALITY, 60])

                b64_str = base64.b64encode(buffer).decode('utf-8')
                try:
                    eel.update_camera_frame(b64_str)()
                except Exception as e:
                    print(f"Chyba streamu: {e}")

            cv2.waitKey(1)

        if cap is not None:
            cap.release()
        print("--- CORE ENGINE IS OFFLINE ---")
