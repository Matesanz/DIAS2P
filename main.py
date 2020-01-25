# from utils.gpios import *
from trackers.boundingbox import BoundingBox
from trackers.bboxtracker import BBoxTracker
from collections import OrderedDict
import dlib
import cv2
from utils.utils import get_frames_and_concatenate, set_cameras, set_detector, check_cameras

if __name__ == "__main__":

        vehicle_bbox_tracker = BBoxTracker(maxDisappeared=15)
        people_bbox_tracker = BBoxTracker(maxDisappeared=50)

        color = (255, 0, 0)
        thickness = 2

        #activate_jetson_board()

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
        skip_frames = 16

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
                frame = get_frames_and_concatenate(cam0, cam1)
                if VIDEO:
                        frame = cv2.resize(frame, (960, 270))
                mask = fgbg.apply(frame)
                mask = cv2.dilate(mask, None, iterations=2)
                cam = cv2.bitwise_and(frame,frame,mask = mask)


                bboxes_cars = []
                bboxes_people = []
                tracked_objects = []
                trackable_objects = []

                # print(totalFrames % skip_frames)

                if totalFrames % skip_frames == 0:


                        # HERE WE USE YOLOV3

                        car_trackers = []
                        people_trackers = []

                        detections = detector.detectCustomObjectsFromImage(
                                input_type="array",
                                custom_objects=custom_objects,
                                input_image=cam,
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
                                        # bboxes_cars.append(bbox)
                                        car_tracker.start_track(frame, bbox.rect)
                                        car_trackers.append(car_tracker)


                                if bbox.type in people_list:
                                        # bboxes_people.append(bbox)
                                        people_tracker.start_track(frame, bbox.rect)
                                        people_trackers.append(people_tracker)


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


                vehicles = vehicle_bbox_tracker.update(bboxes_cars)
                people = people_bbox_tracker.update(bboxes_people)


                if len(vehicles) > 0 and len(people) > 0:
                        seguridad = True
                        frame = cv2.rectangle(frame, (440, 0), (480, 40), (255,255,255), -1)
                        #activate_warnings()
                else:
                        seguridad = False
                        #deactivate_warnings()

                ######## DISPLAY OPTIONS ##########


                tracked_objects = OrderedDict(
                        list(vehicles.items())
                         + list(people.items())
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
                                bbox.type + ': ' + str(bbox.mov[0]),
                                bbox.start_point,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,
                                bbox.color,
                                2
                        )

                info = [
                        ("SEGURIDAD", str(seguridad)),
                        # ("People", len(people))
                ]

                # loop over the data and draw them it in the frame
                for (i, (k, v)) in enumerate(info):
                        text = "{}: {}".format(k, v)
                        cv2.putText(frame, text, (
                                10, 70 - ((i * 20) + 20)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (53, 67, 234), 2
                                    )

                ### END PART ###

                totalFrames += 1
                # out.write(frame)
                cv2.imshow("Frame", frame)
                cv2.imshow("Mask", cam)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                        # close any open windows
                        #deactivate_jetson_board()
                        cv2.destroyAllWindows()
                        # out.release()
                        break
