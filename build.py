import os
import mediapipe
import subprocess

# 1. Najde přesnou cestu k AI modelům MediaPipe u tebe v počítači
mp_path = os.path.dirname(mediapipe.__file__)

# 2. Sestaví ten obří příkaz automaticky s přesnou cestou k MediaPipe
prikaz = [
    "pyinstaller", "--noconfirm", "--onedir", "--windowed",
    "--add-data", "index.html;.",
    "--add-data", "style.css;.",
    "--add-data", "script.js;.",
    "--add-data", "robotic-hand.png;.",
    "--add-data", "Games;Games/",
    "--add-data", "Features;Features/",
    "--add-data", f"{mp_path};mediapipe/",
    "--hidden-import", "cv2",
    "--hidden-import", "mediapipe",
    "--hidden-import", "numpy",
    "--hidden-import", "requests",
    "--hidden-import", "urllib",
    "--hidden-import", "tkinter",
    "--hidden-import", "base64",
    "--hidden-import", "CoreEngine",
    "--hidden-import", "pyautogui",
    "--hidden-import", "eel",
    "app.py"
]

subprocess.run(prikaz)
