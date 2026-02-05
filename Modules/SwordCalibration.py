import cv2
import numpy as np


def empty(a):
    pass


# Nastavení okna a posuvníků
cv2.namedWindow("Nastaveni Barev")
cv2.resizeWindow("Nastaveni Barev", 640, 240)

# Výchozí hodnoty (odhad)
cv2.createTrackbar("Hue Min", "Nastaveni Barev", 0, 179, empty)
cv2.createTrackbar("Hue Max", "Nastaveni Barev", 179, 179, empty)
cv2.createTrackbar("Sat Min", "Nastaveni Barev", 50, 255, empty)
cv2.createTrackbar("Sat Max", "Nastaveni Barev", 255, 255, empty)
cv2.createTrackbar("Val Min", "Nastaveni Barev", 50, 255, empty)
cv2.createTrackbar("Val Max", "Nastaveni Barev", 255, 255, empty)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 720)

print("--- KALIBRACE BAREV ---")
print("Nalaď posuvníky tak, aby byla vidět JEN tvoje barva (bíle).")
print("Pak si hodnoty opiš.")

while True:
    success, img = cap.read()
    if not success: break

    # Převod do HSV (Hue, Saturation, Value) - v tom se barvy hledají lépe
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Čtení hodnot z posuvníků
    h_min = cv2.getTrackbarPos("Hue Min", "Nastaveni Barev")
    h_max = cv2.getTrackbarPos("Hue Max", "Nastaveni Barev")
    s_min = cv2.getTrackbarPos("Sat Min", "Nastaveni Barev")
    s_max = cv2.getTrackbarPos("Sat Max", "Nastaveni Barev")
    v_min = cv2.getTrackbarPos("Val Min", "Nastaveni Barev")
    v_max = cv2.getTrackbarPos("Val Max", "Nastaveni Barev")

    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])

    # Vytvoření masky (to co je v rozsahu barev bude bílé, zbytek černý)
    mask = cv2.inRange(imgHSV, lower, upper)

    # Zobrazíme výsledek
    result = cv2.bitwise_and(img, img, mask=mask)

    # Zmenšíme okna aby se vešla vedle sebe
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    hstack = np.hstack([img, result])

    cv2.imshow("Original vs Maska (Q pro konec)", cv2.resize(hstack, (1000, 360)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()