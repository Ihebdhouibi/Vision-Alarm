from multiprocess import QValkkaOpenCVProcess
from PySide6 import QtCore
import time
import cv2
import numpy as np

# class Testing:
#     pass
    # setValkkaLogLevel(loglevel_silent)
    #
    # image_interval = 1000
    #
    # width = 1920 // 4
    # height = 1080 // 4
    #
    # # posix shared memory
    # shmem_name = "lesson_4"
    # shmem_buffers = 10
    #
    # # branch 1
    # glthread = OpenGLThread("glthread")
    # gl_in_filter = glthread.getFrameFilter()
    #
    # # branch 2
    # shmem_filter = RGBShmemFrameFilter(shmem_name, shmem_buffers, width, height)
    # # shmem_filter = BriefInfoFrameFilter("shmem")
    # sws_filter = SwScaleFrameFilter("sws_filter", width, height, shmem_filter)
    #
    # interval_filter = TimeIntervalFrameFilter("interval_filter", image_interval, sws_filter)
    #
    # fork_filter = ForkFrameFilter("fork_filter", gl_in_filter, interval_filter)
    #
    # av_thread = AVThread("av_thread", fork_filter)
    # av_in_filter = av_thread.getFrameFilter()
    # live_thread = LiveThread("live_thread")
    #
    # ctx = LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://iheb:iheb@192.168.43.1:8080/h264_ulaw.sdp", 1,
    #                             av_in_filter)
    #
    # glthread.startCall()
    # av_thread.startCall()
    # live_thread.startCall()
    # # start decoding
    # av_thread.decodingOnCall()
    # live_thread.registerStreamCall(ctx)
    # live_thread.playStreamCall(ctx)
    # # create an X-window
    # window_id = glthread.createWindow()
    # glthread.newRenderGroupCall(window_id)
    # # maps stream with slot 1 to window "window_id"
    # context_id = glthread.newRenderContextCall(1, window_id, 0)
    # # time.sleep(15)
    # # glthread.delRenderContextCall(context_id)
    # # glthread.delRenderGroupCall(window_id)
    # # stop decoding
    # # av_thread.decodingOffCall()
    # # # stop threads
    # # live_thread.stopCall()
    # # av_thread.stopCall()
    # # glthread.stopCall()
    # bbox = (0.1, 0.75, 0.75, 0.25)
    # glthread.addRectangleCall(context_id, bbox[0], bbox[1], bbox[2], bbox[3])
    #
    # width2 = 1920
    # height2 = 1080
    #
    # shmem_name2 = "lesson_4"
    # shmem_buffers2 = 10
    #
    # client = ShmemRGBClient(
    #     name=shmem_name2,
    #     n_ringbuffer=shmem_buffers2,
    #     width=width2,
    #     height=height2,
    #     mstimeout=1000,
    #     verbose=False
    # )
    #
    # while True:
    #     index, meta = client.pullFrame()
    #     if index is None:
    #         # print('timeout')
    #         continue
    #     data = client.shmem_list[index][0:meta.size]
    #     # print('data : ', data[0:min(10, meta.size)])
    #     # print('width ', meta.width)
    #     # print('height ', meta.height)
    #     # print('slot ', meta.slot)
    #     # print('time ', meta.mstimestamp)
    #     img = data.reshape((meta.height, meta.width, 3))
    #     # img = cv2.GaussianBlur(img, (5, 5), 0)
    #
    #     # convert frame to HSV
    #     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    #
    #     # Define mask
    #     lower_mask_value = [18, 50, 50]
    #     upper_mask_value = [36, 255, 255]
    #
    #     lower_mask_value = np.array(lower_mask_value, dtype='uint8')
    #     upper_mask_value = np.array(upper_mask_value, dtype='uint8')
    #
    #     mask = cv2.inRange(hsv, lower_mask_value, upper_mask_value)
    #
    #     output = cv2.bitwise_and(img, hsv, mask=mask)
    #
    #     # total_number is the total number of non zero pixels
    #     total_number = cv2.countNonZero(mask)
    #
    #     if int(total_number) > 500:
    #         print('fire detected')
    #
    #     cv2.imshow('Frame', img)
    #     cv2.imshow('Frame masked', output)
    #     cv2.waitKey(10)
    #     # window_id2 = glthread.createWindow()
    #     # glthread.newRenderGroupCall(window_id2)
    #     # context_id2 = glthread.newRenderContextCall(1, window_id2, 0)
    #     # glthread.delRenderContextCall(context_id2)
    #     # glthread.delRenderGroupCall(window_id2)


