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
