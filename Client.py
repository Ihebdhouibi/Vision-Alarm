from PySide6 import QtWidgets

from valkka.api2 import LiveThread, OpenGLThread
from valkka.api2 import ShmemFilterchain
from valkka.api2.logging import setValkkaLogLevel, loglevel_silent
from valkka.api2 import FragMP4ShmemClient
# Local imports
from MachineVision.FireDetection import QValkkaFireDetectorProcess
from Streaming.FilterChain import VisionAlarmFilterChain
from multiprocess import QValkkaThread
from Streaming.ForeignWidget import WidgetPair, TestWidget0
from MachineVision.FallDetection import QValkkaFallDetection
setValkkaLogLevel(loglevel_silent)


class MyGui(QtWidgets.QMainWindow):
    class QtFrame:

        def __init__(self, parent, win_id):
            self.widget = QtWidgets.QWidget(parent)
            self.lay = QtWidgets.QVBoxLayout(self.widget)

            self.widget_pair = WidgetPair(self.widget, win_id, TestWidget0)
            self.video = self.widget_pair.getWidget()
            self.lay.addWidget(self.video)


        def getWindowId(self):
            return int(self.widget.winId())

    debug = False

    def __init__(self, pardic, parent=None):
        super(MyGui, self).__init__()
        self.pardic = pardic
        self.initVars()
        self.setupUI()

        if self.debug: return
        self.openValkka()

    def initVars(self):
        pass

    def setupUI(self):
        self.setWindowTitle('Vision alarm system')
        self.resize(1200, 800)

        self.menuBar().addMenu('Add Camera')
        self.menuBar().addMenu('Remove camera')

        self.main = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main)
        self.w = QtWidgets.QWidget(self)
        # self.setCentralWidget(self.w)

        self.mainlay = QtWidgets.QVBoxLayout(self.main)
        self.mainlay.setSpacing(0)
        self.mainlay.setContentsMargins(0, 0, 0, 0)

        self.wlay = QtWidgets.QGridLayout(self.w)
        self.alert = QtWidgets.QTextEdit()

        self.mainlay.addWidget(self.w, 75)
        self.mainlay.addWidget(self.alert, 25)

        self.frames = []  # i currently don't know what it is used for
        self.addresses = self.pardic["cams"]
        print(self.addresses)

    def openValkka(self):

        # RGB Shared memory
        shmem_image_dimensions = (1920 // 4, 1080 // 4)
        shmem_image_interval = 1000
        shmem_rignbuffer_size = 10

        # Frag MP4 Shared memory
        shmem_buffers = 10
        shmem_name = "FragMP4Shmem"
        cellsize = 1024*1024*3
        timeout = 1000

        cs = 1
        cc = 1
        self.processes = []
        for address in self.addresses:
            shmem_name = "camera" + str(cs)
            print("shmem name is {} for process number {} ".format(shmem_name, cc))
            process = QValkkaFireDetectorProcess(
                "process" + str(cs),
                shmem_name=shmem_name,
                n_buffer=shmem_rignbuffer_size,
                image_dimensions=shmem_image_dimensions
            )

            self.processes.append(process)
            process = QValkkaFallDetection(
                "process" + str(cs),
                shmem_name=shmem_name,
                n_buffer=shmem_rignbuffer_size,
                image_dimensions=shmem_image_dimensions
            )
            self.processes.append(process)
            cs += 1
        print(self.processes)

        # Give the multiprocesses to a gthread that's reading their message / thread will be listening to the processes !?

        self.thread = QValkkaThread(processes=self.processes)

        # start the multiprocesses
        self.startProcesses()

        # Now that we successfully forked our multiprocesses lets spawn threads

        self.livethread = LiveThread(
            name="live",
            verbose=False,
            affinity=self.pardic["live_affinity"]
        )
        self.openglthread = OpenGLThread(
            name="mythread",
            # reserve stacks of YUV video frames for various resolutions
            n_720p=50,
            n_1080p=50,
            n_1440p=50,
            n_4K=50,
            verbose=False,
            msbuftime=100,
            affinity=-1
        )
        # if (self.openglthread.hadVsync()):
        #     q = QtWidgets.QMessageBox.warning(self,
        #                                       "VBLANK WARNING",
        #                                       "Syncing to vertical refresh enabled \n THIS WILL DESTROY YOUR FRAMERATE\n disable it using 'export vblank_mode=0'")

        tokens = []
        self.chains = []
        self.frames = []

        cs = 1
        cc = 0

        x = 0
        y = 0
        cam_count = 0
        a = self.pardic["dec affinity start"]
        for address in self.addresses:

            # Livethread/openglthread are running
            print('address :', address)
            if (a > self.pardic["dec affinity stop"]):
                a = self.pardic["dec affinity start"]

            # chain = VisionAlarmFilterChain(
            #     # decoding and branching happens here
            #     livethread=self.livethread,
            #     openglthread=self.openglthread,
            #     address=address,
            #     slot=cs,
            #     affinity=a,
            #     shmem_name="camera" + str(cs),
            #     shmem_image_dimensions=shmem_image_dimensions,
            #     shmem_image_interval=shmem_image_interval,
            #     shmem_ringbuffer_size=shmem_rignbuffer_size,
            #     msreconnect=1000,
            #     frag_shmem_buffers=shmem_buffers,
            #     frag_shmem_name=shmem_name,
            #     frag_shmem_cellsize=cellsize,
            #     frag_shmem_timeout=timeout,
            #
            #
            # )
            chain = ShmemFilterchain(
                livethread=self.livethread,
                openglthread=self.openglthread,
                address=address,
                slot=cs,
                shmem_name="camera" + str(cs),
                shmem_image_dimensions= shmem_image_dimensions,
                shmem_image_interval=shmem_image_interval,
                shmem_ringbuffer_size= shmem_rignbuffer_size,
                msreconnect = 10000
            )
            self.chains.append(chain)

            win_id = self.openglthread.createWindow(show=False)
            frame = self.QtFrame(self.w, win_id)


            # print('setting up layout')
            if y > 1:
                x = 1
                y = 0
            self.wlay.addWidget(frame.widget, x, y)
            y += 1
            token = self.openglthread.connect(slot=cs, window_id=win_id)
            tokens.append(token)

            # take corresponding multiprocess
            process = self.processes[cc]
            process.createClient()  # creates the shared memory client at the multiprocess
            # connect signals to the nested widget

            # process.signals.Fire_detected.connect(self.addAlert)

            chain.decodingOn()  # start the decoding thread
            cs += 1
            a += 1
            cc += 1
            # FragMP4 shmem client



    def startProcesses(self):
        self.thread.start()
        for p in self.processes:
            p.start()

    def stopProcesses(self):
        for p in self.processes:
            p.stop()
        print("stopping QThread")
        self.thread.stop()
        print("QThread stopped")

    def closeValkka(self):
        self.livethread.close()
        for chain in self.chains:
            chain.close()

        self.chains = []
        self.widget_pairs = []
        self.videoframes = []
        self.openglthread.close()

    def closeEvent(self, e):
        print("closeEvent!")
        self.stopProcesses()
        self.closeValkka()
        super().closeEvent()


    # Slot
    def addAlert(self):
        print('inside addAlert ')
        self.alert.append('Fire Detected on camera number 1')
        pass


def main():
    app = QtWidgets.QApplication(["Vision-Alarm-System"])
    pardic = {"cams": ["rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp"],
              "live_affinity": -1,
              "dec affinity start": -1,
              "dec affinity stop": -1}
    mg = MyGui(pardic)
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()
