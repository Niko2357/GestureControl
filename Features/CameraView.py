import cv2
import base64
import eel


class CameraView:
    def __init__(self):
        self.cam_w = 640
        self.cam_h = 480
        self.is_running = False

    def run(self):
        self.is_running = True
        print("--- LAUNCHED: CAMERA ALIGNMENT (WEB FEED) ---")
        cap = None
        for i in range(5):
            temp_cap = cv2.VideoCapture(i)
            if temp_cap.isOpened():
                success, _ = temp_cap.read()
                if success:
                    cap = temp_cap
                    break
                else:
                    temp_cap.release()

        if cap is None:
            print("CRITICAL: Camera not found!")
            return

        cap.set(3, self.cam_w)
        cap.set(4, self.cam_h)

        while self.is_running:
            success, img = cap.read()
            if not success: break

            # Zrcadlové otočení pro přirozený pohyb
            img = cv2.flip(img, 1)

            # Zaměřovací kříž (bez zeleného kruhu)
            cx, cy = self.cam_w // 2, self.cam_h // 2
            cv2.line(img, (cx, cy - 30), (cx, cy + 30), (0, 255, 0), 2)
            cv2.line(img, (cx - 30, cy), (cx + 30, cy), (0, 255, 0), 2)

            # PŘEVOD OBRAZU PRO WEB:
            # 1. Komprese do JPEG
            _, buffer = cv2.imencode('.jpg', img)
            # 2. Převod na Base64 text
            b64_str = base64.b64encode(buffer).decode('utf-8')

            # 3. Odeslání do JavaScriptu k vykreslení
            try:
                eel.update_camera_frame(b64_str)()
            except Exception:
                break  # Zabrání pádu, pokud uživatel mezitím zavře okno aplikace

            # Omezení na ~30 FPS pro snížení zátěže procesoru
            cv2.waitKey(30)

        cap.release()
        print("--- STOPPED: CAMERA ALIGNMENT ---")

    def stop(self):
        # Tato funkce se zavolá po kliknutí na tlačítko "Zavřít" na webu
        self.is_running = False
