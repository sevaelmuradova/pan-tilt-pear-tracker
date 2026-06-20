#include <Servo.h>

Servo panServo;
Servo tiltServo;

void setup() {
  Serial.begin(9600);
  panServo.attach(9);
  tiltServo.attach(10);
  panServo.write(90);
  tiltServo.write(90);
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    int commaIndex = data.indexOf(',');
    if (commaIndex > 0) {
      int panAngle  = data.substring(0, commaIndex).toInt();
      int tiltAngle = data.substring(commaIndex + 1).toInt();
      panAngle  = constrain(panAngle, 0, 180);
      tiltAngle = constrain(tiltAngle, 0, 180);
      panServo.write(panAngle);
      tiltServo.write(tiltAngle);
    }
  }
}