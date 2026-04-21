import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random


class Shooter:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.smoothing = 2.0
        self.max_targets = 12
        self.game_duration = 60
        self.max_ammo = 6
        self.window_name = "GESTURE HUB - SHOOTER"
        self.w = 1280
        self.h = 720

    def run(self, should_quit=None):
        time.sleep(1.0)
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            cap = cv2.VideoCapture(1)

        if not cap.isOpened():
            return 0

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

        targets = []
        last_target_time = time.time()
        spawn_rate = 2.0
        score = 0
        ammo = self.max_ammo
        start_time = time.time()
        game_over = False
        prev_aim_x, prev_aim_y = self.w // 2, self.h // 2
        trigger_active = False

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)

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

                time_left = max(0, int(self.game_duration - (time.time() - start_time)))
                if time_left == 0:
                    game_over = True

                if not game_over:
                    cv2.line(game_board, (0, self.h // 2), (self.w, self.h // 2), (30, 30, 30), 1)
                    cv2.line(game_board, (self.w // 2, 0), (self.w // 2, self.h), (30, 30, 30), 1)

                    aim_x, aim_y = prev_aim_x, prev_aim_y
                    shoot_command, reload_command = False, False

                    if results.multi_hand_landmarks:
                        for handLms in results.multi_hand_landmarks:
                            wx = int(handLms.landmark[0].x * self.w)

                            if wx > self.w // 2:
                                ix, iy = int(handLms.landmark[5].x * self.w), int(handLms.landmark[5].y * self.h)
                                aim_x = int(prev_aim_x + (ix - prev_aim_x) / self.smoothing)
                                aim_y = int(prev_aim_y + (iy - prev_aim_y) / self.smoothing)
                                prev_aim_x, prev_aim_y = aim_x, aim_y

                            else:
                                t_tip, i_tip = handLms.landmark[4], handLms.landmark[8]
                                dist = math.hypot(int(i_tip.x * self.w) - int(t_tip.x * self.w),
                                                  int(i_tip.y * self.h) - int(t_tip.y * self.h))

                                if dist < 40:
                                    if not trigger_active:
                                        shoot_command = True
                                        trigger_active = True
                                    cv2.circle(game_board, (
                                    int((t_tip.x + i_tip.x) * self.w / 2), int((t_tip.y + i_tip.y) * self.h / 2)), 15,
                                               (0, 255, 0), cv2.FILLED)
                                elif dist > 110:
                                    trigger_active = False
                                    reload_command = True
                                    cv2.putText(game_board, "RELOADING", (wx, 100), cv2.FONT_HERSHEY_PLAIN, 2,
                                                (0, 255, 255), 2)
                                else:
                                    trigger_active = False

                    if shoot_command and ammo > 0:
                        ammo -= 1
                        cv2.circle(game_board, (aim_x, aim_y), 40, (255, 255, 255), cv2.FILLED)
                        for i in range(len(targets) - 1, -1, -1):
                            tx, ty, dx, dy, size, color = targets[i]
                            if math.sqrt((aim_x - tx) ** 2 + (aim_y - ty) ** 2) < size:
                                del targets[i]
                                score += 100
                                cv2.circle(game_board, (tx, ty), size + 20, (0, 255, 255), cv2.FILLED)
                                break

                    if reload_command and ammo < self.max_ammo:
                        ammo = self.max_ammo

                    if len(targets) < self.max_targets and time.time() - last_target_time > spawn_rate:
                        size = random.randint(40, 70)
                        targets.append([
                            random.randint(size, self.w - size),
                            random.randint(size, self.h - size),
                            random.choice([-5, 5]),
                            random.choice([-5, 5]),
                            size,
                            (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))
                        ])
                        last_target_time = time.time()

                    for t in targets:
                        t[0] += t[2]
                        t[1] += t[3]
                        if t[0] < t[4] or t[0] > self.w - t[4]: t[2] *= -1
                        if t[1] < t[4] or t[1] > self.h - t[4]: t[3] *= -1
                        cv2.circle(game_board, (t[0], t[1]), t[4], t[5], cv2.FILLED)

                    cv2.circle(game_board, (aim_x, aim_y), 20, (0, 255, 0), 2)
                    cv2.putText(game_board, f"SCORE: {score}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255),
                                2)
                    cv2.putText(game_board, f"TIME: {time_left}", (self.w - 300, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                                (255, 255, 255), 2)

                else:
                    cv2.putText(game_board, "GAME OVER", (self.w // 2 - 250, self.h // 2), cv2.FONT_HERSHEY_DUPLEX, 3,
                                (0, 0, 255), 5)
                    cv2.putText(game_board, f"Final Score: {score}", (self.w // 2 - 200, self.h // 2 + 80),
                                cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)

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
