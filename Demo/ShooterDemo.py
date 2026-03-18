import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

W, H = 1920, 1080


class Shooter:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.smoothing = 2.0
        self.max_targets = 10
        self.game_duration = 60
        self.max_ammo = 6

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        cv2.namedWindow("AI Shooting Range - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("AI Shooting Range - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

        if not cap.isOpened():
            return

        targets, last_target_time = [], time.time()
        spawn_rate, score, ammo = 1.2, 0, self.max_ammo
        start_time, game_over = time.time(), False
        prev_aim_x, prev_aim_y = W // 2, H // 2
        trigger_active = False

        while True:
            success, img = cap.read()
            if not success: break

            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            game_board = np.zeros((H, W, 3), np.uint8)

            time_left = max(0, int(self.game_duration - (time.time() - start_time)))
            if time_left == 0: game_over = True

            if not game_over:
                cv2.line(game_board, (W // 2, 0), (W // 2, H), (20, 20, 20), 1)

                aim_x, aim_y = prev_aim_x, prev_aim_y
                shoot_command, reload_command = False, False

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        wx = int(handLms.landmark[0].x * W)

                        if wx > W // 2:
                            ix, iy = int(handLms.landmark[8].x * W), int(handLms.landmark[8].y * H)
                            aim_x = int(prev_aim_x + (ix - prev_aim_x) / self.smoothing)
                            aim_y = int(prev_aim_y + (iy - prev_aim_y) / self.smoothing)
                            prev_aim_x, prev_aim_y = aim_x, aim_y
                        else:
                            t_tip = handLms.landmark[4]
                            i_tip = handLms.landmark[8]
                            dist = math.hypot(int(i_tip.x * W) - int(t_tip.x * W), int(i_tip.y * H) - int(t_tip.y * H))

                            if dist < 45:
                                if not trigger_active: shoot_command, trigger_active = True, True
                            elif dist > 120:
                                trigger_active, reload_command = False, True
                            else:
                                trigger_active = False

                if shoot_command and ammo > 0:
                    ammo -= 1
                    cv2.circle(game_board, (aim_x, aim_y), 60, (255, 255, 255), 15)
                    for i in range(len(targets) - 1, -1, -1):
                        tx, ty, _, _, size, _ = targets[i]
                        if math.sqrt((aim_x - tx) ** 2 + (aim_y - ty) ** 2) < size:
                            del targets[i]
                            score += 100
                            break

                if reload_command: ammo = self.max_ammo

                if len(targets) < self.max_targets and time.time() - last_target_time > spawn_rate:
                    s = random.randint(40, 80)
                    targets.append([random.randint(s, W - s), random.randint(s, H - s), random.randint(-5, 5),
                                    random.randint(-5, 5), s,
                                    (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))])
                    last_target_time = time.time()

                for t in targets:
                    t[0] += t[2];
                    t[1] += t[3]
                    if t[0] < t[4] or t[0] > W - t[4]: t[2] *= -1
                    if t[1] < t[4] or t[1] > H - t[4]: t[3] *= -1
                    cv2.circle(game_board, (t[0], t[1]), t[4], t[5], -1)
                    cv2.circle(game_board, (t[0], t[1]), t[4], (255, 255, 255), 3)

                cv2.line(game_board, (aim_x - 30, aim_y), (aim_x + 30, aim_y), (0, 255, 0), 3)
                cv2.line(game_board, (aim_x, aim_y - 30), (aim_x, aim_y + 30), (0, 255, 0), 3)

                cv2.putText(game_board, f"SCORE: {score}", (80, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 3)
                cv2.putText(game_board, f"AMMO: {ammo}", (80, 180), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 255, 255), 3)
                cv2.putText(game_board, f"TIME: {time_left}s", (W - 400, 100), cv2.FONT_HERSHEY_SIMPLEX, 2,
                            (255, 255, 255), 3)
            else:
                cv2.putText(game_board, "GAME OVER", (W // 2 - 400, H // 2), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255),
                            10)
                cv2.putText(game_board, f"FINAL SCORE: {score}", (W // 2 - 380, H // 2 + 150), cv2.FONT_HERSHEY_SIMPLEX,
                            2.5, (255, 255, 255), 5)
                cv2.putText(game_board, "Press 'ESC' to Exit", (W // 2 - 250, H - 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                            (100, 100, 100), 2)

            cv2.imshow("AI Shooting Range - STANDALONE DEMO", game_board)
            if cv2.waitKey(1) & 0xFF == ord('esc'): break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    game = Shooter()
    game.run()
