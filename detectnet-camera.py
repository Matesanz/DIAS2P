#!/usr/bin/python
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import jetson.inference
import jetson.utils
import cv2
import sys
import time

from utils import utils, classes, gpios
from trackers.bboxssd import BBox
from trackers.bboxssdtracker import BBoxTracker

if __name__ == "__main__":

        # Show live results
        # when production set this to False as it consume resources
        SHOW = True
        VIDEO = True
        total_frame = 0

        # load the object detection network
        arch = "ssd-mobilenet-v2"
        overlay = "box,labels,conf"
        threshold = 0.5
        W, H = (800, 480)
        net = jetson.inference.detectNet(arch, sys.argv, threshold)

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

        VIDEO_PATH = "video/cross_uma_02.webm"
        VIDEO_PATH2 = "video/car_uma_01.webm"
        # Get both Cameras Input
        if VIDEO:
                print('[*] Starting video...')
                crosswalkCam = cv2.VideoCapture(VIDEO_PATH)
                roadCam = cv2.VideoCapture(VIDEO_PATH2)
                # Override initial width and height
                W = int(crosswalkCam.get(3))  # float
                H = int(crosswalkCam.get(4))  # float

        elif is_jetson:

                print('[*] Starting camera...')
                crosswalkCam = jetson.utils.gstCamera(W, H, "dev/video0")
                roadCam = jetson.utils.gstCamera(W, H, "dev/video1")

        else:
                # Set video source from camera
                print('[*] Starting camera...')
                crosswalkCam = cv2.VideoCapture(0)
                roadCam = cv2.VideoCapture(1)
                # Override initial width and height
                W = int(crosswalkCam.get(3))  # float
                H = int(crosswalkCam.get(4))  # float


        # Get ROIs from cross and road cam
        crossContourUp = utils.select_points_in_frame(crosswalkCam, 5)
        crossContourDown = utils.select_points_in_frame(crosswalkCam, 5)
        roadContour = utils.select_points_in_frame(roadCam)

        # process frames
        while True:
                # print("TOTAL FRAME: ", total_frame)
                # total_frame += 1
                start_time = time.time()  # start time of the loop
                # time.sleep(0.05)
                # if we are on Jetson use jetson inference
                if is_jetson:

                        # get frame from crosswalk and detect
                        crosswalkMalloc, _, _ = crosswalkCam.CaptureRGBA()
                        pedestrianDetections = net.Detect(crosswalkMalloc, W, H, overlay)
                        # get frame from road and detect
                        roadMalloc, _, _ = roadCam.CaptureRGBA()
                        vehicleDetections = net.Detect(roadMalloc, W, H, overlay)

                # If we are not on jetson use CV2
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
                                if utils.is_point_in_contour(crossContourUp, bbox.center):
                                        ped_up_bboxes.append(bbox)
                                if utils.is_point_in_contour(crossContourDown, bbox.center):
                                        ped_down_bboxes.append(bbox)

                # Convert Road Detections to Bbox object
                # filter detections if recognised as vehicles
                # add to vehicle list of bboxes
                for detection in vehicleDetections:
                        bbox = BBox(detection)
                        is_bbox_in_contour = utils.is_point_in_contour(roadContour, bbox.center)
                        if bbox.name in vehicle_classes and is_bbox_in_contour:
                                veh_bboxes.append(bbox)

                # Relate previous detections to new ones
                # updating trackers
                pedestriansUp = ped_tracker_up.update(ped_up_bboxes)
                pedestriansDown = ped_tracker_down.update(ped_down_bboxes)

                print('PEDESTRIANS UP', pedestriansUp)
                print('PEDESTRIANS DOWN', pedestriansDown)

                vehicles = veh_tracker.update(veh_bboxes)

                ##### SECURITY #####

                ped_up_crossing = utils.is_any_bbox_moving_in_direction(pedestriansUp.values(), 'down')
                ped_down_crossing = utils.is_any_bbox_moving_in_direction(pedestriansDown.values(), 'up')

                if ped_up_crossing or ped_down_crossing:
                        # Security actions Here
                        cv2. rectangle(crosswalkFrame, (0,0), (200,200), (255,255,255), -1)
                        if is_jetson:
                                gpios.warning_ON()

                else:
                        # Deactivate security actions here
                        print("SECURITY OFF")
                        if is_jetson:
                                gpios.warning_OFF()

                ##### SHOW #####
                fps = 1.0 / (time.time() - start_time)
                if SHOW and not is_jetson:

                        # print contour
                        utils.drawContour(roadFrame, roadContour)
                        utils.drawContour(crosswalkFrame, crossContourUp)
                        utils.drawContour(crosswalkFrame, crossContourDown)

                        # Print square detections into frame
                        crosswalkFrame = utils.print_items_to_frame(crosswalkFrame, pedestriansUp)
                        crosswalkFrame = utils.print_items_to_frame(crosswalkFrame, pedestriansDown)

                        roadFrame = utils.print_items_to_frame(roadFrame, vehicles)
                        roadFrame = utils.print_fps(roadFrame, fps)
                        # Show the frame
                        cv2.imshow("Crosswalk CAM", crosswalkFrame)
                        cv2.imshow("Road CAM", roadFrame)

                ###### END ####
                # Quit program pressing 'Q'
                key = cv2.waitKey(0) & 0xFF
                if key == ord("q"):
                        # free GPIOs before quit
                        if is_jetson:
                                gpios.warning_OFF()
                                gpios.deactivate_jetson_board()
                        # close any open windows
                        cv2.destroyAllWindows()
                        break
