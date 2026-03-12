int buzzerPin = 8;
char data;

void setup() {
  pinMode(buzzerPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    data = Serial.read();

    if (data == '1') {
      // Alarm ON
      for (int freq = 2500; freq <= 5000; freq += 50) {
        tone(buzzerPin, freq);
        delay(3);
      }
      for (int freq = 5000; freq >= 2500; freq -= 50) {
        tone(buzzerPin, freq);
        delay(3);
      }
    }
    else if (data == '0') {
      // Alarm OFF
      noTone(buzzerPin);
    }
  }
}