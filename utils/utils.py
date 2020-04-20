# load yolov3 model and perform object detection
# based on https://github.com/experiencor/keras-yolo3
import jetson.utils
import platform
from collections import OrderedDict
from numpy import array, zeros, uint8
import cv2
import numpy as np
from imageai.Detection import ObjectDetection
from scipy.optimize import linear_sum_assignment
from scipy.spatial import distance
from os import path, mkdir
from numpy import save, load


# def get_trackable_objects_from_detections(detections):
#         trackable_objects = []
#         for detection in detections[1]:
#                 trackable_object = trackable_object()


##################################
# def draw_boxes(filename, v_boxes, v_labels, v_scores):
#     # load the image
#     data = pyplot.imread(filename)
#     # plot the image
#     pyplot.imshow(data)
#     # get the context for drawing boxes
#     ax = pyplot.gca()
#     # plot each box
#     for i in range(len(v_boxes)):
#         box = v_boxes[i]
#         # get coordinates
#         y1, x1, y2, x2 = box.ymin, box.xmin, box.ymax, box.xmax
#         # calculate width and height of the box
#         width, height = x2 - x1, y2 - y1
#         # create the shape
#         rect = Rectangle((x1, y1), width, height, fill=False, color='white')
#         # draw the box
#         ax.add_patch(rect)
#         # draw text and score in top left corner
#         label = "%s (%.3f)" % (v_labels[i], v_scores[i])
#         pyplot.text(x1, y1, label, color='white')
#     # show the plot
#     pyplot.show()

#############################################################################

def security_ON():
        print("[*] SECURITY ON [*]")

def security_OFF():
        print("[#] SECURITY OFF [#]")

def drawContour(image, contour):
        # Iterate over points in contour
        for idx, point in enumerate(contour):
                # Get previous point on iterable
                previous_point = contour[idx - 1]
                # Draw line between the points
                image = cv2.line(image, tuple(previous_point), tuple(point), (0, 0, 0), 1)


def is_point_in_contour(contour, point):
        # +1, -1, or 0  point is inside, outside, or on the contour, respectively
        is_point_inside_box = cv2.pointPolygonTest(contour, point, False) > 0
        # print(point)
        return is_point_inside_box


def save_contour(contour, name):
        folder = 'resources'
        contour_name = name + '.npy'
        contour_path = folder + '/' + contour_name
        save(contour_path, contour)
        print("Contour Guardado!")


def load_contour(name):
        folder = 'resources'
        contour_name = name + '.npy'
        contour_path = folder + '/' + contour_name

        if not path.isfile(contour_path):
                raise Exception(
                        "No existe ningún contour con el nombre {} en la carpeta {}"\
                                .format(contour_name, folder)
                )

        contour = load(contour_path)
        return contour


def contour_exists(name):
        folder = 'resources'
        contour_name = name + '.npy'
        contour_path = folder + '/' + contour_name

        if not path.isfile(contour_path):
                return False

        return True


def select_points_in_frame(cam, name, point_nb=4):
        # Sanity Check: need min 3 points to make contour
        if point_nb < 3:
                raise Exception('Minimum point required is 3, got', point_nb)

        # Check if contour is stored
        is_contour_stored = contour_exists(name)

        # Initialize points list
        points = []

        # Set params to call left_click()
        params = [points, point_nb]

        # Read frame of cam
        _, first_frame = cam.read()
        # Make copy
        clean_frame = first_frame.copy()

        # Name frame of cam
        cv2.namedWindow("first_frame")

        # Call Mouse Function to get points on frame
        cv2.setMouseCallback("first_frame", left_click, params)

        # Get width and height of frame
        width = int(cam.get(3))  # float
        height = int(cam.get(4))  # float

        while True:

                # Add instructions
                instructions = [
                        "Select " + str(point_nb) + " points in frame",
                        "Remaining points: " + str(point_nb - len(points)),
                        "Press 'c' to clear"
                ]

                # Ask to load stored contour
                if is_contour_stored: instructions.append("press 'l' to load")

                # Add DONE when no points remaining
                if len(points) == point_nb: instructions.append("DONE, press 'q'")

                for idx, ins in enumerate(instructions):
                        cv2.putText(first_frame, ins, (20, 30 * (idx + 1)), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)

                # Show Frame
                cv2.imshow("first_frame", first_frame)

                # Wait for any key to be pressed
                key = cv2.waitKey(1) & 0xFF

                # Clean frame to draw points
                first_frame = clean_frame.copy()

                # For every chosen point
                for idx, point in enumerate(points):

                        # Show point on frame
                        cv2.circle(first_frame, tuple(point), 1, (255, 0, 0), 2)

                        # draw lines connecting points
                        if len(points) > 1:
                                # Get previous point on iterable
                                previous_point = points[idx - 1]
                                # Draw line between the points
                                cv2.line(first_frame, tuple(previous_point), tuple(point), (0, 0, 0), 1)

                # If press 'l' load stored contour
                if key == ord('l'):
                        contour = load_contour(name)
                        cv2.destroyWindow("first_frame")
                        return contour

                # If press 'c' restart selected points
                if key == ord("c"):
                        # Read frame of cam
                        _, first_frame = cam.read()
                        # Make copy
                        clean_frame = first_frame.copy()
                        # Reset points list
                        points = []
                        # Set params to call left_click()
                        params = [points, point_nb]
                        # Call Mouse Function to get points on frame
                        cv2.setMouseCallback("first_frame", left_click, params)

                # If press 'q' try to finish selection
                if key == ord("q"):

                        # if number of points is covered return contour
                        if len(points) == point_nb:
                                cv2.destroyWindow("first_frame")
                                contour = array(points)
                                save_contour(points, name)
                                return contour

                        # else show warning
                        else:
                                print("NO HAY SUFICIENTES PUNTOS")
                                print("QUEDAN:", point_nb - len(points))


