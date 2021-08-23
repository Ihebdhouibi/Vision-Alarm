from datetime import datetime
from multiprocessing import Pipe

from valkka.api2 import FragMP4ShmemClient

from DataBase import storeFireAlertData
from cloudStorage import uploadBlob
from AlertAdmin import send_sms
from multiprocess import QValkkaOpenCVProcess
from PySide6 import QtCore
import time
import cv2
import numpy as np


class QValkkaFireDetectorProcess(QValkkaOpenCVProcess):


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

        self.frames = []
        self.alert = False
        self.num_noFire_Frame = 10
        self.x = 1
        self.counter = 0
        self.fdetect = 0
        self.FireDetected = False
        self.numb_frames = 0
        self.start_time = time.time()

    def alarm(self):
        print('Fire detected')
        self.sendSignal_(name="Fire_detected")

    def cycle_(self):
        # print('inside FireDetectorProcess')
        self.counter += 1
        start_time = time.time()
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
                imgBlurred = cv2.GaussianBlur(img, (23, 23), 0)

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
                print('total number : ', int(total_number))

                # calculate fps
                # self.numb_frames += 1
                # print("Start time : ",self.start_time)
                # print("time now : ",time.time())
                # print("numb_frames :",self.numb_frames)
                # print("start time - time now = ", time.time()- self.start_time)
                # if(time.time() - start_time) > 1:
                #     print("fps : ",self.numb_frames / ( time.time() -self.start_time ))


                if int(total_number) > 1000:
                    self.fdetect += 1
                    self.num_noFire_Frame = 0
                    self.frames.append(img)

                    if self.fdetect >= 1:
                        if self.FireDetected is False:
                            print('Fire detected')
                            self.sendSignal_(name="Fire_detected")
                            self.FireDetected = True
                            self.alert = True
                            print(' fireDetected :', self.FireDetected)
                            print(' fdetect : ', self.fdetect)
                    # pass
                elif self.num_noFire_Frame < 10:
                    # self.fireDetected = False
                    # self.fdetect = 0
                    self.num_noFire_Frame += 1
                    self.frames.append(img)

                else:
                    if self.alert:

                        # if(time.time() - start_time) > self.x:
                        #     print("FPS : ", self.counter / time.time() - start_time)
                        #     self.counter = 0
                        #     start_time = time.time()
                        #     # work on fps


                        video = np.stack(self.frames, axis=0)
                        img_height, img_width, img_channels = img.shape
                        videolink = "{"+ uploadBlob(videoArray=video,
                                               videoName="Fire_Alert",
                                               width=img_width,
                                               height=img_height,
                                               fps=30) + "}"
                        alertTime = "{" + str(datetime.today()) + " " + datetime.now().strftime("%H:%M:%S") + "}"

                        # storing the alert
                        storeFireAlertData(alertTime=alertTime,
                                           videoLink=videolink,
                                           AlertClass=True)
                        self.alert = False

                        print("Video link : ",videolink)

                        msg = "There is a Fire alert " \
                              "Check the following link to view it" \
                              f"{videolink}"

                        phone = +21652562136

                        send_sms(msg=msg, phone=phone)
    # ** frontend methods handling received outgoing signals ***
                print("num_noFire_Frame : ",self.num_noFire_Frame)
    def Fire_detected(self):
        print("At frontend: fire detected ")
        self.signals.Fire_detected.emit()


# class FireDetector:
#
#     fireDetected = False
#     fdetect = 0
#
#     incoming_signal_defs = {
#         # each key corresponds to a front- and backend methods
#     }
#
#     outgoing_signals_defs = {
#         "fire_detected": {}
#     }
#     # For each outgoing signal create a Qt signal with the same name.
#
#     def __init__(self, frame):
#
#
#         imgblurred = cv2.GaussianBlur(frame, (15, 15), 0)
#         # Lets convert the image to HSV
#         imgHSV = cv2.cvtColor(imgblurred, cv2.COLOR_BGR2HSV)
#
#         # Define the mask
#         lower_mask_value = [18, 50, 50]
#         upper_mask_value = [36, 255, 255]
#
#         lower_mask_value = np.array(lower_mask_value, dtype='uint8')
#         upper_mask_value = np.array(upper_mask_value, dtype='uint8')
#
#         mask = cv2.inRange(imgHSV, lower_mask_value, upper_mask_value)
#
#         # Count the total number of red pixels ; total number of non zero pixels
#         total_number = cv2.countNonZero(mask)
#         print('total number : ', int(total_number))
#         if total_number > 500:
#             print("fire detected")

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