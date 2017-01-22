import cv2
from hvlib import visionFile
import os
import json
import numpy as np
#
# blitzar
#

class blitzar(visionFile.visionFile):
    def __init__(self):
        super(blitzar,self).__init__({"HMIN": 70,"HMAX": 90,"VMIN": 0,"VMAX": 200},self.calculateFrame,"blitzar")

    
    def calculateFrame(self,cap):
        cascPath ="/home/john/Documents/2016-Tegra-OpenCV/HVLib/vision/2017-classifier.xml"
        data = self.getDataPoints()
        targetCascade = cv2.CascadeClassifier(cascPath)
        frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        targets = targetCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=7,
        minSize=(30, 30),
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        lower_bound = np.array([float(data['HMIN']),0,float(data['VMIN'])])
        upper_bound = np.array([float(data['HMAX']),255,float(data['VMAX'])])

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,lower_bound,upper_bound)

        largest_area = 0
        xCenter = -1
        yCenter = -1
        targetRect = None

        for (x, y, w, h) in targets:
            #cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            maskROI = mask[x:x+w, y:y+h]
            ret,thresh = cv2.threshold(maskROI,200,255,0)
            contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            area = 0
            for c in contours:
                area += cv2.contourArea(c)
            if area / (w*h) > largest_area:
                xCenter = w/2 + x
                yCenter = h/2 + y
                largest_area = area / (w*h)
                targetRect = [x,y,x+w,y+h]

        if targetRect is not None:
            cv2.rectangle(frame, (targetRect[0],targetRect[1]),(targetRect[2],targetRect[3]), (0, 255, 0), 2)
        output = {}
        output_dict = {"xCenter": xCenter, "yCenter": yCenter}
        output = json.dumps(output_dict)

        
        return frame ,output , True, mask
        
