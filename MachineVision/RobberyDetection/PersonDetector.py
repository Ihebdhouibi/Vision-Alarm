import cv2
import numpy as np

class PersonDetector:

    def __init__(self):
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    def cycle(self, frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        boxes, weights = self.hog.detectMultiScale(gray, winStride=(8, 8))

        if boxes is not None:
            print("Human detected")
            return True
        else:
            return False


