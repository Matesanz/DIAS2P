# import numpy as np
from trackers.boundingbox import BoundingBox
from trackers.bboxtracker import BBoxTracker
from imageai.Detection import ObjectDetection
import dlib


import cv2
# from collections import OrderedDict
# from arduino.main_arduino import arduino
# from ImageAI.imageai.Detection import ObjectDetection
from utils.utils import get_frames_and_concatenate, set_cameras, set_detector, check_cameras

if __name__ == "__main__":

        bbox_tracker = BBoxTracker(maxDisappeared=40)

        color = (255, 0, 0)
        thickness = 0.6
        VIDEO = True
        VIDEO_PATH = "./Crosswalk.mp4"
        # Video / Camera
        if VIDEO:
                print('[*] Starting video...')
                cam0 = cv2.VideoCapture(VIDEO_PATH)
                cam1 = cv2.VideoCapture(VIDEO_PATH)
        else:
                # Set video source from camera
                print('[*] Starting camera...')
                cam0, cam1 = set_cameras()
                check_cameras(cam0, cam1)

        # initialize the total number of frames processed thus far,
        totalFrames = 0
        skip_frames = 30

        trackers = []

        detector = set_detector()
        custom_objects = detector.CustomObjects(
                person=True,
                bicycle=True,
                car=True,
                motorcycle=True,
                bus=True,
                truck=True,
        )

        # Grab both frames first, then retrieve to minimize latency between cameras
        while True:

                if not (cam0.grab() and cam1.grab()):
                        print("No more frames")
                        break

                frame = get_frames_and_concatenate(cam0, cam1)

                bounding_boxes = []
                tracked_objects = []
                trackable_objects = []

                if totalFrames % skip_frames == 0:

                        # HERE WE USE YOLOV3

                        trackers = []
                        detections = detector.detectCustomObjectsFromImage(
                                input_type="array",
                                custom_objects=custom_objects,
                                input_image=frame,
                                minimum_percentage_probability=30,
                                output_type="array")

                        # save dict with all detections
                        detected_objects = detections[1]

                        # loop over results of the detector
                        for detected_object in detected_objects:

                                bbox = BoundingBox(
                                        detected_object['box_points'],
                                        detected_object['name']
                                )

                                bounding_boxes.append(bbox)
                                tracked_objects.append(bbox)

                                tracker = dlib.correlation_tracker()
                                tracker.start_track(frame, bbox.rect)
                                trackers.append(tracker)

                else:

                        # HERE WE USE DLIB TRACKER
                        for tracker in trackers:

                                tracker.update(frame)
                                position = tracker.get_position()

                                # startX, startY, endX, endY
                                box_points = [
                                        int(position.left()),
                                        int(position.top()),
                                        int(position.right()),
                                        int(position.bottom())
                                ]

                                bbox = BoundingBox(box_points)
                                bounding_boxes.append(bbox)

                print('ahi va')
                objects = bbox_tracker.update(bounding_boxes)

                tracked_objects = objects.copy()
                # for obj in tracked_objects:
                #         print(obj)
                print('len objects', len(objects))
                print('tracked objects', tracked_objects)

                thickness = 2

                for bbox_id, bbox in tracked_objects.items():

                        frame = cv2.rectangle(
                                frame,
                                bbox.start_point,
                                bbox.end_point,
                                bbox.color,
                                thickness)

                        cv2.putText(
                                frame,
                                bbox.type + ': ' + str(bbox_id),
                                bbox.start_point,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                bbox.color,
                                2
                        )

                totalFrames += 1

                cv2.imshow("Frame", frame)
                key = cv2.waitKey(0) & 0xFF
                if key == ord("q"):
                        # close any open windows
                        cv2.destroyAllWindows()
                        break
