import dlib
from numpy import gradient, sum, linalg, array, asarray, less
from scipy.spatial.distance import cdist
from scipy.stats import linregress


class BoundingBox:

        def __init__(self, box_points, name='unknown'):

                self.status = "unknown"


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
                self.center = self.get_center()
                self.mov = array([0, 0])
                self.stop_counter = 0

                self.ratio = 1280/ self.rect.width()
                print(self.ratio)

        def update_localization(self, rect):
                self.startX = rect.tl_corner.x
                self.startY = rect.tl_corner.y
                self.endX = rect.br_corner.x
                self.endY = rect.br_corner.y

        def update_name(self, name):
                self.type = name

        def get_center(self):
                x = self.rect.dcenter().x
                y = self.rect.dcenter().y
                return array([x,y])

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
                self.type = bbox_name
                self.color = self.colors[self.type]

                self.trajectory()
                if self.status == 'stop':
                        self.color = self.colors['unknown']


        def trajectory(self):

                prev_center = self.center
                self.center = self.get_center()
                self.mov = self.mov + 0.1*(self.center - prev_center - self.mov)*self.ratio

                if less(self.mov, array([1, 1])).all():
                        self.status = 'stop'
                        if less(self.mov, array([-1, -1])).any():
                                self.status = 'move'

                else:
                        self.status = 'move'









