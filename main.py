import paho.mqtt.client as mqtt
import time
import sys
import cv2
import pandas as pd
import plate_model.darknet as darknet
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
task_in_progress = False  # Track if a task is in progress

def get_fullplate_config():
    return {
        "input": "0",
        "weights": "./plate_model/FullPlates/AntigoPlates_test3_30000.weights",
        "config_file": "./plate_model/FullPlates/AntigoPlates_test3.cfg",
        "data_file": "./plate_model/FullPlates/AntigoPlates_test3.data",
        "gpu_index": 0,
        "out_filename": None,
        "thresh": 0.25,
        "dont_show":True,
        "ext_output":True
    }

def get_ocr_config():
    return {
        "input": "0",
        "weights": "./plate_model/DiffPlates/DiffPlates_best.weights",
        "config_file": "./plate_model/DiffPlates/DiffPlates.cfg",
        "data_file": "./plate_model/DiffPlates/DiffPlates.data",
        "gpu_index": 0,
        "out_filename": "",
    }

def check_arguments_errors_hardcoded(config):
    assert 0 < 0.25 < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(config["config_file"]):
        raise ValueError(f"Invalid config path {os.path.abspath(config['config_file'])}")
    if not os.path.exists(config["weights"]):
        raise ValueError(f"Invalid weight path {os.path.abspath(config['weights'])}")
    if not os.path.exists(config["data_file"]):
        raise ValueError(f"Invalid data file path {os.path.abspath(config['data_file'])}")
    if str2int(config["input"]) == str and not os.path.exists(config["input"]):
        raise ValueError(f"Invalid video path {os.path.abspath(config['input'])}")

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
    global task_in_progress  # Use the global flag to check task status
    message = msg.payload.decode('utf-8').strip()
    # print(f"Ultrasonic detection message: {message}")
    
    # Extract distance from the message using regex
    match = re.search(r"Object detected at (\d+) cm", message)
    if match:
        distance = int(match.group(1))
        # print(f"Detected distance: {distance} cm")
        
        # Only activate if distance is 200 or more and no task is currently in progress
        if distance <= 200 and not task_in_progress:
            print(f"Distance meets threshold. Activating {task_type}.")
            task_queue.append(task_type)  # Add the task to the queue
        # else:
            # print("Distance does not meet threshold or task already in progress. No action taken.")

def client_subscriptions(client):
    client.subscribe("ultrasonic/detection")
    print("Subscribed to topic: ultrasonic/detection")

def run_fullplate():
    global task_in_progress
    task_in_progress = True  # Mark task as in progress
    
    config = get_fullplate_config()
    print(config)
    darknet.set_gpu(config["gpu_index"])
    check_arguments_errors_hardcoded(config)

    # Load FullPlate settings
    names_file = "./plate_model/FullPlates/AntigoPlates_test3.names"
    network = darknet.load_net_custom(config["config_file"].encode("ascii"), config["weights"].encode("ascii"), 0, 1)
    class_names = open(names_file).read().splitlines()
    colours = darknet.class_colors(class_names)
    class_colors = colours

    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    input_path = str2int(config["input"])
    cap = cv2.VideoCapture(input_path)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video = set_saved_video(cap, config["out_filename"], (video_width, video_height))

    # Run FullPlate detection
    confidence_threshold = 50.0
    required_consecutive_detections = 1
    result = video_capture_full(
        cap, confidence_threshold, required_consecutive_detections, network, class_names, darknet_width, darknet_height, class_colors, config
    )
    video.release()

    task_in_progress = False  # Mark task as done

    if result is None:
        print("No valid plate detected.")
    else:
        plate_info, plate_type = result
        plate, confidences = plate_info
        final_plate = validate_plate_full(plate_type, plate)

        print("Final Plate: ", final_plate)
        print("Plate Type: ", plate_type)
        print("Confidence: ", confidences)
        return final_plate, plate_type
                 
def run_ocr():
    global task_in_progress
    task_in_progress = True  # Mark task as in progress
    
    config = get_ocr_config()
    darknet.set_gpu(config["gpu_index"])
    check_arguments_errors_hardcoded(config)

    # Load OCR settings
    names_file = "./plate_model/DiffPlates/DiffPlates.names"
    network = darknet.load_net_custom(config["config_file"].encode("ascii"), config["weights"].encode("ascii"), 0, 1)
    class_names = open(names_file).read().splitlines()
    colours = darknet.class_colors(class_names)
    class_colors = colours

    darknet_width = darknet.network_width(network)
    darknet_height = darknet.network_height(network)
    input_path = str2int(config["input"])
    cap = cv2.VideoCapture(input_path)
    video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    reader = easyocr.Reader(['en'])  # Initialize EasyOCR reader
    video = set_saved_video(cap, config["out_filename"], (video_width, video_height))

    # Run OCR detection
    confidence_threshold = 60.0
    required_consecutive_detections = 20
    result = video_capture_ocr(confidence_threshold, required_consecutive_detections)
    video.release()

    task_in_progress = False  # Mark task as done

    if result is None:
        print("No valid plate detected.")
    else:
        plate_type, image_path = result
        ocr_result = reader.readtext(image_path, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        plate, confidence = validate_plate_ocr(plate_type, ocr_result)

        print("Final Plate: ", plate)
        print("Confidence: ", confidence)
        return plate, confidence
                 
def main():
    global task_type
    task_type = parse_main_args()  # Determine task type from command-line arguments

    # MQTT setup
    client_id = "my_pc2"
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id)
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
        elif task_queue and not task_in_progress:
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

        time.sleep(1)

if __name__ == "__main__":
    main()
