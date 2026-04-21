import cv2
import mediapipe as mp
import time
import random
import math

def run(should_quit=None):
    time.sleep(1.0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        return 0

    w, h = 1280, 720
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)

    window_name = "GESTURE HUB - BUBBLE CATCHER"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mp_draw = mp.solutions.drawing_utils

    score = 0
    start_time = time.time()
    game_duration = 30

    target_x = random.randint(100, w - 100)
    target_y = random.randint(100, h - 100)
    target_radius = 40
    target_color = (0, 165, 255)

    try:
        while True:
            if should_quit and should_quit():
                break

            success, img = cap.read()
            if not success:
                break

            img = cv2.resize(img, (w, h))
            img = cv2.flip(img, 1)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = hands.process(img_rgb)

            index_finger_tip = None
            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
                    lm = hand_lms.landmark[8]
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    index_finger_tip = (cx, cy)
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

            time_left = max(0, int(game_duration - (time.time() - start_time)))
            game_over = time_left == 0

            if not game_over:
                cv2.circle(img, (target_x, target_y), target_radius, target_color, cv2.FILLED)
                cv2.circle(img, (target_x, target_y), target_radius + 5, (255, 255, 255), 2)

                if index_finger_tip:
                    fx, fy = index_finger_tip
                    distance = math.sqrt((fx - target_x) ** 2 + (fy - target_y) ** 2)
                    if distance < target_radius:
                        score += 1
                        target_x = random.randint(100, w - 100)
                        target_y = random.randint(100, h - 100)
                        target_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            else:
                cv2.putText(img, "GAME OVER", (w // 2 - 200, h // 2), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5)
                cv2.putText(img, f"Score: {score}", (w // 2 - 100, h // 2 + 100), cv2.FONT_HERSHEY_DUPLEX, 2,
                            (255, 255, 255), 2)

            cv2.putText(img, f'SCORE: {score}', (50, 80), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)
            cv2.putText(img, f'TIME: {time_left}s', (w - 300, 80), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 2)

            cv2.imshow(window_name, img)
            key = cv2.waitKey(1) & 0xFF

            if key == 27 or (should_quit and should_quit()):
                break

            if game_over:
                cv2.imshow(window_name, img)
                cv2.waitKey(3000)
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

    return score
