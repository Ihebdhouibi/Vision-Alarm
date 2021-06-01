from multiprocess import QValkkaOpenCVProcess
from PySide6 import QtCore
import time
import cv2
import numpy as np


class QValkkaFireDetectorProcess(QValkkaOpenCVProcess):
    fireDetected = False
    fdetect = 0

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_": [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str},
        "start_move": {},
        "Fire_detected": {},
        "stop_move": {}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):

        # PySide2 version:
        pong_o = QtCore.Signal(object)
        start_move = QtCore.Signal()
        Fire_detected = QtCore.Signal()
        stop_move = QtCore.Signal()

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)  # does parameterInitCheck
        self.signals = self.Signals()

        # # parameterInitCheck(QValkkaMovementDetectorProcess.parameter_defs, kwargs, self)
        # self.analyzer=MovementDetector(verbose=True)
        # self.analyzer = MovementDetector(treshold=0.0001)# To be changed

    def alarm(self):
        print('Fire detected')
        self.sendSignal_(name="Fire_detected")

    def cycle_(self):
        # print('inside FireDetectorProcess')
        if self.client is None:
            time.sleep(1.0)
        else:
            index, isize = self.client.pull()
            if (index is None):
                # print(self.pre, "Client timed out..")
                pass
            else:
                print("Client index, size =", index, isize)
                try:
                    data = self.client.shmem_list[index]
                    # print(data)
                except BaseException:
                    print("There is an issue in getting data from shmem_list")
                try:
                    img = data.reshape(
                        (self.image_dimensions[1], self.image_dimensions[0], 3))
                except BaseException:
                    print("QValkkaMovementDetectorProcess: WARNING: could not reshape image")

                # else:
                #     result = self.analyzer(img)
                #     # print(self.pre,">>>",data[0:10])
                #     if (result == MovementDetector.state_same):
                #         pass
                #     elif (result == MovementDetector.state_start):
                #         self.sendSignal_(name="start_move")
                #     elif (result == MovementDetector.state_stop):
                #         self.sendSignal_(name="stop_move")

                # cv2.imshow('image', img)
                # cv2.waitKey(10)
                # lets apply blur to reduce noise
                # imgBlurred = cv2.GaussianBlur(img, (5, 5), 0)

                # Lets convert the image to HSV
                imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

                # Define the mask
                lower_mask_value = [18, 50, 50]
                upper_mask_value = [36, 255, 255]

                lower_mask_value = np.array(lower_mask_value, dtype='uint8')
                upper_mask_value = np.array(upper_mask_value, dtype='uint8')

                mask = cv2.inRange(imgHSV, lower_mask_value, upper_mask_value)

                # Count the total number of red pixels ; total number of non zero pixels
                total_number = cv2.countNonZero(mask)
                print('total number : ', int(total_number))

                print(' fireDetected :', self.fireDetected)
                print(' fdetect : ', self.fdetect)
                if int(total_number) > 1000:
                    self.fdetect += 1

                    if self.fdetect >= 1:
                        if self.fireDetected is False:
                            print('Fire detected')
                            self.sendSignal_(name="Fire_detected")
                            self.fireDetected = True
                            print(' fireDetected :', self.fireDetected)
                            print(' fdetect : ', self.fdetect)
                    # pass
                else:
                    self.fireDetected = False
                    self.fdetect = 0

    # ** frontend methods handling received outgoing signals ***

    def Fire_detected(self):
        print("At frontend: fire detected ")
        self.signals.Fire_detected.emit()