class QValkkaFireDetectorProcess(QValkkaOpenCVProcess):
    # pass
    incoming_signal_defs = {  # each key corresponds to a front- and backend methods
        "create_client_": [],
        "test_": {"test_int": int, "test_str": str},
        "stop_": [],
        "ping_": {"message": str}
    }

    outgoing_signal_defs = {
        "pong_o": {"message": str},
        # "start_move": {},
        "Fire_detected": {},
        "stop_move": {}
    }

    # For each outgoing signal, create a Qt signal with the same name.  The
    # frontend Qt thread will read processes communication pipe and emit these
    # signals.
    class Signals(QtCore.QObject):

        # PySide2 version:
        pong_o = QtCore.Signal(object)
        start_move = QtCore.Signal()
        Fire_detected = QtCore.Signal()
        stop_move = QtCore.Signal()

    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)  # does parameterInitCheck
        self.signals = self.Signals()
        self.fireDetected = False


        # # parameterInitCheck(QValkkaMovementDetectorProcess.parameter_defs, kwargs, self)
        # self.analyzer=MovementDetector(verbose=True)
        # self.analyzer = MovementDetector(treshold=0.0001)# To be changed

    def cycle_(self):
        if self.client is None:
            time.sleep(1.0)
        else:
            index, isize = self.client.pull()
            if (index is None):
                # print(self.pre, "Client timed out..")
                pass
            else:
                # print("Client index, size =", index, isize)
                data = self.client.shmem_list[index]
                try:
                    img = data.reshape(
                        (self.image_dimensions[1], self.image_dimensions[0], 3))
                except BaseException:
                    print("QValkkaMovementDetectorProcess: WARNING: could not reshape image")
                    pass
                # else:
                #     result = self.analyzer(img)
                #     # print(self.pre,">>>",data[0:10])
                #     if (result == MovementDetector.state_same):
                #         pass
                #     elif (result == MovementDetector.state_start):
                #         self.sendSignal_(name="start_move")
                #     elif (result == MovementDetector.state_stop):
                #         self.sendSignal_(name="stop_move")
                # cv2.imshow('image', img)

                # lets apply blur to reduce noise
                imgBlurred = cv2.GaussianBlur(img, (5, 5), 0)

                # Lets convert the image to HSV
                imgHSV = cv2.cvtColor(imgBlurred, cv2.COLOR_BGR2HSV)

                # Define the mask
                lower_mask_value = [18, 50, 50]
                upper_mask_value = [36, 255, 255]

                lower_mask_value = np.array(lower_mask_value, dtype='uint8')
                upper_mask_value = np.array(upper_mask_value, dtype='uint8')

                mask = cv2.inRange(imgHSV, lower_mask_value, upper_mask_value)

                # Count the total number of red pixels ; total number of non zero pixels
                total_number = cv2.countNonZero(mask)
                # print(type(total_number))

                if int(total_number) > 500:
                    print('Fire detected ')
                    # pass


    # ** frontend methods handling received outgoing signals ***

    def start_move(self):
        print(self.pre, "At frontend: got movement")
        self.signals.start_move.emit()

    def stop_move(self):
        print(self.pre, "At frontend: movement stopped")
        self.signals.stop_move.emit()
