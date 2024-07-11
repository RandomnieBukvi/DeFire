#include <Servo.h>

Servo servoX;
Servo servoY;
//Servo servoShoot;
int angleX = 90;
int angleY = 50;
int shoot = 0;

void setup() {
  Serial.begin(9600);
  servoX.attach(9);
  servoY.attach(10);//ya loshara petuh 
//  servoShoot.attach(11);
  servoX.write(angleX);
  servoY.write(angleY);
//  servoShoot.write(0);
  pinMode(4,OUTPUT);
  digitalWrite(4,HIGH);
}


void loop() {
   
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil(';');
    int delimiterIndex1 = data.indexOf('@');
    int delimiterIndex2 = data.indexOf('#');
    if (delimiterIndex1 != -1 && delimiterIndex2 != -1) {
      String strX = data.substring(1, delimiterIndex1);
      String strY = data.substring(delimiterIndex1 + 1, delimiterIndex2);
      String shootStr = data.substring(delimiterIndex2 + 1);

      angleX = strX.toInt();
      angleY = strY.toInt();
      shoot = shootStr.toInt();
      
      servoX.write(angleX);
      servoY.write(angleY);
      if(shoot == 1){
        digitalWrite(4,LOW);
      }else{
        digitalWrite(4,HIGH);
      }
    }
  }
}
