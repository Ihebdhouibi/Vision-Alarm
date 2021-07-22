import time
from collections import OrderedDict

import numpy as np
import openpifpaf
import torch.multiprocessing as mp


from datetime import datetime
from multiprocess import QValkkaOpenCVProcess
from PySide6 import QtCore

# local imports
from .CentroidTracker import CentroidTracker
from .FallDetector import FallDetector
from cloudStorage import uploadBlob
from DataBase import storeFallAlertData


class QValkkaFallDetection(QValkkaOpenCVProcess):
    vdist = 0
    maxHeight = 0

    confidence = 0

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_": [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str},
        "Fall_detected": {}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.

    class Signals(QtCore.QObject):

        pong_o = QtCore.Signal(object)
        Fall_detected = QtCore.Signal()

    def __init__(self, name, **kwargs):

        super().__init__(name, **kwargs)  # Checking parameter
        self.signals = self.Signals()
        self.predictor = openpifpaf.Predictor(checkpoint='shufflenetv2k30', json_data=True)
        self.annotation_painter = openpifpaf.show.AnnotationPainter()

        self.centroid_tracker = CentroidTracker()
        self.fall_detector = FallDetector()

        self.frames = []
        self.alert = False
        self.numb_noFall_Frame = 300

        self.fdetect = 0
        self.fallDetected = False
        # mp.set_start_method('spawn')
    def alarm(self):
        print("Fall detected ! ")
        self.sendSignal_(name="Fall_detected")

    def cycle_(self):
        print("inside cycle of fall detection")
        if self.client is None:
            time.sleep(1.0)
            # print(self.pre, "Client timed out..")
        else:
            index, isize = self.client.pull()

            if index is None:
                # print(self.pre, "Client timed out.. ")
                pass

            else:
                # print("Client index, size =", index, isize)
                try:
                    data = self.client.shmem_list[index]
                except BaseException:
                    print(self.pre, "There is an issue in getting data from shmem_list")
                try:
                    img = data.reshape(
                        (self.image_dimensions[1], self.image_dimensions[0], 3))
                except BaseException:
                    print("QValkkaFallDetectionProcess : WARNING: could not reshape image")

                # Develop Fall Detection model here
                try:
                    predictions, gt_anns, image_meta = self.predictor.numpy_image(img)
                    person_number = len(predictions)

                    person_info_for_CT = []
                    person_info_for_FD = []

                    if predictions:
                        j = 0
                        while j < person_number:
                            print(f"number of person {len(predictions)}")
                            keypoints = predictions[j]["keypoints"]

                            if keypoints.count(0.0) > len(keypoints) / 1.5:
                                # Current keypoint is not valid abandone it
                                j += 1
                                continue

                            # otherwise keypoint is valid ! Lets do the stuff
                            startX = int(predictions[j]["bbox"][0])
                            startY = int(predictions[j]["bbox"][1])
                            endX = int(startX + predictions[j]["bbox"][2])
                            endY = int(startY + predictions[j]["bbox"][3])

                            width = predictions[j]["bbox"][2]
                            height = predictions[j]["bbox"][3]

                            person_info_for_CT.append((startX, startY, endX, endY))
                            person_info_for_FD.append((startX, startY, endX, endY, width, height))

                            j += 1

                    persons = self.centroid_tracker.update(rects=person_info_for_CT)
                    persons2 = OrderedDict()

                    if len(person_info_for_FD) > 0:
                        for ID in range(0, len(person_info_for_FD)):
                            persons2[ID] = person_info_for_FD[ID]

                    fall = self.fall_detector.update(persons2)

                    if fall:
                        self.numb_noFall_Frame = 0
                        self.frames.append(img)
                        # print("Fall detected")
                        self.fdetect += 1
                        if self.fdetect >=1:
                            if self.fallDetected is False:
                                print("Fall detected")
                                self.sendSignal_(name="Fall_detected")
                                self.fallDetected = True
                                print(f"fallDetected = {self.fallDetected}")

                    elif self.numb_noFall_Frame < 300:
                        self.numb_noFall_Frame += 1
                        self.frames.append(img)
                        self.alert = True

                    else:
                        if self.alert:
                            video = np.stack(self.frames, axis=0)
                            img_height, img_width, img_channels = img.shape
                            videoLink = uploadBlob(videoArray=video,
                                                   videoName="Fall_Alert",
                                                   width=img_width,
                                                   height=img_height)

                            alertTime = str(datetime.today()) + " " + datetime.now().strftime("%H:%M:%S")

                            # Storing the alert
                            storeFallAlertData(alertTime=alertTime,
                                               videoLink=videoLink,
                                               AlertClass=True)

                            self.alert = False
                except Exception as e:
                    print(self.pre, "There is an issue extracting info from predictor : ", e)



    def Fall_detected(self):
        print("At frontend : fall detected")
        self.signals.Fall_detected.emit()
