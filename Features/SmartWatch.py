import eel
import math
import time
import mediapipe as mp

W, H = 1280, 720

class SmartWatch:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=2)

    @staticmethod
    def check_time(img, results, draw_surface=None):
        if draw_surface is None:
            draw_surface = img

        # Check if exactly two hands are detected
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            h1 = results.multi_hand_landmarks[0]
            h2 = results.multi_hand_landmarks[1]

            # Index fingertip and Wrist of Hand 1
            p1_ix, p1_iy = int(h1.landmark[8].x * W), int(h1.landmark[8].y * H)
            p1_wx, p1_wy = int(h1.landmark[0].x * W), int(h1.landmark[0].y * H)

            # Index fingertip and Wrist of Hand 2
            p2_ix, p2_iy = int(h2.landmark[8].x * W), int(h2.landmark[8].y * H)
            p2_wx, p2_wy = int(h2.landmark[0].x * W), int(h2.landmark[0].y * H)

            hit = False

            if math.hypot(p1_ix - p2_wx, p1_iy - p2_wy) < 60:
                hit = True
            elif math.hypot(p2_ix - p1_wx, p2_iy - p1_wy) < 60:
                hit = True

            if hit:
                current_time = time.strftime("%H:%M")
                try:
                    eel.show_smartwatch_web(current_time)()
                except Exception:
                    pass

