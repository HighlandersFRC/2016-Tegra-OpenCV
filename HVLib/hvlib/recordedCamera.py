from threading import Thread
import cv2
import os
import datetime as dt

#
# The recordedCamera class makes it easier to write videos out for the system
# It takes the paramater for the directory of the output video and names the video 
# based upon the current day and which video it is to avoid overwriting videos
# 
# Multithreading for this class was considered but has proven to slower on raspberryPI
#
class recordedCamera:
    def __init__(self,destination): 
        self.framerate = 30.0
        self.frame_buffer = []
        self.path = destination
        self.width= 320 
        self.height = 240

    def start(self):
        now = dt.datetime.now()
        if len(self.path) !=0 and self.path[len(self.path)-1] != '/':
            self.path = self.path + '/'    
        output_name = self.path + str(dt.datetime.date(now))+ '-0.avi'
        video_num = 1
        while os.path.isfile(output_name):
            output_name = self.path +str(dt.datetime.date(now)) + '-'+str(video_num)+'.avi'
            video_num = video_num + 1
        fourcc = cv2.cv.CV_FOURCC(*'XVID')
        self.out = cv2.VideoWriter(output_name,fourcc,self.framerate,(self.width,self.height)) 
        return self


    def write(self,frame):
        self.out.write(frame)
