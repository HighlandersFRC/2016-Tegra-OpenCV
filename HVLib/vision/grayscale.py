import cv2
from hvlib import visionFile

#
# Converts image to grayscale
#

class grayscale(visionFile.visionFile):
    def __init__(self):
        super(grayscale,self).__init__({},self.calculateFrame,"grayscale")    
    
    def calculateFrame(self,frame):
       
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)

        mask = frame
        ret = True
        data = ""
        return hsv , data, ret, mask
        
