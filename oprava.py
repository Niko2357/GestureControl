import os
import shutil
import mediapipe

zdroj = os.path.dirname(mediapipe.__file__)
cil = os.path.join("dist", "app", "_internal", "mediapipe")

print("Kopíruji chybějící AI mozek tam, kam patří...")
shutil.copytree(zdroj, cil, dirs_exist_ok=True)
