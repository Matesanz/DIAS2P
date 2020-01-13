import dlib


class BoundingBox:

        def __init__(self, box_points, name='unknown'):

                self.colors = {
                        'person': (255, 0, 0),
                        'car': (0, 255, 0),
                        'bicycle': (0, 0, 255),
                        'motorcycle': (255, 255, 0),
                        'bus': (0, 255, 255),
                        'truck': (255, 0, 255),
                        'unknown': (255, 255, 255)
                }

                self.type = name
                self.startX = box_points[0]
                self.startY = box_points[1]
                self.endX = box_points[2]
                self.endY = box_points[3]
                self.rect = dlib.rectangle(
                        self.startX,
                        self.startY,
                        self.endX,
                        self.endY
                )
                self.start_point = (self.startX, self.startY)
                self.end_point = (self.endX, self.endY)
                self.color = self.colors[self.type]

        def update_localization(self, rect):
                self.startX = rect.tl_corner.x
                self.startY = rect.tl_corner.y
                self.endX = rect.br_corner.x
                self.endY = rect.br_corner.y

        def update_name(self, name):
                self.type = name

        def update(self, bbox):

                rect = bbox.rect
                self.startX = rect.tl_corner().x
                self.startY = rect.tl_corner().y
                self.endX = rect.br_corner().x
                self.endY = rect.br_corner().y

                self.rect = dlib.rectangle(
                        self.startX,
                        self.startY,
                        self.endX,
                        self.endY
                )
                self.start_point = (self.startX, self.startY)
                self.end_point = (self.endX, self.endY)

                bbox_name = bbox.type

                if self.type == 'unknown':
                        self.type = bbox_name
                        self.color = self.colors[self.type]

