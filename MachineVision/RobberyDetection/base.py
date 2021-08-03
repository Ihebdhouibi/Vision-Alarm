from multiprocess import QValkkaOpenCVProcess
from PySide6 import QtCore
import time

# Local imports
from .PersonDetector import PersonDetector


class QValkkaRobberyDetectorProcess(QValkkaOpenCVProcess):
    incoming_signal_defs = {
        "create_client_": [],
        "test_": {"test_int": int, "test_str": str},
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "Robbery_detected": {}
    }

    class Signals(QtCore.QObject):

        Robbery_detected = QtCore.Signal()

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.signals = self.Signals()
        self.personDetector = PersonDetector()

    def alarm(self):
        print("Robbery detected -- inside alarm")
        self.sendSignal_(name="Robbery_detected")

    def cycle_(self):
        print("inside robbery detection")
        if self.client is None:
            time.sleep(1.0)
            # print('client timedout')
        else:
            index, isize = self.client.pull()
            if (index is None):
                print(self.pre, "Client timed out..")
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
                    print("QValkkaRobberyDetectorProcess: WARNING: could not reshape image")

                if self.personDetector.cycle(img):
                    print(self.personDetector.cycle(img))
                    print("Now let's detect if there is ongoing robbery ")
                else:
                    print(self.personDetector.cycle(img))
                    print("Nothing detected yet ! ")
                    pass

    # ** Frontend methods handling recieved outgoing signals

    def Robbery_detected(self):
        print("At frontend: robbery detected ")
        self.signals.Robbery_detected.emit()
