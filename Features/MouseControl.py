import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np


class MouseControl:
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands
        self.screen_w, self.screen_h = pyautogui.size()
        self.cam_w, self.cam_h = 640, 480
        pyautogui.FAILSAFE = False

        # --- LEPŠÍ SMOOTHING ---
        self.ploc_x, self.ploc_y = 0, 0
        self.cloc_x, self.cloc_y = 0, 0
        self.smoothing = 3  # Nižší číslo = rychlejší reakce

        # --- KLIKACÍ POJISTKA ---
        self.frame_reduction = 120  # Větší redukce = citlivější pohyb
        self.click_threshold = 35
        self.clicked = False

    def process_frame(self, img, results):
        # Aktivní zóna
        cv2.rectangle(img, (self.frame_reduction, self.frame_reduction),
                      (self.cam_w - self.frame_reduction, self.cam_h - self.frame_reduction),
                      (0, 255, 255), 2)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                # Špička ukazováčku (8) a špička palce (4)
                idx = handLms.landmark[8]
                thumb = handLms.landmark[4]

                ix, iy = int(idx.x * self.cam_w), int(idx.y * self.cam_h)
                tx, ty = int(thumb.x * self.cam_w), int(thumb.y * self.cam_h)

                # Mapování na obrazovku
                x3 = np.interp(ix, (self.frame_reduction, self.cam_w - self.frame_reduction), (0, self.screen_w))
                y3 = np.interp(iy, (self.frame_reduction, self.cam_h - self.frame_reduction), (0, self.screen_h))

                # --- VYLEPŠENÉ VYHLAZOVÁNÍ ---
                self.cloc_x = self.ploc_x + (x3 - self.ploc_x) / self.smoothing
                self.cloc_y = self.ploc_y + (y3 - self.ploc_y) / self.smoothing

                # Prevence mikro-pohybů (Deadzone)
                if abs(self.cloc_x - self.ploc_x) > 2 or abs(self.cloc_y - self.ploc_y) > 2:
                    pyautogui.moveTo(self.cloc_x, self.cloc_y)

                self.ploc_x, self.ploc_y = self.cloc_x, self.cloc_y

                # Detekce kliku
                dist = math.hypot(ix - tx, iy - ty)
                if dist < self.click_threshold:
                    if not self.clicked:
                        pyautogui.click()
                        self.clicked = True
                    cv2.circle(img, (ix, iy), 15, (0, 255, 0), cv2.FILLED)
                else:
                    self.clicked = False
                    cv2.circle(img, (ix, iy), 10, (255, 0, 255), cv2.FILLED)
