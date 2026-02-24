import cv2
import mediapipe as mp
import random
import time
import math


def run():
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
    cap.set(3, 1920)  # Šířka
    cap.set(4, 1080)  # Výška

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 150)

    # MediaPipe nastavení
    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False,
                          max_num_hands=1,
                          min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    # Proměnné hry
    skore = 0
    start_time = time.time()
    herni_cas = 30  # Hra trvá 30 sekund
    target_x = random.randint(100, 500)
    target_y = random.randint(100, 400)
    target_radius = 40  # Velikost bubliny
    target_color = (0, 165, 255)  # Oranžová barva (BGR)

    print("Hra začíná! Praskej bubliny ukazováčkem.")

    while True:
        success, img = cap.read()
        if not success: break

        # Zrcadlové otočení obrazu (aby se ti lépe ovládalo)
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        h, w, c = img.shape

        # --- LOGIKA DETEKCE RUKY ---
        index_finger_tip = None  # Sem uložíme souřadnice špičky ukazováčku

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                # Získání souřadnic bodu 8 (špička ukazováčku)
                lm = handLms.landmark[8]
                cx, cy = int(lm.x * w), int(lm.y * h)
                index_finger_tip = (cx, cy)

                # Vykreslení "zaměřovače" na prstu
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        # --- HERNÍ LOGIKA ---
        zbyvajici_cas = int(herni_cas - (time.time() - start_time))

        if zbyvajici_cas > 0:
            # Vykreslení cíle (bubliny)
            cv2.circle(img, (target_x, target_y), target_radius, target_color, cv2.FILLED)
            cv2.circle(img, (target_x, target_y), target_radius + 5, (255, 255, 255), 2)  # Bílý okraj

            # Kontrola kolize (Dotkl se prst bubliny?)
            if index_finger_tip:
                fx, fy = index_finger_tip
                # Vzdálenost mezi prstem a středem bubliny (Pythagorova věta)
                vzdalenost = math.sqrt((fx - target_x) ** 2 + (fy - target_y) ** 2)

                if vzdalenost < target_radius:
                    # ZÁSAH!
                    skore += 1
                    # Generuj novou pozici bubliny
                    target_x = random.randint(100, w - 100)
                    target_y = random.randint(100, h - 100)
                    # Změna barvy pro efekt
                    target_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        else:
            # KONEC HRY
            cv2.putText(img, "KONEC HRY", (w // 2 - 200, h // 2), cv2.FONT_HERSHEY_DUPLEX, 3, (0, 0, 255), 5)
            cv2.putText(img, f"Vysledne skore: {skore}", (w // 2 - 180, h // 2 + 100), cv2.FONT_HERSHEY_DUPLEX, 1,
                        (255, 255, 255), 2)

        # --- Vykreslení textů (HUD) ---
        cv2.putText(img, f'Skore: {skore}', (50, 80), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        cv2.putText(img, f'Cas: {zbyvajici_cas}s', (w - 250, 80), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

        cv2.imshow("Rehabilitacni hra", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return skore

