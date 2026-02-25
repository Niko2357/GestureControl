import cv2
import mediapipe as mp
import random
import time
import eel
import base64


def run(should_quit=None):
    print("--- LAUNCHED: R.P.S. GAME ---")
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

    cap.set(3, 1280)
    cap.set(4, 720)

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    # Game variables & Automation
    game_state = "start"
    timer = time.time()
    result_text = ""
    pc_choice = ""
    player_choice = ""
    score_player = 0
    score_pc = 0
    current_round = 0
    max_rounds = 3

    # Colors
    COLOR_TEXT = (255, 255, 255)
    COLOR_WIN = (0, 255, 0)
    COLOR_LOSE = (0, 0, 255)
    COLOR_TIE = (0, 255, 255)
    result_color = COLOR_TEXT

    def get_gesture(lmList):
        if len(lmList) == 0: return None
        fingers = []
        if lmList[4][1] > lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        tip_ids = [8, 12, 16, 20]
        for id in tip_ids:
            if lmList[id][2] < lmList[id - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        finger_count = fingers.count(1)
        if finger_count == 0:
            return "Rock"
        elif finger_count == 5:
            return "Paper"
        elif finger_count == 2 and fingers[1] == 1 and fingers[2] == 1:
            return "Scissors"
        else:
            return "Unknown"

    while True:
        # CHECK FOR 'Q' QUIT SIGNAL
        if should_quit and should_quit():
            break

        success, img = cap.read()
        if not success:
            break

        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        h, w, c = img.shape

        current_gesture = None

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                lmList = []
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                current_gesture = get_gesture(lmList)
                if current_gesture:
                    cv2.putText(img, f"Detect: {current_gesture}", (10, h - 30), cv2.FONT_HERSHEY_PLAIN, 2,
                                (200, 200, 200), 2)

        # --- GAME LOGIC (AUTOMATIC TIMERS) ---
        time_passed = time.time() - timer

        if game_state == "start":
            cv2.putText(img, "GET READY...", (w // 2 - 200, h // 2), cv2.FONT_HERSHEY_DUPLEX, 2, COLOR_TEXT, 3)
            if time_passed > 3:  # 3 seconds before countdown starts
                game_state = "countdown"
                timer = time.time()

        elif game_state == "countdown":
            if time_passed < 1:
                cv2.putText(img, "3", (w // 2, h // 2), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 5)
            elif time_passed < 2:
                cv2.putText(img, "2", (w // 2, h // 2), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 5)
            elif time_passed < 3:
                cv2.putText(img, "1", (w // 2, h // 2), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 5)
            else:
                # Countdown finished - Evaluate!
                game_state = "result"
                timer = time.time()
                current_round += 1
                player_choice = current_gesture
                pc_choice = random.choice(["Rock", "Scissors", "Paper"])

                if player_choice == pc_choice:
                    result_text = "TIE!"
                    result_color = COLOR_TIE
                elif (player_choice == "Rock" and pc_choice == "Scissors") or \
                        (player_choice == "Paper" and pc_choice == "Rock") or \
                        (player_choice == "Scissors" and pc_choice == "Paper"):
                    result_text = "YOU WIN!"
                    score_player += 1
                    result_color = COLOR_WIN
                else:
                    result_text = "YOU LOSE!"
                    if player_choice != "Unknown" and player_choice is not None:
                        score_pc += 1
                    result_color = COLOR_LOSE

        elif game_state == "result":
            cv2.putText(img, f"You: {player_choice}", (100, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            cv2.putText(img, f"PC: {pc_choice}", (w - 300, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
            cv2.putText(img, result_text, (w // 2 - 200, h // 2 - 100), cv2.FONT_HERSHEY_DUPLEX, 2.5, result_color, 4)

            if time_passed > 3.5:  # Show result for 3.5 seconds
                if current_round < max_rounds:
                    game_state = "countdown"  # Next round
                    timer = time.time()
                else:
                    game_state = "game_over"  # Game finished
                    timer = time.time()

        elif game_state == "game_over":
            cv2.putText(img, "GAME OVER", (w // 2 - 200, h // 2 - 100), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 4)
            if score_player > score_pc:
                cv2.putText(img, "OVERALL WINNER!", (w // 2 - 250, h // 2 + 50), cv2.FONT_HERSHEY_DUPLEX, 2, COLOR_WIN,
                            3)
            elif score_player < score_pc:
                cv2.putText(img, "PC WINS MATCH!", (w // 2 - 250, h // 2 + 50), cv2.FONT_HERSHEY_DUPLEX, 2, COLOR_LOSE,
                            3)
            else:
                cv2.putText(img, "OVERALL TIE!", (w // 2 - 200, h // 2 + 50), cv2.FONT_HERSHEY_DUPLEX, 2, COLOR_TIE, 3)

            # Draw and display the final screen
            _, buffer = cv2.imencode('.jpg', img)
            b64_str = base64.b64encode(buffer).decode('utf-8')
            try:
                eel.update_game_frame(b64_str)()
            except:
                pass

            cv2.waitKey(1)

            if time_passed > 4:
                break
            continue

        # HUD display
        cv2.putText(img, f"SCORE: {score_player} - {score_pc}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255),
                    2)
        cv2.putText(img, f"ROUND: {current_round}/{max_rounds}", (w - 250, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                    (0, 255, 255), 2)

        # SEND FRAME TO WEB
        _, buffer = cv2.imencode('.jpg', img)
        b64_str = base64.b64encode(buffer).decode('utf-8')
        try:
            eel.update_game_frame(b64_str)()
        except Exception:
            pass

        cv2.waitKey(1)

    cap.release()
    return score_player * 50
