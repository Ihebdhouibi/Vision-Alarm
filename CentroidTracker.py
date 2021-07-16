from scipy.spatial import distance as dist
from collections import OrderedDict

import numpy as np


class CentroidTracker:

    def __init__(self, maxDisappeared=10):

        # a counter to asign a uniqueID to each object
        # if the object passes the maxDisappeared number of frames we will asign a new ObjectID
        self.nextObjectID = 0

        # a dict that stores for each object the objectID as key
        # and the centroid(x,y) as value
        self.objects = OrderedDict()

        # a dict that stores number of consecutive frames the object has disappeared in as a key
        # and objectID as value
        self.disappeared = OrderedDict()

        # the maximum number of frames for an object to not be in before declared disappeared
        self.maxDisappeared = maxDisappeared

    def register(self, centroid):

        self.objects[self.nextObjectID] = centroid
        self.disappeared[self.nextObjectID] = 0
        self.nextObjectID += 1

    def deregister(self, objectID):

        del self.objects[objectID]
        del self.disappeared[objectID]

    def update(self, rects):

        # rects format is a tuple (startX, startY, endX, endY)

        # checks to see if the list of input bounding box rectangles is empty

        if len(rects) == 0:
            # no object available in the given frame
            # Mark all existing objects as disappeared
            for objectId in list(self.disappeared.keys()):
                self.disappeared[objectId] += 1

                # deregister objects with disappeared_Frames_Number > maxDisappeared
                if self.disappeared[objectId] > self.maxDisappeared:
                    self.deregister(objectId)

            return self.objects

        # a numpy array to store objects centroids
        input_centroids = np.zeros((len(rects), 2), dtype="int")

        # loop over object rectangles and compute centroids than store it in input_centroids
        for (i, (startX, startY, endX, endY)) in enumerate(rects):

            cX = int((startX + endX) / 2.0)
            cY = int((startY + endY) / 2.0)

            input_centroids[i] = (cX, cY)

        # if there is no existing object already being tracked than we register these new objects
        if len(self.objects) == 0:
            for i in range(0, len(input_centroids)):
                self.register(input_centroids[i])


        else:
            # grab objectID/centroid

            objectIDs = list(self.objects.keys())
            objects_centroids = list(self.objects.values())

            # compute the euclidean distance between each pair of object centroids and input_centroids
            D = dist.cdist(np.array(objects_centroids), input_centroids)

            rows = D.min(axis=1).argsort()

            cols = D.argmin(axis=1)[rows]

            usedRows = set()
            usedCols = set()

            for (row, col) in zip(rows, cols):

                # print(f"row : {row} col : {col}")
                if row in usedRows or col in usedCols:
                    continue

                objectID = objectIDs[row]
                self.objects[objectID] = input_centroids[col]
                self.disappeared[objectID] = 0

                usedRows.add(row)
                usedCols.add(col)

            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)

            # if number of existing object_centroids is equal or grater than input_centroids
            # we need to check if some of these objects have been disappeared

            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:

                    objectID = objectIDs[row]
                    self.disappeared[objectID] += 1

                    if self.disappeared[objectID] > self.maxDisappeared:
                        self.deregister(objectID)

            else:
                # register new objects
                for col in unusedCols:
                    self.register(input_centroids[col])

        return self.objects


