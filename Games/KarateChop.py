import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time
from Features.SmartWatch import SmartWatch

W, H = 1280, 720


class KarateChop:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils
        self.max_lives = 3
        self.window_name = "GESTURE HUB"
        self.w = 1280
        self.h = 720

    def run(self, should_quit=None):
        time.sleep(1)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)

        if not cap.isOpened():
            return 0

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

        fruits = []
        score = 0
        lives = self.max_lives
        game_over = False
        start_time = time.time()
        last_spawn_time = time.time()
        spawn_rate = 1.0
        gravity = 1.2

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        try:
            while True:
                if should_quit and should_quit():
                    break

                success, img = cap.read()
                if not success:
                    break

                img = cv2.flip(img, 1)
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(imgRGB)

                game_board = np.zeros((self.h, self.w, 3), np.uint8)

                SmartWatch.check_time(img, results, draw_surface=game_board)

                if not game_over:
                    blade_line = None

                    if results.multi_hand_landmarks:
                        for handLms in results.multi_hand_landmarks:
                            self.mpDraw.draw_landmarks(game_board, handLms, self.mpHands.HAND_CONNECTIONS)

                            wx, wy = int(handLms.landmark[0].x * self.w), int(handLms.landmark[0].y * self.h)
                            px, py = int(handLms.landmark[20].x * self.w), int(handLms.landmark[20].y * self.h)

                            blade_line = (wx, wy, px, py)

                            cv2.line(game_board, (wx, wy), (px, py), (255, 255, 255), 5)
                            cv2.line(game_board, (wx, wy), (px, py), (0, 255, 255), 15)

                    if time.time() - last_spawn_time > spawn_rate:
                        fsize = random.randint(40, 60)
                        fx = random.randint(150, self.w - 150)
                        fy = self.h + 50

                        vx = random.uniform(-6, 6)
                        vy = random.uniform(-28, -38)

                        is_bomb = 1 if random.random() < 0.15 else 0

                        if is_bomb:
                            color = (50, 50, 50)
                        else:
                            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

                        fruits.append([fx, fy, vx, vy, is_bomb, color, fsize])

                        last_spawn_time = time.time()
                        spawn_rate = max(0.4, spawn_rate * 0.98)

                    for f in fruits[:]:
                        f[3] += gravity
                        f[0] += f[2]
                        f[1] += f[3]

                        fx_curr, fy_curr, vx, vy, is_bomb, color, fsize = f
                        hit = False

                        if blade_line:
                            x1, y1, x2, y2 = blade_line

                            if math.hypot(x2 - fx_curr, y2 - fy_curr) < fsize + 20:
                                hit = True
                            else:
                                px_vec = x2 - x1
                                py_vec = y2 - y1
                                norm = px_vec * px_vec + py_vec * py_vec

                                if norm > 0:
                                    u = ((fx_curr - x1) * px_vec + (fy_curr - y1) * py_vec) / float(norm)
                                    if 0 < u < 1:
                                        x_closest = x1 + u * px_vec
                                        y_closest = y1 + u * py_vec
                                        dist = math.hypot(x_closest - fx_curr, y_closest - fy_curr)

                                        if dist < fsize:
                                            hit = True

                        if hit:
                            fruits.remove(f)
                            if is_bomb:
                                game_over = True
                                cv2.circle(game_board, (int(fx_curr), int(fy_curr)), 100, (0, 0, 255), cv2.FILLED)
                            else:
                                score += 10
                                cv2.circle(game_board, (int(fx_curr), int(fy_curr)), fsize + 15, (255, 255, 255),
                                           cv2.FILLED)

                        elif fy_curr > self.h + 100 and vy > 0:
                            fruits.remove(f)
                            if not is_bomb:
                                lives -= 1
                                if lives <= 0:
                                    game_over = True

                        else:
                            cv2.circle(game_board, (int(fx_curr), int(fy_curr)), fsize, color, cv2.FILLED)
                            cv2.circle(game_board, (int(fx_curr) - 10, int(fy_curr) - 10), fsize // 3, (255, 255, 255),
                                       cv2.FILLED)
                            if is_bomb:
                                cv2.line(game_board, (int(fx_curr) - 15, int(fy_curr) - 15),
                                         (int(fx_curr) + 15, int(fy_curr) + 15), (0, 0, 255), 4)
                                cv2.line(game_board, (int(fx_curr) + 15, int(fy_curr) - 15),
                                         (int(fx_curr) - 15, int(fy_curr) + 15), (0, 0, 255), 4)

                    cv2.putText(game_board, f"SCORE: {score}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255),
                                2)

                    for i in range(lives):
                        cv2.circle(game_board, (self.w - 50 - (i * 40), 50), 15, (0, 0, 255), cv2.FILLED)

                else:
                    cv2.putText(game_board, "GAME OVER", (self.w // 2 - 300, self.h // 2), cv2.FONT_HERSHEY_DUPLEX, 4,
                                (0, 0, 255), 5)
                    cv2.putText(game_board, f"Final Score: {score}", (self.w // 2 - 180, self.h // 2 + 80),
                                cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 2)

                cv2.imshow(self.window_name, game_board)
                key = cv2.waitKey(1) & 0xFF

                if key == 27 or (should_quit and should_quit()):
                    break

                if game_over:
                    cv2.imshow(self.window_name, game_board)
                    cv2.waitKey(3000)
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        return score
