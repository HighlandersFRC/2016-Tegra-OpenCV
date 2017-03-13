import cv2
from hvlib import visionFile
import os
import json
import numpy as np
import math
#
# blitzar
#

class dev(visionFile.visionFile):
    def __init__(self):
        super(dev,self).__init__({"HMIN": 70,"HMAX": 90,"VMIN": 0,"VMAX": 200,"SMIN": 0, "SMAX": 200},self.calculateFrame,"dev")
	
    def calculateFrame(self,cap):
	cascPath ="/home/ubuntu/2016-Tegra-OpenCV/HVLib/vision/2017-classifier.xml"
        data = self.getDataPoints()
        targetCascade = cv2.CascadeClassifier(cascPath)
        frame = cap.read()
        frame = frame.copy()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
       	
	# This section builds probabilities based upon the mahine learning available
	ml_weight = 50 
	targets = targetCascade.detectMultiScale(
	gray,
	scaleFactor=1.1,
	minNeighbors=7,
	minSize=(10,10),
	flags = cv2.cv.CV_HAAR_SCALE_IMAGE
	)
	probability = gray.copy()
	probability[:,:] = 0
	for (x,y,w,h) in targets:	
		probability[y:y+h,x:x+w] += ml_weight

	#This section builds probabilities based upon the avaiablie geometry of the target
	geometry_weight = 150
	lower_bound = np.array([float(data['HMIN']),float(data["SMIN"]),float(data['VMIN'])])
        upper_bound = np.array([float(data['HMAX']),float(data["SMAX"]),float(data['VMAX'])])
        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,lower_bound,upper_bound)
        ret,thresh = cv2.threshold(mask,200,255,0)
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	
	
	centers = []
	for c in contours:
		area = cv2.contourArea(c)
		if area > 50 and area < 10000:
			rect = cv2.minAreaRect(c)
			box = cv2.cv.BoxPoints(rect)
					
			xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) /4
			yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) /4
			centers.append((xCenter,yCenter,c))		
	pairs = []
	for i in range(0,len(centers)):
		for j in range(i+1,len(centers)):
			xdelta = abs(centers[i][0] - centers[j][0])
			ydelta = abs(centers[i][1] - centers[j][1])
			if xdelta < 20 and ydelta < 20: 
				if centers[i][1] < centers[j][1]:
					pairs.append((i,j))
				else:
					pairs.append((j,i))	
	for pair in pairs:
		top = (centers[pair[0]])[2] 
		bottom = (centers[pair[1]])[2] 
		xt,yt,wt,ht = cv2.boundingRect(top)
		xb,yb,wb,hb = cv2.boundingRect(bottom)
		w = max(wt,wb)
		h = ht + hb 
		xCorner = int(xCenter-w/2)
		yCorner = int(yCenter-h/2)	
		ratio = cv2.contourArea(top) / (2*cv2.contourArea(bottom))
		weight = int(geometry_weight * min(ratio,1/ratio))
		probability[yCorner:yCorner+h,xCorner: xCorner+w] += weight
	
	# Factor in the mask as a part of the final probability
	probability += mask * 0.15
	
	#Use the new probability map to find the location of the new target
	ret, thresh = cv2.threshold(probability,100,255,0)
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	cnt = None
	if len(contours) > 0:
		areas = [cv2.contourArea(c) for c in contours]
		max_index = np.argmax(areas)
		cnt = contours[max_index]
	xCenter = -1
	yCenter = -1
	if cnt is not None:
		rect = cv2.minAreaRect(c)
		box = cv2.cv.BoxPoints(rect)
		box = np.int0(box)
		cv2.drawContours(frame, [box],0,(0,255,0),1)
		xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) /4
		yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) /4
		
	distance = 0.0025396523 * (yCenter**2) + (0.1000098497 * yCenter) + 46.8824851568
	theta = math.atan2(xCenter-160, distance)
        try:
            output_dict = { "xCenter": xCenter, "yCenter": yCenter,"theta": theta, "distance":distance}	
            print type(output_dict)
            output = json.dumps(output_dict)
            return frame,output,True,probability
        except:
            pass

        return frame ,"" , True, probability
        
