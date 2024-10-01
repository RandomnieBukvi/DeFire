#include <WebServer.h>
#include <WiFi.h>
#include <AsyncUDP.h>
#include <ESP32Servo.h>
#include "esp_camera.h"

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

camera_config_t config;
sensor_t * s;
int exposure = 30;

// Servo pins
Servo servoX;
Servo servoY;
const int servoXPin = 15;
const int servoYPin = 13;
const int pumpPin = 12;

int angleX = 90;
int angleY = 90;
int shoot = 0;

AsyncUDP udp;

const char* WIFI_SSID = "ARedmi";
const char* WIFI_PASS = "RandomnieBukvi";

WebServer server(80);

// Camera setup for Ai-Thinker
#define CAMERA_MODEL_AI_THINKER

// Function to initialize the camera
bool initCamera() {
    config.ledc_channel = LEDC_CHANNEL_0;
    config.ledc_timer = LEDC_TIMER_0;
    config.pin_d0 = Y2_GPIO_NUM;
    config.pin_d1 = Y3_GPIO_NUM;
    config.pin_d2 = Y4_GPIO_NUM;
    config.pin_d3 = Y5_GPIO_NUM;
    config.pin_d4 = Y6_GPIO_NUM;
    config.pin_d5 = Y7_GPIO_NUM;
    config.pin_d6 = Y8_GPIO_NUM;
    config.pin_d7 = Y9_GPIO_NUM;
    config.pin_xclk = XCLK_GPIO_NUM;
    config.pin_pclk = PCLK_GPIO_NUM;
    config.pin_vsync = VSYNC_GPIO_NUM;
    config.pin_href = HREF_GPIO_NUM;
    config.pin_sscb_sda = SIOD_GPIO_NUM;
    config.pin_sscb_scl = SIOC_GPIO_NUM;
    config.pin_pwdn = PWDN_GPIO_NUM;
    config.pin_reset = RESET_GPIO_NUM;
    config.xclk_freq_hz = 20000000;
    config.pixel_format = PIXFORMAT_JPEG;
    config.frame_size = FRAMESIZE_HD; // Resolution 1280x720
    config.jpeg_quality = 12; // JPEG quality
    config.fb_count = 1;

    // Initialize the camera
    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK) {
        Serial.printf("Camera initialization failed: 0x%x\n", err);
        return false;
    }
    
//    sensor_t * s = esp_camera_sensor_get();
    s = esp_camera_sensor_get();
    s->set_hmirror(s, 1);        // 0 = disable , 1 = enable
    s->set_vflip(s, 1);          // 0 = disable , 1 = enable
    s->set_exposure_ctrl(s, 0);  // 0 = disable , 1 = enable
    s->set_aec_value(s, exposure);    // 0 to 1200
      
    return true;
}

// Function to serve JPEG image
void serveJpg() {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb) {
        Serial.println("Image capture failed");
        server.send(503, "", "");
        return;
    }

    server.setContentLength(fb->len);
    server.send(200, "image/jpeg");
    WiFiClient client = server.client();
    client.write(fb->buf, fb->len);
    esp_camera_fb_return(fb);
}

// Handler for image request
void handleJpg() {
//    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    serveJpg();
}

bool remote_control = false;

void toggle_control()
{
  if(remote_control){
      s->set_exposure_ctrl(s, 0);  // 0 = disable , 1 = enable
      s->set_aec_value(s, exposure);    // 0 to 1200
      remote_control = false;
    }
   else{
    s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
    remote_control = true;
   }
  server.send(200, "", "");
}

// Handler for commands received via UDP
void handleCommand(String command) {
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
        
        if (shoot == 1) {
            digitalWrite(pumpPin, HIGH);
        } else {
            digitalWrite(pumpPin, LOW);
        }
    } else {
        Serial.println("Wrong command format");
    }
}

void setup() {
    Serial.begin(115200);

    // Initialize servos
    servoX.attach(servoXPin);
    servoY.attach(servoYPin);
    servoX.write(angleX);
    servoY.write(angleY);

    // Initialize pump pin
    pinMode(pumpPin, OUTPUT);
    digitalWrite(pumpPin, LOW);

    // Initialize camera
    if (!initCamera()) {
        Serial.println("Failed to initialize camera");
        return;
    }

    // Connect to Wi-Fi
    WiFi.persistent(false);
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("WiFi connected!");
    Serial.print("http://");
    Serial.println(WiFi.localIP());
    Serial.println("/cam.jpg");

    // Setup web server
    server.on("/cam.jpg", handleJpg);
    server.on("/toggle_control", toggle_control);
    server.begin();
    Serial.println("Server started!");

    // Setup UDP
    if (udp.listen(1234)) {
        Serial.print("UDP listening on IP: ");
        Serial.println(WiFi.localIP());
        udp.onPacket([](AsyncUDPPacket packet) {
            Serial.print("UDP packet from: ");
            Serial.print(packet.remoteIP());
            Serial.print(":");
            Serial.println(packet.remotePort());

            String command = String((char*)packet.data(), packet.length());
            handleCommand(command);
        });
    }
}

void loop() {
    server.handleClient();
    udp.broadcast("DeFire");
    delay(1);
}
