import imutils
from valkka.api2 import ValkkaProcess, Namespace, safe_select
from PySide6 import QtCore, QtWidgets
from valkka.api2.tools import *
import time
import sys
import cv2
from valkka.api2 import ShmemRGBClient
import multiprocessing as mp
import dill as pickle

class QValkkaProcess(ValkkaProcess):
    """A multiprocess with Qt signals
    """

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):
        # pong_o  =QtCore.pyqtSignal(object) # PyQt5
        pong_o = QtCore.Signal(object)  # PySide2

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.signals = self.Signals()

    def cycle_(self):
        # Do whatever your process should be doing, remember timeout every now
        # and then
        time.sleep(0.5)
        # print(self.pre,"hello!")

    # *** backend methods corresponding to incoming signals ***

    def stop_(self):
        self.running = False

    def test_(self, test_int=0, test_str="nada"):
        print(self.pre, "test_ signal received with", test_int, test_str)

    def ping_(self, message="nada"):
        print(
            self.pre,
            "At backend: ping_ received",
            message,
            "sending it back to front")
        self.sendSignal_(name="pong_o", message=message)

    # ** frontend methods launching incoming signals

    def stop(self):
        self.sendSignal(name="stop_")

    def test(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["test_"], kwargs)
        kwargs["name"] = "test_"
        self.sendSignal(**kwargs)

    def ping(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["ping_"], kwargs)
        kwargs["name"] = "ping_"
        self.sendSignal(**kwargs)

    # ** frontend methods handling received outgoing signals ***
    def pong_o(self, message="nada"):
        print("At frontend: pong got message", message)
        ns = Namespace()
        ns.message = message
        self.signals.pong_o.emit(ns)

class QValkkaThread(QtCore.QThread):
    """A QThread that sits between multiprocesses message pipe and Qt's signal system

    After ValkkaProcess instances have been given to this thread, they are accessible with:
    .process_name
    [process_index]

    The processes have methods that launch ingoing signals (like ping(message="hello")) and Qt signals that can be connected to slots (e.g. process.signals.pong_o.connect(slot))
    """

    def __init__(self, timeout=1, processes=[]):
        super().__init__()
        self.pre = self.__class__.__name__ + " : "
        self.timeout = timeout
        self.processes = processes
        self.process_by_pipe = {}
        self.process_by_name = {}
        for p in self.processes:
            self.process_by_pipe[p.getPipe()] = p
            self.process_by_name[p.name] = p

    def preRun(self):
        pass

    def postRun(self):
        pass

    def run(self):
        self.preRun()
        self.loop = True

        rlis = []
        wlis = []
        elis = []
        for key in self.process_by_pipe:
            rlis.append(key)

        while self.loop:
            tlis = safe_select(rlis, wlis, elis, timeout=self.timeout)
            for pipe in tlis[0]:
                # let's find the process that sent the message to the pipe
                p = self.process_by_pipe[pipe]
                # print("receiving from",p,"with pipe",pipe)
                st = pipe.recv()  # get signal from the process
                # print("got from  from",p,"with pipe",pipe,":",st)
                p.handleSignal(st)

        self.postRun()
        print(self.pre, "bye!")

    def stop(self):
        self.loop = False
        self.wait()

    def __getattr__(self, attr):
        return self.process_by_name[attr]

    def __getitem__(self, i):
        return self.processes[i]


class QValkkaOpenCVProcess(ValkkaProcess):
    """A multiprocess with Qt signals, using OpenCV.  Reads RGB images from shared memory
    """

    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_": [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):

        pong_o = QtCore.Signal(object)  # PySide2

    parameter_defs = {
        "n_buffer": (int, 10),
        "image_dimensions": tuple,
        "shmem_name": str
    }

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.signals = self.Signals()

        parameterInitCheck(QValkkaOpenCVProcess.parameter_defs, kwargs, self)
        typeCheck(self.image_dimensions[0], int)
        typeCheck(self.image_dimensions[1], int)


    def preRun_(self):
        """Create the shared memory client after fork
        """
        super().preRun_()
        self.client = None

    def cycle_(self):
        if self.client is None:
            time.sleep(1.0)
        else:
            index, isize = self.client.pull()
            if (index is None):
                print(self.pre, "Client timed out..")
            else:
                print(self.pre, "Client index, size =", index, isize)
                data = self.client.shmem_list[index]
                img = data.reshape(
                    (self.image_dimensions[1], self.image_dimensions[0], 3))
                """ # WARNING: the x-server doesn't like this, i.e., we're creating a window from a separate python multiprocess, so the program will crash
                print(self.pre,"Visualizing with OpenCV") """
                cv2.imshow("openCV_window", img)
                cv2.waitKey(1)

                print(self.pre, ">>>", data[0:10])

                # res=self.analyzer(img) # does something .. returns something ..

    def postCreateClient_(self):
        """Override in child methods: call after the shmem client has been created
        """
        pass

    # *** backend methods corresponding to incoming signals ***

    def stop_(self):
        self.running = False

    def create_client_(self):
        print("inside create_client of multiprocess \n shmem name is {} for process number ".format(self.shmem_name))
        self.client = ShmemRGBClient(
            name=self.shmem_name,
            n_ringbuffer=self.n_buffer,  # size of ring buffer
            width=self.image_dimensions[0],
            height=self.image_dimensions[1],
            # client timeouts if nothing has been received in 1000 milliseconds
            mstimeout=1000,
            verbose=False
        )
        self.postCreateClient_()

    def test_(self, test_int=0, test_str="nada"):
        print(self.pre, "test_ signal received with", test_int, test_str)

    def ping_(self, message="nada"):
        print(
            self.pre,
            "At backend: ping_ received",
            message,
            "sending it back to front")
        self.sendSignal_(name="pong_o", message=message)

    # ** frontend methods launching incoming signals

    def stop(self):
        self.sendSignal(name="stop_")

    def createClient(self):
        self.sendSignal(name="create_client_")

    def test(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["test_"], kwargs)
        kwargs["name"] = "test_"
        self.sendSignal(**kwargs)

    def ping(self, **kwargs):
        dictionaryCheck(self.incoming_signal_defs["ping_"], kwargs)
        kwargs["name"] = "ping_"
        self.sendSignal(**kwargs)

    # ** frontend methods handling received outgoing signals ***
    def pong_o(self, message="nada"):
        print(self.pre, "At frontend: pong got message", message)
        ns = Namespace()
        ns.message = message
        self.signals.pong_o.emit(ns)


