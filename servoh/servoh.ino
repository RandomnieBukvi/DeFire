#include <Servo.h>
Servo servoX;
Servo servoY;
void setup() {
  Serial.begin(9600);
  servoX.attach(9);
  servoY.attach(10);
}
void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil(';');
    int delimiterIndex = data.indexOf('@');
    if (delimiterIndex != -1) {
      String strX = data.substring(1, delimiterIndex);
      String strY = data.substring(delimiterIndex + 1);
      int posX = strX.toInt();
      int posY = strY.toInt();
     int angleX = map(posX, 0, 1280, 30, 150); 
angleX = 180 - angleX;
int angleY = map(posY, 0, 720, 30, 150); 
//angleY = 180 - angleY;
      servoX.write(angleX);
      servoY.write(angleY);
    }
  }
}
 
