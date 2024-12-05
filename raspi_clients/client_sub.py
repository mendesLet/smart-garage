import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, rc):
    global flag_connected
    flag_connected = 1
    client_subscriptions(client)
    print("Connected to MQTT server")

def on_disconnect(client, userdata, rc):
    global flag_connected
    flag_connected = 0
    print("Disconnected from MQTT server")
   
# Callback function for the ultrasonic detection topic
def callback_ultrasonic_detection(client, userdata, msg):
    print('Ultrasonic detection message: ', msg.payload.decode('utf-8'))

def client_subscriptions(client):
    client.subscribe("ultrasonic/detection")  # Subscribe to the desired topic
    print("Subscribed to topic: ultrasonic/detection")

# MQTT client setup
client_id = "my_pc2"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
flag_connected = 0

client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Add the callback for the ultrasonic detection topic
client.message_callback_add('ultrasonic/detection', callback_ultrasonic_detection)

client.connect('127.0.0.1', 1883)  # Replace with your MQTT broker address
client.loop_start()  # Start a new thread for the MQTT client
client_subscriptions(client)

print("......client setup complete............")

# Keep the script running
while True:
    time.sleep(4)
    if not flag_connected:
        print("Trying to connect to MQTT server...")
