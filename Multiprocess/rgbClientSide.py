import time, sys
from valkka.multiprocess import MessageProcess, MessageObject, safe_select
from valkka.api2 import ShmemRGBClient, ShmemRGBServer, ShmemClient
from Singleton import getEventFd, reserveEventFd, releaseEventFd, eventFdToIndex, reserveIndex
from .rgb import RGB24Process
import numpy as np
import  cv2

class RGBClientProcess(RGB24Process):
    """
    Gets RGB24 frames from valkka side, inspects them and then pass them to master processes (i,e different Machine Vision processes)

    !! Needs to establish an RGB24 shmem server

    Receives a message from Machine vision process
    """

    def __init__(self, mstimeout = 1000, server_img_width = 100, server_img_height = 100):
        super().__init__(mstimeout= mstimeout)
        self.event_fd = reserveEventFd() # event fd for the rgb24 shmem server

        self.server_name = str(id(self))
        self.server_n_ringbuffer = 10
        self.server_width = server_img_width
        self.server_height = server_img_height

        self.intercom_ipc_index = None # event fd index for sending messages to master process (i,e machine vision process)
        self.intercom_client = None
        self.intercom_fd = None

    def __del__(self):
        releaseEventFd(self.event_fd)


    """ BACKEND METHODS 
    
    Never call these methods from the main python process: they are internal for the multiprocess backend
    """

    def preRun__(self):
        super().preRun__()
        # Shmem servers could also be created on-demand for various master processes
        self.server = ShmemRGBServer(
            name = self.server_name,
            n_ringbuffer = self.server_n_ringbuffer,
            width = self.server_width,
            height = self.server_height
        )
        self.server.useEventFd(self.event_fd)
        print("rgbClientSideProcess : using event_fd for serving frames fd=", self.event_fd.getFd())

    def postRun__(self):
        super(RGBClientProcess, self).postRun__()

    def readPipes__(self, timeout):
        """
        Multiplex all intercom pipes / events

        This is used by your multiprocess run() method // no need to modify run() method

        """
        rlis = [self.back_pipe]
        # self.back_pipe is the intercom pipe with the main python process

        # listen to all rgb frame sources
        frame_fds = list(self.client_by_fd.keys())

        rlis += frame_fds

        if self.intercom_fd is not None:
            rlis.append(self.intercom_fd)

        rs, ws, es = safe_select(rlis, [],  [], timeout= timeout)

        # rs is a list of event file descriptors that have been triggered
        for fd in rs:
            # 1. handle the main intercom pipe
            if fd == self.back_pipe:
                self.handleBackPipe__(self.back_pipe)
            # 2. handle frame coming from valkka c++ side
            if fd in frame_fds:
                client = self.client_by_fd[fd]
                index, meta = client.pullFrame()
                if (index == None):
                    print("weird.. rgb client got none ")
                else:
                    data = client.shmem_list[index][0:meta.size]
                    data = data.reshape((meta.height, meta.width, 3))
                    self.handleFrame__(data, meta)
            # 3. handle message from the master process (i,e machine vision process )
            if fd == self.intercom_fd:
                obj = self.intercom_client.pullObject()
                self.handleMessage__(obj)

    def handleFrame__(self, frame, meta):
        print("ClientProcess: handleFrame__ : got frame", frame.shape, "from slot", meta.slot)
        """
        metadata has the following members :
        size 
        width
        height 
        slot 
        mstimeout
        """
        imgblurred = cv2.GaussianBlur(frame, (15, 15), 0)
        # Lets convert the image to HSV
        imgHSV = cv2.cvtColor(imgblurred, cv2.COLOR_BGR2HSV)

        # Define the mask
        lower_mask_value = [18, 50, 50]
        upper_mask_value = [36, 255, 255]

        lower_mask_value = np.array(lower_mask_value, dtype='uint8')
        upper_mask_value = np.array(upper_mask_value, dtype='uint8')

        mask = cv2.inRange(imgHSV, lower_mask_value, upper_mask_value)

        # Count the total number of red pixels ; total number of non zero pixels
        total_number = cv2.countNonZero(mask)
        print('total number : ', int(total_number))
        if total_number > 500:
            print("fire detected")

        # do something with the frame then forward it to the master process (i,e machine vision process )
        ## TODO: if the frame is too big, the client will hang -- To deal with later
        self.server.pushFrame(frame[0:10, 0:10, :], meta.slot, meta.mstimeout)
        # send message to main process like this
        # self.send_out__({})

    def handleMessage__(self, obj):
        print("rgbClientSide process : handleMessage__ : got a message from master ",obj)

    def c__listenIntercom(self,
                          name = None,
                          n_ringbuffer = None,
                          n_bytes = None,
                          ipc_index = None,
                          ):
        client = ShmemClient(
            name = name,
            n_ringbuffer = n_ringbuffer,
            n_bytes = n_bytes,
            mstimeout = self.mstimeout
        )
        eventfd = getEventFd(ipc_index)
        client.useEventFd(eventfd)
        fd = eventfd.getFd()
        # self.intercom_client_by_fd[fd] = client #if you would be listening many clients at a time
        self.intercom_client = client
        self.intercom_fd = fd

    def c__dropIntercom(self
                        # ipc_index = None,
                        ):
        # fd = getFdFromIndex(ipc_index)
        # self.intercom_client_by_fd.pop(fd) # if you would be listening many clients at a time
        self.intercom_client = None
        self.intercom_fd = None

    """FRONTEND

    These methods are called by your main python process
    """

    def getRGB24ServerPars(self):
        pars = {
            "name": self.server_name,
            "n_ringbuffer": self.server_n_ringbuffer,
            "width": self.server_width,
            "height": self.server_height,
            "ipc_index": eventFdToIndex(self.event_fd)
        }
        print("getRGB24ServerPars:", pars)
        return pars

    def listenIntercom(self,
                       name=None,
                       n_ringbuffer=None,
                       n_bytes=None,
                       ipc_index=None
                       ):
        if self.intercom_ipc_index is not None:
            print("listenIntercom: already listening to master")
            return

        self.sendMessageToBack(MessageObject(
            "listenIntercom",
            name=name,
            n_ringbuffer=n_ringbuffer,
            n_bytes=n_bytes,
            ipc_index=ipc_index  # event fd index for the intecom channel
        ))
        self.intercom_ipc_index = ipc_index

    def dropIntercom(self):
        if self.intercom_ipc_index is None:
            print("dropIntercom: no intercom")
            return
        self.sendMessageToBack(MessageObject(
            "dropIntercom"
            # ipc_index = ipc_index # event fd index for the intecom channel
        ))
        self.intercom_ipc_index = None
