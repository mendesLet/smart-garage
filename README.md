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

1. Install Mosquitto on Linux

```
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```