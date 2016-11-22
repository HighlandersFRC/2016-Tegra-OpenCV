import cv2
from hvlib import visionFile
import numpy as np

#
# Edge detection based upon opencv python2 examples edge
#

class edge(visionFile.visionFile):
    def __init__(self):
        super(edge,self).__init__({"Threshold": 128,"Threshold_Two": 128},self.calculateFrame,"edge")    
    
    def calculateFrame(self,frame):
        
        data = self.getDataPoints()
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        edge = cv2.Canny(gray,float(data['Threshold'])* 20,float(data['Threshold_Two'])*20,apertureSize=5)
        vis = frame.copy()
        vis = np.uint8(vis/2.)
        vis[edge != 0] = (0,255,0)
        mask = frame
        ret = True
        data = ""
        return vis , data, ret, mask
        
