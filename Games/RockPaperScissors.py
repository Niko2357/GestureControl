import cv2
import mediapipe as mp
import random
import time
import numpy as np

class RockPaperScissors:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mpDraw = mp.solutions.drawing_utils
        self.max_rounds = 3
        self.w = 1280
        self.h = 720
        self.window_name = "GESTURE HUB - R.P.S."

    def get_gesture(self, hand_landmarks):
        fingers = []
        lm = hand_landmarks.landmark

        if lm[4].x > lm[3].x:
            fingers.append(1)
        else:
            fingers.append(0)

        tip_ids = [8, 12, 16, 20]
        for id in tip_ids:
            if lm[id].y < lm[id - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        count = fingers.count(1)
        if count <= 1:
            return "Rock"
        elif count >= 4:
            return "Paper"
        elif count == 2 and fingers[1] == 1 and fingers[2] == 1:
            return "Scissors"
        return "Unknown"

    def run(self, should_quit=None):
        time.sleep(1.0)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            return 0

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)

        game_state = "start"
        timer = time.time()
        result_text = ""
        pc_choice = ""
        player_choice = ""
        score_player = 0
        score_pc = 0
        current_round = 0

        try:
            while True:
                if should_quit and should_quit():
                    break

                success, img = cap.read()
                if not success:
                    break

                img = cv2.resize(img, (self.w, self.h))
                img = cv2.flip(img, 1)
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.hands.process(img_rgb)

                game_board = np.zeros((self.h, self.w, 3), np.uint8)
                current_gesture = None

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        self.mpDraw.draw_landmarks(game_board, handLms, self.mpHands.HAND_CONNECTIONS)
                        current_gesture = self.get_gesture(handLms)

                time_passed = time.time() - timer

                if game_state == "start":
                    cv2.putText(game_board, "GET READY...", (self.w // 2 - 250, self.h // 2), cv2.FONT_HERSHEY_SIMPLEX, 2.5, (255, 255, 255), 5)
                    if time_passed > 2:
                        game_state = "countdown"
                        timer = time.time()

                elif game_state == "countdown":
                    val = ""
                    if time_passed < 1:
                        val = "3"
                    elif time_passed < 2:
                        val = "2"
                    elif time_passed < 3:
                        val = "1"

                    if val:
                        cv2.putText(game_board, val, (self.w // 2 - 50, self.h // 2), cv2.FONT_HERSHEY_SIMPLEX, 8, (0, 255, 255), 15)
                        if current_gesture:
                            cv2.putText(game_board, f"READY: {current_gesture}", (self.w // 2 - 200, self.h - 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)
                    else:
                        game_state = "result"
                        timer = time.time()
                        current_round += 1
                        player_choice = current_gesture if current_gesture else "None"
                        pc_choice = random.choice(["Rock", "Scissors", "Paper"])

                        if player_choice == pc_choice:
                            result_text = "TIE!"
                        elif (player_choice == "Rock" and pc_choice == "Scissors") or \
                                (player_choice == "Paper" and pc_choice == "Rock") or \
                                (player_choice == "Scissors" and pc_choice == "Paper"):
                            result_text = "YOU WIN!"
                            score_player += 1
                        else:
                            result_text = "YOU LOSE!"
                            score_pc += 1

                elif game_state == "result":
                    color = (0, 255, 255) if "TIE" in result_text else (0, 255, 0) if "WIN" in result_text else (0, 0, 255)
                    cv2.putText(game_board, result_text, (self.w // 2 - 200, self.h // 2 - 100), cv2.FONT_HERSHEY_SIMPLEX, 3, color, 8)
                    cv2.putText(game_board, f"YOU: {player_choice}", (150, self.h // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)
                    cv2.putText(game_board, f"PC: {pc_choice}", (self.w - 450, self.h // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 5)

                    if time_passed > 2.5:
                        if current_round < self.max_rounds:
                            game_state, timer = "countdown", time.time()
                        else:
                            game_state, timer = "game_over", time.time()

                elif game_state == "game_over":
                    if score_player > score_pc:
                        msg, col = "VICTORY!", (0, 255, 0)
                    elif score_pc > score_player:
                        msg, col = "DEFEAT!", (0, 0, 255)
                    else:
                        msg, col = "DRAW!", (0, 255, 255)

                    cv2.putText(game_board, msg, (self.w // 2 - 200, self.h // 2), cv2.FONT_HERSHEY_SIMPLEX, 3, col, 8)
                    cv2.putText(game_board, f"FINAL SCORE: {score_player} - {score_pc}", (self.w // 2 - 250, self.h // 2 + 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 4)

                    cv2.imshow(self.window_name, game_board)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or (should_quit and should_quit()):
                        break
                    if time_passed > 4:
                        break
                    continue

                cv2.putText(game_board, f"SCORE: {score_player} - {score_pc}", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
                cv2.putText(game_board, f"ROUND: {current_round}/{self.max_rounds}", (self.w - 350, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)

                cv2.imshow(self.window_name, game_board)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or (should_quit and should_quit()):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

        return score_player * 50

def run(should_quit=None):
    game = RockPaperScissors()
    return game.run(should_quit)
