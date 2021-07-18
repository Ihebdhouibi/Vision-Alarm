import math
from collections import OrderedDict
import logging

LOG = logging.getLogger(__name__)


class FallDetector:

    def __init__(self):
        self.old_persons = OrderedDict()

    def update(self, persons):
        self.falls = OrderedDict()

        for ID, (x, y, x_, y_, w_, h_) in persons.items():

            if ID in self.old_persons:
                (old_x, old_y, old_w, old_h, fall) = self.old_persons[ID]

                if w_ >= 1.2 * h_:
                    if fall:
                        self.falls[ID] = (x_, y_, w_, h_)

                    elif math.sqrt(pow(abs(x-old_x), 2) + pow((y - old_y), 2)) >= 0.5 * math.sqrt(pow(old_w, 2) + pow(old_h, 2)):
                        LOG.info("Fall detected ")
                        self.falls[ID] = True
                        self.old_persons[ID] = (x, y, old_w, old_h, True)



            else :
                self.old_persons[ID] = (x, y, w_, h_, False)

        return self.falls