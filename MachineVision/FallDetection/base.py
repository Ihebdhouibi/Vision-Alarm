import time

import cv2
import openpifpaf

from multiprocess import QValkkaOpenCVProcess
from PySide6 import QtCore


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
        self.noseX = 0
        self.noseY = 0

    def alarm(self):
        print("Fall detected ! ")
        self.sendSignal_(name="Fall_detected")

    def cycle_(self):
        # print("inside cycle of fall detection")
        if self.client is None:
            time.sleep(1.0)
            # print(self.pre, "Client timed out..")
        else:
            index, isize = self.client.pull()

            if index is None:
                print(self.pre, "Client timed out.. ")
                # pass

            else:
                print("Client index, size =",index, isize)
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

                # RGB_img = img

                predictions, gt_anns, image_meta = self.predictor.numpy_image(img)

                try:

                    if predictions:
                        # there is a person in the frame
                        if predictions[0]["keypoints"][2] != 0:
                            # nose keypoint valid
                            if self.noseX == 0:
                                self.noseX = predictions[0]["keypoints"][0]
                                current_noseX = self.noseX
                            if self.noseY == 0:
                                self.noseY = predictions[0]["keypoints"][1]
                                current_noseY = self.noseY

                            current_noseY = predictions[0]["keypoints"][1]
                            height = predictions[0]["bbox"][3]
                            width = predictions[0]["bbox"][2]

                            print("height : ", height)
                            print("width : ", width)
                        if self.noseY < current_noseY * 2:

                            if width > height:

                               print("Fall detected")
                    else:
                        print("no person available ")

                except BaseException as e:
                    print("Exception : ", e)



    def Fall_detected(self):
        print("At frontend : fall detected")
        self.signals.Fall_detected.emit()
