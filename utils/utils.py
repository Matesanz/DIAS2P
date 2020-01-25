# load yolov3 model and perform object detection
# based on https://github.com/experiencor/keras-yolo3
from scipy.spatial import distance
import numpy as np
from numpy import expand_dims
from keras.models import load_model
from keras.preprocessing.image import load_img
from keras.preprocessing.image import img_to_array
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import cv2
from imageai.Detection import ObjectDetection
from collections import OrderedDict
from scipy.optimize import linear_sum_assignment


def get_trackable_objects_from_detections(detections):

    trackable_objects = []
    for detection in detections[1]:
        trackable_object = trackable_object()










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


def draw_boxes(image, bboxes, ids=[0,1,2], font = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 1, color = (255, 0, 0), thickness = 2):

    # cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
    #
    # x1, y1 - -----
    # |              |
    # |              |
    # |              |
    # --------x2, y2


    image = cv2.putText(image, str(ids), (30,30), font, fontScale, color, thickness)

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

    #calculates a matrix with all the percentage of intersections betwwen bboxes
    iou_matrix = np.ndarray(shape=(len(tracked_bboxes), len(detected_bboxes)))
    empty_trk = []
    for t, trk in enumerate(tracked_bboxes):
        # t: index: 0,1,2,3....
        # trk: value: [x1, y1, x2, y2]
        trk_center = trk.get_center()

        for d, det in enumerate(detected_bboxes):
            # d: index: 0,1,2....
            #det: value: [x1, y1, x2, y2]

            # calculate the intersection percentage [0,1]
            det_center = det.get_center()
            dist = distance.euclidean(trk_center, det_center)
            iou_matrix[t][d] = dist



    # print('matriz de interseccion')
    # print(iou_matrix)
    #iou_matrix_normalized = (iou_matrix == iou_matrix.max(axis=1)[:, None]).astype(int)
    #print(iou_matrix_normalized)


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
