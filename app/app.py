import eel
import threading
import cv2

eel.init('.')


@eel.expose
def check_camera_py():
    print("Provádím diagnostiku optického senzoru...")
    for i in range(3):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap.isOpened():
            success, _ = cap.read()
            cap.release()
            if success:
                print(f"Kamera úspěšně nalezena na indexu {i}.")
                return True

    print("Kritická chyba: Žádná kamera neodesílá obraz.")
    return False


@eel.expose
def run_shooting():
    from Games import Shooter
    hra = Shooter.Shooter()
    threading.Thread(target=hra.run, daemon=True).start()


@eel.expose
def run_karate():
    from Games import KarateChop
    hra = KarateChop.KarateChop()
    threading.Thread(target=hra.run, daemon=True).start()


@eel.expose
def run_bubbles():
    from Games import bubbleCatcher
    threading.Thread(target=bubbleCatcher.run, daemon=True).start()


@eel.expose
def run_rps():
    from Games import rockPaperScissors
    threading.Thread(target=rockPaperScissors.run, daemon=True).start()


@eel.expose
def run_volume():
    from Features import VolumeControl
    threading.Thread(target=VolumeControl.VolumeControl.run, daemon=True).start()


@eel.expose
def run_watch():
    from Features import SmartWatch
    threading.Thread(target=SmartWatch.SmartWatch.check_time, daemon=True).start()


eel.start('index.html', size=(1200, 800))
