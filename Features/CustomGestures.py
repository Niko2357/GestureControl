import cv2
import webbrowser
import time
import json
import os

CONFIG_FILE = "macro_config.json"


class CustomGestures:
    def __init__(self):
        self.links = ["", "", ""]
        self.load_links()  # Při startu hned načte uložené odkazy

        self.cooldown = 3.0
        self.last_trigger_time = 0
        self.current_message = ""
        self.message_time = 0

        # Proměnné pro dynamické gesto "Pojď ke mně" (Klávesnice)
        self.is_tracking_up = False
        self.start_y = None
        self.swipe_threshold = 0.2  # Ruka musí urazit 20% výšky obrazovky nahoru

    def load_links(self):
        """Načte uložené odkazy ze souboru, pokud existuje."""
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    self.links = json.load(f)
            except:
                pass

    def update_links(self, link1, link2, link3):
        """Uloží nové odkazy do souboru."""
        self.links = [link1, link2, link3]
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(self.links, f)
        print("--- MACRO LINKS SAVED ---")

    def check_fingers(self, hand_landmarks):
        tip_ids = [4, 8, 12, 16, 20]
        fingers = []
        if hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y and hand_landmarks.landmark[4].y < \
                hand_landmarks.landmark[5].y:
            fingers.append(1)
        else:
            fingers.append(0)
        for id in range(1, 5):
            if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def process_frame(self, img, results):
        if time.time() - self.message_time < 2.0:
            h, w, _ = img.shape
            cv2.putText(img, self.current_message, (w // 2 - 200, 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)

        if time.time() - self.last_trigger_time < self.cooldown:
            return

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                fingers = self.check_fingers(handLms)

                # --- DYNAMICKÉ GESTO: Virtuální Klávesnice (Ruka jede nahoru) ---
                wrist = handLms.landmark[0]
                if not self.is_tracking_up:
                    self.start_y = wrist.y
                    self.is_tracking_up = True
                else:
                    dy = wrist.y - self.start_y
                    if dy < -self.swipe_threshold:
                        try:
                            os.system("osk")
                            self.current_message = "[ VIRTUAL KEYBOARD ]"
                            self.message_time = time.time()
                            self.last_trigger_time = time.time()
                        except:
                            pass
                        self.is_tracking_up = False
                        break
                    elif dy > 0.05:
                        self.start_y = wrist.y

                # --- STATICKÁ GESTA (Odkazy) ---
                triggered_index = -1
                gesture_name = ""

                if fingers == [0, 1, 1, 0, 0]:
                    triggered_index = 0
                    gesture_name = "[ VICTORY ]"
                elif fingers == [1, 0, 0, 0, 0]:
                    triggered_index = 1
                    gesture_name = "[ THUMBS UP ]"
                elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
                    triggered_index = 2
                    gesture_name = "[ ROCK ON ]"

                if triggered_index != -1 and self.links[triggered_index] != "":
                    link = self.links[triggered_index]
                    if not link.startswith("http") and "." in link:
                        link = "https://" + link
                    try:
                        webbrowser.open(link)
                        self.current_message = f"EXECUTING: {gesture_name}"
                        self.message_time = time.time()
                        self.last_trigger_time = time.time()
                        break
                    except Exception as e:
                        print("Error opening link:", e)
