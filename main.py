# import numpy as np
import numpy as np
from scipy.spatial import distance
from trackers.boundingbox import BoundingBox
from trackers.bboxtracker import BBoxTracker
from collections import OrderedDict
from imageai.Detection import ObjectDetection
import dlib


import cv2
# from collections import OrderedDict
# from arduino.main_arduino import arduino
# from ImageAI.imageai.Detection import ObjectDetection
from utils.utils import get_frames_and_concatenate, set_cameras, set_detector, check_cameras

if __name__ == "__main__":

        vehicle_bbox_tracker = BBoxTracker(maxDisappeared=29)
        people_bbox_tracker = BBoxTracker(maxDisappeared=40)

        color = (255, 0, 0)
        thickness = 2

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

        detector = set_detector()
        custom_objects = detector.CustomObjects(
                person=True,
                bicycle=True,
                car=True,
                motorcycle=True,
                bus=True,
                truck=True,
        )

        vehicles_list = ['car', 'motorcycle', 'bus', 'truck']
        people_list = ['person', 'bicycle']

        fgbg = cv2.createBackgroundSubtractorMOG2()
        # Grab both frames first, then retrieve to minimize latency between cameras
        while True:

                if not (cam0.grab() and cam1.grab()):
                        print("No more frames")
                        break

                # frame = get_frames_and_concatenate(cam0, cam1)
                _, frame = cam1.retrieve()
                #mask = fgbg.apply(frame)
                #_, mask = cv2.threshold(mask,127,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

                # frame = cv2.bitwise_and(frame,frame,mask = mask)


                bboxes_cars = []
                bboxes_people = []
                tracked_objects = []
                trackable_objects = []

                print(totalFrames % skip_frames)

                if totalFrames % skip_frames == 0:

                        print("######   Detecting ######")

                        # HERE WE USE YOLOV3

                        car_trackers = []
                        people_trackers = []

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

                                car_tracker = dlib.correlation_tracker()
                                people_tracker = dlib.correlation_tracker()

                                if bbox.type in vehicles_list:
                                        bboxes_cars.append(bbox)
                                        car_tracker.start_track(frame, bbox.rect)
                                        car_trackers.append(car_tracker)


                                if bbox.type in people_list:
                                        bboxes_people.append(bbox)
                                        people_tracker.start_track(frame, bbox.rect)
                                        people_trackers.append(people_tracker)

                                # print('se han detectado', len(bboxes_people))

                                tracked_objects.append(bbox)

                        # if len(people_trackers) == 0:
                        #         people_bbox_tracker.deregisterall()
                        # if len(car_trackers) == 0:
                        #         vehicle_bbox_tracker.deregisterall()
                else:

                        # HERE WE USE DLIB TRACKER
                        for ctracker in car_trackers:

                                ctracker.update(frame)
                                position = ctracker.get_position()

                                # startX, startY, endX, endY
                                box_points = [
                                        int(position.left()),
                                        int(position.top()),
                                        int(position.right()),
                                        int(position.bottom())
                                ]

                                bbox = BoundingBox(box_points, name='car')
                                bboxes_cars.append(bbox)

                        for ptracker in people_trackers:
                                ptracker.update(frame)
                                position = ptracker.get_position()

                                # startX, startY, endX, endY
                                box_points = [
                                        int(position.left()),
                                        int(position.top()),
                                        int(position.right()),
                                        int(position.bottom())
                                ]

                                bbox = BoundingBox(box_points, name='person')
                                bboxes_people.append(bbox)

                for i in bboxes_cars:
                        frame = cv2.rectangle(
                                frame,
                                i.start_point,
                                i.end_point,
                                (0,0  , 0),
                                6)

                # print('ahi va')
                vehicles = vehicle_bbox_tracker.update(bboxes_cars)
                #people = people_bbox_tracker.update(bboxes_people)

                tracked_objects = OrderedDict(
                        list(vehicles.items())
                        # + list(people.items())
                )

                for (i, (bbox_id, bbox)) in enumerate(tracked_objects.items()):

                        frame = cv2.rectangle(
                                frame,
                                bbox.start_point,
                                bbox.end_point,
                                bbox.color,
                                thickness)

                        cv2.putText(
                                frame,
                                bbox.type + ': ' + str(i),
                                bbox.start_point,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                bbox.color,
                                2
                        )




                info = [
                        ("Vehicles", len(vehicles)),
                        #("People", len(people))
                ]

                # loop over the data and draw them it in the frame
                for (i, (k, v)) in enumerate(info):
                        text = "{}: {}".format(k, v)
                        cv2.putText(frame, text, (
                                10, 70 - ((i * 20) + 20)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (53, 67, 234), 2
                                    )


                totalFrames += 1

                cv2.imshow("Frame", frame)
                key = cv2.waitKey(0) & 0xFF
                if key == ord("q"):
                        # close any open windows
                        cv2.destroyAllWindows()
                        break
