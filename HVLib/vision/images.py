import cv2
from hvlib import visionFile

#
# default vision file with no special features
#

class images(visionFile.visionFile):
    def __init__(self):
        super(images,self).__init__({},self.calculateFrame,"images")    
    	self.count = 0
	self.image_num = 0
    def calculateFrame(self,cap):
        #cap.set_capture_time(10)
        frame = cap.read()
	
	if self.count % 30 == 0:
		cv2.imwrite("/home/ubuntu/images/"+str(self.image_num) + ".jpg",frame)
		self.image_num = self.image_num + 1
	self.count = self.count + 1
        mask = frame
        ret = True
        data = ""
        return frame , data, ret, mask
        
