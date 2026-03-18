import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random
from Features.SmartWatch import SmartWatch
import base64
import eel

W, H = 1280, 720


class Shooter:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.smoothing = 2.0
        self.max_targets = 12
        self.game_duration = 60
        self.max_ammo = 6

    def run(self, should_quit=None):
        print("--- LAUNCHING: SHOOTING RANGE ---")

        # POJISTKA: Krátce počkáme, než CoreEngine kameru opravdu pustí
        time.sleep(0.5)

        cap = None
        # Zkusíme primárně index 0 s rozhraním DSHOW pro Windows
        for i in [0, 1]:
            temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if temp_cap.isOpened():
                # Ověříme, že z kamery lezou data
                for _ in range(10):
                    success, _ = temp_cap.read()
                    if success:
                        cap = temp_cap
                        break
                    time.sleep(0.1)
            if cap:
                break
            else:
                temp_cap.release()

        if cap is None:
            print("CRITICAL: Camera not found or occupied by another process!")
            return 0

        # Nastavení rozlišení (Shooter počítá s 1280x720)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

        targets, last_target_time = [], time.time()
        spawn_rate, score, ammo = 2.0, 0, self.max_ammo
        start_time, game_over = time.time(), False
        prev_aim_x, prev_aim_y = W // 2, H // 2
        trigger_active = False
        frame_counter = 0

        while True:
            # Kontrola externího ukončení (tlačítko v UI nebo klávesa Q)
            if should_quit and should_quit():
                print("--- GAME TERMINATED BY USER ---")
                break

            success, img = cap.read()
            if not success:
                print("--- LOSS OF CAMERA SIGNAL ---")
                break

            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            game_board = np.zeros((H, W, 3), np.uint8)

            # --- SMART WATCH ---
            SmartWatch.check_time(img, results, draw_surface=game_board)

            time_left = max(0, int(self.game_duration - (time.time() - start_time)))
            if time_left == 0:
                game_over = True

            if not game_over:
                # Zaměřovač a mřížka
                cv2.line(game_board, (0, H // 2), (W, H // 2), (30, 30, 30), 1)
                cv2.line(game_board, (W // 2, 0), (W // 2, H), (30, 30, 30), 1)

                aim_x, aim_y = prev_aim_x, prev_aim_y
                shoot_command, reload_command = False, False

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        wx = int(handLms.landmark[0].x * W)

                        # PRAVÁ RUKA = MÍŘENÍ
                        if wx > W // 2:
                            ix, iy = int(handLms.landmark[5].x * W), int(handLms.landmark[5].y * H)
                            aim_x = int(prev_aim_x + (ix - prev_aim_x) / self.smoothing)
                            aim_y = int(prev_aim_y + (iy - prev_aim_y) / self.smoothing)
                            prev_aim_x, prev_aim_y = aim_x, aim_y

                        # LEVÁ RUKA = STŘELBA / PŘEBÍJENÍ
                        else:
                            t_tip, i_tip = handLms.landmark[4], handLms.landmark[8]
                            dist = math.hypot(int(i_tip.x * W) - int(t_tip.x * W), int(i_tip.y * H) - int(t_tip.y * H))

                            if dist < 40:  # Gesto "Pinch" (stisk)
                                if not trigger_active: shoot_command, trigger_active = True, True
                                cv2.circle(game_board,
                                           (int((t_tip.x + i_tip.x) * W / 2), int((t_tip.y + i_tip.y) * H / 2)), 15,
                                           (0, 255, 0), cv2.FILLED)
                            elif dist > 110:  # Otevřená dlaň
                                trigger_active, reload_command = False, True
                                cv2.putText(game_board, "RELOADING", (wx, 100), cv2.FONT_HERSHEY_PLAIN, 2,
                                            (0, 255, 255), 2)
                            else:
                                trigger_active = False

                # LOGIKA STŘELBY
                if shoot_command and ammo > 0:
                    ammo -= 1
                    cv2.circle(game_board, (aim_x, aim_y), 40, (255, 255, 255), cv2.FILLED)
                    for i in range(len(targets) - 1, -1, -1):
                        tx, ty, _, _, size, _ = targets[i]
                        if math.sqrt((aim_x - tx) ** 2 + (aim_y - ty) ** 2) < size:
                            del targets[i]
                            score += 100
                            cv2.circle(game_board, (tx, ty), size + 20, (0, 255, 255), cv2.FILLED)
                            break

                if reload_command and ammo < self.max_ammo:
                    ammo = self.max_ammo

                # TERČE
                if len(targets) < self.max_targets and time.time() - last_target_time > spawn_rate:
                    size = random.randint(40, 70)
                    targets.append(
                        [random.randint(size, W - size), random.randint(size, H - size), random.choice([-5, 5]),
                         random.choice([-5, 5]), size,
                         (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))])
                    last_target_time = time.time()

                for t in targets:
                    t[0] += t[2];
                    t[1] += t[3]
                    if t[0] < t[4] or t[0] > W - t[4]: t[2] *= -1
                    if t[1] < t[4] or t[1] > H - t[4]: t[3] *= -1
                    cv2.circle(game_board, (t[0], t[1]), t[4], t[5], cv2.FILLED)

                # HUD
                cv2.circle(game_board, (aim_x, aim_y), 20, (0, 255, 0), 2)
                cv2.putText(game_board, f"SCORE: {score}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)
                cv2.putText(game_board, f"TIME: {time_left}", (W - 300, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                            (255, 255, 255), 2)

            else:
                cv2.putText(game_board, "GAME OVER", (W // 2 - 250, H // 2), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5)
                cv2.putText(game_board, f"Final Score: {score}", (W // 2 - 200, H // 2 + 80), cv2.FONT_HERSHEY_DUPLEX,
                            1.5, (255, 255, 255), 2)

            # --- STREAMOVÁNÍ DO WEBU ---
            frame_counter += 1
            if frame_counter % 2 == 0:
                print("FRAME SENT")
                small_board = cv2.resize(game_board, (640, 360))
                _, buffer = cv2.imencode('.jpg', small_board, [cv2.IMWRITE_JPEG_QUALITY, 55])
                b64_str = base64.b64encode(buffer).decode('utf-8')
                try:
                    eel.update_camera_frame(b64_str)()
                except Exception as e:
                    print("EEL ERROR", e)

            if cv2.waitKey(1) & 0xFF == ord('q') or game_over and frame_counter > 200:
                if game_over:
                    time.sleep(2)
                break

        cap.release()
        return score
