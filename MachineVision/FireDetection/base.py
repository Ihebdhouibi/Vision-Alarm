from multiprocessing import Pipe

from valkka.api2 import FragMP4ShmemClient

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
        "Fire_detected": {},

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
            # print('client timedout')
        else:
            index, isize = self.client.pull()
            if (index is None):
                # print(self.pre, "Client timed out..")
                pass
            else:
                # print("Client index, size =", index, isize)
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

                # lets apply blur to reduce noise
                imgBlurred = cv2.GaussianBlur(img, (15, 15), 0)

                # Lets convert the image to HSV
                imgHSV = cv2.cvtColor(imgBlurred, cv2.COLOR_BGR2HSV)

                # Define the mask
                lower_mask_value = [18, 50, 50]
                upper_mask_value = [36, 255, 255]

                lower_mask_value = np.array(lower_mask_value, dtype='uint8')
                upper_mask_value = np.array(upper_mask_value, dtype='uint8')

                mask = cv2.inRange(imgHSV, lower_mask_value, upper_mask_value)

                # Count the total number of red pixels ; total number of non zero pixels
                total_number = cv2.countNonZero(mask)
                # print('total number : ', int(total_number))

                if int(total_number) > 5000:
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


class FireDetector:

    fireDetected = False
    fdetect = 0

    incoming_signal_defs = {
        # each key corresponds to a front- and backend methods
    }

    outgoing_signals_defs = {
        "fire_detected": {}
    }
    # For each outgoing signal create a Qt signal with the same name.

    def __init__(self, frame):


        imgblurred = cv2.GaussianBlur(frame, (15, 15), 0)
        # Lets convert the image to HSV
        imgHSV = cv2.cvtColor(imgblurred, cv2.COLOR_BGR2HSV)

        # Define the mask
        lower_mask_value = [18, 50, 50]
        upper_mask_value = [36, 255, 255]

        lower_mask_value = np.array(lower_mask_value, dtype='uint8')
        upper_mask_value = np.array(upper_mask_value, dtype='uint8')

        mask = cv2.inRange(imgHSV, lower_mask_value, upper_mask_value)

        # Count the total number of red pixels ; total number of non zero pixels
        total_number = cv2.countNonZero(mask)
        print('total number : ', int(total_number))
        if total_number > 500:
            print("fire detected")

    # """
    # Frontend methods
    # """
    # def sendSignal(self, **kwargs):
    #
    # """
    # Backend methods
    # """
    #
    # def sendSignal_(self, **kwargs):
    #     """
    #     Outgoing signals: signals from backend to frontend
    #     """
    #     try:
    #         name = kwargs.pop("name")
    #     except KeyError:
    #         raise(AttributeError("Signal name missing "))
    #
    #     model = self.outgoing_signals_defs[name]
    #
    #     for key in kwargs:
    #         # raises error if user is using undefined signal
    #         try:
    #             model_type = model[key]
    #         except KeyError:
    #             print("your outgoing_signal_defs for", name, " is : ", model)
    #             print("you requested key : ", key)
    #             raise
    #         parameter_type = kwargs[key].__class__
    #         if (model_type == parameter_type):
    #             pass
    #         else:
    #             raise(AttributeError("wrong type for parameter "+ str(key)))
    #     kwargs["name"] = name
    #
    #     self.childpipe.send(kwargs)