def left_click(event, x, y, flags, param):
        # Returns selected points in mouse callback
        # params expected: [0] list of points [1] max points
        points = param[0]
        limit_of_points = param[1]

        # Check if maximum points reached
        allow_selection = len(points) < limit_of_points

        # On double click get append coordinates
        if event == cv2.EVENT_LBUTTONDBLCLK and allow_selection:
                points.append([x, y])


def is_jetson_platform():
        return platform.processor() != "x86_64"


def print_fps(frame, fps):
        fr = frame
        cv2.putText(
                fr,
                "FPS: " + str(round(fps, 2)),
                # + str(bbox.dx) + ' ' + str(bbox.dy) ,
                # + ': ' + str(bbox.name),
                (30, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                2
        )

        return fr


def is_any_pedestrian_crossing(pedestrians, crossContourUp, crossContourDown):
        for ped in pedestrians:
                is_bbox_in_contour_up = is_point_in_contour(crossContourUp, ped.center)
                is_ped_moving_down = is_bbox_moving_in_direction(ped, 'down')
                if is_bbox_in_contour_up and is_ped_moving_down:
                        return True
                is_bbox_in_contour_down = is_point_in_contour(crossContourDown, ped.center)
                is_ped_moving_up = is_bbox_moving_in_direction(ped, 'up')
                if is_bbox_in_contour_down and is_ped_moving_up:
                        return True

        return False


def is_bbox_moving_in_direction(bbox, direction):
        if direction in bbox.mov:
                return True

        return False


def is_any_bbox_moving_in_direction(bboxes, direction):
        for bbox in bboxes:
                # Coef is a measure of movement
                # If Coef is high it means object is traversing fast
                # in x direction: Which is normal in cars.
                # Thus help avoiding fake positives
                coef = 0
                if bbox.dy != 0: coef = abs(bbox.dx / bbox.dy)
                if coef < 10 and direction in bbox.mov:
                        return True

        return False


def is_any_item_moving(items):
        for _, bbox in items.items():
                if bbox.status == 'move':
                        return True

        return False

        return False


def print_items_to_frame(frame, items):
        fr = frame

        for (k, v) in items.items():
                ids = k
                bbox = v

                fr = cv2.rectangle(
                        fr,
                        bbox.start_point,
                        bbox.end_point,
                        bbox.color,
                        2)

                cv2.putText(
                        fr,
                        str(ids) + ': ' + bbox.mov[1],
                        # + str(bbox.dx) + ' ' + str(bbox.dy) ,
                        # + ': ' + str(bbox.name),
                        bbox.start_point,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        bbox.color,
                        2
                )

        return fr


def print_bboxes_to_frame(frame, bboxes):
        fr = frame

        for bbox in bboxes:
                fr = cv2.rectangle(
                        frame,
                        bbox.start_point,
                        bbox.end_point,
                        bbox.color,
                        2)

                cv2.putText(
                        fr,
                        bbox.name,
                        # + ': ' + str(bbox.name),
                        bbox.start_point,
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        bbox.color,
                        2
                )

        return fr


def frameToCuda(frame, width, height):
        # converts cv2 frame to Cuda Malloc
        # Resize is neccesary just if video input has different
        # shape from camera input
        fr = cv2.resize(frame, (width, height))
        fr = cv2.cvtColor(fr, cv2.COLOR_BGR2RGBA)
        cuda_malloc = jetson.utils.cudaFromNumpy(fr)
        fr = cv2.cvtColor(fr, cv2.COLOR_RGBA2BGR)

        return fr, cuda_malloc


def draw_boxes(image, bboxes, ids=[0, 1, 2], font=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 0, 0),
               thickness=2):
        # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
        #
        # x1, y1 - -----
        # |              |
        # |              |
        # |              |
        # --------x2, y2

        image = cv2.putText(image, str(ids), (30, 30), font, fontScale, color, thickness)

        for i, bbox in enumerate(bboxes):
                start_point = (bbox[0], bbox[1])
                end_point = (bbox[2], bbox[3])
                image = cv2.rectangle(image, start_point, end_point, color, thickness)
                image = cv2.putText(image, str(ids[i]), start_point, font, fontScale, color, thickness)

        return image


