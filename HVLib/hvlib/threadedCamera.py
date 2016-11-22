from threading import Thread
import cv2

#
# A class that takes a videoCapture object and multithreads the frame grab 
#
class USBCamera:
    def __init__(self,cap): 
        self.stream = cap
        (self.grabbed,self.frame) = self.stream.read()

    def start(self):
        Thread(target=self.update,args=()).start()
        return self
    
    def update(self):
        while True:
        	(self.grabbed,self.frame) = self.stream.read()
            
    def read(self):
        return self.frame
