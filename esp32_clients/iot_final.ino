#include <Arduino.h>
#include "PinDefinitionsAndMore.h" // Define macros for input and output pin etc.
#include <WiFi.h>
#include <PubSubClient.h>
#include <IRremote.hpp>

// WiFi and MQTT configuration
const char* ssid = "";         // Replace with your WiFi SSID
const char* password = ""; // Replace with your WiFi password
const char* mqtt_server = ""; // Replace with your computer's IP address
const int mqtt_port = 1883;                 // MQTT port (default is 1883)

WiFiClient espClient;
PubSubClient client(espClient);

// Ultrasonic Sensor Pins
const int TRIG_PIN = 5;
const int ECHO_PIN = 13;
const long DISTANCE_THRESHOLD = 20; // Threshold in centimeters

// Storage for the recorded code
struct storedIRDataStruct {
    IRData receivedIRData;
    uint8_t rawCode[RAW_BUFFER_LENGTH];
    uint8_t rawCodeLength;
} sStoredIRData;

void setup_wifi();
void reconnect();
void storeCode();
void sendCode(storedIRDataStruct* aIRDataToSend);
long measureDistance();

void callback(char* topic, byte* payload, unsigned int length) {
    Serial.print("Message arrived [");
    Serial.print(topic);
    Serial.print("] ");
    for (unsigned int i = 0; i < length; i++) {
        Serial.print((char)payload[i]);
    }
    Serial.println();

    // If the topic is garage/open_garage and a valid message is received
    if (strcmp(topic, "garage/open_garage") == 0) {
        Serial.println(F("Sending stored IR code..."));
        sendCode(&sStoredIRData);
    }
}

void setup_wifi() {
    delay(10);
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);

    WiFi.begin(ssid, password);

    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("");
    Serial.println("WiFi connected");
}

void reconnect() {
    // Loop until we're reconnected
    while (!client.connected()) {
        Serial.print("Attempting MQTT connection...");
        // Attempt to connect
        if (client.connect("ESP32Client")) {
            Serial.println("connected");
            // Subscribe to the topic
            client.subscribe("garage/open_garage");
        } else {
            Serial.print("failed, rc=");
            Serial.print(client.state());
            Serial.println(" try again in 5 seconds");
            delay(5000);
        }
    }
}

long measureDistance() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH);
    long distance = duration * 0.034 / 2; // Convert to centimeters
    return distance;
}

void setup() {
    Serial.begin(115200);
    while (!Serial)
        ; // Wait for Serial to become available.

    delay(4000); // Wait for Serial Monitor after reset or power-up

    Serial.println(F("START " __FILE__ " from " __DATE__ "\r\nUsing library version " VERSION_IRREMOTE));
    
    IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
    Serial.print(F("Ready to receive IR signals of protocols: "));
    printActiveIRProtocols(&Serial);
    Serial.println(F("at pin " STR(IR_RECEIVE_PIN)));

    IrSender.begin();
    Serial.print(F("Ready to send IR signals at pin " STR(IR_SEND_PIN)));
    Serial.println();

    setup_wifi();
    client.setServer(mqtt_server, mqtt_port);
    client.setCallback(callback);

    // Set ultrasonic sensor pins
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
}

void loop() {
    if (!client.connected()) {
        reconnect();
    }
    client.loop();

    if (IrReceiver.decode()) {
        Serial.println(F("IR code received. Storing it..."));
        storeCode();
        IrReceiver.resume(); // Resume receiver
    }

    // Measure distance and publish to MQTT if within threshold
    long distance = measureDistance();
    if (distance > 0 && distance <= DISTANCE_THRESHOLD) {
        String message = "Object detected at " + String(distance) + " cm";
        client.publish("ultrasonic/detection", message.c_str());
        Serial.println(message);
    }

    delay(100); // Delay to avoid spamming MQTT
}

void storeCode() {
    if (IrReceiver.decodedIRData.rawDataPtr->rawlen < 4) {
        Serial.print(F("Ignore data with rawlen="));
        Serial.println(IrReceiver.decodedIRData.rawDataPtr->rawlen);
        return;
    }
    if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT) {
        Serial.println(F("Ignore repeat"));
        return;
    }
    if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_AUTO_REPEAT) {
        Serial.println(F("Ignore autorepeat"));
        return;
    }
    if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_PARITY_FAILED) {
        Serial.println(F("Ignore parity error"));
        return;
    }

    sStoredIRData.receivedIRData = IrReceiver.decodedIRData;

    if (sStoredIRData.receivedIRData.protocol == UNKNOWN) {
        Serial.print(F("Received unknown code and store "));
        Serial.print(IrReceiver.decodedIRData.rawDataPtr->rawlen - 1);
        Serial.println(F(" timing entries as raw "));
        IrReceiver.printIRResultRawFormatted(&Serial, true);
        sStoredIRData.rawCodeLength = IrReceiver.decodedIRData.rawDataPtr->rawlen - 1;
        IrReceiver.compensateAndStoreIRResultInArray(sStoredIRData.rawCode);
    } else {
        IrReceiver.printIRResultShort(&Serial);
        IrReceiver.printIRSendUsage(&Serial);
        sStoredIRData.receivedIRData.flags = 0; // Clear flags for later sending
        Serial.println();
    }
}

void sendCode(storedIRDataStruct* aIRDataToSend) {
    if (aIRDataToSend->receivedIRData.protocol == UNKNOWN) {
        IrSender.sendRaw(aIRDataToSend->rawCode, aIRDataToSend->rawCodeLength, 38);
        Serial.print(F("Sent raw code with "));
        Serial.print(aIRDataToSend->rawCodeLength);
        Serial.println(F(" marks or spaces"));
    } else {
        IrSender.write(&aIRDataToSend->receivedIRData);
        printIRResultShort(&Serial, &aIRDataToSend->receivedIRData, false);
    }
}
