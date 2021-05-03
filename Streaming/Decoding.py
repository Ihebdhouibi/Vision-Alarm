from valkka.core import *


class Decoding:

    def __init__(self, gl_in_filter, address, slot):
        self.gl_in_filter = gl_in_filter
        self.address = address
        self.slot = slot

        # Decoding part
        self.avthread = AVThread('AVthread', self.gl_in_filter)
        self.av_in_filter = self.avthread.getFrameFilter()

        # Define connection to the camera
        self.ctx = LiveConnectionContext(LiveConnectionType_rtsp, self.address, self.slot, self.av_in_filter)

        self.avthread.startCall()
        self.avthread.decodingOnCall()

    def close(self):
        self.avthread.decodingOffCall()
        self.avthread.stopCall()

