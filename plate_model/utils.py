from ctypes import *
import random
import os
import cv2
import time
import plate_model.darknet as darknet
import argparse
import sys
from datetime import datetime
import re
import easyocr

def str2int(video_path):
    try:
        return int(video_path)
    except ValueError:
        return video_path

def set_saved_video(input_video, output_video, size):
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")  # Use MJPG codec for video saving
    fps = int(input_video.get(cv2.CAP_PROP_FPS))  # Get the original FPS of the input video
    video = cv2.VideoWriter(output_video, fourcc, fps, size)  # Create VideoWriter object
    return video

def convert2relative(bbox, darknet_height, darknet_width):
    x, y, w, h = bbox
    _height = darknet_height
    _width = darknet_width
    return x / _width, y / _height, w / _width, h / _height

def convert2original(image, bbox, darknet_height, darknet_width):
    x, y, w, h = convert2relative(bbox, darknet_height, darknet_width)
    image_h, image_w, __ = image.shape
    orig_x = int(x * image_w)
    orig_y = int(y * image_h)
    orig_width = int(w * image_w)
    orig_height = int(h * image_h)
    return (orig_x, orig_y, orig_width, orig_height)
