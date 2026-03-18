import cv2
import numpy as np
import mediapipe as mp
import math


class AirCanvas:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=1, min_detection_confidence=0.85)
        self.mpDraw = mp.solutions.drawing_utils
        self.colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 0, 0), (255, 255, 255)]
        self.color_index = 0
        self.brush_thickness = 15
        self.eraser_thickness = 100
        self.xp, self.yp = 0, 0
        self.imgCanvas = None
        self.header_h = 100

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

        # Ponecháme nastavení Full HD, ale kód si s tím poradí, i když kamera neumí
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

        cv2.namedWindow("Air Canvas - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("Air Canvas - STANDALONE DEMO", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        while True:
            success, img = cap.read()
            if not success: break

            img = cv2.flip(img, 1)
            h, w, _ = img.shape

            if self.imgCanvas is None or self.imgCanvas.shape[:2] != (h, w):
                self.imgCanvas = np.zeros((h, w, 3), np.uint8)
                self.header_h = int(h * 0.15)  # Dynamická výška lišty (15% výšky)

            # --- DYNAMICKÉ ROZMÍSTĚNÍ TLAČÍTEK ---
            w_btn = w // 5  # Šířka jednoho tlačítka

            # Tlačítka
            cv2.rectangle(img, (0 * w_btn, 0), (1 * w_btn, self.header_h), (0, 0, 255), cv2.FILLED)  # RED
            cv2.rectangle(img, (1 * w_btn, 0), (2 * w_btn, self.header_h), (0, 255, 0), cv2.FILLED)  # GREEN
            cv2.rectangle(img, (2 * w_btn, 0), (3 * w_btn, self.header_h), (255, 0, 0), cv2.FILLED)  # BLUE
            cv2.rectangle(img, (3 * w_btn, 0), (4 * w_btn, self.header_h), (255, 255, 255), cv2.FILLED)  # ERASER
            cv2.rectangle(img, (4 * w_btn, 0), (5 * w_btn, self.header_h), (50, 50, 50), cv2.FILLED)  # CLEAR

            # Text (přizpůsobený velikosti)
            f_scale = w / 1200  # Měřítko fontu
            f_thick = int(w / 400)  # Tloušťka fontu
            cv2.putText(img, "RED", (int(0.5 * w_btn - 40 * f_scale), int(self.header_h * 0.7)),
                        cv2.FONT_HERSHEY_SIMPLEX, f_scale, (255, 255, 255), f_thick)
            cv2.putText(img, "GREEN", (int(1.5 * w_btn - 70 * f_scale), int(self.header_h * 0.7)),
                        cv2.FONT_HERSHEY_SIMPLEX, f_scale, (255, 255, 255), f_thick)
            cv2.putText(img, "BLUE", (int(2.5 * w_btn - 50 * f_scale), int(self.header_h * 0.7)),
                        cv2.FONT_HERSHEY_SIMPLEX, f_scale, (255, 255, 255), f_thick)
            cv2.putText(img, "ERASER", (int(3.5 * w_btn - 70 * f_scale), int(self.header_h * 0.7)),
                        cv2.FONT_HERSHEY_SIMPLEX, f_scale, (0, 0, 0), f_thick)
            cv2.putText(img, "CLEAR", (int(4.5 * w_btn - 60 * f_scale), int(self.header_h * 0.7)),
                        cv2.FONT_HERSHEY_SIMPLEX, f_scale, (255, 255, 255), f_thick)

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    lmList = []
                    for id, lm in enumerate(handLms.landmark):
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        lmList.append([id, cx, cy])

                    if len(lmList) != 0:
                        x1, y1 = lmList[8][1:]
                        x2, y2 = lmList[12][1:]

                        index_up = lmList[8][2] < lmList[6][2]
                        middle_up = lmList[12][2] < lmList[10][2]

                        if index_up and middle_up:
                            self.xp, self.yp = 0, 0
                            # Vizuální indikátor výběru
                            cv2.circle(img, (int((x1 + x2) / 2), int((y1 + y2) / 2)), 30, self.colors[self.color_index],
                                       5)

                            # Logika výběru v horní liště (dynamická výška)
                            if y1 < self.header_h:
                                self.color_index = x1 // w_btn  # Index barvy podle pozice x
                                if self.color_index == 4:  # CLEAR ALL
                                    self.imgCanvas = np.zeros((h, w, 3), np.uint8)
                                    self.color_index = 0  # Výchozí barva po vymazání

                        elif index_up and not middle_up:
                            cv2.circle(img, (x1, y1), self.brush_thickness, self.colors[self.color_index], cv2.FILLED)

                            if self.xp == 0 and self.yp == 0:
                                self.xp, self.yp = x1, y1

                            thickness = self.eraser_thickness if self.color_index == 3 else self.brush_thickness
                            cv2.line(img, (self.xp, self.yp), (x1, y1), self.colors[self.color_index], thickness)
                            cv2.line(self.imgCanvas, (self.xp, self.yp), (x1, y1), self.colors[self.color_index],
                                     thickness)

                            self.xp, self.yp = x1, y1
                        else:
                            self.xp, self.yp = 0, 0

            # Kombinace plátna a obrazu z kamery
            imgGray = cv2.cvtColor(self.imgCanvas, cv2.COLOR_BGR2GRAY)
            _, imgInv = cv2.threshold(imgGray, 20, 255, cv2.THRESH_BINARY_INV)
            imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)

            img = cv2.bitwise_and(img, imgInv)
            img = cv2.bitwise_or(img, self.imgCanvas)

            cv2.imshow("Air Canvas - STANDALONE DEMO", img)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27: break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    canvas = AirCanvas()
    canvas.run()
