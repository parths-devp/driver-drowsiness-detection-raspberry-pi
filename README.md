# Driver-Drowsiness-Detection 🚗



A real-time driver monitoring system that detects eye closure using computer vision and triggers an alarm when drowsiness is detected.



This project uses a Raspberry Pi + camera module to monitor the driver's eyes. If the driver's eyes remain closed for a specified duration, a buzzer alarm is activated to alert the driver.



The system is designed to run autonomously, starting automatically when the Raspberry Pi powers on.



### Project Overview



Driver drowsiness is one of the major causes of road accidents. This project demonstrates a lightweight embedded system that can monitor driver alertness using facial landmarks and eye aspect ratio (EAR).



* The system performs the following steps:
* Captures real-time video using the Raspberry Pi camera
* Detects facial landmarks using MediaPipe FaceMesh
* Calculates the Eye Aspect Ratio (EAR)
* Determines if the eyes are closed for a continuous duration
* Triggers a buzzer alarm when drowsiness is detected



### **Features**



* Real-time eye tracking
* Eye Aspect Ratio based drowsiness detection
* Passive buzzer alarm system
* Runs on Raspberry Pi without a monitor
* Automatic startup on boot
* Lightweight and efficient



### **Hardware Components**



* Raspberry Pi (any model supporting camera)
* Raspberry Pi Camera Module
* Passive buzzer module (3-pin)
* Jumper wires
* Power supply
* Hardware Connection



### **Passive buzzer wiring:**



VCC  → 5V or 3.3V

GND  → GND

SIG  → GPIO18



GPIO18 is used because it supports hardware PWM for generating sound frequencies.



### **Software Requirements :**



* Python version: Python 3.10+
* Required libraries:

1. OpenCV
2. MediaPipe
3. NumPy
4. RPi.GPIO
5. Picamera2



### **Install dependencies:**



pip install opencv-python mediapipe numpy RPi.GPIO

sudo apt install python3-picamera2



#### 

### **Project Structure**



driver-drowsiness-detection-system/

│

├── README.md

│

├── arduino\_code/

│   └── buzzer\_control.ino

│

├── raspberry\_pi\_code/

│   ├── drowsiness\_detection.py

│   └── requirements.txt

│

├── hardware\_design/

│   └── enclosure.blend

│

├── images/

│   ├── system\_architecture.png

│   ├── hardware\_setup.jpg

│   └── demo\_output.jpg

│

└── docs/

&nbsp;   └── project\_report.pdf





### **How the Algorithm Works**



The system calculates the Eye Aspect Ratio (EAR) from eye landmarks.



#### **EAR formula:**



#### **EAR = (||p2 - p6|| + ||p3 - p5||) / (2 \* ||p1 - p4||)**



Where:



vertical eye distances measure eye openness



horizontal distance measures eye width



When the EAR drops below a threshold, the system interprets the eye as closed.



If the eye remains closed for more than 2 seconds, the system detects drowsiness and activates the alarm.





### **Running the System**



#### **Run the script manually**:



python3 drowsy\_detection.py



The system will start the camera and begin monitoring the driver.



Press ESC to exit.



Running Automatically on Boot



The system can be configured to start automatically using a Linux service.



### **Create a system service:**



sudo nano /etc/systemd/system/drowsy.service



Enable the service:



sudo systemctl enable drowsy.service



Now the system will start automatically when the Raspberry Pi powers on.



### **Future Improvements**



* Yawn detection
* Head pose estimation
* Mobile notifications
* Fatigue scoring system



### **Applications**



* Automotive driver monitoring systems
* Fleet safety monitoring
* Research on fatigue detection
* Embedded AI vision systems





Team:

Parth Somwanshi, Aditi Machwe, Atharva Sonawane

Walchand College of Engineering



License



This project is released under the MIT License.

