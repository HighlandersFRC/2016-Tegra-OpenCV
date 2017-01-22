from threading import Thread
import cv2
import os


#
# A class that takes a videoCapture object and multithreads the frame grab 
#
class USBCamera:
    def __init__(self,cap): 
        self.stream = cap
        self.device = 0
        (self.grabbed,self.frame) = self.stream.read()
        self.isStopped = False

    def start(self):
        Thread(target=self.update,args=()).start()
        return self
    def set_capture_index(self,index):
        self.device = index
    
    def set_capture_time(self,exposure_time):
        self.exposure_time = exposure_time
        self.v4l = "/usr/bin/v4l2-ctl"
        # Select's the specified camera
        device_setting = "--device=/dev/video{0}".format(self.device)

        # The camera must be set to manual exposure before we set
        # the exposure time below.
        manual_exp_setting = "--set-ctrl=exposure_auto={0}".format(1)

        self.C920_FOCAL_RATIO = 0.61744858
        self.frame_wid = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
        self.frame_hgt = self.stream.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

        self.focal_len = self.C920_FOCAL_RATIO * self.frame_wid

        _, self.frame = self.stream.read()

        # Millisecond exposure time
        if (self.exposure_time == -1):
            exp_setting = "--set-ctrl=exposure_absolute={0}".format(5)
            #print "Use default exposure time {0}".format(exp_setting)
        else:
            exp_setting = "--set-ctrl=exposure_absolute={0}".format(self.exposure_time)

        command = "{0} {1} {2}".format(self.v4l, device_setting, manual_exp_setting)
        os.system(command)
        command = "{0} {1} {2}".format(self.v4l, device_setting, exp_setting)
        os.system(command)

        # Turn off auto focus
        focus_auto = "--set-ctrl=focus_auto=0"
        command = "{0} {1} {2}".format(self.v4l, device_setting, focus_auto)
        os.system(command)

        # Set focus depth to infinity
        focus_infinite = "--set-ctrl=focus_absolute=0"
        command = "{0} {1} {2}".format(self.v4l, device_setting, focus_infinite)
        os.system(command)

        # Set width and height
        focus_auto = "--set-fmt-video=width=1920,height=1080,pixelformat=1"
        command = "{0} {1} {2}".format(self.v4l, device_setting, focus_auto)
        os.system(command)
    
    def update(self):
        while not self.isStopped:
        	(self.grabbed,self.frame) = self.stream.read()
            
    def read(self):
        return self.frame
    def stop(self):
        self.isStopped = True
