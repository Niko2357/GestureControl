import cv2
import mediapipe as mp
import math
import pyautogui
import time
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from Modules.SmartWatch import SmartWatch

W, H = 1280, 720


class VolumeControl:
    def __init__(self):
        self.citlivost = 1.5
        self.minuly_uhel = None
        self.cas_posledni_petky = 0
        pyautogui.PAUSE = 0.001
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils

    def spocitej_prsty(self, hand_landmarks):
        tip_ids = [4, 8, 12, 16, 20]
        prsty = []
        wrist = hand_landmarks.landmark[0]
        thumb_tip = hand_landmarks.landmark[4]
        thumb_ip = hand_landmarks.landmark[3]
        if math.hypot(thumb_tip.x - wrist.x, thumb_tip.y - wrist.y) > math.hypot(thumb_ip.x - wrist.x,
                                                                                 thumb_ip.y - wrist.y):
            prsty.append(1)
        else:
            prsty.append(0)
        for id in range(1, 5):
            if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
                prsty.append(1)
            else:
                prsty.append(0)
        return prsty.count(1)

    def run(self):
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, W)
        cap.set(4, H)
        print("Hlasitost start...")
        while True:
            success, img = cap.read()
            if not success: break
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            SmartWatch.zkontroluj(img, results)

            prsty_v_obraze = []
            ruce_data = []
            vidim_petku = False
            vidim_pest = False

            if results.multi_hand_landmarks:
                for handLms in results.multi_hand_landmarks:
                    pocet = self.spocitej_prsty(handLms)
                    prsty_v_obraze.append(pocet)
                    ruce_data.append((pocet, handLms))

                    color = (200, 200, 200)
                    if pocet == 5: color = (0, 255, 0)
                    if pocet == 1 and 5 in prsty_v_obraze:
                        color = (255, 0, 255)
                    elif pocet == 1:
                        color = (0, 0, 255)
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS,
                                               self.mpDraw.DrawingSpec(color=color))

                if 5 in prsty_v_obraze: vidim_petku = True
                if 0 in prsty_v_obraze: vidim_pest = True

                aktualni_cas = time.time()
                if vidim_petku:
                    self.cas_posledni_petky = aktualni_cas
                    cv2.putText(img, "SYSTEM AKTIVNI", (50, 650), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                else:
                    cv2.putText(img, "ZAMCENO (Ukaz 5 prstu)", (50, 650), cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 0, 255), 2)

                if aktualni_cas - self.cas_posledni_petky < 2.0 and vidim_pest:
                    cv2.putText(img, "NAVRAT DO MENU...", (W // 2 - 200, H // 2), cv2.FONT_HERSHEY_DUPLEX, 2,
                                (0, 0, 255), 4)
                    cv2.imshow("Volume Control", img)
                    cv2.waitKey(1000)
                    break

                nasel_ovladac = False
                if vidim_petku and not vidim_pest:
                    for pocet, lms in ruce_data:
                        if pocet == 1:
                            nasel_ovladac = True
                            h_im, w_im, _ = img.shape
                            x_wrist, y_wrist = lms.landmark[0].x * w_im, lms.landmark[0].y * h_im
                            x_thumb, y_thumb = lms.landmark[4].x * w_im, lms.landmark[4].y * h_im
                            dx = abs(x_thumb - x_wrist)
                            dy = y_wrist - y_thumb
                            aktualni_uhel = math.degrees(math.atan2(dy, dx))
                            aktualni_uhel = max(0, min(90, aktualni_uhel))
                            cv2.line(img, (int(x_wrist), int(y_wrist)), (int(x_thumb), int(y_thumb)), (0, 255, 255), 4)
                            if self.minuly_uhel is not None:
                                rozdil = aktualni_uhel - self.minuly_uhel
                                if abs(rozdil) > self.citlivost:
                                    if rozdil > 0:
                                        pyautogui.press('volumeup')
                                    elif rozdil < 0:
                                        pyautogui.press('volumedown')
                                    self.minuly_uhel = aktualni_uhel
                            else:
                                self.minuly_uhel = aktualni_uhel
                if not nasel_ovladac: self.minuly_uhel = None

            cv2.imshow("Volume Control", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        cap.release()
        cv2.destroyAllWindows()

