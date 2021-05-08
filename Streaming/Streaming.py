from valkka.core import *
# from Filterchain import FilterChain
from Dashboard.Client import MyGui


class Streaming:
    def openValkka():
        """
        Filtergraph:
        (LiveThread:livethread) --> FilterChain --> {FifoFrameFilter:gl_in_gilter} --> [OpenGLFrameFifo:gl_fifo] -->> (OpenGLThread:glthread)

        See "single_stream_rtsp.py" for more details !
        """
        MyGui.gl_ctx = OpenGLFrameFifoContext();
        MyGui.gl_ctx.n_720p = 200;
        MyGui.gl_ctx.n_1080p = 200;
        MyGui.gl_ctx.n_1440p = 200;
        MyGui.gl_ctx.n_4K = 200;
        MyGui.gl_ctx.n_setup = 200;
        MyGui.gl_ctx.n_signal = 200;
        MyGui.gl_ctx.flush_when_full = False;

        MyGui.glthread = OpenGLThread("glthread", MyGui.gl_ctx);
        MyGui.gl_in_filter = MyGui.glthread.getFrameFilter();
        MyGui.livethread = LiveThread("livethread")

        # Start threads
        MyGui.glthread.startCall()
        MyGui.livethread.startCall()

    def closeValkka(self):
        MyGui.livethread.stopCall()
        MyGui.glthread.stopCall()

