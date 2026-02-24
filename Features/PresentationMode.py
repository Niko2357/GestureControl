import mediapipe as mp
import pyautogui
import time
import cv2


class PresentationMode:
    def __init__(self):
        # We track the wrist for macro-movements like swiping
        self.swipe_threshold = 0.15  # Minimum distance to trigger a swipe
        self.cooldown = 1.0  # 1 second cooldown between swipes to prevent double-skips
        self.last_swipe_time = 0
        self.start_x = None
        self.is_tracking = False

    def process_frame(self, img, results):
        current_time = time.time()

        # If we are in cooldown, draw a warning and ignore movements
        if current_time - self.last_swipe_time < self.cooldown:
            h, w, _ = img.shape
            cv2.putText(img, "SWIPE COOLDOWN...", (w // 2 - 150, 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            return

        if results.multi_hand_landmarks:
            # We only track the first detected hand for swiping
            handLms = results.multi_hand_landmarks[0]
            wrist = handLms.landmark[0]  # Landmark 0 is the wrist

            # Start tracking motion
            if not self.is_tracking:
                self.start_x = wrist.x
                self.is_tracking = True
            else:
                # Calculate horizontal difference
                dx = wrist.x - self.start_x

                # Check if the horizontal movement exceeds our swipe threshold
                if abs(dx) > self.swipe_threshold:
                    if dx > 0:
                        # Hand moved Left to Right -> Swipe Right -> Previous Slide
                        pyautogui.press('left')
                        print("SWIPE RIGHT DETECTED -> PREVIOUS SLIDE")
                    else:
                        # Hand moved Right to Left -> Swipe Left -> Next Slide
                        pyautogui.press('right')
                        print("SWIPE LEFT DETECTED -> NEXT SLIDE")

                    # Trigger cooldown and reset tracking
                    self.last_swipe_time = current_time
                    self.is_tracking = False

                    # Visual indicator for tracking (optional, visible if Camera View is ON)
                h, w, _ = img.shape
                cv2.circle(img, (int(wrist.x * w), int(wrist.y * h)), 15, (255, 0, 255), cv2.FILLED)
        else:
            # Reset tracking if hand is removed from frame
            self.is_tracking = False