class Analyzer(object):
    """A generic analyzer class
    """

    parameter_defs = {
        "verbose": (bool, False),  # :param verbose: verbose output or not?  Default: False.
        "debug": (bool, False)
        # :param debug:   When this is True, will visualize on screen what the analyzer is doing (using OpenCV highgui)
    }

    def __init__(self, **kwargs):
        parameterInitCheck(Analyzer.parameter_defs, kwargs, self,
                           undefined_ok=True)  # checks that kwargs is consistent with parameter_defs.  Attaches parameters as attributes to self.  This is a mother class: there might be more parameters not defined here from child classes
        self.pre = self.__class__.__name__ + " : "
        # self.reset() # do this in child classes only ..

    def reset(self):
        """If the analyzer has an internal state, reset it
        """
        pass

    def __call__(self, img):
        """Do the magic for image img. Shape of the image array is (i,j,colors)
        """
        pass

    def report(self, *args):
        if (self.verbose):
            print(self.pre, *args)
            # pass


class MovementDetector(Analyzer):
    """A demo movement detector, written using OpenCV
    """

    # return values:
    state_same = 0  # no state change
    state_start = 1  # movement started
    state_stop = 2  # movement stopped

    parameter_defs = {
        "verbose": (bool, False),  # :param verbose:  Verbose output or not?  Default: False.
        "debug": (bool, False),
        # :param debug:    When this is True, will visualize on screen what the analyzer is doing.  Uses OpenCV highgui.  WARNING: this will not work with multithreading/processing.
        "deadtime": (int, 3),  # :param deadtime: Movement inside this time interval belong to the same event
        "treshold": (float, 0.001)  # :param treshold: How much movement is an event (area of the image place)
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        parameterInitCheck(MovementDetector.parameter_defs, kwargs,
                           self)  # checks that kwargs is consistent with parameter_defs.  Attaches parameters as attributes to self
        self.pre = self.__class__.__name__ + " : "
        self.reset()

    def reset(self):
        self.prevframe = None
        self.wasmoving = False
        self.t0 = 0

    def __call__(self, img):
        # self.report("got frame :",img)

        modframe = imutils.resize(img, width=500)

        if (self.debug): cv2.imshow("SimpleMovementDetector_channels-modframe", modframe)

        modframe = cv2.GaussianBlur(modframe, (21, 21), 0)

        if (self.prevframe.__class__ == None.__class__):  # first frame
            self.prevframe = modframe.copy()
            self.report("First image found!")
            result = self.state_same

        else:  # second or n:th frame
            delta = cv2.absdiff(self.prevframe.max(2), modframe.max(2))
            if (self.debug): cv2.imshow("SimpleMovementDetector_channels-delta0", delta)
            delta = cv2.threshold(delta, 100, 1, cv2.THRESH_BINARY)[1]  # TODO: how much treshold here..?
            val = delta.sum() / (delta.shape[0] * delta.shape[1])
            # print(self.pre,"MovementDetector: val=",val)
            self.prevframe = modframe.copy()

            if (val >= self.treshold):  # one promille ok .. there is movement
                self.t0 = time.time()
                self.report("==>MOVEMENT!")
                if (self.wasmoving):
                    result = self.state_same
                else:
                    self.t0_event = self.t0
                    self.wasmoving = True
                    self.report("==> NEW MOVEMENT EVENT!")
                    result = self.state_start

            else:  # no movement
                dt = time.time() - self.t0  # how much time since the last movement event
                if (dt >= self.deadtime and self.wasmoving):  # lets close this event ..
                    dt_event = time.time() - self.t0_event
                    self.wasmoving = False
                    result = self.state_stop
                    self.report("==> MOVEMENT STOPPED!")
                else:
                    result = self.state_same

            if (self.debug): cv2.imshow("SimpleMovementDetector_channels-delta", delta * 255)

        if (self.debug):
            # cv2.waitKey(40*25) # 25 fps
            # cv2.waitKey(self.frametime)
            cv2.waitKey(1)

        return result

