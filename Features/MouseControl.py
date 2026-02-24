import cv2
import mediapipe as mp
import pyautogui
import math
import numpy as np
import os


class MouseControl:
    def __init__(self):
        self.mpDraw = mp.solutions.drawing_utils
        self.mpHands = mp.solutions.hands

        # Get actual screen resolution
        self.screen_w, self.screen_h = pyautogui.size()

        # Camera setup (must match CoreEngine)
        self.cam_w, self.cam_h = 640, 480

        # Prevent app crash if mouse hits the screen corner
        pyautogui.FAILSAFE = False

        # Smoothing variables
        self.smooth_x, self.smooth_y = 0, 0
        self.smoothing = 5
        self.frame_reduction = 100
        self.click_threshold = 40
        self.clicked = False

    def process_frame(self, img, results):
        # Draw active zone (purple rectangle)
        cv2.rectangle(img, (self.frame_reduction, self.frame_reduction),
                      (self.cam_w - self.frame_reduction, self.cam_h - self.frame_reduction),
                      (255, 0, 255), 2)

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)

                # Get coordinates of Index finger (8) and Thumb (4)
                index_finger = handLms.landmark[8]
                thumb = handLms.landmark[4]

                # Convert proportional coordinates to camera pixels
                ix, iy = int(index_finger.x * self.cam_w), int(index_finger.y * self.cam_h)
                tx, ty = int(thumb.x * self.cam_w), int(thumb.y * self.cam_h)

                # --- 1. MOUSE MOVEMENT ---
                # Map camera coordinates to screen coordinates using the active zone
                screen_x = np.interp(ix, (self.frame_reduction, self.cam_w - self.frame_reduction), (0, self.screen_w))
                screen_y = np.interp(iy, (self.frame_reduction, self.cam_h - self.frame_reduction), (0, self.screen_h))

                # Apply smoothing
                self.smooth_x = self.smooth_x + (screen_x - self.smooth_x) / self.smoothing
                self.smooth_y = self.smooth_y + (screen_y - self.smooth_y) / self.smoothing

                try:
                    pyautogui.moveTo(self.smooth_x, self.smooth_y)
                except Exception:
                    pass

                # --- 2. MOUSE CLICK ---
                # Calculate distance between index finger and thumb
                distance = math.hypot(ix - tx, iy - ty)

                # Visual indicator for index finger
                cv2.circle(img, (ix, iy), 10, (0, 255, 255), cv2.FILLED)

                if distance < self.click_threshold:
                    # Fingers are close -> Click (Green indicator)
                    cv2.circle(img, (ix, iy), 10, (0, 255, 0), cv2.FILLED)
                    if not self.clicked:
                        pyautogui.click()
                        self.clicked = True
                else:
                    self.clicked = False
