import time
import sys
from valkka import core

# Local imports
from Singleton import reserveEventFd, releaseEventFd, eventFdToIndex
from Streaming.ForeignWidget import QtFrame
class VisionAlarmFilterChain:
    """
    This is the filter graph of VisionAlarm system :

            * Stream live video from rtsp cameras using live555
            * Branch A 'Decoding' :
                    -  A.1 : RGB frames branch : Stores rgb frames to shared memory
                    -  A.2 : OpenGL branch     : Display stream on dashboard
            * Branch B 'Muxing'  :
                    - Stores frag-mp4 into shared memory


            Filterchain :

            (LiveThread:livethread) -->------------------------+ main_fork (Forks into A and B branches )
                                                               |
                                                               |
            ----------------------------------------------------
            |
            |--> Branch A : decoding : --> (AVThread:avthread) --------+ decoding fork ( forks into A.1 and A.2)
                                                                       |
                                                                       |
                                        +---------------------------<--+
                                        |
                                        |+--> Branch A.1 : RGB branch : --> {IntervalFrameFilter: interval_filter} --> {SwScaleFrameFilter: sws_filter} --> {RGBSharedMemFrameFilter: shmem_filter}
                                        |
                                        |+--> Branch A.2 : Displaying : --> (OpenGLThread:glthread)


            |--> Branch B : Muxing : +--> {FragMP4MuxFrameFilter:fmp4_muxer} --> {FragMP4ShmemFrameFilter:fmp4_shmem}

    """

    def __init__(self, address = None, slot = None):
        assert(isinstance(address, str))
        assert(isinstance(slot, int))

        self.rgb_sync_event = reserveEventFd()
        self.fmp4_sync_event = reserveEventFd()

        id_ = str(id(self))

        self.active = True
        self.rtsp_address = address
        self.slot = slot

        # RGB interpolation and shared memory definition
        # Defining YUV to RGB interpolation interval
        self.image_interval = 1000
        # Defining RGB image dimensions
        self.width = 1920
        self.height = 1080
        # Posix shared memory
        self.rgb_shmem_name = id_ + "_rgb"
        self.rgb_shmem_buffers = 10 # number of cells in ringbuffer

        # Shared memory defition for fragMP4
        self.fmp4_shmem_buffers = 10
        self.fmp4_shmem_name = id_ + "_fragmp4"
        self.fmp4_shmem_cellsize = 1024*1024*1


    def __del__(self):
        if self.active:
            self.close()

    def alert_cb(self, tup):
        print("alert cb got ",tup)

    def __call__(self, livethread = None, openglthread = None):
        """
        Register running live & openglthreads, construct filterchain, start threads

        """
        assert(livethread is not None)
        self.livethread = livethread
        self.openglthread = openglthread

        # Construct Filter graph from end to beginning
        # Main branch
        self.main_fork = core.ForkFrameFilterN("main_fork"+str(self.slot))

        # connect livethread to main branch
        self.live_ctx = core.LiveConnectionContext(core.LiveConnectionType_rtsp,
                                                   self.rtsp_address,
                                                   self.slot,
                                                   self.main_fork)  # stream rights to main_fork

        # Some aditional parameters you can give to livethread streaming context
        ## 1 : for NATs and Streaming over the internet, use tcp streaming
        self.live_ctx.request_tcp = True
        ## 2 : if you don't have enough buffering or timestamps are wrong, use this:
        #self.live_ctx.time_correction = core.TimeCorrectionType_smart
        ## 3 : enable automatic reconnection every 10 seconds if camera is offline
        self.live_ctx.mstimeout = 10000

        self.livethread.registerStreamCall(self.live_ctx)

        # Branch B : Mux Branch
        self.fmp4_shmem = core.FragMP4ShmemFrameFilter(
                    self.fmp4_shmem_name,
                    self.fmp4_shmem_buffers,
                    self.fmp4_shmem_cellsize
        )
        print(">", self.fmp4_sync_event)
        self.fmp4_shmem.useFd(self.fmp4_sync_event)
        self.fmp4_muxer = core.FragMP4MuxFrameFilter("mp4_muxer", self.fmp4_shmem)
        # self.fmp4_muxer.activate()
        # connect main branch to mux branch
        self.main_fork.connect("fragmp4_terminal" +str(self.slot), self.fmp4_muxer)
        # muxer must be connected from the very beginning so that it receives setupframes, sent only in the beginning of streaming process

        # Branch A : Decoding Branch
        self.decode_fork = core.ForkFrameFilterN("decode_fork_"+str(self.slot))
        self.avthread = core.AVThread("avthread_"+str(self.slot), self.decode_fork) # Here avthread feeds decode_fork
        # connect main branch to avthread to decode_fork
        self.avthread_in_filter = self.avthread.getFrameFilter()
        self.main_fork.connect("decoder_"+str(self.slot), self.avthread_in_filter)

        # Branch A : Sub_Branch_A.1 : RGB shared memory
        self.rgb_shmem_filter = core.RGBShmemFrameFilter(
                    self.rgb_shmem_name,
                    self.rgb_shmem_buffers,
                    self.width,
                    self.height
        )
        self.rgb_shmem_filter.useFd(self.rgb_sync_event)
        self.sws_filter = core.SwScaleFrameFilter("sws_filter", self.width, self.height, self.rgb_shmem_filter)
        self.interval_filter = core.TimeIntervalFrameFilter("interval_filter", self.image_interval, self.sws_filter)
        self.decode_fork.connect("rgb_shmem_terminal"+str(self.slot), self.interval_filter)

        # Branch A : Sub_Branch_A.2 : OpenGl branch Displaying
        if self.openglthread is not None:
            # connect decode frames in opengl
            self.opengl_input_filter = self.openglthread.getFrameFilter()
            self.decode_fork.connect("gl_terminal"+str(self.slot), self.opengl_input_filter)
            # Create X window
            self.window_id = self.openglthread.createWindow(show=False)
            self.openglthread.newRenderGroupCall(self.window_id)
            # frame = QtFrame()
            # maps stream with slot 1 to window "window_id"
            self.context_id = self.openglthread.newRenderContextCall(self.slot, self.window_id, 0)

        self.livethread.playStreamCall(self.live_ctx)
        self.avthread.startCall()
        self.avthread.decodingOnCall()




    def activateFragMP4(self):
        print("connecting fragmp4")
        self.fmp4_muxer.activate()

    def deactivateFragMP4(self):
        print("deconnecting fragmp4")
        self.fmp4_muxer.deActivate()

    def resendMP4Meta(self):
        self.fmp4_muxer.sendMeta()

    def getRGBParameters(self):
        """
        Returns shared memory parameters to be used in client side
        TODO: get eventfd & add it to the pars, same for fmp4
        """
        return {
            "name": self.rgb_shmem_name,
            "n_ringbuffer": self.rgb_shmem_buffers,
            "width": self.width,
            "height": self.height,
            "ipc_index": eventFdToIndex(self.rgb_sync_event)
        }

    def getRGBSyncEvent(self):
        """
        Eventfd for synchronization with the process that reads the RGB24 frames from shared memory
        """
        return self.rgb_sync_event

    def getFragMP4Parameters(self):
        """
        Returs shared memory parameters to be used in client side
        """
        return {
            "name": self.fmp4_shmem_name,
            "n_ringbuffer": self.fmp4_shmem_buffers,
            "n_size": self.fmp4_shmem_cellsize,
            "ipc_index": eventFdToIndex(self.fmp4_sync_event)
        }

    def getFMP4SyncEvent(self):
        return self.fmp4_sync_event

    def close(self):
        """
        Called on garbage-collection (see the __del__ method)
        """
        # stop muxing
        self.fmp4_muxer.deActivate()

        # stop streaming
        self.livethread.stopStreamCall(self.live_ctx)
        self.livethread.deregisterStreamCall(self.live_ctx)
        # WARNING
        """
        This VisionAlarmFilterChain object contains a series of framefilter that are written by self.livethread
        The effect of "self.livethread.deregisterStreamCall" may kick in _after_ the garbage collection of those framefilters 
        has been performed.
        In that case livethread will try to write into non-existing framefilters, So wait untill livethread has processed its pending operations:
        """
        self.livethread.waitReady()

        self.avthread.stopCall()
        if self.openglthread is not None:
            self.openglthread.delRenderContextCall(self.context_id)
            self.openglthread.delRenderGroupCall(self.window_id)

        releaseEventFd(self.rgb_sync_event)
        releaseEventFd(self.fmp4_sync_event)

        self.active = False


def main():
    """Simple filterchain creation test
    """
    openglthread = core.OpenGLThread("openglthread")
    openglthread.startCall()
    livethread = core.LiveThread("livethread")
    livethread.startCall()

    if len(sys.argv) < 2:
        print("please give rtsp camera address as the first argument")

    filterchain = VisionAlarmFilterChain(
        address = sys.argv[1],
        slot = 1,
        rgb_sync_event = reserveEventFd(),
        fmp4_sync_event = reserveEventFd()
    )

    ## runs the filterchain
    filterchain(livethread = livethread, openglthread = openglthread)
    print("server is running for some time")
    filterchain.activateFragMP4()
    time.sleep(12)
    print("livethread stop")
    # preferably shutdown the system from beginning-to-end
    livethread.stopCall()
    filterchain.close()
    print("openglthread stop")
    openglthread.stopCall()
    print("bye!")


if __name__ == "__main__":
    main()