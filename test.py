import cv2
import numpy as np

print("--- DIAGNOSTIKA ČERNÉ OBRAZOVKY ---")

# Zkusíme indexy 0, 1, 2
for index in range(3):
    print(f"\nTestuji kameru na indexu {index}...")
    cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)

    # Nastavíme rozlišení (klíčové pro DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    if not cap.isOpened():
        print(f"❌ Index {index}: Nelze otevřít.")
        cap.release()
        continue

    # Přečteme 10 snímků, aby se kamera "zahřála" (někdy první snímky bývají černé)
    frame = None
    for i in range(10):
        ret, frame = cap.read()

    if ret and frame is not None:
        # Matematická kontrola: Je obraz úplně černý?
        total_brightness = np.sum(frame)
        if total_brightness == 0:
            print(f"⚠️ Index {index}: Kamera běží, ale obraz je 100% ČERNÝ (TMA).")
            print("   -> Zkontroluj krytku, světlo nebo zkus jiný USB port.")
        else:
            print(f"✅ Index {index}: OBRAZ NALEZEN! (Není černý)")
            print("   -> Toto je správná kamera pro tvůj projekt.")

            # Ukázat obraz
            while True:
                cv2.imshow(f"Kamera {index} (Q pro konec)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                ret, frame = cap.read()
            cv2.destroyAllWindows()
    else:
        print(f"❌ Index {index}: Kamera otevřena, ale neposílá data (ret=False).")

    cap.release()

print("\n--- KONEC TESTU ---")
