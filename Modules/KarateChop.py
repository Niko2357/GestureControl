import cv2
import mediapipe as mp
import numpy as np
import math
import random
import time
from Modules.SmartWatch import SmartWatch

W, H = 1280, 720


class KarateChop:
    def __init__(self):
        self.mpHands = mp.solutions.hands
        # Potřebujeme jen jednu ruku na sekání, ale povolíme 2 pro hodinky
        self.hands = self.mpHands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils
        self.max_lives = 3

    def run(self):
        print("--- SPUŠTĚNO: KARATE CHOP ---")
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, W)
        cap.set(4, H)

        # Herní proměnné
        fruits = []  # [x, y, rychlost, typ(0=ovoce, 1=bomba), barva, velikost]
        score = 0
        lives = self.max_lives
        game_over = False
        start_time = time.time()
        last_spawn_time = time.time()
        spawn_rate = 1.0  # Každou vteřinu nové ovoce (bude se zrychlovat)

        while True:
            success, img = cap.read()
            if not success: break
            img = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.hands.process(imgRGB)

            # Černé herní pozadí (AR styl - vidíš jen ovoce a svou ruku)
            # Pokud chceš vidět sebe, zakomentuj tento řádek a používej 'img'
            game_board = np.zeros((H, W, 3), np.uint8)
            # Pokud chceš vidět kameru, odkomentuj toto a zakomentuj řádek výše:
            # game_board = img.copy()

            # Chytré hodinky (vykreslit na herní plochu)
            SmartWatch.zkontroluj(img, results, draw_surface=game_board)

            if not game_over:
                # --- 1. RUKA JAKO ČEPEL ---
                blade_line = None  # (x1, y1, x2, y2)

                if results.multi_hand_landmarks:
                    for handLms in results.multi_hand_landmarks:
                        # Vykreslíme ruku (aby hráč viděl, čím seká)
                        self.mpDraw.draw_landmarks(game_board, handLms, self.mpHands.HAND_CONNECTIONS)

                        # Definice Čepele: Čára od Zápěstí (0) k Prostředníčku (12)
                        # To simuluje hranu dlaně pro karate chop
                        wx, wy = int(handLms.landmark[0].x * W), int(handLms.landmark[0].y * H)
                        mx, my = int(handLms.landmark[12].x * W), int(handLms.landmark[12].y * H)

                        # Uložíme si čepel pro kontrolu kolize
                        blade_line = (wx, wy, mx, my)

                        # Vykreslení čepele (zářivá čára)
                        cv2.line(game_board, (wx, wy), (mx, my), (255, 255, 255), 5)  # Jádro
                        cv2.line(game_board, (wx, wy), (mx, my), (0, 255, 255), 15)  # Záře

                # --- 2. GENERUJEME OVOCE ---
                if time.time() - last_spawn_time > spawn_rate:
                    # Náhodná pozice X
                    fx = random.randint(50, W - 50)
                    fy = -50  # Začíná nad obrazovkou
                    fspeed = random.randint(8, 15)  # Rychlost pádu
                    fsize = random.randint(30, 50)

                    # 10% šance na bombu
                    is_bomb = 1 if random.random() < 0.1 else 0

                    # Barva: Bomba=Černá/Červená, Ovoce=Náhodná
                    if is_bomb:
                        color = (50, 50, 50)  # Tmavě šedá
                    else:
                        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

                    fruits.append([fx, fy, fspeed, is_bomb, color, fsize])

                    last_spawn_time = time.time()
                    # Zrychlování hry
                    spawn_rate = max(0.4, spawn_rate * 0.98)

                # --- 3. POHYB A KOLIZE ---
                for f in fruits[:]:  # Iterujeme přes kopii, abychom mohli mazat
                    # Pohyb dolů
                    f[1] += f[2]

                    # Souřadnice ovoce
                    fx, fy, fspeed, is_bomb, color, fsize = f

                    hit = False

                    # Kontrola kolize s čepelí
                    if blade_line:
                        x1, y1, x2, y2 = blade_line
                        # Zjednodušená kolize: Zkontrolujeme vzdálenost středu ovoce od úsečky ruky
                        # 1. Spočítáme vzdálenost bodu (fx,fy) od přímky
                        # Matika: distance = |Ax + By + C| / sqrt(A^2 + B^2)

                        # Vektor ruky
                        px = x2 - x1
                        py = y2 - y1
                        norm = px * px + py * py

                        if norm > 0:  # Abychom nedělili nulou
                            u = ((fx - x1) * px + (fy - y1) * py) / float(norm)

                            if u > 0 and u < 1:  # Bod kolmice leží na úsečce ruky (ne mimo)
                                x_closest = x1 + u * px
                                y_closest = y1 + u * py
                                dist = math.hypot(x_closest - fx, y_closest - fy)

                                if dist < fsize:  # ZÁSAH!
                                    hit = True

                        # Záložní kolize (kdyby matika selhala nebo pro špičku prstu)
                        # Pokud je ovoce blízko špičky prstu (mx, my)
                        if math.hypot(mx - fx, my - fy) < fsize + 20:
                            hit = True

                    if hit:
                        fruits.remove(f)
                        if is_bomb:
                            # GAME OVER EFEKT
                            game_over = True
                            cv2.circle(game_board, (fx, fy), 100, (0, 0, 255), cv2.FILLED)  # Výbuch
                        else:
                            # Zásah ovoce
                            score += 10
                            # Efekt rozseknutí (bílá čára)
                            cv2.circle(game_board, (fx, fy), fsize + 10, (255, 255, 255), cv2.FILLED)

                    # Pokud ovoce propadne dolů
                    elif fy > H + 50:
                        fruits.remove(f)
                        if not is_bomb:  # Pokud nám spadlo dobré ovoce -> ztráta života
                            lives -= 1
                            if lives == 0: game_over = True

                    # Vykreslení ovoce
                    else:
                        cv2.circle(game_board, (fx, fy), fsize, color, cv2.FILLED)
                        # Odlesk na ovoci (aby vypadalo 3D)
                        cv2.circle(game_board, (fx - 10, fy - 10), fsize // 3, (255, 255, 255), cv2.FILLED)
                        if is_bomb:
                            # Nakreslit "X" na bombu
                            cv2.line(game_board, (fx - 15, fy - 15), (fx + 15, fy + 15), (0, 0, 255), 3)
                            cv2.line(game_board, (fx + 15, fy - 15), (fx - 15, fy + 15), (0, 0, 255), 3)

                # --- HUD ---
                cv2.putText(game_board, f"SKORE: {score}", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)

                # Životy (Srdíčka)
                for i in range(lives):
                    cv2.circle(game_board, (W - 50 - (i * 40), 50), 15, (0, 0, 255), cv2.FILLED)

            else:
                # GAME OVER SCREEN
                cv2.putText(game_board, "GAME OVER", (W // 2 - 300, H // 2), cv2.FONT_HERSHEY_DUPLEX, 4, (0, 0, 255), 5)
                cv2.putText(game_board, f"Skore: {score}", (W // 2 - 150, H // 2 + 80), cv2.FONT_HERSHEY_DUPLEX, 2,
                            (255, 255, 255), 2)
                cv2.putText(game_board, "Q = Menu", (W // 2 - 100, H // 2 + 150), cv2.FONT_HERSHEY_PLAIN, 2,
                            (150, 150, 150), 2)

            cv2.imshow("Karate Chop", game_board)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
