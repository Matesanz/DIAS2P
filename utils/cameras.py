import cv2


def get_available_cam_indexes(max_cameras=2):
    
    i = 0
    cameras = []
    while len(cameras) < max_cameras:
        cam = cv2.VideoCapture(i)
        if cam.grab():
            cameras.append(i)

        cam.release()
        i += 1

    return cameras


def get_cams_from_indexes(indexes):
    
    cams = []
    for i in indexes:
        cam = cv2.VideoCapture(i)
        cams.append(cam)
    
    return cams
    

def grab_frame_and_ask(cam, question):
    
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


if __name__ == "__main__":
    
    get_road_and_crosswalk_indexes()
