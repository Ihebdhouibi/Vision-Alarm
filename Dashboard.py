from PySide6 import QtWidgets

from valkka import core
from valkka.multiprocess import safe_select
from FilterChain.FilterChain import VisionAlarmFilterChain

from Multiprocess import RGB24Process, rgbClientSide


class Dashboard:
    """
    Starting multiprocesses (aka "forking") must be started
    before anything else.

    """

    def __init__(self, address):
        self.address = address

        filterchain = VisionAlarmFilterChain(
            address=self.address,
            slot=1
        )

        rgb_pars = filterchain.getRGBParameters()

        # process that recieves RGB24 frames
        rgb_process = RGB24Process()
        rgb_process.ignoreSIGINT()
        rgb_process.start()

        # opengl is used to dump video to the screen
        # preserved frames in the memory and at the GPI
        gl_ctx = core.OpenGLFrameFifoContext()
        gl_ctx.n_720p = 20
        gl_ctx.n_1080p = 20
        gl_ctx.n_1440p = 0
        gl_ctx.n_4K = 0

        # max buffering time depends on the frames available
        buffering_time_ms = 200

        # Forking is done, Begin multithreading instantiation
        # Create opengl thread
        openglthread = core.OpenGLThread(
            "openglthread",
            gl_ctx,
            buffering_time_ms
        )
        openglthread.startCall()

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

        # multiprocesses derived from valkka.multiprocess.AsyncBackMessageProcess
        # have a slightly different API from multiprocessing.Pipe:
        # mp4_pipe = frag_mp4_process.getPipe()
        # mp4_pipe_fd = mp4_pipe.getReadFd()

        # could be called within the main loop
        # in a real-life application you could do it like this:
        # - your ws server receives a request for fmp4
        # - your ws server process sends a request to main process
        # -.. which then calls this:
        # filterchain.activateFragMP4()

        """
        C++ side threads are running 
        Python multiprocesses are running 
        Starting main program
        """


        while True:
            try:
                # multiplex intercom from two multiprocess
                rlis = [rgb_pipe]
                r, w, e = safe_select(rlis, [], [], timeout= 1)

                if rgb_pipe in r:
                    # there is an incoming message object from the rgb process
                    msg = rgb_pipe.recv()
                    print("MainProcess Dashboard: message from rgb process", msg)

                if len(r)  < 1 :
                    # Dashboard process is alive
                    print("Dashboard process is alive")

            except KeyboardInterrupt:
                print("Terminating the program !! You stupid shit head pressed ctrl + c ")
                break

        print("Bye ")
        print(" stopping process")

        rgb_process.deactivateRGB24Client(ipc_index = rgb_pars["ipc_index"])
        rgb_process.stop()

        print("stopping livethread")
        livethread.stopCall()
        filterchain.close()
        print("stopping openglthread")
        openglthread.stopCall()


def main():
    add = "rtsp://iheb:iheb@192.168.1.4:8080/h264_ulaw.sdp"

    dashboard = Dashboard(add)

if (__name__ == "__main__"):
    main()