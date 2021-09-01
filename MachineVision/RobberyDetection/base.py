# import cv2
#
# from multiprocess import QValkkaOpenCVProcess
# from PySide6 import QtCore
# import time
# from keras.models import load_model
# from keras.preprocessing.image import img_to_array
# import tensorflow as tf
#
# # Local imports
# from .PersonDetector import PersonDetector
#
#
# class QValkkaRobberyDetectorProcess(QValkkaOpenCVProcess):
#     incoming_signal_defs = {
#         "create_client_": [],
#         "test_": {"test_int": int, "test_str": str},
#         "ping_": {"message": str}
#     }
#
#     outgoing_signal_defs = {
#         "Robbery_detected": {}
#     }
#
#     class Signals(QtCore.QObject):
#
#         Robbery_detected = QtCore.Signal()
#
#     def __init__(self, name, **kwargs):
#         super().__init__(name, **kwargs)
#         self.signals = self.Signals()
#         self.personDetector = PersonDetector()
#         self.RobberyDetector = load_model('/home/iheb/PycharmProjects/Vision-Alarm/MachineVision/RobberyDetection/Robbery_Detection_Model3.h5')
#
#     def alarm(self):
#         print("Robbery detected -- inside alarm")
#         self.sendSignal_(name="Robbery_detected")
#
#     def cycle_(self):
#         # print("inside robbery detection")
#         if self.client is None:
#             time.sleep(3.0)
#             # print('client timedout')
#         else:
#             index, isize = self.client.pull()
#             if (index is None):
#                 print(self.pre, "Client timed out..")
#                 pass
#
#             else:
#                 print("Client index, size =", index, isize)
#                 try:
#                     data = self.client.shmem_list[index]
#                     # print(data)
#                 except BaseException:
#                     print("There is an issue in getting data from shmem_list")
#                 try:
#                     img = data.reshape(
#                         (self.image_dimensions[1], self.image_dimensions[0], 3))
#                 except BaseException:
#                     print("QValkkaRobberyDetectorProcess: WARNING: could not reshape image")
#
#                 # if self.personDetector.cycle(img):
#                 #     print(self.personDetector.cycle(img))
#                 #     print("Now let's detect if there is ongoing robbery ")
#
#                 img_resized = cv2.resize(img, (224,224))
#                 img_array = img_to_array(img=img_resized)
#                 img_array = tf.expand_dims(img_array, 0)
#
#                 predictions = self.RobberyDetector.predict(img_array)
#                 score = predictions[0]
#                 print("this image is %.2f percent No robbery and %.2f robber" % (100 * (1 - score), 100 * score))
#
#                 # else:
#                 print(self.personDetector.cycle(img))
#                 print("Nothing detected yet ! ")
#                     # pass
#                 # if self.RobberyDetector(img):
#                 #     print("yeaaaaaaaaaaaaah")
#                 # else:
#                 #     print("tnekna")
#     # ** Frontend methods handling recieved outgoing signals
#
#     def Robbery_detected(self):
#         print("At frontend: robbery detected ")
#         self.signals.Robbery_detected.emit()

import cv2
import time
import tensorflow as tf
import numpy as np
from PIL import Image
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from datetime import datetime
from PySide6 import QtCore

# local imports
from DataBase import storeFireAlertData
from cloudStorage import uploadBlob
from AlertAdmin import send_sms
from multiprocess import QValkkaOpenCVProcess
from .PersonDetector import PersonDetector


class QValkkaRobberyDetectorProcess(QValkkaOpenCVProcess):


    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_": [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str},
        "Robbery_detected": {},

    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):

        # PySide2 version:
        pong_o = QtCore.Signal(object)
        start_move = QtCore.Signal()
        Robbery_detected = QtCore.Signal()
        stop_move = QtCore.Signal()

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)  # does parameterInitCheck
        self.signals = self.Signals()

        # # parameterInitCheck(QValkkaMovementDetectorProcess.parameter_defs, kwargs, self)
        # self.analyzer=MovementDetector(verbose=True)
        # self.analyzer = MovementDetector(treshold=0.0001)# To be changed

        self.personDetector = PersonDetector()
        self.RobberyDetector = load_model('/home/iheb/PycharmProjects/Vision-Alarm/MachineVision/RobberyDetection/Robbery_Detection_Model3.h5')

    def alarm(self):
        print('Robbery Robbery')
        self.sendSignal_(name="Robbery_detected")

    def cycle_(self):
        # print('inside Robbery detection')
        if self.client is None:
            time.sleep(1.0)
            print('client timedout')
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
                    print("QValkkaRobberyDetectorProcess: WARNING: could not reshape image")

                print("Let's try our model for each input image : \n")
                img_resized = cv2.resize(img, (224, 224))
                img = Image.fromarray(img_resized)

                print(img_resized.shape)
                print(type(img_resized))
                print(type(img))
                img_array = img_to_array(img=img)
                img_array = tf.expand_dims(img_array, 0)

                print("img : ",type(img))
                print("img_array : ",type(img_array))
                # print(img_array)
                try:
                    predictions = self.RobberyDetector.predict(img_array)
                    print("preds :",predictions)
                    score = predictions[0]
                    print("this image is %.2f No Robber and %.2f Robbery" %(100 * (1-score), 100 * score))
                except Exception as e:
                    print("Unable to predict image class : "+str(e))
    # ** frontend methods handling received outgoing signals ***

    def Robbery_detected(self):
        print("At frontend: Robbery detected ")
        self.signals.Robbery_detected.emit()

