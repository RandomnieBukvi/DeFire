#include <WebServer.h>
#include <WiFi.h>
#include <esp32cam.h>
#include <AsyncUDP.h>
#include <ESP32Servo.h>

Servo servoX;
Servo servoY;
const int servoXPin = 15;
const int servoYPin = 13;
const int pumpPin = 12;
int angleX = 90;
int angleY = 90;
int shoot = 0;

AsyncUDP udp;


const char* WIFI_SSID = "ARedmi";//DSL-2740U-77b4
const char* WIFI_PASS = "RandomnieBukvi";//70873528
 
WebServer server(80);

const int ledPin = 4; // Встроенный светодиод на ESP32

static auto hiRes = esp32cam::Resolution::find(1280, 720);


void serveJpg()
{
  auto frame = esp32cam::capture();
  if (frame == nullptr) {
    Serial.println("CAPTURE FAIL");
    server.send(503, "", "");
    return;
  }
  Serial.printf("CAPTURE OK %dx%d %db\n", frame->getWidth(), frame->getHeight(),
                static_cast<int>(frame->size()));
 
  server.setContentLength(frame->size());
  server.send(200, "image/jpeg");
  WiFiClient client = server.client();
  frame->writeTo(client);
}
 
void handleJpg()
{
  if (!esp32cam::Camera.changeResolution(hiRes)) {
    Serial.println("SET-HI-RES FAIL");
  }
  serveJpg();
}

void handleCommand(String command){
//  int delimiterIndex1 = data.indexOf('@');
//    int delimiterIndex2 = data.indexOf('#');
//    if (delimiterIndex1 != -1 && delimiterIndex2 != -1) {
//      String strX = data.substring(1, delimiterIndex1);
//      String strY = data.substring(delimiterIndex1 + 1, delimiterIndex2);
//      String shootStr = data.substring(delimiterIndex2 + 1);
//  if(command.indexOf('on') != -1){
//      digitalWrite(ledPin, HIGH);
//    }
//  else if(command.indexOf('off') != -1){
//      digitalWrite(ledPin, LOW);
//    }
//  String data = Serial.readStringUntil(';');
  int delimiterIndex1 = command.indexOf('@');
  int delimiterIndex2 = command.indexOf('#');
  int delimiterIndex3 = command.indexOf(';');
  if (delimiterIndex1 != -1 && delimiterIndex2 != -1 && delimiterIndex3 != -1) {
    String strX = command.substring(1, delimiterIndex1);
    String strY = command.substring(delimiterIndex1 + 1, delimiterIndex2);
    String shootStr = command.substring(delimiterIndex2 + 1, delimiterIndex3);

    angleX = strX.toInt();
    angleY = strY.toInt();
    shoot = shootStr.toInt();
      
    servoX.write(angleX);
    servoY.write(angleY);
//    analogWrite(pumpPinENB,shoot);
    if(shoot == 1){
      digitalWrite(pumpPin,HIGH);
    }else{
      digitalWrite(pumpPin,LOW);
    }
  }else{
    Serial.println("Wrong command format");
  }
}

//void ledOn()
//{
//  digitalWrite(ledPin, HIGH);
////  server.send(200, "text/plain", "LED is ON");
//  server.send(200, "", "");
//}
// 
//void ledOff()
//{
//  digitalWrite(ledPin, LOW);
////  server.send(200, "text/plain", "LED is OFF");
//  server.send(200, "", "");
//}
 
void  setup(){
  Serial.begin(115200);
  
//  pinMode(ledPin, OUTPUT);
//  digitalWrite(ledPin, LOW);
  servoX.attach(servoXPin);
  servoY.attach(servoYPin);
  servoX.write(angleX);
  servoY.write(angleY);
  
  pinMode(pumpPin,OUTPUT);
  digitalWrite(pumpPin, LOW);
//  pinMode(pumpPin1,OUTPUT);
//  pinMode(pumpPin2,OUTPUT);
//  digitalWrite(pumpPin1,HIGH);
//  digitalWrite(pumpPin2,LOW);
  
  Serial.println();
  {
    using namespace esp32cam;
    Config cfg;
    cfg.setPins(pins::AiThinker);
    cfg.setResolution(hiRes);
//    cfg.setBufferCount(2);
    cfg.setJpeg(90);
 
    bool ok = Camera.begin(cfg);
    Serial.println(ok ? "CAMERA OK" : "CAMERA FAIL");
  }
//  WiFi.softAP(WIFI_SSID, WIFI_PASS);
  WiFi.persistent(false);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println(".");
  }
  Serial.println("WiFi connected!");
  Serial.print("http://");
  Serial.println(WiFi.localIP());
  Serial.println("  /cam.jpg");
  
  server.on("/cam.jpg", handleJpg);

//  server.on("/led/on", ledOn);

//  server.on("/led/off", ledOff);
 
  server.begin();
  Serial.println("Server started!");

  if(udp.listen(1234)) {
        Serial.print("UDP Listening on IP: ");
        Serial.println(WiFi.localIP());
        udp.onPacket([](AsyncUDPPacket packet) {
            Serial.print("UDP Packet Type: ");
            Serial.print(packet.isBroadcast()?"Broadcast":packet.isMulticast()?"Multicast":"Unicast");
            Serial.print(", From: ");
            Serial.print(packet.remoteIP());
            Serial.print(":");
            Serial.print(packet.remotePort());
            Serial.print(", To: ");
            Serial.print(packet.localIP());
            Serial.print(":");
            Serial.print(packet.localPort());
            Serial.print(", Length: ");
            Serial.print(packet.length());
            Serial.print(", Data: ");
            Serial.write(packet.data(), packet.length());
            Serial.println();
            //reply to the client
            packet.printf("Got %u bytes of data", packet.length());

            String comand = String((char*)packet.data(), packet.length());
            handleCommand(comand);
        });
    }
}
 
void loop()
{
  server.handleClient();
  udp.broadcast("DeFire");
}