def set_cameras(camera_width=320, camera_height=240, index_cam0=0, index_cam1=1):
        """
    Vigilar los índices de las cámaras. Puede que sean 0 y 1 ó 0 y 2..
    """
        c0 = cv2.VideoCapture(index_cam0)
        c1 = cv2.VideoCapture(index_cam1)
        print('cameras ready')
        # Increase the resolution
        c0.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        c0.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)
        c1.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
        c1.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

        # Use MJPEG to avoid overloading the USB 2.0 bus at this resolutionq
        # c0.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        # c1.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

        return c0, c1


def check_cameras(cam0, cam1):
        if cam0.grab() and cam1.grab():
                print("Camera Ready")
                return True
        else:
                print("No camera is available, may try another index")
                return False


def set_detector():
        print("creating detector...")
        detect = ObjectDetection()
        detect.setModelTypeAsTinyYOLOv3()
        detect.setModelPath("yolo-tiny.h5")
        print("loading model")
        detect.loadModel()

        print("initializing")
        return detect


def get_frames_and_concatenate(c0, c1):
        _, c0_frame = c0.retrieve()
        # c0_frame = crop_horizontal(c0_frame)
        _, c1_frame = c1.retrieve()
        # c1_frame = crop_horizontal(c1_frame)

        # WE CONCATENATE BOTH IMAGES HERE
        vis = np.concatenate((c0_frame, c1_frame), axis=1)

        return vis


def crop_horizontal(image, crop_width=700, camera_width=720):
        # The distortion in the cam0 and cam1 edges prevents a good calibration, so
        # discard the edges
        return image[:,
               int((camera_width - crop_width) / 2):
               int(crop_width + (camera_width - crop_width) / 2)]


def bb_intersection_over_union(boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA.tl_corner.x, boxB.tl_corner.x)
        yA = max(boxA.tl_corner.y, boxB.tl_corner.y)
        xB = min(boxA.br_corner.x, boxB.br_corner.x)
        yB = min(boxA.br_corner.y, boxB.br_corner.y)

        # compute the area of intersection rectangle
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

        # compute the area of both the prediction and ground-truth
        # rectangles
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # return the intersection over union value
        return iou


def get_detected_bboxes(detector):
        detected_bboxes = []
        for each_object in detector[1]:
                detected_bboxes.append(each_object["box_points"])

        return detected_bboxes


def calculate_intersection_matrix(detected_bboxes, tracked_bboxes):
        # calculates a matrix with all the percentage of intersections betwwen bboxes
        iou_matrix = np.ndarray(shape=(len(tracked_bboxes), len(detected_bboxes)))
        empty_trk = []
        for t, trk in enumerate(tracked_bboxes):
                # t: index: 0,1,2,3....
                # trk: value: [x1, y1, x2, y2]
                trk_center = trk.get_center()

                for d, det in enumerate(detected_bboxes):
                        # d: index: 0,1,2....
                        # det: value: [x1, y1, x2, y2]

                        # calculate the intersection percentage [0,1]
                        det_center = det.get_center()
                        dist = distance.euclidean(trk_center, det_center)
                        iou_matrix[t][d] = dist

        # print('matriz de interseccion')
        # print(iou_matrix)
        # iou_matrix_normalized = (iou_matrix == iou_matrix.max(axis=1)[:, None]).astype(int)
        # print(iou_matrix_normalized)

        # hungarian_matrix = (array objetos trackeados([0, 1]), array objetos detectados([2, 3]))
        # al objeto trackeado 0 le corresponde el detectado 2 y al
        # objeto trackeado 1 le corresponde el detectado 3
        hungarian_matrix = linear_sum_assignment(iou_matrix)

        # print('matriz hungara')
        # print(hungarian_matrix)

        return hungarian_matrix


def update_tracked_boxes(tracked_objects, detected_boxes, hungarian_matrix):
        tracked_ids = hungarian_matrix[0]
        detected_ids = hungarian_matrix[1]

        for i, tracked_id in enumerate(tracked_ids):
                tracked_objects[str(tracked_id)] = detected_boxes[detected_ids[i]]

        return tracked_objects


def create_orderedDict_from_list(list):
        ordDict = OrderedDict()
        for i, val in enumerate(list):
                ordDict[str(i)] = val

        return ordDict


if __name__ == "__main__":
        pass
