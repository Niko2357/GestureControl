import time
import joblib
import numpy as np
import pyautogui
import os
import sys
import eel


class GestureKeyboard:
    def __init__(self):
        self.models = {
            "Alphabet": {
                "file": "alphabet_model.pkl",
                "scaler": "alphabet_scaler.pkl",
                "gestures": {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G", 7: "H",
                             8: "I", 9: "J", 10: "K", 11: "L", 12: "M", 13: "N", 14: "O",
                             15: "P", 16: "Q", 17: "R", 18: "S", 19: "T", 20: "U", 21: "V",
                             22: "W", 23: "Y", 24: "Z", 25: ".", 26: ",", 27: "?", 28: " ", 29: "switch"}
            },
            "Numbers": {
                "file": "num_model.pkl",
                "scaler": "num_scaler.pkl",
                "gestures": {0: "0", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8", 9: "9",
                             10: "switch"}
            }
        }
        self.mode = "Alphabet"
        self.all_modes = list(self.models.keys())
        self.model, self.scaler, self.letter_map = self._load_model(self.mode)

        self.last_detected = None
        self.start_time = None
        self.req_time = 2.0

    def _get_resource_path(self, filename):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, filename)
        return os.path.join(os.path.abspath("."), filename)

    def _load_model(self, name):
        setting = self.models[name]
        model_path = self._get_resource_path(setting["file"])
        scaler_path = self._get_resource_path(setting["scaler"])

        if os.path.exists(model_path) and os.path.exists(scaler_path):
            return joblib.load(model_path), joblib.load(scaler_path), setting["gestures"]
        return None, None, None

    def process_frame(self, img, results):
        if self.model is None or self.scaler is None:
            self._update_hud("NO PKL", 0, "ERROR")
            return

        if not results.multi_hand_landmarks:
            self.last_detected = None
            self._update_hud("...", 0, self.mode)
            return

        hand = results.multi_hand_landmarks[0]
        data = []
        zero_x = hand.landmark[0].x
        zero_y = hand.landmark[0].y
        zero_z = hand.landmark[0].z

        for point in hand.landmark:
            data.append(point.x - zero_x)
            data.append(point.y - zero_y)
            data.append(point.z - zero_z)

        entry = np.array(data).reshape(1, -1)
        entry_scaled = self.scaler.transform(entry)
        num = self.model.predict(entry_scaled)[0]
        message = self.letter_map.get(num, "?")

        progress = 0.0

        if message not in ["switch", "?"]:
            if message == self.last_detected:
                progress = min(1.0, (time.time() - self.start_time) / self.req_time)
                if progress >= 1.0:
                    char_to_type = message.lower() if message.isalpha() else message
                    pyautogui.write(char_to_type)
                    self.last_detected = None
                    self.start_time = time.time()
                    self._update_hud("OK!", 1.0, self.mode)
                    return
            else:
                self.last_detected = message
                self.start_time = time.time()

        elif message == "switch":
            if self.last_detected == "switch":
                progress = min(1.0, (time.time() - self.start_time) / 2.0)
                if progress >= 1.0:
                    self.mode = self.all_modes[(self.all_modes.index(self.mode) + 1) % len(self.all_modes)]
                    self.model, self.scaler, self.letter_map = self._load_model(self.mode)
                    self.last_detected = None
                    self.start_time = time.time()
                    self._update_hud("SW!", 1.0, self.mode)
                    time.sleep(0.5)
                    return
            else:
                self.last_detected = "switch"
                self.start_time = time.time()
        else:
            self.last_detected = None

        display_text = self.last_detected if self.last_detected else message
        if display_text == "switch":
            display_text = "SW"
        self._update_hud(display_text, progress, self.mode)

    def _update_hud(self, text, progress, mode):
        try:
            eel.show_keyboard_hud_web(mode.upper(), text, progress)()
        except Exception:
            pass

    def close_hud(self):
        try:
            eel.hide_keyboard_hud_web()()
        except Exception:
            pass
