
from valkka import core
from valkka.api2.threads import LiveThread, OpenGLThread
from valkka.api2.tools import parameterInitCheck, typeCheck
from valkka.api2 import FragMP4ShmemClient
from valkka.api2.logging import setValkkaLogLevel, loglevel_silent

class VisionAlarmFilterChain:
    """A filter chain with a shared mem hook and FragMP4ShmemFrameFilter

        ::

          (LiveThread:livethread) -->>  --------------------- +
                                                             |   main branch
          (AVThread:avthread1)  <----------------------------+
                      |
          {ForkFrameFilter2: fork_filter}
                     |
            branch 1 +-->>(OpenGLThread:glthread)
                     |
            branch 2 +--> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {RGBShmemFrameFilter: shmem_filter}



        * Frames are decoded in the main branch from H264 => YUV
        * The stream of YUV frames is forked into two branches
        * branch 1 goes to OpenGLThread that interpolates YUV to RGB on the GPU
(        * branch 2 goes to interval_filter that passes a YUV frame only once every second.  From there, frames are interpolated on the CPU from YUV to RGB and finally passed through shared memory to another process.
        * branch 3 goes to fragmp4muxer
        """

    parameter_defs = {
        "livethread": LiveThread,
        "openglthread": OpenGLThread,
        "address": str,
        "slot": int,

        # Parameters of the AVThread instance
        "n_basic": (int, 20),  # Number of payload frames in the stack
        "n_setup": (int, 20),  # Number of setup frames in the stack
        "n_signal": (int, 20),  # Number of signal frames in the stack
        "flush_when_full": (bool, False),  # Clear fifo at overflow

        "affinity": (int, -1),
        "verbose": (bool, False),
        "msreconnect": (int, 0),

        # Timestamp correction type : TimeCorrectionType_none,
        # TimeCorrectionType_dummy, or TimeCorrectionType_smart ( default)
        "time_correction": None,

        # operating system socket ringbuffer size in bytes # 0 means default
        "recv_buffer_size": (int, 0),

        # Reordering buffer time for live555 packets in milliseconds # 0 means default
        "reordering_mstime": (int, 0),
        "n_threads": (int, 1),

        # Shared memory of each stream
        # Images passed over shmem are full-hd/4 reso
        "shmem_image_dimensions": (tuple, (1920 // 4, 1080 // 4)),
        # Intervall in which a frame is passed to the shared memory
        "shmem_image_interval": (int, 1000),
        # size of the ringbuffer
        "shmem_ringbuffer_size": (int, 10),
        "shmem_name": str,

        # Shared memory for FragMP4 chunks
        # FragMP4Shmem buffers size
        "frag_shmem_buffers": (int, 10),
        # FragMP4Shmem name
        "frag_shmem_name": str,
        # FragMP4Shmem cellsize
        "frag_shmem_cellsize": (int, 1024 * 1024 * 3),
        # FragMP4Shmem timeout
        "frag_shmem_timeout": (int, 1000)
    }

    def __init__(self, **kwargs):
        # auxiliary string for debugging output
        self.pre = self.__class__.__name__ + " : "

        # check for input parameters, attach them to this instance as attributes
        parameterInitCheck(self.parameter_defs, kwargs, self)
        typeCheck(self.shmem_image_dimensions[0], int)
        typeCheck(self.shmem_image_dimensions[1], int)

        # check type of frag_shmem_cellsize  to review !!!
        # typeCheck(self.frag_shmem_cellsize[0], int)
        # typeCheck(self.frag_shmem_cellsize[1], int)
        # typeCheck(self.frag_shmem_cellsize[2], int)

        self.init()
        setValkkaLogLevel(loglevel_silent)

    def init(self):
        self.idst = str(id(self))
        self.makeChain()
        self.createContext()
        self.startThreads()
        self.active = True

    def __del__(self):
        self.close()

    def close(self):
        if self.active:
            if self.verbose:
                print(self.pre, "closing threads and contexes")
            self.decodingOff()
            self.closeContext()
            self.stopThreads()
            self.active = False

    def makeChain(self):
        """
        Create the filter chain
        """
        setValkkaLogLevel(loglevel_silent)
        # if (self.shmem_name is None):
        #     self.shmem_name = "shmemff" + self.idst

        print(self.pre, self.shmem_name)

        # self.n_bytes = self.shmem_image_dimensions[0] * self.shmem_image_dimensions[1]*3
        n_buf = self.shmem_ringbuffer_size

        # Branch 1 : Displaying Stream to the dashboard
        # get input FrameFilter from OpenGLThread

        self.gl_in_filter = self.openglthread.getFrameFilter()

        # Decoding for displaying
        # self.avthread1_1 = core.AVThread(
        #     "avthread_" + self.idst,
        #     # self.fork_filter,  # AVthread writes to self.fork_filter
        #     self.gl_in_filter,
        #     # self.framefifo_ctx
        # )
        # self.avthread1_1.setAffinity(self.affinity)

        # # get input framefilter from avthread
        # self.av_in_filter1_1 = self.avthread1_1.getFrameFilter()

        # Branch 2 : Saving frames to shared memory for openCV/Tensorflow process
        
        try:
            self.shmem_filter = core.RGBShmemFrameFilter(
                self.shmem_name,
                n_buf,
                self.shmem_image_dimensions[0],
                self.shmem_image_dimensions[1]
            )
            if self.shmem_filter:
                print("Shared mem created ")
        except Exception as e:
            print(" There is a problem in allocating memory to RGBShmemFrameFilter : \n" + e)

        # self.shmem_filter = core.InfoFrameFilter("info"+ selft.idst) ## debugging
        self.sws_filter = core.SwScaleFrameFilter(
            "sws_filter" + self.idst,
            self.shmem_image_dimensions[0],
            self.shmem_image_dimensions[1],
            self.shmem_filter
        )
        if self.sws_filter:
            print("Sws_filter created !")
        self.interval_filter = core.TimeIntervalFrameFilter(
            "interval_filter" + self.idst, self.shmem_image_interval, self.sws_filter
        )
        if self.interval_filter:
            print("interval_filter created ")
        # self.avthread2_1 = core.AVThread(
        #     "avthread_" + self.idst,
        #     # self.fork_filter,  # AVthread writes to self.fork_filter
        #     self.interval_filter,
        #     # self.framefifo_ctx
        # )
        # self.avthread2_1.setAffinity(self.affinity)

        # get input framefilter from avthread
        # self.av_in_filter2_1 = self.avthread2_1.getFrameFilter()

        # Fork : Writes to branches 1, 2 and 3
        self.fork_filter = core.ForkFrameFilter(
            "fork_filter" + self.idst,
            self.gl_in_filter,
            self.interval_filter

        )
 
        # Main branch
        self.framefifo_ctx = core.FrameFifoContext()
        self.framefifo_ctx.n_basic = self.n_basic
        self.framefifo_ctx.n_setup = self.n_setup
        self.framefifo_ctx.n_signal = self.n_signal
        self.framefifo_ctx.flush_when_full = self.flush_when_full

    # A functions that returns Shared memory parameters
    def getShmemPars(self):
        """
        Returns shared mem name that should be used in the client process and the ring buffer size
        """
        return self.shmem_name, self.shmem_ringbuffer_size, self.shmem_image_dimensions

    # A function that returns FragMP4 shared memory parameters
    def getFragShmemPars(self):
        """
        Returns fragmp4 shared mem name that should be used in the client process
        """
        return self.frag_shmem_name, self.frag_shmem_buffers, self.frag_shmem_cellsize, self.frag_shmem_timeout

    def createContext(self):
        """
        Creates a LiveConnectionContext and registers it to LiveThread
        """

        # Define the stream source, how the stream is passed on, etc
        self.ctx = core.LiveConnectionContext()
        # slot number identifies the stream source
        self.ctx.slot = self.slot

        if (self.address.find("rtsp://")) == 0:
            self.ctx.connection_type = core.LiveConnectionType_rtsp
        else:
            self.ctx.connection_type = core.LiveConnectionType_sdp

        self.ctx.address = self.address

        self.ctx.framefilter = self.fork_filter
        self.ctx.msreconnect = self.msreconnect

        # some extra parameters
        """
        // ctx.time_correction =TimeCorrectionType::none;
        // ctx.time_correction =TimeCorrectionType::dummy;
        // default time correction is smart
        // ctx.recv_buffer_size=1024*1024*2;  // Operating system ringbuffer size for incoming socket
        // ctx.reordering_time =100000;       // Live555 packet reordering treshold time (microsecs)
        """

        if (self.time_correction is not None):
            self.ctx.time_correction = self.time_correction
        # self.time_correction = core.TimeCorrectionType_smart # default
        self.ctx.recv_buffer_size = self.recv_buffer_size
        self.ctx.reordering_time = self.reordering_mstime * 1000

        # send information about the stream to livethread
        self.livethread.registerStream(self.ctx)
        self.livethread.playStream(self.ctx)
        # self.mux_filter.activate()

    def closeContext(self):
        self.livethread.stopStream(self.ctx)
        self.livethread.deregisterStream(self.ctx)
        # self.mux_filter.deActivate()

    def startThreads(self):
        """
        Starts thread required by the filterchain
        """
        self.avthread1_1.startCall()
        self.avthread2_1.startCall()

    def stopThreads(self):
        """
        Stops threads in the filter chain
        """
        self.avthread1_1.stopCall()
        self.avthread2_1.stopCall()

    def decodingOff(self):

        self.avthread1_1.decodingOffCall()
        self.avthread2_1.decodingOffCall()

    def decodingOn(self):
        self.avthread1_1.decodingOnCall()
        self.avthread2_1.decodingOnCall()
