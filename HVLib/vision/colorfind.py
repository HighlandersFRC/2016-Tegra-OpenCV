import cv2
from hvlib import visionFile
import numpy as np

#
# Masks image based upon h value of color
#

class colorfind(visionFile.visionFile):
    def __init__(self):
        super(colorfind,self).__init__({"HMIN": 128,"HMAX": 128},self.calculateFrame,"colorfid")    
    
    def calculateFrame(self,frame):

        data = self.getDataPoints()

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        lower_bound = np.array([float(data['HMIN']),0,0])
        upper_bound = np.array([float(data['HMAX']),255,255])

        mask = cv2.inRange(hsv,lower_bound,upper_bound)
        ret = True
        data = ""
        return frame , data, ret, mask
        
