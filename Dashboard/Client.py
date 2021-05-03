# # This is the client Dhasboard
#
# from PySide6 import QtWidgets, QtGui, QtCore
# import sys
# from valkka.core import *
#
# class Client(QtWidgets.QMainWindow):
#     """
#     This is our main Application window
#
#     This window will be devided into three area :
#
#     Left Panel for additional informations
#
#     Right Panel for camera feed, which will be devided into 4 areas to stream each a single camera
#
#     Bottom Panel for displaying alert history and interact with it
#
#     Developed by : Iheb dhouibi
#
#     """
#
#     def __init__(self, parent=None, stream_address=[]):
#         super(Client, self).__init__()
#
#         self.stream_address = stream_address
#         self.nstreams = len(self.stream_address)
#         self.initVars()
#         self.setGui()
#         self.openValkka()
#         self.makeFilterChains()
#         self.start_streams()
#
#     def initVars(self):
#         self.filterchains = []
#         self.videoframes = []
#
#     def setGui(self):
#         self.setWindowTitle('Vision Alarm')
#         self.resize(1200, 800)
#
#         # Status Bar showing how many camera streaming **** To be developed
#         self.statusBar().showMessage('Streaming on ')
#
#         self.menuBar().addMenu('Add camera')
#         self.menuBar().addMenu('Remove camera')
#         # self.camera1 = QtWidgets.QFrame(self)  # Creating Streaming frame
#         # self.camera1id = int(self.camera1.winId()) # storing id of the streaming frame
#         # self.camera2 = QtWidgets.QFrame(self) # Creating Streaming frame
#         # self.camera2id = int(self.camera2.winId()) # storing id of the streaming frame
#
#         self.w = QtWidgets.QWidget(self)
#         self.setCentralWidget(self.w)
#         self.lay = QtWidgets.QGridLayout(self.w)
#
#
#         for i, address in enumerate(self.stream_address):
#             fr = QtWidgets.QFrame(self.w)
#             self.lay.addWidget(fr, i//4, i%4)
#             self.videoframes.append((fr,address))
#         # camera3 = QtWidgets.QLabel('Camera 3 ')
#         # camera4 = QtWidgets.QLabel('Camera 4 ')
#         # alets = QtWidgets.QLabel('This is where alerts will be shown')
#         #
#         # layout1 = QtWidgets.QGridLayout()
#         # layout1.addWidget(self.camera1, 0, 0, 1, 1)
#         # layout1.addWidget(self.camera2, 0, 1, 1, 1)
#         # layout1.addWidget(camera3, 1, 0, 1, 1)
#         # layout1.addWidget(camera4, 1, 1, 1, 1)
#         #
#         # camerawidget = QtWidgets.QWidget()
#         # camerawidget.setLayout(layout1)
#         #
#         # layout = QtWidgets.QVBoxLayout()
#         # layout.addWidget(camerawidget)
#         # layout.addWidget(alets)
#         #
#         # widget = QtWidgets.QWidget()
#         # widget.setLayout(layout)
#         #
#         # self.setCentralWidget(widget)
#
#     def openValkka(self):
#         """
#         Filtergraph:
#         (LiveThread:livethread) --> FilterChain --> {FifoFrameFilter:gl_in_gilter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)
#
#         See "single_stream_rtsp.py" for more details !
#         """
#         self.gl_ctx = OpenGLFrameFifoContext();
#         self.gl_ctx.n_720p = 200;
#         self.gl_ctx.n_1080p = 200;
#         self.gl_ctx.n_1440p = 200;
#         self.gl_ctx.n_4K = 200;
#         self.gl_ctx.n_setup = 200;
#         self.gl_ctx.n_signal = 200;
#         self.gl_ctx.flush_when_full = False;
#
#         self.glthread = OpenGLThread("glthread", self.gl_ctx);
#         self.gl_in_filter = self.glthread.getFrameFilter();
#         self.livethread = LiveThread("livethread")
#
#         # Start threads
#         self.glthread.startCall()
#         self.livethread.startCall()
#
#     def closeValkka(self):
#         self.livethread.stopCall()
#         self.glthread.stopCall()
#
#     def makeFilterChains(self):
#         for i, videoframe in enumerate(self.videoframes):  # videoframe == (QFrame, address) pairs
#             window_id = int(videoframe[0].winId())  # QFrame.windId() returns x-window id
#             address = videoframe[1]
#             self.filterchains.append(Client(self.gl_in_filter, window_id, address, i + 1))
#
#     def start_streams(self):
#         print("starting streams")
#         for filterchain in self.filterchains:
#             ctx = filterchain.getConnectionCtx()
#             self.livethread.registerStreamCall(ctx)
#             self.livethread.playStreamCall(ctx)
#             filterchain.decodingOn()
#
#             window_id = filterchain.getWindowId()
#             self.glthread.newRenderGroupCall(window_id)
#             context_id = self.glthread.newRenderContextCall(filterchain.getSlot(), window_id, 0)
#             filterchain.setRenderCtx(context_id)  # save context id to filterchain
#
#     def stop_streams(self):
#         print("stopping streams")
#         for filterchain in self.filterchains:
#             filterchain.stop()
#             ctx = filterchain.getConnectionCtx()
#             self.livethread.stopStreamCall(ctx)
#             self.livethread.deregisterStreamCall(ctx)
#             self.glthread.delRenderContextCall(filterchain.getRenderCtx())
#             self.glthread.delRenderGroupCall(filterchain.getWindowId())
#
#     def closeEvent(self, e):
#         print("closeEvent!")
#         self.stop_streams()
#         self.closeValkka()
#         e.accept()
#
# # Launching the client
#
# app = QtWidgets.QApplication(sys.argv)
#
# window = Client(stream_address=
#                 "rtsp://iheb:iheb@192.168.1.13:8080/h264_ulaw.sdp")
# window.show()
#
# sys.exit(app.exec_())

