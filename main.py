import jetson.inference
import jetson.utils
import cv2
import sys
import time
from threading import Timer
from utils import utils, classes, gpios, cameras, info, tracking, contour
from trackers.bboxssd import BBox
from trackers.bboxssdtracker import BBoxTracker
import platform
import curses


if __name__ == "__main__":
    
    # ---------------------------------------
    #
    #      PARAMETER INITIALIZATION
    #
    # ---------------------------------------
    
    # Show live results
    # when production set this to False as it consume resources
    SHOW = False
    VIDEO = True

    # load the object detection network
    arch = "ssd-mobilenet-v2"
    overlay = "box,labels,conf"
    threshold = 0.7
    W, H = (800, 480)
    net = jetson.inference.detectNet(arch, sys.argv, threshold)
    
    # Start printing console
    console = curses.initscr()
    consoleConfig = info.ConsoleParams()
    consoleConfig.system = platform.system()
    
    # Get array of classes detected by the net
    classes = classes.classesDict
    # List to filter detections
    pedestrian_classes = [
        "person",
        "bicycle"
    ]
    vehicle_classes = [
        "car",
        "motorcycle",
        "bus",
        "truck",
    ]
    
    # Initialize Trackers
    ped_tracker_up = BBoxTracker(15)
    ped_tracker_down = BBoxTracker(15)
    veh_tracker = BBoxTracker(15)
    
    # check if running on jetson
    is_jetson = utils.is_jetson_platform()
    # Activate Board
    if is_jetson: gpios.activate_jetson_board()
    
    # Initialize Warning scheduler
    DELAY_TIME = 5
    if is_jetson:
        # if in Jetson Platform schedule GPIOs power off
        scheduler = Timer(DELAY_TIME, gpios.warning_OFF, ())
    else:
        # if not Jetson Platform schedule dummy GPIOs power off
        scheduler = Timer(DELAY_TIME, gpios.security_OFF, ())

    # ---------------------------------------
    #
    #      VIDEO CAPTURE INITIALIZATION
    #
    # ---------------------------------------
    
    VIDEO_PATH = "video/cross_uma_02.webm"
    VIDEO_PATH2 = "video/car_uma_01.webm"
    
    # Get two Video Input Resources
    # Rather from VIDEO file (testing) or CAMERA file
    
    if VIDEO:
        print('[*] Starting video...')
        crosswalkCam = cv2.VideoCapture(VIDEO_PATH)
        roadCam = cv2.VideoCapture(VIDEO_PATH2)
        # Override initial width and height
        W = int(crosswalkCam.get(3))  # float
        H = int(crosswalkCam.get(4))  # float
    
    elif is_jetson:
        # If in jetson platform initialize Cameras from CUDA (faster inferences)
        print('[*] Starting camera...')
        # Select Road and Crosswalk cameras
        road_idx, crosswalk_idx = cameras.get_road_and_crosswalk_indexes()
        road_idx = "dev/video" + str(road_idx)
        crosswalk_idx = "dev/video" + str(crosswalk_idx)
        crosswalkCam = jetson.utils.gstCamera(W, H, "dev/video0")
        roadCam = jetson.utils.gstCamera(W, H, "dev/video1")
    
    else:
        # If NOT in jetson platform initialize Cameras from cv2 (slower inferences)
        # Set video source from camera
        print('[*] Starting camera...')
        
        # Select Road and Crosswalk cameras
        road_idx, crosswalk_idx = cameras.get_road_and_crosswalk_indexes()
        crosswalkCam = cv2.VideoCapture(crosswalk_idx)
        roadCam = cv2.VideoCapture(road_idx)
        # Override initial width and height
        W = int(crosswalkCam.get(3))  # float
        H = int(crosswalkCam.get(4))  # float
    
    # Get ROIs from cross and road cam
    crossContourUp = contour.select_points_in_frame(crosswalkCam, 'crossContourUp')
    crossContourDown = contour.select_points_in_frame(crosswalkCam, 'crossContourDown')
    roadContour = contour.select_points_in_frame(roadCam, 'roadContour')

    # ---------------------------------------
    #
    #      VIDEO PROCESSING MAIN LOOP
    #
    # ---------------------------------------
    
    while True:

        start_time = time.time()  # start time of the loop
        
        # ---------------------------------------
        #
        #              DETECTION
        #
        # ---------------------------------------

        # if we are on Jetson use jetson inference
        if is_jetson:
            
            # get frame from crosswalk and detect
            crosswalkMalloc, _, _ = crosswalkCam.CaptureRGBA()
            pedestrianDetections = net.Detect(crosswalkMalloc, W, H, overlay)
            # get frame from road and detect
            roadMalloc, _, _ = roadCam.CaptureRGBA()
            vehicleDetections = net.Detect(roadMalloc, W, H, overlay)
        
        # If we are NOT on jetson use CV2
        else:
            # Check if more frames are available
            if crosswalkCam.grab() and roadCam.grab():
                # capture the image
                _, crosswalkFrame = crosswalkCam.read()
                _, roadFrame = roadCam.read()
            else:
                print("no more frames")
                break
            
            # Synchronize system
            jetson.utils.cudaDeviceSynchronize()
            
            # Get Cuda Malloc to be used by the net
            # Get processes frame to fit Cuda Malloc Size
            crosswalkFrame, crosswalkMalloc = utils.frameToCuda(crosswalkFrame, W, H)
            roadFrame, roadMalloc = utils.frameToCuda(roadFrame, W, H)
            
            # Get detections Detectnet.Detection Object
            pedestrianDetections = net.Detect(crosswalkMalloc, W, H, overlay)
            vehicleDetections = net.Detect(roadMalloc, W, H, overlay)
        
        # ---------------------------------------
        #
        #               TRACKING
        #
        # ---------------------------------------
        
        # Initialize bounding boxes lists
        ped_up_bboxes = []
        ped_down_bboxes = []
        veh_bboxes = []
        
        # Convert Crosswalk Detections to Bbox object
        # filter detections if recognised as pedestrians
        # add to pedestrian list of bboxes
        for detection in pedestrianDetections:
            bbox = BBox(detection)
            if bbox.name in pedestrian_classes:
                if tracking.is_point_in_contour(crossContourUp, bbox.center):
                    ped_up_bboxes.append(bbox)
                if tracking.is_point_in_contour(crossContourDown, bbox.center):
                    ped_down_bboxes.append(bbox)
        
        # Convert Road Detections to Bbox object
        # filter detections if recognised as vehicles
        # add to vehicle list of bboxes
        for detection in vehicleDetections:
            bbox = BBox(detection)
            is_bbox_in_contour = tracking.is_point_in_contour(roadContour, bbox.center)
            if bbox.name in vehicle_classes and is_bbox_in_contour:
                veh_bboxes.append(bbox)
        
        # Relate previous detections to new ones
        # updating trackers
        pedestriansUp = ped_tracker_up.update(ped_up_bboxes)
        pedestriansDown = ped_tracker_down.update(ped_down_bboxes)
        vehicles = veh_tracker.update(veh_bboxes)

        # ---------------------------------------
        #
        #         MANAGING SECURITY
        #
        # ---------------------------------------
        
        ped_up_crossing = tracking.is_any_bbox_moving_in_direction(pedestriansUp.values(), 'down')
        ped_down_crossing = tracking.is_any_bbox_moving_in_direction(pedestriansDown.values(), 'up')
        
        if veh_bboxes and (ped_up_crossing or ped_down_crossing):
            # Security actions Here
            if is_jetson:
                # Activate Warnings
                gpios.warning_ON()
                # Deactivate Warnings after DELAY_TIME
                scheduler.cancel()
                scheduler = Timer(DELAY_TIME, gpios.warning_OFF, ())
                scheduler.start()
            
            else:
                
                # Deactivate Warnings after DELAY_TIME
                scheduler.cancel()  # Cancel every possible Scheduler Thread
                scheduler = Timer(DELAY_TIME, gpios.security_OFF, ())  # Restart
                scheduler.start()

        # ---------------------------------------
        #
        #           SHOWING PROGRAM INFO
        #
        # ---------------------------------------
       
        consoleConfig.fps = 1.0 / (time.time() - start_time)
        consoleConfig.warnings = scheduler.is_alive()  # if True warnings are still ON
        
        # Transform CUDA MALLOC to NUMPY frame
        # is highly computationally expensive for Jetson Platforms
        if SHOW and not is_jetson:
            
            # Activate Visual Warnings
            cv2.rectangle(crosswalkFrame, (0, 0), (200, 200), (255, 255, 255), -1)
            
            # print contour
            contour.drawContour(roadFrame, roadContour)
            contour.drawContour(crosswalkFrame, crossContourUp)
            contour.drawContour(crosswalkFrame, crossContourDown)
            
            # Print square detections into frame
            crosswalkFrame = info.print_items_to_frame(crosswalkFrame, pedestriansUp)
            crosswalkFrame = info.print_items_to_frame(crosswalkFrame, pedestriansDown)
            
            roadFrame = info.print_items_to_frame(roadFrame, vehicles)
            roadFrame = info.print_fps_on_frame(roadFrame, consoleConfig.fps)
            
            # Show the frames
            cv2.imshow("Crosswalk CAM", crosswalkFrame)
            cv2.imshow("Road CAM", roadFrame)
    
        # SHOW DATA IN CONSOLE
        info.print_console(console, consoleConfig)

        # ----------------------------------
        #
        #           PROGRAM END
        #
        # ----------------------------------
        
        # Quit program pressing 'q'
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            # free GPIOs before quit
            if is_jetson:
                gpios.warning_OFF()
                gpios.deactivate_jetson_board()
            # close any open windows
            curses.endwin()
            cv2.destroyAllWindows()
            break
