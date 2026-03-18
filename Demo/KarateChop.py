import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time

W, H = 1920, 1080


class KarateChop:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils
        self.max_lives = 3

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cv2.namedWindow("Karate Chop - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Karate Chop - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

        fruits = []
        score = 0
        lives = self.max_lives
        game_over = False
        last_spawn_time = time.time()
        spawn_rate = 1.0
        gravity = 1.5

        while True:
            success, img = cap.read()
            if not success: break

            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)
            game_board = np.zeros((H, W, 3), np.uint8)

            if not game_over:
                blade_lines = []
                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        wx, wy = int(handLms.landmark[0].x * W), int(handLms.landmark[0].y * H)
                        px, py = int(handLms.landmark[20].x * W), int(handLms.landmark[20].y * H)
                        blade_lines.append((wx, wy, px, py))
                        cv2.line(game_board, (wx, wy), (px, py), (255, 255, 255), 5)
                        cv2.line(game_board, (wx, wy), (px, py), (0, 255, 255), 15)

                if time.time() - last_spawn_time > spawn_rate:
                    fsize = random.randint(50, 80)
                    fx = random.randint(200, W - 200)
                    fy = H + 50
                    vx = random.uniform(-8, 8)
                    vy = random.uniform(-35, -45)
                    is_bomb = 1 if random.random() < 0.15 else 0
                    color = (50, 50, 50) if is_bomb else (
                    random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                    fruits.append([fx, fy, vx, vy, is_bomb, color, fsize])
                    last_spawn_time = time.time()
                    spawn_rate = max(0.4, spawn_rate * 0.98)

                for f in fruits[:]:
                    f[3] += gravity
                    f[0] += f[2]
                    f[1] += f[3]
                    fx_curr, fy_curr, vx, vy, is_bomb, color, fsize = f
                    hit = False

                    for b_line in blade_lines:
                        x1, y1, x2, y2 = b_line
                        if math.hypot(x2 - fx_curr, y2 - fy_curr) < fsize + 30:
                            hit = True
                        else:
                            px_vec, py_vec = x2 - x1, y2 - y1
                            norm = px_vec ** 2 + py_vec ** 2
                            if norm > 0:
                                u = ((fx_curr - x1) * px_vec + (fy_curr - y1) * py_vec) / float(norm)
                                if 0 < u < 1:
                                    dist = math.hypot(x1 + u * px_vec - fx_curr, y1 + u * py_vec - fy_curr)
                                    if dist < fsize: hit = True

                    if hit:
                        fruits.remove(f)
                        if is_bomb:
                            game_over = True
                        else:
                            score += 10
                    elif fy_curr > H + 100 and vy > 0:
                        fruits.remove(f)
                        if not is_bomb:
                            lives -= 1
                            if lives <= 0: game_over = True
                    else:
                        cv2.circle(game_board, (int(fx_curr), int(fy_curr)), fsize, color, -1)
                        if is_bomb:
                            cv2.line(game_board, (int(fx_curr) - 20, int(fy_curr) - 20),
                                     (int(fx_curr) + 20, int(fy_curr) + 20), (0, 0, 255), 5)
                            cv2.line(game_board, (int(fx_curr) + 20, int(fy_curr) - 20),
                                     (int(fx_curr) - 20, int(fy_curr) + 20), (0, 0, 255), 5)

                cv2.putText(game_board, f"SCORE: {score}", (80, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                for i in range(lives):
                    cv2.circle(game_board, (W - 100 - (i * 60), 80), 20, (0, 0, 255), -1)
            else:
                cv2.putText(game_board, "GAME OVER", (W // 2 - 400, H // 2), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255),
                            10)
                cv2.putText(game_board, f"FINAL SCORE: {score}", (W // 2 - 350, H // 2 + 150), cv2.FONT_HERSHEY_SIMPLEX,
                            2.5, (255, 255, 255), 5)

            cv2.imshow("Karate Chop - STANDALONE DEMO", game_board)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    game = KarateChop()
    game.run()
    