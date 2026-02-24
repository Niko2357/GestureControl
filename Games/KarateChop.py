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

    def run(self):
        print("--- LAUNCHED: KARATE CHOP ---")
        cap = None
        for i in range(3):
            temp_cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if temp_cap.isOpened():
                success, _ = temp_cap.read()
                if success:
                    cap = temp_cap
                    break
                else:
                    temp_cap.release()

        if cap is None:
            print("CRITICAL: Camera not found!")
            return 0

        cap.set(3, W)
        cap.set(4, H)

        # Game Variables
        # Format: [x, y, velocity_x, velocity_y, is_bomb, color, size]
        fruits = []
        score = 0
        lives = self.max_lives
        game_over = False
        start_time = time.time()
        last_spawn_time = time.time()
        spawn_rate = 1.0
        gravity = 1.2  # Physics: Pulls objects down every frame

        while True:
            success, img = cap.read()
            if not success: break
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            # Black background (AR style)
            game_board = np.zeros((H, W, 3), np.uint8)

            SmartWatch.check_time(img, results, draw_surface=game_board)

            if not game_over:
                # --- 1. BLADE DETECTION (PINKY FINGER) ---
                blade_line = None

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        self.mpDraw.draw_landmarks(game_board, handLms, self.mpHands.HAND_CONNECTIONS)

                        # Define Blade: From Wrist (0) to Pinky Tip (20)
                        wx, wy = int(handLms.landmark[0].x * W), int(handLms.landmark[0].y * H)
                        px, py = int(handLms.landmark[20].x * W), int(handLms.landmark[20].y * H)

                        blade_line = (wx, wy, px, py)

                        # Draw the blade glowing effect
                        cv2.line(game_board, (wx, wy), (px, py), (255, 255, 255), 5)  # Core
                        cv2.line(game_board, (wx, wy), (px, py), (0, 255, 255), 15)  # Glow

                # --- 2. FRUIT SPAWN (THROWN UPWARDS) ---
                if time.time() - last_spawn_time > spawn_rate:
                    fsize = random.randint(40, 60)
                    fx = random.randint(150, W - 150)
                    fy = H + 50  # Spawns BELOW the screen

                    # Physics parameters for the throw
                    vx = random.uniform(-6, 6)  # Drift left or right
                    vy = random.uniform(-28, -38)  # Strong upward force

                    is_bomb = 1 if random.random() < 0.15 else 0

                    if is_bomb:
                        color = (50, 50, 50)  # Dark grey bomb
                    else:
                        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

                    fruits.append([fx, fy, vx, vy, is_bomb, color, fsize])

                    last_spawn_time = time.time()
                    spawn_rate = max(0.4, spawn_rate * 0.98)  # Speeds up over time

                # --- 3. PHYSICS & COLLISION ---
                for f in fruits[:]:
                    # Apply gravity and movement
                    f[3] += gravity  # vy increases (becomes positive/downward) over time
                    f[0] += f[2]  # move x
                    f[1] += f[3]  # move y

                    fx_curr, fy_curr, vx, vy, is_bomb, color, fsize = f

                    hit = False

                    # Check collision with the Pinky blade
                    if blade_line:
                        x1, y1, x2, y2 = blade_line

                        # Direct collision with the Pinky tip
                        if math.hypot(x2 - fx_curr, y2 - fy_curr) < fsize + 20:
                            hit = True
                        else:
                            # Advanced line collision (distance from point to line segment)
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
                            cv2.circle(game_board, (int(fx_curr), int(fy_curr)), 100, (0, 0, 255),
                                       cv2.FILLED)  # Explosion
                        else:
                            score += 10
                            cv2.circle(game_board, (int(fx_curr), int(fy_curr)), fsize + 15, (255, 255, 255),
                                       cv2.FILLED)  # Slash effect

                    # Remove if it falls back down off screen
                    elif fy_curr > H + 100 and vy > 0:
                        fruits.remove(f)
                        if not is_bomb:
                            lives -= 1
                            if lives <= 0: game_over = True

                    # Draw the object
                    else:
                        cv2.circle(game_board, (int(fx_curr), int(fy_curr)), fsize, color, cv2.FILLED)
                        cv2.circle(game_board, (int(fx_curr) - 10, int(fy_curr) - 10), fsize // 3, (255, 255, 255),
                                   cv2.FILLED)  # Highlight
                        if is_bomb:
                            cv2.line(game_board, (int(fx_curr) - 15, int(fy_curr) - 15),
                                     (int(fx_curr) + 15, int(fy_curr) + 15), (0, 0, 255), 4)
                            cv2.line(game_board, (int(fx_curr) + 15, int(fy_curr) - 15),
                                     (int(fx_curr) - 15, int(fy_curr) + 15), (0, 0, 255), 4)

                # --- HUD ---
                cv2.putText(game_board, f"SCORE: {score}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)

                # Draw Lives
                for i in range(lives):
                    cv2.circle(game_board, (W - 50 - (i * 40), 50), 15, (0, 0, 255), cv2.FILLED)

            else:
                # GAME OVER SCREEN
                cv2.putText(game_board, "GAME OVER", (W // 2 - 300, H // 2), cv2.FONT_HERSHEY_DUPLEX, 4, (0, 0, 255), 5)
                cv2.putText(game_board, f"Final Score: {score}", (W // 2 - 180, H // 2 + 80), cv2.FONT_HERSHEY_DUPLEX,
                            2, (255, 255, 255), 2)
                cv2.putText(game_board, "Press 'Q' to exit", (W // 2 - 120, H // 2 + 150), cv2.FONT_HERSHEY_PLAIN, 2,
                            (150, 150, 150), 2)

            cv2.imshow("Karate Chop", game_board)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return score
