from valkka.core import *
from PySide6 import QtWidgets, QtGui

# class FilterChain:
#
#     def __init__(self, gl_in_filter, window_id, address, slot):
#         self.gl_in_filter = gl_in_filter
#         self.window_id = window_id
#         self.address = address
#         self.slot = slot
#         self.render_ctx = None
#
#         self.avthread = AVThread("avthread", self.gl_in_filter)
#         self.av_in_filter = self.avthread.getFrameFilter()
#
#         self.ctx = LiveConnectionContext()
#         self.ctx.slot = slot
#         if (self.address.find("rtsp://") > -1):
#             self.ctx.connection_type = LiveConnectionType_rtsp
#         else:
#             self.ctx.connection_type = LiveConnectionType_sdp
#         self.ctx.address = self.address
#         self.ctx.framefilter = self.av_in_filter
#         self.ctx.msreconnect = 1  # do reconnection if the stream dies out
#
#         self.avthread.startCall()
#         self.avthread.decodingOnCall()
#
#     def getSlot(self):
#         return self.slot
#
#     def getConnectionCtx(self):
#         return self.ctx
#
#     def getWindowId(self):
#         return self.window_id
#
#     def decodingOn(self):
#         self.avthread.decodingOnCall()
#
#     def decodingOff(self):
#         self.avthread.decodingOffCall()
#
#     # These two setters and getters are used simply to save the render context id
#     def setRenderCtx(self, n):
#         self.render_ctx = n
#
#     def getRenderCtx(self):
#         return self.render_ctx
#
#     def stop(self):
#         self.avthread.stopCall()
#
#     def __del__(self):  # call at garbage collection
#         self.stop()


class TestWidget0(QtWidgets.QWidget):

    def mouseDoubleClickEvent(self, e):
        print("double click!")


def getForeignWidget(parent, win_id):
    """Valkka creates a window.  The window is used to generate the widget.. however.. here we loose the interaction with the window .. clicks on it, etc. (were detached from the qt system)
    """
    # some interesting flags for the createWindowContainer method: QtCore.Qt.ForeignWindow QtCore.Qt.X11BypassWindowManagerHint
    # other things: QtGui.QSurface(QtGui.QSurface.OpenGLSurface), q_widget.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
    q_window = QtGui.QWindow.fromWinId(win_id)

    q_widget = QtWidgets.QWidget.createWindowContainer(q_window, parent=parent)
    # q_widget.activateWindow()

    return q_widget


class WidgetPair:
    """Creates a "foreign" QWidget by using the X window id win_id.  Another "top" widget is placed on top of the foreign widget that catches the mouse gestures.

    :param parent:       Parent (a QWidget) of the widget pair
    :param win_id:       An X-window id
    :param widget_class: Class for the top widget
    """

    def __init__(self, parent, win_id, widget_class):
        self.foreign_window = QtGui.QWindow.fromWinId(win_id)
        self.foreign_widget = QtWidgets.QWidget.createWindowContainer(self.foreign_window, parent=parent)

        self.widget = widget_class(self.foreign_widget)
        self.lay = QtWidgets.QHBoxLayout(self.foreign_widget)
        self.lay.addWidget(self.widget)

    def getWidget(self):
        return self.foreign_widget

