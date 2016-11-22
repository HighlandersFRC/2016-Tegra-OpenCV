import cv2
from hvlib import visionFile

#
# default vision file with no special features
#

class novision(visionFile.visionFile):
    def __init__(self):
        super(novision,self).__init__({},self.calculateFrame,"novision")    
    
    def calculateFrame(self,frame):
        mask = frame
        ret = True
        data = ""
        return frame , data, ret, mask
        
