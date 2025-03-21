#include <Servo.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

const char* WIFI_SSID = "ARedmi";
const char* WIFI_PASS = "RandomnieBukvi";

unsigned int localPort = 1235;  // local port to listen on

// buffers for receiving and sending data
char packetBuffer[UDP_TX_PACKET_MAX_SIZE + 1];  // buffer to hold incoming packet,

WiFiUDP Udp;

const char* broadcastIP = "255.255.255.255";  // Широковещательный адрес
const char* message = "car";  // Сообщение для вещания

Servo servoR;
int servoRPin = D4;
Servo servoL;
int servoLPin = D5;
// Определение пинов
const int motor1Pin1 = D2; // IN1 для мотора 1
const int motor1Pin2 = D3; // IN2 для мотора 1
const int motor2Pin1 = D6; // IN3 для мотора 2
const int motor2Pin2 = D7; // IN4 для мотора 2



void setup() {
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(motor2Pin1, OUTPUT);
  pinMode(motor2Pin2, OUTPUT);
  servoR.attach(servoRPin);
  servoL.attach(servoLPin);

  Serial.begin(9600);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(500);
  }
  Serial.print("Connected! IP address: ");
  Serial.println(WiFi.localIP());
  Serial.printf("UDP server on port %d\n", localPort);
  Udp.begin(localPort);
}

void loop() {
  // if there's data available, read a packet
  int packetSize = Udp.parsePacket();
  if (packetSize) {
    Serial.printf("Received packet of size %d from %s:%d\n    (to %s:%d, free heap = %d B)\n", packetSize, Udp.remoteIP().toString().c_str(), Udp.remotePort(), Udp.destinationIP().toString().c_str(), Udp.localPort(), ESP.getFreeHeap());

    // read the packet into packetBuffer
    int n = Udp.read(packetBuffer, UDP_TX_PACKET_MAX_SIZE);
    packetBuffer[n] = 0;
    Serial.println("Contents:");
    Serial.println(packetBuffer);


    handleCommand(packetBuffer);
    
    // Try to parse the packet as an integer
//    int angle = atoi(packetBuffer);
//
//    
//    // Check if the angle is within the valid range for a servo (0-180)
//    if (angle >= 0 && angle <= 180) {
//      Serial.printf("Setting servo to %d degrees\n", angle);
//      myServo.write(angle);  // Write the angle to the servo
//    } else {
//      Serial.println("Received value is out of range.");
//    }
  }else{
    Udp.beginPacket(broadcastIP, localPort);
    Udp.write(message);
    Udp.endPacket();
//    Serial.println("Broadcasting message: car");
  }
}

void handleCommand(String packetBuffer){
  if (packetBuffer == "forward") {
    moveForward();
  } else if (packetBuffer == "backward") {
    moveBackward();
  } else if (packetBuffer == "left") {
    turnLeft();
  } else if (packetBuffer == "right") {
    turnRight();
  } else if (packetBuffer == "stop") {
    stopMotors();
  } else {
    Serial.println("wrong command");
  }
}


void moveForward() {
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, HIGH);
  digitalWrite(motor2Pin2, LOW);

  servoR.write(0);//быстро направо
  servoL.write(180);//быстро налево
}

void moveBackward() {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, HIGH);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, HIGH);
  
  servoR.write(180);//быстро налево
  servoL.write(0);//быстро направо
}

void turnLeft() {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, HIGH);
  digitalWrite(motor2Pin1, HIGH);
  digitalWrite(motor2Pin2, LOW);

  servoR.write(0);//быстро направо
  servoL.write(0);//быстро направо
}

void turnRight() {
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, HIGH);

  servoR.write(180);//быстро налево
  servoL.write(180);//быстро налево
}

void stopMotors() {
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor2Pin1, LOW);
  digitalWrite(motor2Pin2, LOW);

  servoR.write(90);//остановка
  servoL.write(90);//остановка
}
