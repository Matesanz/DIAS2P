import jetson.utils
import platform
import cv2
import numpy as np
from imageai.Detection import ObjectDetection


def is_jetson_platform():
    
    """
    Checks if program is running on Nvidia embedded system
    :return: bool
    """
    
    return platform.processor() != "x86_64"


def frameToCuda(frame, width, height):
    
    """
    Converts cv2 frame to Cuda Malloc
    Resize is neccesary just if video input has different
    shape than camera input
    
    :param frame: numpy array, image
    :param width: cam width
    :param height: cam height
    :return: numpy array frame, and cudaMalloc frame
    """
    
    fr = cv2.resize(frame, (width, height))
    fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGBA)
    cuda_malloc = jetson.utils.cudaFromNumpy(fr)
    fr = cv2.cvtColor(fr, cv2.COLOR_RGBA2BGR)
    
    return fr, cuda_malloc


def draw_boxes(image, bboxes, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=1, color=(255, 0, 0),
               thickness=2):
    
    """
    Takes a list of points and draws bboxes on frame
    :param image: frame
    :param bboxes: lsit of bounding boxes
    :param font: font style
    :param font_scale: font scale
    :param color: font color
    :param thickness: font thickness
    :return: frame
    """
    
    #
    # x1, y1 - -----
    # |              |
    # |              |
    # |              |
    # --------x2, y2
    #
    
    ids = np.linspace(0, len(bboxes))
    
    image = cv2.putText(image, str(ids), (30, 30), font, font_scale, color, thickness)
    
    for i, bbox in enumerate(bboxes):
        start_point = (bbox[0], bbox[1])
        end_point = (bbox[2], bbox[3])
        image = cv2.rectangle(image, start_point, end_point, color, thickness)
        image = cv2.putText(image, str(i), start_point, font, font_scale, color, thickness)
    
    return image


def set_detector():
    """
    Sets imageAI detector with tinyyoloweigths
    :return: iamgeAI detector object
    """
    print("creating detector...")
    detect = ObjectDetection()
    detect.setModelTypeAsTinyYOLOv3()
    detect.setModelPath("yolo-tiny.h5")
    print("loading model")
    detect.loadModel()
    
    print("initializing")
    return detect


def get_frames_and_concatenate(c0, c1):
    """
    takes two frames and stack them along x axis
    :param c0: Videocapture object
    :param c1: Videocapture object
    :return: stacked frames
    """
    _, c0_frame = c0.retrieve()
    _, c1_frame = c1.retrieve()
    
    # WE CONCATENATE BOTH IMAGES HERE
    vis = np.concatenate((c0_frame, c1_frame), axis=1)
    
    return vis
