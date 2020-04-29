import cv2
import warnings


def get_available_cam_indexes(max_cameras=2):
    
    """
    Returns the indexes of the connected cameras
    /dev/video<index>
    :param max_cameras: number of cameras to take
    :return: list of indexes of the connected cameras
    """
    
    i = 0
    indexes = []
    while len(indexes) < max_cameras:
        cam = cv2.VideoCapture(i)
        if cam.grab():
            indexes.append(i)
        
        cam.release()
        i += 1
    
    return indexes


def get_cams_from_indexes(indexes):
    
    """
    Take a list of active indexes and return VideoCapture objects from opencv
    :param indexes: indexes list
    :return: ideoCapture objects list
    """
    
    cams = []
    for i in indexes:
        cam = cv2.VideoCapture(i)
        cams.append(cam)
    
    return cams


def grab_frame_and_ask(cam, question):
    
    """
    Take a camera present a frame and ask a yes / no question
    :param cam: VideoCapture
    :param question: str, desired question
    :return: bool, yes == True / no == False
    """
    
    _, frame = cam.read()
    question += " y / n"
    cv2.putText(frame, question, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 3)
    cv2.putText(frame, question, (20, 30), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)
    
    while True:
        
        cv2.imshow("Select Crosswalk Cam", frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('y'):
            cv2.destroyAllWindows()
            cam.release()
            return True
        
        if key == ord('n'):
            cv2.destroyAllWindows()
            cam.release()
            return False


def get_road_and_crosswalk_indexes():
    
    """
    Take the available cameras and present frames of them
    to determine which camera corresponds to the crosswalk
    and which camera corresponds to the road
    :return: road cam index and crosswalkcam index
    """
    
    # Desired number of cameras == 2
    cams_n = 2
    # Get first two cameras indexes available
    cam_indexes = get_available_cam_indexes(max_cameras=cams_n)
    # Get cv2 cam objects from indexes
    cams = get_cams_from_indexes(cam_indexes)
    # Ask whether a camera is looking towards the crosswalk or not
    answers = []
    for cam in cams:
        # opens window showing camera frame
        answer = grab_frame_and_ask(cam, "is this the crosswalk?")
        answers.append(answer)
    
    # Perform XOR on Answers: Raise Exception if answers == [False, False] or answers == [True, True]
    if not (answers[0] ^ answers[1]): raise Exception("Both Cameras were set as Crosswalk / RoadCam")
    
    # Zip the camera indexes and if they are looking towards crosswalk e.g.: [[True, 0], [False, 2]]
    answers_and_indexes = list(zip(answers, cam_indexes))
    # Sort cameras_indexes by its boolean value: False first e.g.: [[False, 2], [True, 0]]
    answers_and_indexes = sorted(answers_and_indexes)
    
    # So now RoadCam Index (boolean value == False) comes first
    road_cam_idx = answers_and_indexes[0][1]
    # And Crosswalk Index (boolean value == True) comes second
    crosswalk_cam_idx = answers_and_indexes[1][1]
    
    print('[*] CrosswalkCam index:', crosswalk_cam_idx, '[*]')
    print('[*] RoadCam index:', road_cam_idx, '[*]')
    
    # Return indexes
    return road_cam_idx, crosswalk_cam_idx
    
    
def set_camera(camera_width=320, camera_height=240, index_cam=0):
    
    """
    Initialize Cam with desired width and height
    :param camera_width: int, cam width
    :param camera_height: int, cam height
    :param index_cam: int, cam index
    :return: videoCapture Object
    """
    
    # Initialize Camera
    cam = cv2.VideoCapture(index_cam)
    print('camera {} ready'.format(index_cam))
    
    # Increase the resolution
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, camera_width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_height)

    # Use MJPEG to avoid overloading the USB 2.0 bus at this resolution
    cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

    return cam


def check_camera(cam):
    
    """
    Check cam availability
    :param cam: VideoCapture Object
    :return: raise Exception
    """
    
    if cam.grab():
        print("Camera Ready")
        return True
    else:
        warnings.warn("Camera is not available, may try another index")
        return False
