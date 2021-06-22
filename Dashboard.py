from PySide6 import QtWidgets

from valkka.api2 import OpenGLThread, LiveThread
from  valkka import core
from valkka.multiprocess import safe_select
from FilterChain.FilterChain import VisionAlarmFilterChain

from Multiprocess import RGB24Process, rgbClientSide, FragMP4Process
from Streaming.ForeignWidget import QtFrame
from valkka.api2.logging import setValkkaLogLevel, loglevel_silent
class Dashboard(QtWidgets.QMainWindow):
    """
    Starting multiprocesses (aka "forking") must be started
    before anything else.

    TODO : embed valkka x-window to QT dashboard
    """

    def setupUI(self):
        print("starting ui")
        self.setWindowTitle('Vision alarm system')
        self.resize(1200, 800)

        self.menuBar().addMenu('Add Camera')
        self.menuBar().addMenu('Remove camera')

        self.main = QtWidgets.QWidget(self)
        self.setCentralWidget(self.main)
        self.w = QtWidgets.QWidget(self)
        # self.setCentralWidget(self.w)

        self.mainlay = QtWidgets.QVBoxLayout(self.main)
        # self.mainlay.setSpacing(0)
        # self.mainlay.setContentsMargins(0, 0, 0, 0)

        self.wlay = QtWidgets.QGridLayout(self.w)
        self.alert = QtWidgets.QTextEdit()

        self.mainlay.addWidget(self.w, 75)
        self.mainlay.addWidget(self.alert, 25)

        # self.frames = []  # i currently don't know what it is used for
        # self.addresses = self.pardic["cams"]
        # print(self.addresses)

    def __init__(self, address, parent=None):
        super(Dashboard, self).__init__()
        self.address = address
        self.setupUI()
        self.alertFireDetected = True
        setValkkaLogLevel(loglevel_silent)
        filterchain = VisionAlarmFilterChain(
            self.w,
            self.wlay,
            address=self.address,
            slot=1
        )

        rgb_pars = filterchain.getRGBParameters()
        frag_mp4_pars = filterchain.getFragMP4Parameters()

        # process that recieves RGB24 frames
        rgb_process = RGB24Process()
        rgb_process.ignoreSIGINT()
        rgb_process.start()

        # process that receives frag mp4 fragments & prints out info
        if self.alertFireDetected:
            frag_mp4_process = FragMP4Process()
            frag_mp4_process.ignoreSIGINT()
            frag_mp4_process.start()


        # opengl is used to dump video to the screen
        # preserved frames in the memory and at the GPI
        gl_ctx = core.OpenGLFrameFifoContext()
        gl_ctx.n_720p = 100
        gl_ctx.n_1080p = 100
        gl_ctx.n_1440p = 0
        gl_ctx.n_4K = 0

        # max buffering time depends on the frames available
        buffering_time_ms = 100

        # Forking is done, Begin multithreading instantiation
        # Create opengl thread
        openglthread = core.OpenGLThread(
            "openglthread",
            gl_ctx,
            buffering_time_ms
        )
        openglthread.startCall()
        # openglthread = OpenGLThread(
        #     name="openglthread",
        #     n_720p=50,
        #     n_1080p=50,
        #     n_1440p=50,
        #     verbose=False,
        #     msbuftime=buffering_time_ms
        # )




        # Livethread using live555
        livethread = core.LiveThread("livethread")
        livethread.startCall()


        # start decoders, create shmem servers etc
        filterchain(
            livethread= livethread,
            openglthread= openglthread
        )

        # pass shmem arguments ( from the server side) to the client processes
        rgb_process.activateRGB24Client(**rgb_pars)
        rgb_pipe = rgb_process.getPipe()

        # if alert detected activate frag-MP4
        if self.alertFireDetected:
            frag_mp4_process.activateFMP4Client(**frag_mp4_pars)

            # multiprocesses derived from valkka.multiprocess.AsyncBackMessageProcess
            # have a slightly different API from multiprocessing.Pipe:
            mp4_pipe = frag_mp4_process.getPipe()
            mp4_pipe_fd = mp4_pipe.getReadFd()




            # could be called within the main loop
            # in a real-life application you could do it like this:
            # - your ws server receives a request for fmp4
            # - your ws server process sends a request to main process
            # -.. which then calls this:
            filterchain.activateFragMP4()


        print("video array ", frag_mp4_process.returnVideoArray())

        """
        C++ side threads are running
        Python multiprocesses are running
        Starting main program
        """



        while True:
            try:
                if self.alertFireDetected:
                    # multiplex intercom from two multiprocess
                    rlis = [rgb_pipe, mp4_pipe_fd]
                    r, w, e = safe_select(rlis, [], [], timeout=1)

                    if rgb_pipe in r:
                        # there is an incoming message object from the rgb process
                        msg = rgb_pipe.recv()
                        print("MainProcess Dashboard: message from rgb process", msg)
                    if mp4_pipe_fd in r:
                        # there is an incoming message object from the frag mp4 process
                        msg = mp4_pipe.recv()
                        print("MainProcess Dashboard: message from frag-MP4 process", msg)

                    if len(r) < 1:
                        # Dashboard process is alive
                        # print("Dashboard process is alive")
                        pass
                else:
                    # multiplex intercom from two multiprocess
                    rlis = [rgb_pipe]
                    r, w, e = safe_select(rlis, [], [], timeout=1)

                    if rgb_pipe in r:
                        # there is an incoming message object from the rgb process
                        msg = rgb_pipe.recv()
                        print("MainProcess Dashboard: message from rgb process", msg)

                    if len(r) < 1:
                        # Dashboard process is alive
                        # print("Dashboard process is alive")
                        pass

            except KeyboardInterrupt:
                print("Terminating the program !! You stupid shit head pressed ctrl + c ")
                break


        print("Bye ")
        print(" stopping process")

        frag_mp4_process.deactivateFMP4Client(
            ipc_index= frag_mp4_pars["ipc_index"]
        )
        frag_mp4_process.stop()

        rgb_process.deactivateRGB24Client(ipc_index = rgb_pars["ipc_index"])
        rgb_process.stop()

        print("stopping livethread")
        livethread.stopCall()
        filterchain.close()
        print("stopping openglthread")
        openglthread.stopCall()

    def closeValkka(self):
        pass
        """
        Closing valkka...

        TODO : Develop closevalkka method
        """



def main():
    add = "rtsp://iheb:iheb@192.168.1.12:8080/h264_ulaw.sdp"

    app = QtWidgets.QApplication(["Vision Alarm"])
    dashboard = Dashboard(add)
    dashboard.show()
    app.exec_()

if (__name__ == "__main__"):
    main()