import cv2
import math
import datetime

W, H = 1280, 720


class SmartWatch:
    """Třída pro detekci gesta hodinek."""

    @staticmethod
    def zkontroluj(img, results, draw_surface=None):
        if draw_surface is None:
            draw_surface = img

        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            h1 = results.multi_hand_landmarks[0]
            h2 = results.multi_hand_landmarks[1]

            p1_ix, p1_iy = int(h1.landmark[8].x * W), int(h1.landmark[8].y * H)
            p1_wx, p1_wy = int(h1.landmark[0].x * W), int(h1.landmark[0].y * H)

            p2_ix, p2_iy = int(h2.landmark[8].x * W), int(h2.landmark[8].y * H)
            p2_wx, p2_wy = int(h2.landmark[0].x * W), int(h2.landmark[0].y * H)

            hit = False
            pos_x, pos_y = 0, 0

            # Detekce dotyku (křížem)
            if math.hypot(p1_ix - p2_wx, p1_iy - p2_wy) < 60:
                hit, pos_x, pos_y = True, p2_wx, p2_wy
            elif math.hypot(p2_ix - p1_wx, p2_iy - p1_wy) < 60:
                hit, pos_x, pos_y = True, p1_wx, p1_wy

            if hit:
                now = datetime.datetime.now()
                cas_str = now.strftime("%H:%M:%S")

                cv2.circle(draw_surface, (pos_x, pos_y), 60, (255, 255, 0), 2)
                cv2.line(draw_surface, (pos_x, pos_y), (pos_x, pos_y - 80), (255, 255, 0), 2)
                cv2.rectangle(draw_surface, (pos_x - 80, pos_y - 110), (pos_x + 80, pos_y - 70), (0, 0, 0), cv2.FILLED)
                cv2.rectangle(draw_surface, (pos_x - 80, pos_y - 110), (pos_x + 80, pos_y - 70), (255, 255, 0), 2)
                cv2.putText(draw_surface, cas_str, (pos_x - 65, pos_y - 80),
                            cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)