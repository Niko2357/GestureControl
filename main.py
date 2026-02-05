import eel
# Importujeme naše třídy ze složky modules
from Modules.VolumeControl import VolumeControl
from Modules.Shooter import Shooter
from Modules.KarateChop import KarateChop

# Inicializace Eelu
eel.init('web')


@eel.expose
def spustit_hlasitost_py():
    app = VolumeControl()
    app.run()


@eel.expose
def spustit_strelnici_py():
    app = Shooter()
    app.run()


@eel.expose
def spustit_katanu_py():
    app = KarateChop()
    app.run()


# Spuštění
if __name__ == "__main__":
    print("Spouštím GESTURE HUB...")
    try:
        eel.start('index.html', size=(500, 700), mode='default')
    except (SystemExit, MemoryError, KeyboardInterrupt):
        pass
