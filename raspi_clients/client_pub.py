import time
import paho.mqtt.client as mqtt

def on_publish(client, userdata, mid):
    print("Message published")

client_id = "my_pc"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
client.on_publish = on_publish
client.connect('127.0.0.1', 1883)
# Start a new thread
client.loop_start()

k = 0

while True:
    user_input = input("Enter 'True' to publish a message (or 'exit' to quit): ").strip()
    if user_input.lower() == "exit":
        print("Exiting...")
        break
    elif user_input.lower() == "true":
        k += 1
        if k > 20:
            k = 1

        try:
            msg = str(k)
            pubMsg = client.publish(
                topic='garage/open_garage',
                payload=msg.encode('utf-8'),
                qos=0,
            )
            pubMsg.wait_for_publish()
            print("Message published:", pubMsg.is_published())
        except Exception as e:
            print("Error:", e)

    time.sleep(2)

client.loop_stop()
client.disconnect()