# from PyQt5 import QtWidgets, QtCore, QtGui # If you use PyQt5, be aware of the licensing consequences
from PySide2 import QtWidgets, QtCore, QtGui
import sys
from valkka.core import *


class FilterChain:

    def __init__(self, gl_in_filter, window_id, address, slot):
        self.gl_in_filter = gl_in_filter
        self.window_id = window_id
        self.address = address
        self.slot = slot
        self.render_ctx = None

        self.avthread = AVThread("avthread", self.gl_in_filter)
        self.av_in_filter = self.avthread.getFrameFilter()

        self.ctx = LiveConnectionContext()
        self.ctx.slot = slot
        if (self.address.find("rtsp://") > -1):
            self.ctx.connection_type = LiveConnectionType_rtsp
        else:
            self.ctx.connection_type = LiveConnectionType_sdp
        self.ctx.address = self.address
        self.ctx.framefilter = self.av_in_filter
        self.ctx.msreconnect = 1  # do reconnection if the stream dies out

        self.avthread.startCall()
        self.avthread.decodingOnCall()

    def getSlot(self):
        return self.slot

    def getConnectionCtx(self):
        return self.ctx

    def getWindowId(self):
        return self.window_id

    def decodingOn(self):
        self.avthread.decodingOnCall()

    def decodingOff(self):
        self.avthread.decodingOffCall()

    # These two setters and getters are used simply to save the render context id
    def setRenderCtx(self, n):
        self.render_ctx = n

    def getRenderCtx(self):
        return self.render_ctx

    def stop(self):
        self.avthread.stopCall()

    def __del__(self):  # call at garbage collection
        self.stop()


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

        for i, address in enumerate(self.addresses):
            fr = QtWidgets.QFrame(self.w)
            print("setupUi: layout index, address : ", i // 4, i % 4, address)
            self.lay.addWidget(fr, i // 4, i % 4)
            self.videoframes.append((fr, address))  # list of (QFrame, address) pairs
        alertwidget = QtWidgets.QLabel('Alerts to be shown here')
        self.lay.addWidget(alertwidget)

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
    mg = MyGui(addresses=["rtsp://Sami:sami@192.168.1.23:8080/h264_ulaw.sdp",
                          "rtsp://iheb:iheb@192.168.1.13:8080/h264_ulaw.sdp"])
    mg.show()
    app.exec_()


if (__name__ == "__main__"):
    main()

