import cv2
import math
import datetime
import mediapipe as mp

W, H = 1280, 720

class SmartWatch:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=1)

    @staticmethod
    def check_time(img, results, draw_surface=None):
        if draw_surface is None:
            draw_surface = img

        # Check if exactly two hands are detected
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            h1 = results.multi_hand_landmarks[0]
            h2 = results.multi_hand_landmarks[1]

            # Index finger tip and Wrist of Hand 1
            p1_ix, p1_iy = int(h1.landmark[8].x * W), int(h1.landmark[8].y * H)
            p1_wx, p1_wy = int(h1.landmark[0].x * W), int(h1.landmark[0].y * H)

            # Index finger tip and Wrist of Hand 2
            p2_ix, p2_iy = int(h2.landmark[8].x * W), int(h2.landmark[8].y * H)
            p2_wx, p2_wy = int(h2.landmark[0].x * W), int(h2.landmark[0].y * H)

            hit = False
            pos_x, pos_y = 0, 0

            # Cross-detection (Index finger of one hand touching the wrist of the other)
            if math.hypot(p1_ix - p2_wx, p1_iy - p2_wy) < 60:
                hit, pos_x, pos_y = True, p2_wx, p2_wy
            elif math.hypot(p2_ix - p1_wx, p2_iy - p1_wy) < 60:
                hit, pos_x, pos_y = True, p1_wx, p1_wy

            # Draw the digital watch if touched
            if hit:
                now = datetime.datetime.now()
                time_str = now.strftime("%H:%M:%S")

                cv2.circle(draw_surface, (pos_x, pos_y), 60, (255, 255, 0), 2)
                cv2.line(draw_surface, (pos_x, pos_y), (pos_x, pos_y - 80), (255, 255, 0), 2)
                cv2.rectangle(draw_surface, (pos_x - 80, pos_y - 110), (pos_x + 80, pos_y - 70), (0, 0, 0), cv2.FILLED)
                cv2.rectangle(draw_surface, (pos_x - 80, pos_y - 110), (pos_x + 80, pos_y - 70), (255, 255, 0), 2)
                cv2.putText(draw_surface, time_str, (pos_x - 65, pos_y - 80),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)

