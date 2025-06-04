#include <Wire.h>
#include <Adafruit_SSD1306.h>
#include <ArduinoJson.h>

#include "ESP8266WiFi.h"
#include "ESP8266mDNS.h"
#include "EspMQTTClient.h"
#include "LEAmDNS.h"
#include "PubSubClient.h"
#include "Secrets.h"
#include "Display.h"
#include "RotaryEncoder.h"

#define CLK    D6
#define DT     D7
#define SW     D4

Display display{};
RotaryEncoder encoder{CLK, DT, SW};
EspMQTTClient mqtt(WIFI_SSID, WIFI_PSK, BROKER_IP, DEVICE_NAME);

#define STATE_TOPIC "rigor/state/"  DEVICE_NAME
#define INPUT_TOPIC "rigor/input/" DEVICE_NAME
#define SCREEN_TOPIC "rigor/screen"

void handleRotaryInput() {
  auto rotation = encoder.getRotation();
  auto button_pressed = encoder.isButtonPressed();

  const char* action = nullptr;
  if (button_pressed)     action = "ENTER";
  else if (rotation ==-1) action = "PREV";
  else if (rotation == 1) action = "NEXT";

  if(action == nullptr) return;
  mqtt.publish(INPUT_TOPIC, String(action), false);
  Serial.print("Published ");
  Serial.println(String(action));
}

void onConnectionEstablished() {
  Serial.println("MQTT Connected");
  mqtt.subscribe(SCREEN_TOPIC, [](const String &payload) {
    Serial.print("Screen: ");
    Serial.println(String(payload));

    JsonDocument doc;
    deserializeJson(doc, payload);
    display.update(doc["title"], doc["body"]);
  });
  mqtt.publish(STATE_TOPIC, "ON");
}

void setup() {
  encoder.init();
  Serial.begin(9600);

  display.init();
  display.update("RIGOR", "v0.0.1");
  display.show();
  Serial.println("Setup complete, starting loop...");

  mqtt.setKeepAlive(60);
  mqtt.enableLastWillMessage(STATE_TOPIC, "OFF");
}

void loop() {
  mqtt.loop();

  if (false == mqtt.isMqttConnected()) {
    delay(100);
    return;
  }

  // Handle rotary encoder input
  handleRotaryInput();
  display.show();
}
