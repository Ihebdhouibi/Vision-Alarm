from PySide6 import QtWidgets, QtCore, QtGui
import sys
from valkka.core import *
from Streaming.Filterchain import FilterChain


class MyGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None, addresses=[]):
        super(MyGui, self).__init__()
        self.debug = False
        # self.debug=True
        if (len(addresses) < 1):
            print("No streams!")
            return
        self.addresses = addresses
        self.n_streams = len(self.addresses)
        self.initVars()
        self.setupUi()
        if (self.debug): return
        self.openValkka()
        self.makeFilterChains()
        self.start_streams()

    def initVars(self):
        self.filterchains = []
        self.videoframes = []

    def setupUi(self):
        self.setWindowTitle('Vision Alarm')
        self.resize(1200, 800)

        # Status Bar showing how many camera streaming **** To be developed
        self.statusBar().showMessage('Streaming on ')

        self.menuBar().addMenu('Add camera')
        self.menuBar().addMenu('Remove camera')

        self.w = QtWidgets.QWidget(self)
        self.setCentralWidget(self.w)

        self.lay = QtWidgets.QGridLayout(self.w)

        # for i, address in enumerate(self.addresses):
        #     fr = QtWidgets.QFrame(self.w)
        #     print("setupUi: layout index, address : ", i // 4, i % 4, address)
        #     self.lay.addWidget(fr, i // 4, i % 4)
        #     self.videoframes.append((fr, address))  # list of (QFrame, address) pairs
        fr = QtWidgets.QFrame(self.w)
        self.lay.addWidget(fr, 0, 0)
        self.videoframes.append((fr, "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp"))
        fr2 = QtWidgets.QFrame(self.w)
        self.lay.addWidget(fr2, 0, 1)
        self.videoframes.append((fr2, "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp"))
        fr3 = QtWidgets.QFrame(self.w)
        self.lay.addWidget(fr3, 1, 0)
        self.videoframes.append((fr3, "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp"))
        fr4 = QtWidgets.QFrame(self.w)
        self.lay.addWidget(fr4, 1, 1)
        self.videoframes.append((fr4, "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp"))

        # Alerts
        # alertwidget = QtWidgets.QPlainTextEdit(self.w)
        #
        # self.lay.addWidget(alertwidget, 2, 0)

    def openValkka(self):
        """
        Filtergraph:
        (LiveThread:livethread) --> FilterChain --> {FifoFrameFilter:gl_in_gilter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)

        See "single_stream_rtsp.py" for more details !
        """
        self.gl_ctx = OpenGLFrameFifoContext();
        self.gl_ctx.n_720p = 200;
        self.gl_ctx.n_1080p = 200;
        self.gl_ctx.n_1440p = 200;
        self.gl_ctx.n_4K = 200;
        self.gl_ctx.n_setup = 200;
        self.gl_ctx.n_signal = 200;
        self.gl_ctx.flush_when_full = False;

        self.glthread = OpenGLThread("glthread", self.gl_ctx);
        self.gl_in_filter = self.glthread.getFrameFilter();
        self.livethread = LiveThread("livethread")

        # Start threads
        self.glthread.startCall()
        self.livethread.startCall()

    def closeValkka(self):
        self.livethread.stopCall()
        self.glthread.stopCall()

    def makeFilterChains(self):
        for i, videoframe in enumerate(self.videoframes):  # videoframe == (QFrame, address) pairs
            window_id = int(videoframe[0].winId())  # QFrame.windId() returns x-window id
            address = videoframe[1]
            self.filterchains.append(FilterChain(self.gl_in_filter, window_id, address, i + 1))

    def start_streams(self):
        print("starting streams")
        for filterchain in self.filterchains:
            ctx = filterchain.getConnectionCtx()
            self.livethread.registerStreamCall(ctx)
            self.livethread.playStreamCall(ctx)
            filterchain.decodingOn()

            window_id = filterchain.getWindowId()
            self.glthread.newRenderGroupCall(window_id)
            context_id = self.glthread.newRenderContextCall(filterchain.getSlot(), window_id, 0)
            filterchain.setRenderCtx(context_id)  # save context id to filterchain

    def stop_streams(self):
        print("stopping streams")
        for filterchain in self.filterchains:
            filterchain.stop()
            ctx = filterchain.getConnectionCtx()
            self.livethread.stopStreamCall(ctx)
            self.livethread.deregisterStreamCall(ctx)
            self.glthread.delRenderContextCall(filterchain.getRenderCtx())
            self.glthread.delRenderGroupCall(filterchain.getWindowId())

    def closeEvent(self, e):
        print("closeEvent!")
        self.stop_streams()
        self.closeValkka()
        e.accept()


def main():
    app = QtWidgets.QApplication(["multiple_stream_test"])
    mg = MyGui(addresses=["rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp",
                          "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp",
                          "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp",
                          "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp"])
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()
