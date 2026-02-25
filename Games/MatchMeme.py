import cv2
import mediapipe as mp
import time
import random
import requests
import numpy as np
import urllib.request
import base64
import eel


class MatchMeme:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.7)
        self.score = 0
        self.memes = []
        self.load_memes_from_api()

    def load_memes_from_api(self):
        print("Stahuji memy z Imgflip API...")
        try:
            response = requests.get("https://api.imgflip.com/get_memes").json()
            if response["success"]:
                all_memes = response["data"]["memes"]
                # Vybereme 5 náhodných memů pro tuto hru (bez opakování)
                self.memes = random.sample(all_memes, 5)
        except Exception as e:
            print(f"Chyba API: {e}")

    def url_to_image(self, url):
        try:
            resp = urllib.request.urlopen(url)
            image = np.asarray(bytearray(resp.read()), dtype="uint8")
            return cv2.imdecode(image, cv2.IMREAD_COLOR)
        except:
            return np.zeros((300, 300, 3), dtype=np.uint8)

    def run(self, should_quit=None):
        print("--- LAUNCHED: MEME MATCH ---")
        if not self.memes:
            print("Nepodařilo se načíst memy.")
            return 0

        cap = cv2.VideoCapture(0)  # Zkusíme rovnou defaultní kameru
        cap.set(3, 1280)
        cap.set(4, 720)

        for meme_data in self.memes:
            meme_img = self.url_to_image(meme_data["url"])
            meme_img = cv2.resize(meme_img, (400, 400))

            start_time = time.time()
            round_duration = 10

            while True:
                if should_quit and should_quit():
                    break
                success, img = cap.read()
                if not success:
                    break

                img = cv2.flip(img, 1)
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(imgRGB)

                time_left = max(0, int(round_duration - (time.time() - start_time)))

                img[20:420, 860:1260] = meme_img

                # HUD
                cv2.putText(img, f"Napodob Meme! Cas: {time_left}s", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                            (0, 255, 255), 2)
                cv2.putText(img, meme_data["name"], (860, 450), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 255, 255), 2)
                cv2.putText(img, f"SKORE: {self.score}", (30, 120), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)

                # POSÍLÁNÍ OBRAZU DO WEBU (Místo cv2.imshow)
                _, buffer = cv2.imencode('.jpg', img)
                b64_str = base64.b64encode(buffer).decode('utf-8')
                try:
                    eel.update_camera_frame(b64_str)()
                except Exception:
                    pass

                cv2.waitKey(1)

                if time_left == 0:
                    # Po uplynutí času simulujeme zisk bodů podle detekce obličeje
                    if results.multi_face_landmarks:
                        self.score += random.randint(50, 100)  # Zjednodušené skórování za snahu
                    break  # Jdeme na další meme

        cap.release()
        return self.score
