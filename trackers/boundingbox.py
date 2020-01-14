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
                self.prev_rect = self.rect

                self.start_point = (self.startX, self.startY)
                self.end_point = (self.endX, self.endY)
                self.color = self.colors[self.type]
                self.center = self.get_center()
                self.mov = 0.9
                self.stop_counter = 0
                self.area = 0

                self.up = self.rect.top()
                self.down = self.rect.bottom()
                self.left = self.rect.left()
                self.right = self.rect.right()



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

                # self.up = self.rect.top()
                # self.down = self.rect.bottom()
                # self.left = self.rect.left()
                # self.right = self.rect.right()

                self.trajectory()
                self.prev_rect = self.rect



                if self.status == 'stop':
                        self.color = self.colors['unknown']


        def trajectory(self):

                areaA = self.rect.intersect(self.prev_rect).area()
                areaB = self.prev_rect.intersect(self.rect).area()
                porc = (areaA + areaB) / (self.rect.area() + self.prev_rect.area())
                # self.area = self.area + 0.01*(((self.rect.area() - self.prev_rect.area()) / self.rect.area()) - self.area)

                self.mov = self.mov + 0.01*(porc- self.mov)





                if self.rect.bottom() < self.down:
                      self.status = 'stop'

                if self.rect.top() > self.up:
                      self.status = 'stop'

                if self.rect.right() < self.right:
                       self.status = 'stop'

                if self.rect.left() > self.left:
                        self.status = 'stop'

                if self.rect.top() < self.up:
                        self.up = self.rect.top()
                        self.status = 'move'

                if self.rect.bottom() > self.down:
                      self.down = self.rect.bottom()
                      self.status = 'move'

                if self.rect.right() > self.right:
                       self.right = self.rect.right()
                       self.status = 'move'

                if self.rect.left() < self.left:
                        self.left = self.rect.left()
                        self.status = 'move left'

                # self.status = str(self.up) + ' ' + str(self.right) + ' ' + str(self.down) + ' ' + str(self.left)



                #
                # if self.mov > 0.95:
                #         self.status = 'stop'
                # else:
                #         self.status = 'move'









