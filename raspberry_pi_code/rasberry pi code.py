import cv2
import mediapipe as mp
import numpy as np
import time
from picamera2 import Picamera2
import RPi.GPIO as GPIO


BUZZER_PIN = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

buzzer = GPIO.PWM(BUZZER_PIN, 2500)
buzzer.start(0)

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESHOLD = 0.25
DROWSINESS_THRESHOLD = 2.0

closed_frames = 0



picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(
        main={"format": "RGB888", "size": (640, 480)}
    )
)
picam2.start()



def calculate_ear(landmarks, eye_indices):

    p1 = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
    p2 = np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y])
    p3 = np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y])
    p4 = np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y])
    p5 = np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y])
    p6 = np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y])

    vertical1 = np.linalg.norm(p2 - p6)
    vertical2 = np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)

    ear = (vertical1 + vertical2) / (2 * horizontal)
    return ear



prev_time = time.time()

try:

    while True:

        frame = picam2.capture_array()
        frame = cv2.flip(frame, 1)

        rgb = frame
        result = face_mesh.process(rgb)

        current_time = time.time()
        fps = 1 / (current_time - prev_time)
        prev_time = current_time

        drowsiness_detected = False
        left_ear = 0
        right_ear = 0

        if result.multi_face_landmarks:

            face = result.multi_face_landmarks[0]
            landmarks = face.landmark

            left_ear = calculate_ear(landmarks, LEFT_EYE)
            right_ear = calculate_ear(landmarks, RIGHT_EYE)

            avg_ear = (left_ear + right_ear) / 2

            if avg_ear < EAR_THRESHOLD:

                closed_frames += 1
                closed_time = closed_frames / fps

                if closed_time >= DROWSINESS_THRESHOLD:
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

        

        cv2.putText(frame, f"Left EAR: {left_ear:.2f}", (20,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

        cv2.putText(frame, f"Right EAR: {right_ear:.2f}", (20,60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

        cv2.putText(frame, f"FPS: {int(fps)}", (20,90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0),2)

        if drowsiness_detected:
            cv2.putText(frame, "DROWSY!", (300,50),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)
        else:
            cv2.putText(frame, "Awake", (300,50),
                        cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

        cv2.imshow("Drowsiness Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    pass

finally:

    buzzer.stop()
    GPIO.cleanup()
    cv2.destroyAllWindows()