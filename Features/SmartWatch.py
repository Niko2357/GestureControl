import cv2
import math
import time
import datetime
import threading
import tkinter as tk

_show_watch = False


def _watch_window_thread():
    global _show_watch
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-transparentcolor", "black")
    root.config(bg="black")

    w, h = 320, 130
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{sw - w - 40}+{sh - h - 80}")

    canvas = tk.Canvas(root, width=w, height=h, bg="black", highlightthickness=0)
    canvas.pack()

    canvas.create_rectangle(5, 5, w - 5, h - 5, outline="#00f3ff", width=3)
    canvas.create_text(w // 2, 30, text="[ LOCAL SYSTEM TIME ]", fill="#00f3ff", font=("Courier", 13, "bold"))
    time_id = canvas.create_text(w//2, 80, text="00:00", fill="#e0f7ff", font=("Consolas", 55, "bold"))

    root.withdraw()
    visible = False
    hide_timer = 0

    def loop():
        nonlocal visible, hide_timer
        global _show_watch

        if _show_watch:
            _show_watch = False
            hide_timer = time.time() + 3.0
            if not visible:
                root.deiconify()
                visible = True

        if visible:
            canvas.itemconfig(time_id, text=datetime.datetime.now().strftime("%H:%M"))
            if time.time() > hide_timer:
                root.withdraw()
                visible = False

        root.after(100, loop)

    loop()
    root.mainloop()


threading.Thread(target=_watch_window_thread, daemon=True).start()


class SmartWatch:
    @staticmethod
    def check_time(img, results, draw_surface=None):
        global _show_watch

        if not results.multi_hand_landmarks or len(results.multi_hand_landmarks) < 2:
            return

        h, w, _ = img.shape
        hands = results.multi_hand_landmarks

        wrist1 = hands[0].landmark[0]
        index1 = hands[1].landmark[8]
        dist1 = math.hypot((wrist1.x - index1.x) * w, (wrist1.y - index1.y) * h)

        wrist2 = hands[1].landmark[0]
        index2 = hands[0].landmark[8]
        dist2 = math.hypot((wrist2.x - index2.x) * w, (wrist2.y - index2.y) * h)

        if dist1 < 80 or dist2 < 80:
            _show_watch = True



