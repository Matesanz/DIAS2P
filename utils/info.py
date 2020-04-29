from tabulate import tabulate
from sys import stdout
import cv2


class ConsoleParams:
    """
    Class containing parameters to be presented
    on terminal
    """
    system: str
    fps: float
    warnings: bool = False


def print_console(console, params: ConsoleParams):
    """
    Runs a Dynamic Terminal to present program info
    :param console: Terminal Object
    :param params: ConsoleParams object
    """
    fps = round(params.fps, 2)
    
    if params.warnings:
        warnings = 'ON'
    else:
        warnings = "OFF"
    
    system = params.system
    template = tabulate(
        [
            ["WARNINGS:", warnings],
            ["FPS:", str(fps)]
        ]
    )
    
    console.clear()
    console.addstr(system + '\n')
    console.addstr(template + '\n')
    
    console.refresh()
    

def print_fps_on_terminal(fps):
    """
    prints one line on terminal dynamically
    :param fps:
    :return:
    """
    stdout.write("\r{0} {1}>".format("[*] fps", fps))


def print_fps_on_frame(frame, fps):
    
    """
    takes a frame and returns same frame with fps on the upperleft corner
    :param frame: numpy array, image
    :param fps: float, fps value
    :return: printed frame
    """
    
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


def print_items_to_frame(frame, items):
    
    """
    take bboxes items from dict and print them into frame
    :param frame: numpy array, image
    :param items: orderedDict with bboxes on values
    :return: numpy array, new frame
    """
    
    fr = frame
    
    for (k, v) in items.items():
        
        ids = k
        bbox = v
        
        text_over_bbox = str(ids) + ': ' + bbox.mov[1]
        
        fr = cv2.rectangle(
            fr,
            bbox.start_point,
            bbox.end_point,
            bbox.color,
            2)
        
        cv2.putText(
            fr,
            text_over_bbox,
            bbox.start_point,
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            bbox.color,
            2
        )
    
    return fr


def print_bboxes_to_frame(frame, bboxes):
    
    """
    take bboxes and print them into frame
    :param frame: numpy array, image
    :param bboxes: bboxssd objects
    :return: numpy array, new frame
    """
    
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
