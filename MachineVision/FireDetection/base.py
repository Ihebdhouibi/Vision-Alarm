from valkka.core import *
from valkka.api2 import ShmemRGBClient
import time
import cv2
import numpy as np
from valkka.api2.logging import  setValkkaLogLevel, loglevel_silent, loglevel_normal


# setValkkaLogLevel(loglevel_silent)


image_interval = 1000

width = 1920 // 4
height = 1080 // 4

# posix shared memory
shmem_name = "lesson_4"
shmem_buffers = 10

# branch 1
glthread = OpenGLThread("glthread")
gl_in_filter = glthread.getFrameFilter()

# branch 2
shmem_filter = RGBShmemFrameFilter(shmem_name, shmem_buffers, width, height)
# shmem_filter = BriefInfoFrameFilter("shmem")
sws_filter = SwScaleFrameFilter("sws_filter", width, height, shmem_filter)

interval_filter = TimeIntervalFrameFilter("interval_filter", image_interval, sws_filter)

fork_filter = ForkFrameFilter("fork_filter", gl_in_filter, interval_filter)

av_thread = AVThread("av_thread", fork_filter)
av_in_filter = av_thread.getFrameFilter()
live_thread = LiveThread("live_thread")

ctx = LiveConnectionContext(LiveConnectionType_rtsp, "rtsp://iheb:iheb@192.168.1.102:8080/h264_ulaw.sdp", 1,
                            av_in_filter)

glthread.startCall()
av_thread.startCall()
live_thread.startCall()
# start decoding
av_thread.decodingOnCall()
live_thread.registerStreamCall(ctx)
live_thread.playStreamCall(ctx)
# create an X-window
window_id = glthread.createWindow()
glthread.newRenderGroupCall(window_id)
# maps stream with slot 1 to window "window_id"
context_id = glthread.newRenderContextCall(1, window_id, 0)
# time.sleep(15)
# glthread.delRenderContextCall(context_id)
# glthread.delRenderGroupCall(window_id)
# stop decoding
# av_thread.decodingOffCall()
# # stop threads
# live_thread.stopCall()
# av_thread.stopCall()
# glthread.stopCall()


width2 = 1920 // 4
height2 = 1080 // 4

shmem_name2 = "lesson_4"
shmem_buffers2 = 10

client = ShmemRGBClient(
    name=shmem_name2,
    n_ringbuffer=shmem_buffers2,
    width=width2,
    height=height2,
    mstimeout=1000,
    verbose=False
)

while True:
    index, meta = client.pullFrame()
    if index is None:
        # print('timeout')
        continue
    data = client.shmem_list[index][0:meta.size]
    # print('data : ', data[0:min(10, meta.size)])
    # print('width ', meta.width)
    # print('height ', meta.height)
    # print('slot ', meta.slot)
    # print('time ', meta.mstimestamp)
    img = data.reshape((meta.height, meta.width, 3))
    img = cv2.GaussianBlur(img, (5, 5), 0)

    # convert frame to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define mask
    lower_mask_value = [18, 50, 50]
    upper_mask_value = [35, 255, 255]

    lower_mask_value = np.array(lower_mask_value, dtype='uint8')
    upper_mask_value = np.array(upper_mask_value, dtype='uint8')

    mask = cv2.inRange(hsv, lower_mask_value, upper_mask_value)

    output = cv2.bitwise_and(img, hsv, mask=mask)

    # total_number is the total number of non zero pixels
    total_number = cv2.countNonZero(mask)

    if int(total_number) > 400:
        print('fire detected')

    cv2.imshow('img', output)
    cv2.waitKey(10)
    # window_id2 = glthread.createWindow()
    # glthread.newRenderGroupCall(window_id2)
    # context_id2 = glthread.newRenderContextCall(1, window_id2, 0)
    # glthread.delRenderContextCall(context_id2)
    # glthread.delRenderGroupCall(window_id2)




