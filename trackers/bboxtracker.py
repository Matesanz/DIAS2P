from collections import OrderedDict
from utils.utils import calculate_intersection_matrix


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
                        objectbboxes = list(self.objects.values())

                        unused_objects_ids = objectIDs.copy()
                        unused_detected_idxs = list(range(0, len(boundingBoxes)))

                        matrix = calculate_intersection_matrix(boundingBoxes, objectbboxes)

                        for tracked, detected in zip(matrix[0], matrix[1]):

                                if tracked == -1:
                                        continue

                                objectID = objectIDs[tracked]
                                detectedbbox = boundingBoxes[detected]
  
                                self.objects[objectID].update(detectedbbox)
                                self.disappeared[objectID] = 0

                                unused_objects_ids.remove(objectID)
                                unused_detected_idxs.remove(detected)


                        # in the event that the number of object centroids is
                        # equal or greater than the number of input centroids
                        # we need to check and see if some of these objects have
                       # potentially disappeared

                        tracked_objects_n = len(objectbboxes)
                        detected_objects_n = len(boundingBoxes)

                        if tracked_objects_n >= detected_objects_n:

                                for object_id in unused_objects_ids:
                                        self.disappeared[object_id] += 1

                                # check to see if the number of consecutive
                                # frames the object has been marked "disappeared"
                                # for warrants deregistering the object
                                        if self.disappeared[object_id] > self.maxDisappeared:

                                                self.deregister(object_id)

                        # otherwise, if the number of input centroids is greater
                        # than the number of existing object centroids we need to
                        # register each new input centroid as a trackable object
                        else:

                                for new_idx in unused_detected_idxs:
                                        self.register(boundingBoxes[new_idx])

                # return the set of trackable objects
                return self.objects


