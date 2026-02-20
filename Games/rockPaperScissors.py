import cv2
import mediapipe as mp
import random
import time


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
    cap.set(3, 1280)
    cap.set(4, 720)

    mpHands = mp.solutions.hands
    hands = mpHands.Hands(static_image_mode=False,
                          max_num_hands=1,
                          min_detection_confidence=0.7)
    mpDraw = mp.solutions.drawing_utils

    # Herní proměnné
    stav_hry = "start"  # start, odpocet, vysledek
    timer = 0
    vysledek_text = ""
    pocitac_volba = ""
    hrac_volba = ""
    skore_hrac = 0
    skore_pc = 0

    # Barvy
    BARVA_TEXT = (255, 255, 255)
    BARVA_WIN = (0, 255, 0)
    BARVA_LOSE = (0, 0, 255)
    BARVA_TIE = (0, 255, 255)

    def zjisti_gesto(lmList):
        """
        Rozpozná gesto podle zvednutých prstů.
        Vrací: "Kamen", "Nuzky", "Papir" nebo None
        """
        if len(lmList) == 0: return None

        # Pole pro stavy prstů (1 = nahoře, 0 = dole)
        prsty = []

        # PALEC (je specifický - porovnáváme osu X)
        # Pro pravou ruku: pokud je špička (4) vpravo od kloubu (3)
        if lmList[4][1] > lmList[3][1]:
            prsty.append(1)
        else:
            prsty.append(0)

        # OSTATNÍ 4 PRSTY (porovnáváme osu Y - špička vs spodní kloub)
        # Body: 8 (Ukazovacek), 12 (Prostrednicek), 16 (Pstenicek), 20 (Malicek)
        tip_ids = [8, 12, 16, 20]
        for id in tip_ids:
            if lmList[id][2] < lmList[id - 2][2]:  # Y souřadnice je nahoře menší!
                prsty.append(1)
            else:
                prsty.append(0)

        pocet_prstu = prsty.count(1)

        # LOGIKA GEST
        if pocet_prstu == 0:
            return "Kamen"
        elif pocet_prstu == 5:
            return "Papir"
        elif pocet_prstu == 2 and prsty[1] == 1 and prsty[2] == 1:
            # Pouze ukazováček a prostředníček jsou nahoře
            return "Nuzky"
        else:
            return "Nezname"

    print("Hra běží. Zmáčkni MEZERNÍK pro start kola.")

    while True:
        success, img = cap.read()
        if not success:
            break

        # Zrcadlové otočení a barvy
        img = cv2.flip(img, 1)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        aktualni_gesto = None

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)

                # Získání souřadnic bodů
                lmList = []
                h, w, c = img.shape
                for id, lm in enumerate(handLms.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                aktualni_gesto = zjisti_gesto(lmList)

                # Vypis aktuálně detekovaného gesta (pro kontrolu)
                if aktualni_gesto:
                    cv2.putText(img, f"Vidim: {aktualni_gesto}", (10, 70),
                                cv2.FONT_HERSHEY_PLAIN, 2, (200, 200, 200), 2)

        # --- HERNÍ LOGIKA (STAVY) ---

        # 1. STAV: START (Čekání)
        if stav_hry == "start":
            cv2.putText(img, "Zmackni MEZERNIK pro hru", (w // 2 - 250, h // 2),
                        cv2.FONT_HERSHEY_DUPLEX, 1, BARVA_TEXT, 2)

        # 2. STAV: ODPOČET (3..2..1)
        elif stav_hry == "odpocet":
            cas_ubehlo = time.time() - timer
            if cas_ubehlo < 1:
                cv2.putText(img, "3", (w // 2, h // 2), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 5)
            elif cas_ubehlo < 2:
                cv2.putText(img, "2", (w // 2, h // 2), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 5)
            elif cas_ubehlo < 3:
                cv2.putText(img, "1", (w // 2, h // 2), cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 255), 5)
            else:
                # KONEC ODPOČTU -> VYHODNOCENÍ
                stav_hry = "vysledek"
                hrac_volba = aktualni_gesto
                volby = ["Kamen", "Nuzky", "Papir"]
                pocitac_volba = random.choice(volby)

                # Kdo vyhrál?
                if hrac_volba == pocitac_volba:
                    vysledek_text = "REMIZA!"
                    barva_vysledku = BARVA_TIE
                elif (hrac_volba == "Kamen" and pocitac_volba == "Nuzky") or \
                        (hrac_volba == "Papir" and pocitac_volba == "Kamen") or \
                        (hrac_volba == "Nuzky" and pocitac_volba == "Papir"):
                    vysledek_text = "VYHRALA JSI!"
                    skore_hrac += 1
                    barva_vysledku = BARVA_WIN
                elif hrac_volba == "Nezname" or hrac_volba is None:
                    vysledek_text = "NEPLATNE GESTO"
                    barva_vysledku = (100, 100, 100)
                else:
                    vysledek_text = "PROHRALA JSI..."
                    skore_pc += 1
                    barva_vysledku = BARVA_LOSE

        # 3. STAV: VÝSLEDEK (Zobrazení)
        elif stav_hry == "vysledek":
            cv2.putText(img, f"Ty: {hrac_volba}", (50, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(img, f"PC: {pocitac_volba}", (w - 300, h // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            cv2.putText(img, vysledek_text, (w // 2 - 200, h // 2 - 100), cv2.FONT_HERSHEY_DUPLEX, 2, barva_vysledku, 3)
            cv2.putText(img, "Zmackni MEZERNIK pro dalsi kolo", (w // 2 - 230, h - 50), cv2.FONT_HERSHEY_PLAIN, 1.5,
                        (200, 200, 200), 2)

        # Skóre trvale na obrazovce
        cv2.putText(img, f"Hrac: {skore_hrac}  |  PC: {skore_pc}", (w // 2 - 150, 50), cv2.FONT_HERSHEY_COMPLEX, 1,
                    (255, 255, 0), 2)

        cv2.imshow("Kamen Nuzky Papir AI", img)

        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        if key & 0xFF == ord(' '):  # Mezerník
            if stav_hry == "start" or stav_hry == "vysledek":
                stav_hry = "odpocet"
                timer = time.time()
    cap.release()
    cv2.destroyAllWindows()
