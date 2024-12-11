import paho.mqtt.client as mqtt
import time
import sys
import cv2
import pandas as pd
import darknet
import easyocr
from plate_model.utils import *
from plate_model.darknet_video_full_detect import (
    parse_args as fullplate_parse_args,
    check_arguments_errors as fullplate_check_arguments_errors,
    video_capture_full,
    validate_plate_full,
)
from plate_model.darknet_video_ocr import (
    parse_args as ocr_parse_args,
    check_arguments_errors as ocr_check_arguments_errors,
    video_capture_ocr,
    validate_plate_ocr,
)

# Global variables
flag_connected = 0
task_queue = []
task_type = None  # Set this dynamically based on the script argument

def parse_main_args():
    """
    Parse the main script arguments to determine which task to run.
    """
    import argparse
    parser = argparse.ArgumentParser(description="Ultrasonic-triggered task selector")
    parser.add_argument("--fullplate", action="store_true", help="Run FullPlate detection")
    parser.add_argument("--ocr", action="store_true", help="Run OCR detection")
    args = parser.parse_args()

    if args.fullplate:
        return "fullplate"
    elif args.ocr:
        return "ocr"
    else:
        print("You must specify either --fullplate or --ocr.")
        sys.exit(1)

def on_connect(client, userdata, flags, rc):
    global flag_connected
    flag_connected = 1
    client_subscriptions(client)
    print("Connected to MQTT server")

def on_disconnect(client, userdata, rc):
    global flag_connected
    flag_connected = 0
    print("Disconnected from MQTT server")

def callback_ultrasonic_detection(client, userdata, msg):
    message = msg.payload.decode('utf-8').strip()
    print(f"Ultrasonic detection message: {message}")
    
    # Extract distance from the message using regex
    match = re.search(r"Object detected at (\d+) cm", message)
    if match:
        distance = int(match.group(1))
        print(f"Detected distance: {distance} cm")
        
        # Only activate if distance is 200 or more
        if distance <= 200:
            print(f"Distance meets threshold'. Activating {task_type}.")
            task_queue.append(task_type)  # Add the task to the queue
        else:
            print("Distance does not meet threshold. No action taken.")

def client_subscriptions(client):
    client.subscribe("ultrasonic/detection")
    print("Subscribed to topic: ultrasonic/detection")

def run_fullplate():
    args = fullplate_parse_args()
    darknet.set_gpu(args.gpu_index)
    fullplate_check_arguments_errors(args)

    # Load FullPlate settings
    names_file = "./FullPlates/AntigoPlates_test3.names"
    network = darknet.load_net_custom(args.config_file.encode("ascii"), args.weights.encode("ascii"), 0, 1)
    class_names = open(names_file).read().splitlines()
    colours = darknet.class_colors(class_names)
    class_colors = colours

    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    input_path = str2int(args.input)
    cap = cv2.VideoCapture(input_path)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Initialize video writer if an output filename is specified
    video = set_saved_video(cap, args.out_filename, (video_width, video_height))

    # Run FullPlate detection
    confidence_threshold = 50.0
    required_consecutive_detections = 10
    result = video_capture_full(confidence_threshold, required_consecutive_detections)
    video.release()

    if result is None:
        print("No valid plate detected.")
    else:
        plate_info, plate_type = result
        plate, confidences = plate_info
        final_plate = validate_plate_full(plate_type, plate)

        print("Final Plate: ", final_plate)
        print("Plate Type: ", plate_type)
        print("Confidence: ", confidences)

        registered_plates_file = "data/registered_plate.csv"
        try:
            registered_plates = pd.read_csv(registered_plates_file)

            # Check if the detected plate is in the "plate" column
            if plate in registered_plates['plate'].values:
                return True
            else:
                return False
        except FileNotFoundError:
            print(f"Error: Registered plates file '{registered_plates_file}' not found.")
        except KeyError:
            print(f"Error: 'plate' column not found in '{registered_plates_file}'.")

def run_ocr():
    args = ocr_parse_args()
    darknet.set_gpu(args.gpu_index)
    ocr_check_arguments_errors(args)

    # Load OCR settings
    names_file = "./DiffPlates/DiffPlates.names"
    network = darknet.load_net_custom(args.config_file.encode("ascii"), args.weights.encode("ascii"), 0, 1)
    class_names = open(names_file).read().splitlines()
    colours = darknet.class_colors(class_names)
    class_colors = colours

    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    input_path = str2int(args.input)
    cap = cv2.VideoCapture(input_path)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader

    # Initialize video writer if an output filename is specified
    video = set_saved_video(cap, args.out_filename, (video_width, video_height))

    # Run OCR detection
    confidence_threshold = 60.0
    required_consecutive_detections = 20
    result = video_capture_ocr(confidence_threshold, required_consecutive_detections)
    video.release()

    if result is None:
        print("No valid plate detected.")
    else:
        plate_type, image_path = result
        ocr_result = reader.readtext(image_path, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        plate, confidence = validate_plate_ocr(plate_type, ocr_result)

        print("Final Plate: ", plate)
        print("Confidence: ", confidence)

        # Load the registered plates data
        registered_plates_file = "data/registered_plate.csv"
        try:
            registered_plates = pd.read_csv(registered_plates_file)

            # Check if the detected plate is in the "plate" column
            if plate in registered_plates['plate'].values:
                return True
            else:
                return False
        except FileNotFoundError:
            print(f"Error: Registered plates file '{registered_plates_file}' not found.")
        except KeyError:
            print(f"Error: 'plate' column not found in '{registered_plates_file}'.")

def main():
    global task_type
    task_type = parse_main_args()  # Determine task type from command-line arguments

    # MQTT setup
    client_id = "my_pc2"
    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.message_callback_add('ultrasonic/detection', callback_ultrasonic_detection)

    client.connect('127.0.0.1', 1883)  # Replace with your MQTT broker address
    client.loop_start()

    client_subscriptions(client)
    print("Waiting for messages...")

    # Main loop
    while True:
        if not flag_connected:
            print("Trying to connect to MQTT server...")
        elif task_queue:
            task = task_queue.pop(0)
            if task == "fullplate":
                result = run_fullplate()
            elif task == "ocr":
                result = run_ocr()

            if result:  # Publish a True message if the result is True
                try:
                    pubMsg = client.publish(
                        topic='garage/open_garage',
                        payload="True".encode('utf-8'),
                        qos=0,
                    )
                    pubMsg.wait_for_publish()
                    print("Message published to topic 'garage/open_garage':", pubMsg.is_published())
                except Exception as e:
                    print("Error while publishing message:", e)

        time.sleep(10)

if __name__ == "__main__":
    main()
