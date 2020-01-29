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

from utils import utils, classes
from trackers.bboxssd import BBox


if __name__ == "__main__":

        # Show live results
        # when production set this to False as it consume resources
        SHOW = True

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

        # Get both Cameras Input
        crosswalkCam = cv2.VideoCapture(0)
        roadCam = cv2.VideoCapture(2)

        # process frames
        while True:

                # Check if get frames is available
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
                ped_bboxes = []
                veh_bboxes = []

                for detection in pedestrianDetections:
                        bbox = BBox(detection)
                        if bbox.name in pedestrian_classes:
                                ped_bboxes.append(bbox)

                for detection in vehicleDetections:
                        bbox = BBox(detection)
                        if bbox.name in pedestrian_classes:
                                veh_bboxes.append(bbox)

                # print("PERSONAS: ", str(len(ped_bboxes)))
                # print("COCHES: ", str(len(veh_bboxes)))




                ##### SHOW #####
                if SHOW:

                        crosswalkFrame = utils.print_bboxes_to_frame(crosswalkFrame, ped_bboxes)
                        roadFrame = utils.print_bboxes_to_frame(roadFrame, veh_bboxes)


                        cv2.imshow("Crosswalk CAM", crosswalkFrame)
                        cv2.imshow("Road CAM", roadFrame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                        # close any open windows
                        cv2.destroyAllWindows()
                        break
