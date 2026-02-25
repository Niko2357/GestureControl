import cv2
import mediapipe as mp
import random
import time
import math
import base64
import eel

def run(should_quit=None):
    print("--- LAUNCHED: BUBBLE CATCHER ---")
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
    cap.set(3, 1280)
    cap.set(4, 720)

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    skore = 0
    start_time = time.time()
    herni_cas = 30
    target_x = random.randint(100, 1000)
    target_y = random.randint(100, 500)
    target_radius = 40
    target_color = (0, 165, 255)

    while True:
        if should_quit and should_quit():
            break

        success, img = cap.read()
        if not success: break

        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        h, w, c = img.shape

        index_finger_tip = None

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                lm = handLms.landmark[8]
                cx, cy = int(lm.x * w), int(lm.y * h)
                index_finger_tip = (cx, cy)
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        zbyvajici_cas = int(herni_cas - (time.time() - start_time))

        if zbyvajici_cas > 0:
            cv2.circle(img, (target_x, target_y), target_radius, target_color, cv2.FILLED)
            cv2.circle(img, (target_x, target_y), target_radius + 5, (255, 255, 255), 2)

            if index_finger_tip:
                fx, fy = index_finger_tip
                vzdalenost = math.sqrt((fx - target_x) ** 2 + (fy - target_y) ** 2)

                if vzdalenost < target_radius:
                    skore += 1
                    target_x = random.randint(100, w - 100)
                    target_y = random.randint(100, h - 100)
                    target_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            cv2.putText(img, "GAME OVER", (w // 2 - 200, h // 2), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5)
            cv2.putText(img, f"Score: {skore}", (w // 2 - 100, h // 2 + 100), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 2)

        cv2.putText(img, f'SCORE: {skore}', (50, 80), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)
        cv2.putText(img, f'TIME: {zbyvajici_cas}s', (w - 300, 80), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 2)

        _, buffer = cv2.imencode('.jpg', img)
        b64_str = base64.b64encode(buffer).decode('utf-8')
        try: eel.update_game_frame(b64_str)()
        except Exception: pass

        cv2.waitKey(1)
        if zbyvajici_cas <= 0:
            time.sleep(2)
            break

    cap.release()
    return skore


