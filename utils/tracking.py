from utils.contour import is_point_in_contour
from scipy.optimize import linear_sum_assignment
from scipy.spatial import distance
from numpy import ndarray


def is_any_pedestrian_crossing(pedestrians, crossContourUp, crossContourDown):
    
    """
    check if any pedestrian bbox is about to cross
    :param pedestrians: list of bboxssd objects
    :param crossContourUp: other side of crosswalk contour
    :param crossContourDown: this side of crosswalk contour
    :return: bool, True if ped is crossing / False if not
    """
    
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
    
    """
    check bbox direction
    :param bbox: bboxssd object
    :param direction: str, "up", "down, "left" or "right"
    :return: bool, True if bbox is moving in direction / false if not
    """
    
    if direction in bbox.mov:
        return True
    
    return False


def is_any_bbox_moving_in_direction(bboxes, direction):
    """
    Checks if any bbox direction matches desired direction
    Filters fast objects by applying speed coefficient
    :param bboxes: list of bounding boxes
    :param direction: str, "up", "down, "left" or "right"
    :return: bool
    """
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
    
    """
    Check if bboxes in dict are moving
    :param items: bboxes dict
    :return: bool
    """
    
    for _, bbox in items.items():
        if bbox.status == 'move':
            return True
    
    return False


def bb_intersection_over_union(boxA, boxB):
    
    """
    measures the area shared by boxA and boxB
    :param boxA: list of two points
    :param boxB: list of two points
    :return: float, percentage of common area
    """
    
    # determine the (x, y)-coordinates of the intersection rectangle
    xa = max(boxA.tl_corner.x, boxB.tl_corner.x)
    ya = max(boxA.tl_corner.y, boxB.tl_corner.y)
    xb = min(boxA.br_corner.x, boxB.br_corner.x)
    yb = min(boxA.br_corner.y, boxB.br_corner.y)
    
    # compute the area of intersection rectangle
    interArea = max(0, xb - xa + 1) * max(0, yb - ya + 1)
    
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


def calculate_intersection_matrix(detected_bboxes, tracked_bboxes):
    """
    calculates a matrix with all the percentage of intersections between bboxes
    :param detected_bboxes: new bounding boxes
    :param tracked_bboxes: already tracked bounding boxes
    :return: matrix with percentage of intersections between bounding boxes
    """
    iou_matrix = ndarray(shape=(len(tracked_bboxes), len(detected_bboxes)))

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

    # hungarian matrix example
    # hungarian_matrix = (array tracked objects ([0, 1]), array detected objects ([2, 3]))
    # tracked bbox 0 corresponds to detected bbox 2 and
    # tracked bbox 1 corresponds to detected bbox 3
    hungarian_matrix = linear_sum_assignment(iou_matrix)

    return hungarian_matrix


def update_tracked_boxes(tracked_objects, detected_boxes, hungarian_matrix):
    
    """
    assigns new bboxes to already tracked bboxes based on intersection matrix
    :param tracked_objects: list of tracked bboxes
    :param detected_boxes: list of new detected bboxes
    :param hungarian_matrix: matrix of intersections between tracked bboxes
    :return: list of uptdated tracked bboxes
    """
    
    tracked_ids = hungarian_matrix[0]
    detected_ids = hungarian_matrix[1]
    
    for i, tracked_id in enumerate(tracked_ids):
        tracked_objects[str(tracked_id)] = detected_boxes[detected_ids[i]]
    
    return tracked_objects
