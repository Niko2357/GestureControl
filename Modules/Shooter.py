import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random
from Modules.SmartWatch import SmartWatch

W, H = 1280, 720


class Shooter:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.smoothing = 2.0
        self.max_targets = 12
        self.game_duration = 60
        self.max_naboju = 6

    def run(self):
        print("--- SPUŠTĚNO: AI STŘELNICE ---")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, W)
        cap.set(4, H)
        targets, last_target_time = [], time.time()
        spawn_rate, skore, nabito = 2.0, 0, self.max_naboju
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

            SmartWatch.zkontroluj(img, results, draw_surface=game_board)
            time_left = max(0, int(self.game_duration - (time.time() - start_time)))
            if time_left == 0: game_over = True

            if not game_over:
                cv2.line(game_board, (0, H // 2), (W, H // 2), (30, 30, 30), 1)
                cv2.line(game_board, (W // 2, 0), (W // 2, H), (30, 30, 30), 1)
                aim_x, aim_y = prev_aim_x, prev_aim_y
                shoot_command, reload_command = False, False

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        wx = int(handLms.landmark[0].x * W)
                        if wx > W // 2:
                            ix, iy = int(handLms.landmark[5].x * W), int(handLms.landmark[5].y * H)
                            aim_x = int(prev_aim_x + (ix - prev_aim_x) / self.smoothing)
                            aim_y = int(prev_aim_y + (iy - prev_aim_y) / self.smoothing)
                            prev_aim_x, prev_aim_y = aim_x, aim_y
                        else:
                            t_tip, i_tip = handLms.landmark[4], handLms.landmark[8]
                            x1, y1 = int(t_tip.x * W), int(t_tip.y * H)
                            x2, y2 = int(i_tip.x * W), int(i_tip.y * H)
                            dist = math.hypot(x2 - x1, y2 - y1)
                            if dist < 40:
                                if not trigger_active: shoot_command, trigger_active = True, True
                                cv2.circle(game_board, ((x1 + x2) // 2, (y1 + y2) // 2), 15, (0, 255, 0), cv2.FILLED)
                            elif dist > 100:
                                trigger_active, reload_command = False, True
                                cv2.putText(game_board, "PREBIJIM", (wx, int(handLms.landmark[0].y * H) + 50),
                                            cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 255), 2)
                            else:
                                trigger_active = False

                if shoot_command and nabito > 0:
                    nabito -= 1
                    cv2.circle(game_board, (aim_x, aim_y), 40, (255, 255, 255), cv2.FILLED)
                    for i in range(len(targets) - 1, -1, -1):
                        tx, ty, _, _, size, _ = targets[i]
                        if math.sqrt((aim_x - tx) ** 2 + (aim_y - ty) ** 2) < size:
                            del targets[i]
                            skore += 100
                            cv2.circle(game_board, (tx, ty), size + 15, (0, 255, 255), cv2.FILLED)
                            break
                if reload_command and nabito < self.max_naboju:
                    nabito = self.max_naboju
                    cv2.putText(game_board, "NABITO!", (aim_x, aim_y - 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                if len(targets) < self.max_targets and time.time() - last_target_time > spawn_rate:
                    size = random.randint(40, 70)
                    targets.append(
                        [random.randint(size, W - size), random.randint(size, H - size), random.choice([-4, 4]),
                         random.choice([-4, 4]), size,
                         (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))])
                    last_target_time = time.time()
                for t in targets:
                    t[0] += t[2]
                    t[1] += t[3]
                    if t[0] < t[4] or t[0] > W - t[4]: t[2] *= -1
                    if t[1] < t[4] or t[1] > H - t[4]: t[3] *= -1
                    cv2.circle(game_board, (t[0], t[1]), t[4], t[5], cv2.FILLED)
                    cv2.circle(game_board, (t[0] - 15, t[1] - 10), 8, (255, 255, 255), cv2.FILLED)
                    cv2.circle(game_board, (t[0] + 15, t[1] - 10), 8, (255, 255, 255), cv2.FILLED)

                cv2.line(game_board, (aim_x - 20, aim_y), (aim_x + 20, aim_y), (0, 255, 0), 2)
                cv2.line(game_board, (aim_x, aim_y - 20), (aim_x, aim_y + 20), (0, 255, 0), 2)
                cv2.putText(game_board, f"CAS: {time_left}", (W // 2 - 100, 60), cv2.FONT_HERSHEY_DUPLEX, 2,
                            (0, 255, 0) if time_left > 10 else (0, 0, 255), 3)
                cv2.putText(game_board, f"SKORE: {skore}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)
                for i in range(self.max_naboju):
                    c = (0, 255, 255) if i < nabito else (50, 50, 50)
                    cv2.rectangle(game_board, (W - 180 + (i * 25), H - 60), (W - 180 + (i * 25) + 15, H - 20), c,
                                  cv2.FILLED)
            else:
                cv2.putText(game_board, "GAME OVER", (W // 2 - 300, H // 2 - 50), cv2.FONT_HERSHEY_DUPLEX, 4,
                            (0, 0, 255), 5)
                cv2.putText(game_board, f"Skore: {skore}", (W // 2 - 150, H // 2 + 50), cv2.FONT_HERSHEY_DUPLEX, 2,
                            (255, 255, 255), 2)
                cv2.putText(game_board, "Stiskni Q pro menu", (W // 2 - 150, H // 2 + 120), cv2.FONT_HERSHEY_PLAIN, 1.5,
                            (150, 150, 150), 1)

            cv2.imshow("AI Shooter", game_board)
            if cv2.waitKey(1) & 0xFF == ord('q'): break
        cap.release()
        cv2.destroyAllWindows()
