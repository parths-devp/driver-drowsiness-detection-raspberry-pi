import cv2
import mediapipe as mp
import numpy as np
import time
import serial
import os 

mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)
mp_draw = mp.solutions.drawing_utils


cap = cv2.VideoCapture(0)
overlay = cv2.imread(r"C:\Users\parth\Downloads\LEFT EAR.png")
arduino = serial.Serial('COM19', 9600)  
time.sleep(2)


LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]


EAR_THRESHOLD = 0.25


DROWSINESS_THRESHOLD = 2.0


closed_frames = 0
fps = 30 

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
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)  
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
   
    result = face_mesh.process(rgb)
    
    current_time = time.time()
    frame_fps = 1 / (current_time - prev_time) if current_time != prev_time else 30
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
        
        
        h, w, _ = frame.shape
        
        
        for idx in LEFT_EYE:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            cv2.circle(frame, (x, y), 1, (255,255,0), -1)
        
        
        for idx in RIGHT_EYE:
            x = int(landmarks[idx].x * w)
            y = int(landmarks[idx].y * h)
            cv2.circle(frame, (x, y), 1, (255,255,0), -1)
        
        
        if avg_ear < EAR_THRESHOLD:
            closed_frames += 1
            closed_time = closed_frames / frame_fps
            
            
            if closed_time >= DROWSINESS_THRESHOLD:
                drowsiness_detected = True
        else:
            closed_frames = 0
    
    frame[0:100,0:640] = overlay
    cv2.putText(
        frame,
        f"{left_ear:.2f}",
        (140, 36),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    
    
    cv2.putText(
        frame,
        f"{right_ear:.2f}",
        (140, 84),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    
  
    closed_time_display = closed_frames / frame_fps if frame_fps > 0 else 0
    cv2.putText(
        frame,
        f"{closed_time_display:.2f}s",
        (322, 84),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    
    
    cv2.putText(
        frame,
        f"{int(frame_fps)}",
        (532,36),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )
    
    
    if drowsiness_detected:
        arduino.write(b'1')  
        cv2.putText( frame, "DROWSINESS DETECTED!", (80,300 ), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3 )
        cv2.putText( frame, "Please Take a Break!", (180, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3 ) 
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 5)
        cv2.putText(frame, "sleepy", (322, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
       
    else:
        arduino.write(b'0') 

        status = "Awake" if closed_frames == 0 else "Eyes Closing..."
        cv2.putText(frame, status, (322, 36),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8,
                    (0, 255, 0) if status == "Awake" else (0, 165, 255), 2)
        

    cv2.imshow("Driver Drowsiness Detection", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break


cap.release()
cv2.destroyAllWindows()
