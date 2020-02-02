from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np


class BBoxTracker:

        def __init__(self, maxDisappeared = 50):
                # initialize the next unique object ID along with two ordered
                # dictionaries used to keep track of mapping a given object
                # ID to its centroid and number of consecutive frames it has
                # been marked as "disappeared", respectively
                self.nextObjectID = 0
                self.objects = OrderedDict()
                self.disappeared = OrderedDict()


                # store the number of maximum consecutive frames a given
                # object is allowed to be marked as "disappeared" until we
                # need to deregister the object from tracking
                self.maxDisappeared = maxDisappeared

        def register(self, boundingBox):
                # when registering an object we use the next available object
                # ID to store the centroid
                self.objects[self.nextObjectID] = boundingBox
                self.disappeared[self.nextObjectID] = 0
                self.nextObjectID += 1

        def deregisterall(self):
                for obj in list(self.objects.keys()) :
                        self.deregister(obj)

        def deregister(self, objectID):
                # to deregister an object ID we delete the object ID from
                # both of our respective dictionaries
                del self.objects[objectID]
                del self.disappeared[objectID]

        def update(self, boundingBoxes):

                # Si no recibimos nuevas bounding boxes
                # Anotamos los objetos como desaparecidos
                # durante un frame y los devolvemos tal cual están
                if len(boundingBoxes) == 0:
                        for objectID in list(self.disappeared.keys()):
                                self.disappeared[objectID] += 1

                                # if we have reached a maximum number of consecutive
                                # frames where a given object has been marked as
                                # missing, deregister it
                                if self.disappeared[objectID] > self.maxDisappeared:
                                        self.deregister(objectID)
                        return self.objects

                # Si no hay objetos siendo trackeados anotamos
                # todas las detecciones como objetos a seguir
                if len(self.objects) == 0:

                        for bbox in boundingBoxes:
                                self.register(bbox)

                else:

                        #Controlar a qué objetos pertenecen las
                        # Bounding boxes que acabamos de reconocer

                        # grab the set of object IDs and corresponding centroids
                        objectIDs = list(self.objects.keys())
                        objectCentroids = np.asarray([bbox.center for bbox in self.objects.values()], dtype=np.int)
                        inputCentroids = np.asarray([bbox.center for bbox in boundingBoxes], dtype=np.int)

                        # compute the distance between each pair of object
                        # centroids and input centroids, respectively -- our
                        # goal will be to match an input centroid to an existing
                        # object centroid
                        D = dist.cdist(np.array(objectCentroids), inputCentroids)

                        # in order to perform this matching we must (1) find the
                        # smallest value in each row and then (2) sort the row
                        # indexes based on their minimum values so that the row
                        # with the smallest value as at the *front* of the index
                        # list
                        rows = D.min(axis=1).argsort()


                        # next, we perform a similar process on the columns by
                        # finding the smallest value in each column and then
                        # sorting using the previously computed row index list
                        cols = D.argmin(axis=1)[rows]


                        # in order to determine if we need to update, register,
                        # or deregister an object we need to keep track of which
                        # of the rows and column indexes we have already examined
                        usedRows = set()
                        usedCols = set()

                        # loop over the combination of the (row, column) index
                        # tuples
                        for (row, col) in zip(rows, cols):
                                # if we have already examined either the row or
                                # column value before, ignore it
                                # val
                                if row in usedRows or col in usedCols:
                                        continue

                                # otherwise, grab the object ID for the current row,
                                # set its new centroid, and reset the disappeared
                                # counter
                                objectID = objectIDs[row]
                                assignedBBox = boundingBoxes[col]
                                # self.objects[objectID] = assignedBBox
                                self.objects[objectID].update(assignedBBox)

                                self.disappeared[objectID] = 0

                                # indicate that we have examined each of the row and
                                # column indexes, respectively
                                usedRows.add(row)
                                usedCols.add(col)

                        # compute both the row and column index we have NOT yet
                        # examined
                        unusedRows = set(range(0, D.shape[0])).difference(usedRows)
                        unusedCols = set(range(0, D.shape[1])).difference(usedCols)

                        # in the event that the number of object centroids is
                        # equal or greater than the number of input centroids
                        # we need to check and see if some of these objects have
                        # potentially disappeared
                        if D.shape[0] >= D.shape[1]:
                                # loop over the unused row indexes
                                for row in unusedRows:
                                        # grab the object ID for the corresponding row
                                        # index and increment the disappeared counter
                                        objectID = objectIDs[row]
                                        self.disappeared[objectID] += 1

                                        # check to see if the number of consecutive
                                        # frames the object has been marked "disappeared"
                                        # for warrants deregistering the object
                                        if self.disappeared[objectID] > self.maxDisappeared:
                                                self.deregister(objectID)

                        # otherwise, if the number of input centroids is greater
                        # than the number of existing object centroids we need to
                        # register each new input centroid as a trackable object
                        else:

                                for col in unusedCols:
                                        self.register(boundingBoxes[col])

                # return the set of trackable objects
                return self.objects
