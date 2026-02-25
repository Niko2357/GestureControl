import math
import time
import mediapipe as mp
import tkinter as tk
import threading

W, H = 1280, 720


def show_os_hologram(time_str):
    """Vytvoří průhledné systémové okno s hodinami, které za 2 vteřiny samo zmizí."""

    def create_overlay():
        root = tk.Tk()
        # Odstraní okraje, křížek a lištu
        root.overrideredirect(True)
        # Zůstane nad všemi programy (i nad hrami a prohlížečem)
        root.attributes('-topmost', True)
        # Udělá z černé barvy 100% průhlednost!
        root.attributes('-transparentcolor', 'black')
        root.configure(bg='black')

        # Pozice: Pravý dolní roh (přizpůsobí se monitoru)
        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()
        x = ws - 350
        y = hs - 180
        root.geometry(f"300x150+{x}+{y}")

        # Vykreslení textu
        lbl_title = tk.Label(root, text="[ SYSTEM TIME ]", font=('Courier', 12, 'bold'), fg='#00f3ff', bg='black')
        lbl_title.pack(pady=(20, 0))

        lbl_time = tk.Label(root, text=time_str, font=('Courier', 55, 'bold'), fg='white', bg='black')
        lbl_time.pack()

        # Samozničení po 2000 ms (2 vteřiny)
        root.after(2000, root.destroy)
        root.mainloop()

    # Spustí se jako samostatné vlákno, aby to nezaseklo detekci kamery
    threading.Thread(target=create_overlay, daemon=True).start()


class SmartWatch:
    last_trigger = 0  # Chrání před tím, aby to nespamovalo tisíc oken za vteřinu

    def __init__(self):
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=2)

    @staticmethod
    def check_time(img, results, draw_surface=None):
        if results.multi_hand_landmarks and len(results.multi_hand_landmarks) == 2:
            h1 = results.multi_hand_landmarks[0]
            h2 = results.multi_hand_landmarks[1]

            p1_ix, p1_iy = int(h1.landmark[8].x * W), int(h1.landmark[8].y * H)
            p1_wx, p1_wy = int(h1.landmark[0].x * W), int(h1.landmark[0].y * H)

            p2_ix, p2_iy = int(h2.landmark[8].x * W), int(h2.landmark[8].y * H)
            p2_wx, p2_wy = int(h2.landmark[0].x * W), int(h2.landmark[0].y * H)

            hit = False
            if math.hypot(p1_ix - p2_wx, p1_iy - p2_wy) < 60:
                hit = True
            elif math.hypot(p2_ix - p1_wx, p2_iy - p1_wy) < 60:
                hit = True

            if hit and (time.time() - SmartWatch.last_trigger > 3):
                SmartWatch.last_trigger = time.time()
                current_time = time.strftime("%H:%M")
                show_os_hologram(current_time)


