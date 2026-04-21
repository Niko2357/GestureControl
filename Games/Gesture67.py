import cv2
import mediapipe as mp
import time


class Gesture67:
    def __init__(self):
        # PŘECHOD Z 'HANDS' NA 'POSE' (Sledování těla místo prstů)
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Nejrychlejší model
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.window_name = "GESTURE HUB - SPEED PUMP"
        self.w = 1280
        self.h = 720
        self.game_duration = 20

    def run(self, should_quit=None):
        time.sleep(1.0)
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            return 0

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.h)

        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setWindowProperty(self.window_name, cv2.WND_PROP_TOPMOST, 1)

        score = 0
        state_left = "wait"
        state_right = "wait"
        start_time = time.time()
        game_over = False

        up_thresh = int(0.4 * self.h)
        down_thresh = int(0.6 * self.h)

        try:
            while True:
                if should_quit and should_quit():
                    break

                success, img = cap.read()
                if not success:
                    break

                img = cv2.resize(img, (self.w, self.h))
                img = cv2.flip(img, 1)
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Zpracování celého těla místo malých rukou
                results = self.pose.process(imgRGB)

                time_left = max(0, int(self.game_duration - (time.time() - start_time)))
                if time_left == 0:
                    game_over = True

                if not game_over:
                    cv2.line(img, (0, up_thresh), (self.w, up_thresh), (0, 255, 0), 3)
                    cv2.line(img, (0, down_thresh), (self.w, down_thresh), (0, 0, 255), 3)

                    overlay = img.copy()
                    cv2.rectangle(overlay, (0, 0), (self.w, up_thresh), (0, 255, 0), cv2.FILLED)
                    cv2.rectangle(overlay, (0, down_thresh), (self.w, self.h), (0, 0, 255), cv2.FILLED)
                    cv2.addWeighted(overlay, 0.1, img, 0.9, 0, img)

                    if results.pose_landmarks:
                        # Získání pozice levého (15) a pravého (16) zápěstí
                        left_wrist = results.pose_landmarks.landmark[15]
                        right_wrist = results.pose_landmarks.landmark[16]

                        # Logika pro LEVOU RUKU
                        if left_wrist.visibility > 0.3:
                            ly = int(left_wrist.y * self.h)
                            lx = int(left_wrist.x * self.w)
                            cv2.circle(img, (lx, ly), 25, (255, 0, 0), cv2.FILLED)

                            if ly < up_thresh and state_left != "up":
                                state_left = "up"
                            elif ly > down_thresh and state_left == "up":
                                state_left = "down"
                                score += 1

                        # Logika pro PRAVOU RUKU
                        if right_wrist.visibility > 0.3:
                            ry = int(right_wrist.y * self.h)
                            rx = int(right_wrist.x * self.w)
                            cv2.circle(img, (rx, ry), 25, (0, 255, 255), cv2.FILLED)

                            if ry < up_thresh and state_right != "up":
                                state_right = "up"
                            elif ry > down_thresh and state_right == "up":
                                state_right = "down"
                                score += 1

                    cv2.putText(img, f"SCORE: {score}", (50, 100), cv2.FONT_HERSHEY_DUPLEX, 2.5, (255, 255, 255), 4)
                    cv2.putText(img, f"TIME: {time_left}s", (self.w - 350, 100), cv2.FONT_HERSHEY_DUPLEX, 2,
                                (0, 255, 255), 3)
                else:
                    cv2.putText(img, "GAME OVER", (self.w // 2 - 250, self.h // 2), cv2.FONT_HERSHEY_DUPLEX, 3,
                                (0, 0, 255), 5)
                    cv2.putText(img, f"Final Score: {score}", (self.w // 2 - 200, self.h // 2 + 80),
                                cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 255, 255), 2)

                cv2.imshow(self.window_name, img)
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord('q') or (should_quit and should_quit()):
                    break

                if game_over:
                    cv2.imshow(self.window_name, img)
                    cv2.waitKey(3000)
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        return score
