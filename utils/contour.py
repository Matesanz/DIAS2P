import cv2
from os import path
from numpy import save, load
from numpy import array
import warnings


def drawContour(image, contour):
    
    """
    Draw contour on frame
    :param image: numpy array, image
    :param contour: list, points on frame
    """
    
    # Iterate over points in contour
    for idx, point in enumerate(contour):
        # Get previous point on iterable
        previous_point = contour[idx - 1]
        # Draw line between the points
        image = cv2.line(image, tuple(previous_point), tuple(point), (0, 0, 0), 1)


def is_point_in_contour(contour, point):
    
    """
    check if coordinates are inside/outside of contour
    :param contour: list, points on frame
    :param point: tuple, coordinates
    :return: bool, True if inside / False if outside
    """
    
    # +1, -1, or 0  point is inside, outside, or on the contour, respectively
    is_point_inside_box = cv2.pointPolygonTest(contour, point, False) > 0
    # print(point)
    return is_point_inside_box


def save_contour(contour, name):
    """
    Saves list of points
    :param contour: list, points on frame
    :param name: str, name of file
    """
    folder = 'resources'
    contour_name = name + '.npy'
    contour_path = folder + '/' + contour_name
    save(contour_path, contour)
    print("Contour Guardado!")


def load_contour(name):
    
    """
    Loads list of points
    :param name: str, name of file
    """
    
    folder = 'resources'
    contour_name = name + '.npy'
    contour_path = folder + '/' + contour_name
    
    if not path.isfile(contour_path):
        raise Exception(
            "No existe ningún contour con el nombre {} en la carpeta {}" \
            .format(contour_name, folder)
        )
    
    contour = load(contour_path)
    return contour


def contour_exists(name):
    
    """
    Check if numpy file exists
    :param name: str, file name
    :return bool, True if exists / False if not
    """
    
    folder = 'resources'
    contour_name = name + '.npy'
    contour_path = path.join(folder, contour_name)

    if not path.isfile(contour_path):
        return False
    
    return True


def select_points_in_frame(cam, name, point_nb=4):
    
    """
    Grabs frame of cam and waits till user has selected points
    This function will be called to initialize contour
    :param cam: cv2 VideoCapture object
    :param name: str, contour name
    :param point_nb: int, number of points
    :return: contour, list of coordinates of contour
    """
    
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
    # width = int(cam.get(3))  # float
    # height = int(cam.get(4))  # float

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
                warnings.warn("NO HAY SUFICIENTES PUNTOS")
                warnings.warn("QUEDAN:", point_nb - len(points))


def left_click(event, x, y, flags, param):
    
    """
    Returns selected points in mouse callback
    :param event: waiting for cv2 event
    :param x: float, x coordinate on click
    :param y: float, y coordinate on click
    :param flags: callback required param
    :param param: params expected: list, [0] list of points [1] max points
    """

    points = param[0]
    limit_of_points = param[1]

    # Check if maximum points reached
    allow_selection = len(points) < limit_of_points

    # On double click get append coordinates
    if event == cv2.EVENT_LBUTTONDBLCLK and allow_selection:
        points.append([x, y])
