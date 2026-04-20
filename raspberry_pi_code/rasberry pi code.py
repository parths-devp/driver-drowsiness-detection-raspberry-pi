import cv2
import RPi.GPIO as GPIO
import mediapipe as mp
import numpy as np
import time
import os
from picamera2 import Picamera2

print("Starting Drowsiness Detection System")

# Detect if GUI available
GUI = "DISPLAY" in os.environ
print("GUI Mode:", GUI)

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

print("Camera started")

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESHOLD = 0.25
DROWSINESS_THRESHOLD = 2.0

closed_frames = 0

BUZZER_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

buzzer = GPIO.PWM(BUZZER_PIN, 2500)
buzzer.start(0)

print("Buzzer initialized")


def calculate_ear(landmarks, eye_indices):

    p1 = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
    p2 = np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y])
    p3 = np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y])
    p4 = np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y])
    p5 = np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y])
    p6 = np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y])

    vertical_dist1 = np.linalg.norm(p2 - p6)
    vertical_dist2 = np.linalg.norm(p3 - p5)
    horizontal_dist = np.linalg.norm(p1 - p4)

    ear = (vertical_dist1 + vertical_dist2) / (2 * horizontal_dist)

    return ear


prev_time = time.time()

while True:

    frame = picam2.capture_array()
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    current_time = time.time()
    frame_fps = 1 / (current_time - prev_time) if current_time != prev_time else 30
    prev_time = current_time

    drowsiness_detected = False
    left_ear = 0
    right_ear = 0
    closed_time_display = 0

    if result.multi_face_landmarks:

        face = result.multi_face_landmarks[0]
        landmarks = face.landmark

        left_ear = calculate_ear(landmarks, LEFT_EYE)
        right_ear = calculate_ear(landmarks, RIGHT_EYE)

        avg_ear = (left_ear + right_ear) / 2

        print("Left EAR:", left_ear, "Right EAR:", right_ear)

        h, w, _ = frame.shape

        if GUI:
            for idx in LEFT_EYE:
                x = int(landmarks[idx].x * w)
                y = int(landmarks[idx].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)

            for idx in RIGHT_EYE:
                x = int(landmarks[idx].x * w)
                y = int(landmarks[idx].y * h)
                cv2.circle(frame, (x, y), 2, (0, 255, 255), -1)

        if avg_ear < EAR_THRESHOLD:

            closed_frames += 1
            closed_time = closed_frames / frame_fps
            closed_time_display = closed_time

            if closed_time >= DROWSINESS_THRESHOLD:

                print("DROWSINESS DETECTED")
                drowsiness_detected = True

        else:
            closed_frames = 0

    if GUI:

        cv2.putText(frame, f"Left EAR: {left_ear:.2f}", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f"Right EAR: {right_ear:.2f}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f"Closed Time: {closed_time_display:.2f}s", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    if drowsiness_detected:

        if GUI:
            cv2.putText(frame, "DROWSY!", (200, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 3)

        for freq in range(2500, 5000, 50):
            buzzer.ChangeFrequency(freq)
            buzzer.ChangeDutyCycle(50)
            time.sleep(0.003)

        for freq in range(5000, 2500, -50):
            buzzer.ChangeFrequency(freq)
            buzzer.ChangeDutyCycle(50)
            time.sleep(0.003)

    else:

        buzzer.ChangeDutyCycle(0)

        if GUI:
            cv2.putText(frame, "Awake", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 255, 0), 2)

    if GUI:
        cv2.imshow("Drowsiness Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break


if GUI:
    cv2.destroyAllWindows()

GPIO.cleanup()
