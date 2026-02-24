import cv2
import webbrowser
import time


class CustomGestures:
    def __init__(self):
        # Default empty links (0: Victory, 1: Thumbs Up, 2: Rock On)
        self.links = ["", "", ""]
        self.cooldown = 3.0  # Wait 3 seconds before another gesture can be triggered
        self.last_trigger_time = 0
        self.current_message = ""
        self.message_time = 0

    def update_links(self, link1, link2, link3):
        self.links = [link1, link2, link3]
        print("--- MACRO GESTURES UPDATED ---")

    def check_fingers(self, hand_landmarks):
        tip_ids = [4, 8, 12, 16, 20]
        fingers = []

        # Thumb: check if tip is higher than the lower knuckle
        if hand_landmarks.landmark[4].y < hand_landmarks.landmark[3].y and hand_landmarks.landmark[4].y < \
                hand_landmarks.landmark[5].y:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers
        for id in range(1, 5):
            if hand_landmarks.landmark[tip_ids[id]].y < hand_landmarks.landmark[tip_ids[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def process_frame(self, img, results):
        # Display confirmation message on screen for 2 seconds
        if time.time() - self.message_time < 2.0:
            h, w, _ = img.shape
            cv2.putText(img, self.current_message, (w // 2 - 200, 50), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)

        # If in cooldown, ignore gestures
        if time.time() - self.last_trigger_time < self.cooldown:
            return

        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                fingers = self.check_fingers(handLms)

                triggered_index = -1
                gesture_name = ""

                # 1. VICTORY (Index and Middle)
                if fingers == [0, 1, 1, 0, 0]:
                    triggered_index = 0
                    gesture_name = "[ VICTORY ]"

                # 2. THUMBS UP (Only Thumb)
                elif fingers == [1, 0, 0, 0, 0]:
                    triggered_index = 1
                    gesture_name = "[ THUMBS UP ]"

                # 3. ROCK ON (Index and Pinky up)
                elif fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:
                    triggered_index = 2
                    gesture_name = "[ ROCK ON ]"

                # If a valid gesture is made AND a link is assigned to it
                if triggered_index != -1 and self.links[triggered_index] != "":
                    link = self.links[triggered_index]

                    # Ensure it's a valid URL format
                    if not link.startswith("http") and "." in link:
                        link = "https://" + link

                    try:
                        webbrowser.open(link)
                        self.current_message = f"EXECUTING: {gesture_name}"
                        self.message_time = time.time()
                        self.last_trigger_time = time.time()
                        break
                    except Exception as e:
                        print("Error opening link:", e)

