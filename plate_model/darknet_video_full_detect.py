#!/usr/bin/env python3
# Uses "FullPlates" model, aka: AntigoPlates_test3

from ctypes import *
import random
import os
import cv2
import time
import darknet
import argparse
import sys
from datetime import datetime
from utils import *

# Global variables for speed control
frame_delay = 30  # Delay in milliseconds (default is 30 for normal speed)

def parse_args():
    # Create an ArgumentParser object with a description for YOLO Object Detection.
    parser = argparse.ArgumentParser(description="YOLO Object Detection")
    parser.add_argument("--input", type=str, default=0, help="video source. If empty, uses webcam 0 stream")
    parser.add_argument("--out_filename", type=str, default="", help="inference video name. Not saved if empty")
    parser.add_argument("--weights", default="yolov4.weights", help="yolo weights path")
    parser.add_argument("--dont_show", action='store_true', help="window inference display. For headless systems")
    parser.add_argument("--ext_output", action='store_true', help="display bbox coordinates of detected objects")
    parser.add_argument("--config_file", default="yolov4.cfg", help="path to config file")
    parser.add_argument("--data_file", default="coco.data", help="path to data file")
    parser.add_argument("--thresh", type=float, default=.25, help="remove detections with confidence below this value")
    parser.add_argument("--gpu_index", type=int, default=0, help="GPU index to use for processing")
    return parser.parse_args()

def check_arguments_errors(args):
    assert 0 < args.thresh < 1, "Threshold should be a float between zero and one (non-inclusive)"
    if not os.path.exists(args.config_file):
        raise(ValueError("Invalid config path {}".format(os.path.abspath(args.config_file))))
    if not os.path.exists(args.weights):
        raise(ValueError("Invalid weight path {}".format(os.path.abspath(args.weights))))
    if not os.path.exists(args.data_file):
        raise(ValueError("Invalid data file path {}".format(os.path.abspath(args.data_file))))
    if str2int(args.input) == str and not os.path.exists(args.input):
        raise(ValueError("Invalid video path {}".format(os.path.abspath(args.input))))

