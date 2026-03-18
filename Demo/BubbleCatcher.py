import cv2
import mediapipe as mp
import numpy as np
import random
import time
import math

W, H = 1920, 1080


class BubbleCatcher:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils
        self.game_duration = 30

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cv2.namedWindow("Bubble Catcher - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Bubble Catcher - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)

        score = 0
        start_time = time.time()
        target_x = random.randint(200, W - 200)
        target_y = random.randint(200, H - 200)
        target_radius = 60
        target_color = (0, 165, 255)

        while True:
            success, img = cap.read()
            if not success: break

            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)
            game_board = np.zeros((H, W, 3), np.uint8)

            index_pos = None
            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    lm = handLms.landmark[8]
                    index_pos = (int(lm.x * W), int(lm.y * H))
                    cv2.circle(game_board, index_pos, 25, (255, 0, 255), -1)

            time_left = max(0, int(self.game_duration - (time.time() - start_time)))

            if time_left > 0:
                cv2.circle(game_board, (target_x, target_y), target_radius, target_color, -1)
                cv2.circle(game_board, (target_x, target_y), target_radius + 10, (255, 255, 255), 3)
                if index_pos:
                    dist = math.hypot(index_pos[0] - target_x, index_pos[1] - target_y)
                    if dist < target_radius:
                        score += 1
                        target_x = random.randint(200, W - 200)
                        target_y = random.randint(200, H - 200)
                        target_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            else:
                cv2.putText(game_board, "TIME'S UP", (W // 2 - 350, H // 2), cv2.FONT_HERSHEY_SIMPLEX, 5, (0, 0, 255),
                            10)
                cv2.putText(game_board, f"FINAL SCORE: {score}", (W // 2 - 300, H // 2 + 150), cv2.FONT_HERSHEY_SIMPLEX,
                            2.5, (255, 255, 255), 5)

            cv2.putText(game_board, f"SCORE: {score}", (80, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.putText(game_board, f"TIME: {time_left}s", (W - 400, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)

            cv2.imshow("Bubble Catcher - STANDALONE DEMO", game_board)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: break
            if time_left <= 0 and time.time() - (start_time + self.game_duration) > 5: break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    game = BubbleCatcher()
    game.run()
