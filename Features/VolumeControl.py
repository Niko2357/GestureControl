import cv2
import math
import pyautogui
import time


class VolumeControl:
    def __init__(self):
        self.citlivost = 1.5
        self.minuly_uhel = None
        pyautogui.PAUSE = 0.001

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

    # TATO FUNKCE NAHRADILA PŮVODNÍ run()
    def process_frame(self, img, results):
        prsty_v_obraze = []
        ruce_data = []
        vidim_petku = False

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                pocet = self.spocitej_prsty(handLms)
                prsty_v_obraze.append(pocet)
                ruce_data.append((pocet, handLms))

            if 5 in prsty_v_obraze: vidim_petku = True

            nasel_ovladac = False
            if vidim_petku:
                for pocet, lms in ruce_data:
                    if pocet == 1:  # Ruka, která ukazuje 1 prst (ovládá)
                        nasel_ovladac = True
                        h_im, w_im, _ = img.shape
                        x_wrist, y_wrist = lms.landmark[0].x * w_im, lms.landmark[0].y * h_im
                        x_thumb, y_thumb = lms.landmark[4].x * w_im, lms.landmark[4].y * h_im
                        dx = abs(x_thumb - x_wrist)
                        dy = y_wrist - y_thumb
                        aktualni_uhel = math.degrees(math.atan2(dy, dx))
                        aktualni_uhel = max(0, min(90, aktualni_uhel))

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
