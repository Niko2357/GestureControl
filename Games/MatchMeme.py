import cv2
import mediapipe as mp
import time
import random
import math


class MatchMeme:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        # Initialize Face Mesh (we need refine_landmarks for better precision)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

        self.score = 0
        self.game_duration = 30  # Game lasts 30 seconds
        self.expressions = ["SMILE", "OPEN MOUTH", "SURPRISE"]
        self.current_target = random.choice(self.expressions)
        self.target_achieved = False
        self.last_switch_time = time.time()

    def calculate_distance(self, p1, p2, img_w, img_h):
        """Helper to calculate distance between two face landmarks."""
        x1, y1 = int(p1.x * img_w), int(p1.y * img_h)
        x2, y2 = int(p2.x * img_w), int(p2.y * img_h)
        return math.hypot(x2 - x1, y2 - y1)

    def run(self):
        print("--- LAUNCHED: MEME FACE MATCH ---")
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
            return 0

        cap.set(3, 1280)
        cap.set(4, 720)

        start_time = time.time()

        while True:
            success, img = cap.read()
            if not success: break

            img = cv2.flip(img, 1)
            img_h, img_w, _ = img.shape
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            results = self.face_mesh.process(imgRGB)

            time_left = max(0, int(self.game_duration - (time.time() - start_time)))
            if time_left == 0:
                break  # Game Over

            face_detected = False

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    face_detected = True

                    # Draw subtle face mesh (optional, for cool cyber effect)
                    self.mp_draw.draw_landmarks(
                        image=img,
                        landmark_list=face_landmarks,
                        connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                        landmark_drawing_spec=None,
                        connection_drawing_spec=self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=1,
                                                                         circle_radius=1)
                    )

                    # Get key landmarks
                    top_lip = face_landmarks.landmark[13]
                    bottom_lip = face_landmarks.landmark[14]
                    left_mouth_corner = face_landmarks.landmark[61]
                    right_mouth_corner = face_landmarks.landmark[291]
                    left_eyebrow = face_landmarks.landmark[105]
                    left_eye_top = face_landmarks.landmark[159]

                    # Calculate facial metrics
                    mouth_height = self.calculate_distance(top_lip, bottom_lip, img_w, img_h)
                    mouth_width = self.calculate_distance(left_mouth_corner, right_mouth_corner, img_w, img_h)
                    eyebrow_height = self.calculate_distance(left_eyebrow, left_eye_top, img_w, img_h)

                    # Logic to detect current expression
                    detected_expression = "NEUTRAL"
                    if mouth_height > 40 and eyebrow_height > 25:
                        detected_expression = "SURPRISE"
                    elif mouth_height > 40:
                        detected_expression = "OPEN MOUTH"
                    elif mouth_width > 110 and mouth_height < 30:
                        detected_expression = "SMILE"

                    # Check if target is met
                    if detected_expression == self.current_target and not self.target_achieved:
                        self.target_achieved = True
                        self.score += 50
                        cv2.putText(img, "MATCH!", (img_w // 2 - 100, img_h // 2), cv2.FONT_HERSHEY_DUPLEX, 3,
                                    (0, 255, 0), 4)
                        cv2.imshow("Meme Face Match", img)
                        cv2.waitKey(500)  # Pause to show success

                        # Generate new target
                        self.current_target = random.choice(self.expressions)
                        self.target_achieved = False
                        self.last_switch_time = time.time()

            # --- HUD (Heads Up Display) ---
            if not face_detected:
                cv2.putText(img, "NO FACE DETECTED", (img_w // 2 - 200, img_h // 2), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                            (0, 0, 255), 3)

            # Show Target
            cv2.rectangle(img, (img_w // 2 - 250, 20), (img_w // 2 + 250, 100), (0, 0, 0), cv2.FILLED)
            cv2.rectangle(img, (img_w // 2 - 250, 20), (img_w // 2 + 250, 100), (255, 0, 255), 2)
            cv2.putText(img, f"TARGET: {self.current_target}", (img_w // 2 - 220, 75), cv2.FONT_HERSHEY_DUPLEX, 1.5,
                        (255, 0, 255), 2)

            cv2.putText(img, f"TIME: {time_left}s", (30, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 255), 2)
            cv2.putText(img, f"SCORE: {self.score}", (img_w - 300, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 0), 2)

            cv2.imshow("Meme Face Match", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return self.score
