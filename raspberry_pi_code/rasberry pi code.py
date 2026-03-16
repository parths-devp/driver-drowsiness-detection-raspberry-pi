import cv2
import RPi.GPIO as GPIO
import mediapipe as mp
import numpy as np
import time
from picamera2 import Picamera2

print("Starting Drowsiness Detection System")

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration())
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
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb)

    current_time = time.time()
    frame_fps = 1 / (current_time - prev_time) if current_time != prev_time else 30
    prev_time = current_time

    drowsiness_detected = False
    left_ear = 0
    right_ear = 0

    print("Frame processed")

    if result.multi_face_landmarks:

        print("Face detected")

        face = result.multi_face_landmarks[0]
        landmarks = face.landmark

        left_ear = calculate_ear(landmarks, LEFT_EYE)
        right_ear = calculate_ear(landmarks, RIGHT_EYE)

        avg_ear = (left_ear + right_ear) / 2

        print("EAR:", avg_ear)

        if avg_ear < EAR_THRESHOLD:

            closed_frames += 1
            closed_time = closed_frames / frame_fps

            if closed_time >= DROWSINESS_THRESHOLD:

                print("DROWSINESS DETECTED")
                drowsiness_detected = True

        else:
            closed_frames = 0

    if drowsiness_detected:

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
