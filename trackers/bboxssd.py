from utils import classes


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

        def update(self, bbox):

                detection = bbox.detection

                self.update_trajectory(detection)
                self.update_status()

                self.start_point = (int(detection.Left), int(detection.Top))
                self.end_point = (int(detection.Right), int(detection.Bottom))
                self.center = tuple(map(int, detection.Center))

        def update_trajectory(self, detection):

                prev_center = self.center
                actual_center = tuple(map(int, detection.Center))

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
        #
        #         self.type = name
        #         self.startX = box_points[0]
        #         self.startY = box_points[1]
        #         self.endX = box_points[2]
        #         self.endY = box_points[3]
        #         self.rect = dlib.rectangle(
        #                 self.startX,
        #                 self.startY,
        #                 self.endX,
        #                 self.endY
        #         )
        #         self.prev_rect = self.rect
        #
        #         self.start_point = (self.startX, self.startY)
        #         self.end_point = (self.endX, self.endY)
        #         self.color = self.colors[self.type]
        #         self.center = self.get_center()
        #
        #         self.mov = ['unknown', 'unknown']
        #         self.dx = 0
        #         self. dy = 0
        #
        #
        #
        # def update_localization(self, rect):
        #         self.startX = rect.tl_corner.x
        #         self.startY = rect.tl_corner.y
        #         self.endX = rect.br_corner.x
        #         self.endY = rect.br_corner.y
        #
        # def update_name(self, name):
        #         self.type = name
        #
        # def get_center(self):
        #         x = self.rect.dcenter().x
        #         y = self.rect.dcenter().y
        #         return (x, y)
        #
        # def update(self, bbox):
        #
        #
        #         rect = bbox.rect
        #
        #         self.startX = rect.tl_corner().x
        #         self.startY = rect.tl_corner().y
        #         self.endX = rect.br_corner().x
        #         self.endY = rect.br_corner().y
        #
        #         self.rect = rect
        #
        #         self.start_point = (self.startX, self.startY)
        #         self.end_point = (self.endX, self.endY)
        #
        #         self.trajectory()
        #         # self.calculate_color()
        #
        #
        #
        #

        #
        # def calculate_color(self):
        #
        #         fraction = abs((7 - abs(self.dx)) / 7)
        #         r = 255 * fraction
        #         self.color = (r, r, 255)








