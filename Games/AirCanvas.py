import cv2
import numpy as np
import mediapipe as mp
import base64
import eel
import time


class AirCanvas:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=1, min_detection_confidence=0.85)
        self.mpDraw = mp.solutions.drawing_utils
        self.colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0)]
        self.color_index = 0
        self.brush_thickness = 10
        self.eraser_thickness = 80
        self.xp, self.yp = 0, 0
        self.imgCanvas = None

    def run(self, should_quit=None):
        print("--- LAUNCHED: AIR CANVAS ---")
        cap = None
        for i in range(5):
            temp_cap = cv2.VideoCapture(i)
            if not temp_cap.isOpened():
                continue
            for _ in range(15):
                success, _ = temp_cap.read()
                if success:
                    cap = temp_cap
                    break
                time.sleep(0.1)
            if cap is not None:
                break

        cap.set(3, 1280)
        cap.set(4, 720)

        frame_counter = 0

        while True:
            if should_quit and should_quit():
                break

            success, img = cap.read()
            if not success:
                break

            if self.imgCanvas is None or self.imgCanvas.shape[:2] != img.shape[:2]:
                self.imgCanvas = np.zeros_like(img)

            img = cv2.flip(img, 1)

            cv2.rectangle(img, (50, 20), (250, 90), self.colors[0], cv2.FILLED)
            cv2.putText(img, "RED", (100, 65), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

            cv2.rectangle(img, (300, 20), (500, 90), self.colors[1], cv2.FILLED)
            cv2.putText(img, "GREEN", (340, 65), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

            cv2.rectangle(img, (550, 20), (750, 90), self.colors[2], cv2.FILLED)
            cv2.putText(img, "BLUE", (600, 65), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

            cv2.rectangle(img, (800, 20), (1000, 90), (255, 255, 255), cv2.FILLED)
            cv2.putText(img, "ERASER", (830, 65), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 0), 2)

            cv2.rectangle(img, (1050, 20), (1230, 90), (50, 50, 50), cv2.FILLED)
            cv2.putText(img, "CLEAR", (1080, 65), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    lmList = []
                    for id, lm in enumerate(handLms.landmark):
                        h, w, c = img.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])

                    if len(lmList) != 0:
                        x1, y1 = lmList[8][1:]
                        x2, y2 = lmList[12][1:]

                        fingers = []
                        if lmList[8][2] < lmList[6][2]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                        if lmList[12][2] < lmList[10][2]:
                            fingers.append(1)
                        else:
                            fingers.append(0)

                        if fingers[0] and fingers[1]:
                            self.xp, self.yp = 0, 0
                            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), self.colors[self.color_index], cv2.FILLED)
                            if y1 < 90:
                                if 50 < x1 < 250:
                                    self.color_index = 0
                                elif 300 < x1 < 500:
                                    self.color_index = 1
                                elif 550 < x1 < 750:
                                    self.color_index = 2
                                elif 800 < x1 < 1000:
                                    self.color_index = 3
                                elif 1050 < x1 < 1230:
                                    self.imgCanvas = np.zeros_like(img)

                        elif fingers[0] and not fingers[1]:
                            cv2.circle(img, (x1, y1), 15, self.colors[self.color_index], cv2.FILLED)
                            if self.xp == 0 and self.yp == 0:
                                self.xp, self.yp = x1, y1

                            if self.color_index == 3:
                                cv2.line(img, (self.xp, self.yp), (x1, y1), self.colors[self.color_index],
                                         self.eraser_thickness)
                                cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.colors[self.color_index],
                                         self.eraser_thickness)
                            else:
                                cv2.line(img, (self.xp, self.yp), (x1, y1), self.colors[self.color_index],
                                         self.brush_thickness)
                                cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.colors[self.color_index],
                                         self.brush_thickness)

                            self.xp, self.yp = x1, y1

            imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

            img = cv2.bitwise_and(img, imgInv)
            img = cv2.bitwise_or(img, self.imgCanvas)

            # --- ODESLÁNÍ DO WEBU (Zrychleně a bez chyb) ---
            frame_counter += 1
            if frame_counter % 2 == 0:
                small_img = cv2.resize(img, (640, 360))
                _, buffer = cv2.imencode('.jpg', small_img, [cv2.IMWRITE_JPEG_QUALITY, 60])
                b64_str = base64.b64encode(buffer).decode('utf-8')
                try:
                    eel.update_game_frame(b64_str)()
                except Exception:
                    pass

            cv2.waitKey(1)

        cap.release()

