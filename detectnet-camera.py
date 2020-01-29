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


if __name__ == "__main__":

        SHOW = True

        # load the object detection network
        # net = jetson.inference.detectNet(opt.network, sys.argv, opt.threshold)
        overlay = "box,labels,conf"
        W, H = (800, 480)
        net2 = jetson.inference.detectNet("ssd-mobilenet-v2", sys.argv, 0.5)

        # create the camera and display
        # camera = jetson.utils.gstCamera(opt.width, opt.height, opt.camera)
        display = jetson.utils.glDisplay()
        cam = cv2.VideoCapture(2)
        cam2 = cv2.VideoCapture(0)

        # process frames until user exits
        while True:
                # capture the image
                _, frame = cam.read()
                _, frame2 = cam2.read()
                # frame2 = np.concatenate((frame, frame2), axis=1)

                # img, width, height = camera.CaptureRGBA(zeroCopy=1)
                jetson.utils.cudaDeviceSynchronize()
                # frame = jetson.utils.cudaToNumpy(img, width, height, 4)
                # frame = cv2.cvtColor(frame.astype(np.uint8), cv2.COLOR_RGBA2BGR)
                # _, frame2 = cam.read()

                frame2 = cv2.resize(frame2, (W, H))
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGBA)
                img2 = jetson.utils.cudaFromNumpy(frame2)
                frame2 = cv2.cvtColor(frame2, cv2.COLOR_RGBA2BGR)

                frame = cv2.resize(frame, (W, H))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                img = jetson.utils.cudaFromNumpy(frame)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)

                detections2 = net2.Detect(img2, W, H, overlay)
                detections = net2.Detect(img, W, H, overlay)

                if SHOW:

                        for detection in detections:
                                start_point = (int(detection.Left), int(detection.Top))
                                end_point = (int(detection.Right), int(detection.Bottom))
                                print(start_point, '  ', end_point)
                                frame = cv2.rectangle(
                                        frame,
                                        start_point,
                                        end_point,
                                        (255, 0, 0),
                                        thickness=2)

                        for detection in detections2:
                                start_point = (int(detection.Left), int(detection.Top))
                                end_point = (int(detection.Right), int(detection.Bottom))
                                print(start_point, '  ', end_point)
                                frame2 = cv2.rectangle(
                                        frame2,
                                        start_point,
                                        end_point,
                                        (255, 0, 0),
                                        thickness=2)

                        cv2.putText(frame2,
                                    "FPS: " + str(int(net2.GetNetworkFPS())),
                                    (5, 20),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5,
                                    (0, 0, 255),
                                    2
                                    )

                        # display.RenderOnce(img, W, H)
                        # display.RenderOnce(img2, W, H)
                        cv2.imshow("Infrarroja", frame)
                        cv2.imshow("SSD Mobile Net", frame2)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                        # close any open windows
                        cv2.destroyAllWindows()
                        break
