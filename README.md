## Smart Garage System

This repository contains the implementation of an IoT-based Smart Garage system. The project integrates an ESP32 microcontroller, a Raspberry Pi, and a Streamlit dashboard to automate garage door operations and vehicle entry logging. The system uses MQTT (via Mosquitto) for message communication between the components.

### Directory Structure

```
smart-garage/
├── esp32_clients/
│   ├── iot_final.ino               # Main Arduino sketch for ESP32
│   ├── PinDefinitionsAndMore.h     # Pin definitions and helper functions
├── raspi_clients/
│   ├── client_pub.py               # MQTT Publisher (Ultrasonic sensor)
│   ├── client_sub.py               # MQTT Subscriber (Garage door control)
├── plate_model/
│   ├── # TODO
├── README.md                       # Documentation
```

### Setup Instructions

**1. Install Mosquitto on Linux**

```
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

<details>
<summary>Make sure to add this to the Mosquitto config files</summary>

```
listener 1883
allow_anonymous true
```

</details>


**2. ESP32 Setup**
- Upload the iot_final.ino sketch to your ESP32:
- Open esp32_clients/iot_final.ino in Arduino IDE.
- Connect your ESP32 device and select the correct port under Tools > Port.
- Compile and upload the sketch.

**3. Raspberry Pi Setup**
- Install the dependencys
```
pip install paho-mqtt
```

- Run the MQTT publisher:
```
python raspi_clients/client_pub.py
```
- Run the MQTT subscriber:
```
python raspi_clients/client_sub.py
```

### Usage

1. Start the ESP32 with the uploaded iot_final.ino sketch.

2. Ensure the Raspberry Pi is running both client_pub.py and client_sub.py.

3. Monitor and control the garage door via MQTT topics:

    - Publish to ultrasonic/detection to simulate vehicle detection.
    - Subscribe to garage/open_garage to control the garage door.

4. Open the Streamlit dashboard for monitoring (future integration).