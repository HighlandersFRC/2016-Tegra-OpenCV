import cv2
from hvlib import visionFile
import os
import json
import numpy as np
import math
#
# blitzar
#

class blitzar(visionFile.visionFile):
    def __init__(self):
        super(blitzar,self).__init__({"HMIN": 70,"HMAX": 90,"VMIN": 0,"VMAX": 200,"SMIN": 0, "SMAX": 200},self.calculateFrame,"blitzar")

    
    def calculateFrame(self,cap):
        data = self.getDataPoints()
        #targetCascade = cv2.CascadeClassifier(cascPath)
        frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        lower_bound = np.array([float(data['HMIN']),float(data["SMIN"]),float(data['VMIN'])])
        upper_bound = np.array([float(data['HMAX']),float(data["SMAX"]),float(data['VMAX'])])

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,lower_bound,upper_bound)

        largest_area = 0
        xCenter = -1
        yCenter = -1
        targetRect = None

        ret,thresh = cv2.threshold(mask,200,255,0)
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	if len(contours) > 1:
		areas = [cv2.contourArea(c) for c in contours]
		max_index = np.argmax(areas)
		cnt = contours[max_index]
		rect = cv2.minAreaRect(cnt)
		box = cv2.cv.BoxPoints(rect)
		box = np.int0(box)

		xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) /4
		yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) /4
		cv2.drawContours(frame,[box],0,(0,255,0),2)	
  

        output = {}
	distance = 0.0025396523 * yCenter**2 + 0.1000098497 *yCenter + 46.8824851568
	theta = math.atan2(xCenter-160, distance)
        output_dict = {"xCenter": xCenter, "yCenter": yCenter,"theta": theta, "distance":distance}
        output = json.dumps(output_dict)

        
        return frame ,output , True, mask
        
