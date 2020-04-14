from utils import classes
from collections import deque


class BBox:

        def __init__(self, detection):

                self.detection = detection
                self.name = classes.classesDict[detection.ClassID]
                self.start_point = (int(detection.Left), int(detection.Top))
                self.end_point = (int(detection.Right), int(detection.Bottom))
                self.center = tuple(map(int, detection.Center))

                # Colors for known classes
                self.colors = {
                        'person': (255, 0, 0),
                        'car': (0, 255, 0),
                        'bicycle': (0, 0, 255),
                        'motorcycle': (255, 255, 0),
                        'bus': (0, 255, 255),
                        'truck': (255, 0, 255),
                        'unknown': (255, 255, 255)
                }

                # Set color only to known classes
                self.color = self.colors[self.name] if self.name in self.colors.keys() else self.colors['unknown']

                # Initialize Movement variables
                # It tracks whether the object is going
                # up down right or left

                self.status = 'stop'
                self.mov = ['unknown', 'unknown']
                self.dx = 0
                self. dy = 0
                self.coef = 0

                self.memory = deque([], maxlen=5)
                self.memory.append(self.center)

        def update(self, bbox):

                detection = bbox.detection

                self.update_trajectory(detection)
                # self.update_status()

                self.start_point = (int(detection.Left), int(detection.Top))
                self.end_point = (int(detection.Right), int(detection.Bottom))
                self.center = tuple(map(int, detection.Center))

        def update_trajectory(self, detection):

                actual_center = tuple(map(int, detection.Center))
                self.memory.append(actual_center)

                if len(self.memory) >= self.memory.maxlen:

                        prev_center = self.memory[0]

                        dx = actual_center[0] - prev_center[0]
                        dy = actual_center[1] - prev_center[1]

                        self.dx += 0.1*(dx - self.dx)
                        self.dy += 0.1*(dy - self.dy)

                        self.mov[0] = 'left' if self.dx < 0 else 'right'
                        self.mov[1] = 'up' if self.dy < 0 else 'down'

        def update_status(self):
                if abs(self.dx) > 1 or abs(self.dy) > 1:
                        self.color = self.colors[self.name] if self.name in self.colors.keys() else self.colors[
                                'unknown']
                        self.status = 'move'
                else:
                        self.color = self.colors['unknown']
                        self.status = 'stop'








