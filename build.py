import os
import mediapipe
import subprocess

# 1. Najde přesnou cestu k AI modelům MediaPipe u tebe v počítači
mp_path = os.path.dirname(mediapipe.__file__)

# 2. Sestaví obří příkaz automaticky s přesnou cestou k MediaPipe
prikaz = [
    "pyinstaller", "--noconfirm", "--onefile", "--windowed",
    "--add-data", "app/index.html;.",
    "--add-data", "app/style.css;.",
    "--add-data", "app/script.js;.",
    "--add-data", "app/robotic-hand.png;.",
    "--add-data", "*.pkl;.",
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
    "--hidden-import", "sklearn",
    "--hidden-import", "sklearn.ensemble",
    "--hidden-import", "sklearn.ensemble._forest",
    "--hidden-import", "sklearn.tree",
    "--hidden-import", "sklearn.tree._classes",
    "app/app.py"
]

print("Spouštím PyInstaller. Může to trvat několik minut...")
subprocess.run(prikaz)
print("Hotovo! Tvůj .exe soubor najdeš ve složce 'dist'.")