def video_capture_full(confidence_threshold, required_consecutive_detections):
    global frame_delay
    consecutive_count = 0
    reference_classes = None
    plate = None
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        start = time.time()

        key = cv2.waitKey(frame_delay) & 0xFF
        if key == ord('q'):
            break
        elif key == 82:
            frame_delay = max(1, frame_delay - 5)
        elif key == 84:
            frame_delay += 5

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_resized = cv2.resize(frame_rgb, (darknet_width, darknet_height), interpolation=cv2.INTER_LINEAR)

        # Create a Darknet image from the resized frame
        img_for_detect = darknet.make_image(darknet_width, darknet_height, 3)
        darknet.copy_image_from_bytes(img_for_detect, frame_resized.tobytes())

        # Perform inference and drawing
        detections = darknet.detect_image(network, class_names, img_for_detect, thresh=args.thresh)

        end = time.time()  # End time for FPS calculation
        fps_label = f"FPS: {round(1.0 / (end - start), 2)}"

        detections_adjusted = []
        if frame is not None:
            for label, confidence, bbox in detections:
                bbox_adjusted = convert2original(frame, bbox, darknet_height, darknet_width)
                detections_adjusted.append((str(label), float(confidence), bbox_adjusted))

            image = darknet.draw_boxes(detections_adjusted, frame, class_colors)
            print("Detections: ", detections_adjusted)
            
            current_classes = {lbl for (lbl, conf, b) in detections_adjusted if conf >= confidence_threshold}
            current_classes = [lbl for (lbl, conf, b) in detections_adjusted if conf >= confidence_threshold]
            
            # If we have no reference_classes yet, or if the current classes don't match the reference
            if reference_classes is None or sorted(current_classes) != sorted(reference_classes):
                reference_classes = current_classes
                consecutive_count = 1 if len(current_classes) > 0 else 0
            else:
                if len(current_classes) > 7:
                    consecutive_count += 1
                else:
                    consecutive_count = 0
            
            if consecutive_count >= required_consecutive_detections:
                filtered_detections = []
                for (lbl, conf, b) in detections_adjusted:
                    if lbl not in ["plate_mercosul", "plate_antigo"] and conf >= confidence_threshold:
                        center_x, center_y, w, h = b
                        left_x = center_x - (w / 2)
                        # Store (label, left_x) for sorting
                        filtered_detections.append((lbl, conf, b, left_x))
                    elif lbl in ["plate_mercosul", "plate_antigo"]:
                        full_plate_type = lbl

                # Sort filtered detections by left_x
                filtered_detections.sort(key=lambda x: x[3])

                # Print the classes left-to-right
                # Only print the class values (labels)
                platelbl = ""
                plateconf = []
                for (lbl, conf, b, lx) in filtered_detections:
                    platelbl += lbl
                    plateconf.append(conf)
                plate = (platelbl, plateconf)

                if consecutive_count >= required_consecutive_detections:

                    # Identify plate bounding boxes
                    plate_boxes = [(lbl, b) for (lbl, conf, b) in detections_adjusted 
                                   if lbl in ["plate_mercosul", "plate_antigo"] and conf >= confidence_threshold]

                    max_inside = -1
                    chosen_label = None
                    chosen_bbox = None

                    for (p_lbl, p_bbox) in plate_boxes:
                        px, py, pw, ph = p_bbox
                        # Convert plate center-based coords to top-left coords for inside check
                        px1 = px - pw / 2
                        py1 = py - ph / 2
                        px2 = px + pw / 2
                        py2 = py + ph / 2

                        inside_count = 0
                        # Count how many filtered classes are inside this plate
                        for (lbl, conf, b, lx) in filtered_detections:
                            cx, cy, cw, ch = b
                            # Check center (cx, cy) of this class inside plate bounds
                            if (cx >= px1 and cx <= px2 and cy >= py1 and cy <= py2):
                                inside_count += 1

                        # If this plate has more classes, select it
                        if inside_count > max_inside:
                            max_inside = inside_count
                            chosen_label = p_lbl
                            chosen_bbox = p_bbox

                    # print(f"{required_consecutive_detections} consecutive detections with confidence >= {confidence_threshold}%")
                    # print("Bounding Box Coordinates:", chosen_bbox)

                    consecutive_count = 0

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    bbox_str = "_".join(map(str, chosen_bbox))
                    filename = f"{chosen_label}_{timestamp}.png"

                    # Save the image
                    cv2.imwrite(filename, image)
                    print(f"Full image saved as: {filename}")

                    center_x, center_y, box_w, box_h = chosen_bbox

                    # Convert center-based coords to top-left
                    x1 = int(center_x - box_w / 2)
                    y1 = int(center_y - box_h / 2)
                    x2 = int(center_x + box_w / 2)
                    y2 = int(center_y + box_h / 2)

                    # Clip to image boundaries
                    height, width = image.shape[:2]
                    x1 = max(0, x1)
                    y1 = max(0, y1)
                    x2 = min(width - 1, x2)
                    y2 = min(height - 1, y2)

                    bbox_crop = image[y1:y2, x1:x2]
                    bbox_filename = f"{chosen_label}_{bbox_str}_{timestamp}_boundingbox.png"
                    cv2.imwrite(bbox_filename, bbox_crop)
                    print(f"Cropped bounding box image saved as: {bbox_filename}")

                    return plate, full_plate_type

            cv2.putText(image, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 5)
            cv2.putText(image, fps_label, (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

            if not args.dont_show:
                cv2.imshow('Inference', image)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                return None

            # Write the frame to the output video file if specified
            if args.out_filename is not None:
                video.write(image)  # Save the frame to video file
        
        # Free Darknet image after inference
        darknet.free_image(img_for_detect)
    cap.release()

def validate_plate_full(plate_type, plate):
    corrected_text = ""
    for i, char in enumerate(plate):
        if plate_type == "plate_mercosul":
            # Mercosul format: Letter, Letter, Letter, Number, Letter, Number, Number
            if i in [0, 1, 2, 4]:  # Letter sections
                corrected_text += 'O' if char == '0' else char
            elif i in [3, 5, 6]:  # Number sections
                corrected_text += '0' if char == 'O' else char
            else:
                corrected_text += char
        elif plate_type == "plate_antigo":
            # Antiga format: Letter, Letter, Letter, Number, Number, Number, Number
            if i in [0, 1, 2]:  # Letter sections
                corrected_text += 'O' if char == '0' else char
            elif i in [3, 4, 5, 6]:  # Number sections
                corrected_text += '0' if char == 'O' else char
            else:
                corrected_text += char
    
    return corrected_text

if __name__ == '__main__':
    args = parse_args()
    darknet.set_gpu(args.gpu_index)
    check_arguments_errors(args)

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

    # Run everything sequentially
    confidence_threshold = 50.0
    required_consecutive_detections = 10
    result = video_capture_full(confidence_threshold, required_consecutive_detections)
    video.release()

    print("Result: ", result)

    if result == None:
        print("No valid plate detected.")
    else:
        (plate_info, plate_type) = result
        (plate, confidences) = plate_info
        final_plate = validate_plate_full(plate_type, plate)

        print("Final Plate: ", final_plate)
        print("Plate Type: ", plate_type)
        print("Confidance: ", confidences)

    # Flush and close standard outputs
    sys.stdout.flush()
    sys.stderr.flush()
    sys.stdout.close()
    sys.stderr.close()
