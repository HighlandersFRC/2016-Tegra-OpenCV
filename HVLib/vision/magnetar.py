import cv2
from hvlib import visionFile
import numpy as np

#
# Port of Magnetar's 2016 system to new system
#

class magnetar(visionFile.visionFile):
    def __init__(self):
        super(magnetar,self).__init__({"HMIN": 0,"HMAX": 255,"SMIN": 0,"SMAX": 255,"VMIN": 0,"VMAX": 255},self.calculateFrame,"magnetar")    
    
    def calculateFrame(self,frame):

        data = self.getDataPoints()

        mask = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        lower_bound = np.array([int(data['HMIN']),int(data['SMIN']),int(data['VMIN'])])
        upper_bound = np.array([int(data['HMAX']),int(data['SMAX']),int(data['VMAX'])])
        mask = cv2.inRange(mask, lower_bound, upper_bound)
        ret,thresh = cv2.threshold(mask,200,255,0)
        contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        if len(contours) >1:
            cnt = None
            for cont in contours:
                approx = cv2.approxPolyDP(cont,0.022*cv2.arcLength(cont,True),True)
                rect = cv2.minAreaRect(cont)
                box = cv2.cv.BoxPoints(rect)
                box = np.int0(box)

                xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
                yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
        
                if len(approx)>8:
                    cv2.drawContours(frame,[cont],0,(255,0,0),-1)
                elif len(approx)<8:
                    cv2.drawContours(frame,[cont],0,(0,0,255),-1)
                else:
                    if cnt ==None:
                        cnt = cont
                    elif cv2.arcLength(cont,True) > cv2.arcLength(cnt,True):
                        cnt = cont
                    cv2.drawContours(frame,[cont],0,(255,255,255),-1)
            if cnt == None:
                areas = [cv2.contourArea(c) for c in contours]
                max_index = np.argmax(areas)
                cnt = contours[max_index]
            rect = cv2.minAreaRect(cnt)
            box = cv2.cv.BoxPoints(rect)
            box = np.int0(box)

            xCenter = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
            yCenter = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4

            xLocked = abs(160 - xCenter) < 10
            yLocked = abs(120 - yCenter) < 10

            if xLocked:
                cv2.line(frame,(160,0),(160,240),(0,0,255),3)
            else:
                cv2.line(frame,(320,0),(320,480),(255,0,0),3)
            if yLocked:
                cv2.line(frame,(0,120),(640,120),(0,0,255),3)
            else:
                cv2.line(frame,(0,120),(640,120),(255,0,0),3)
            if xLocked and yLocked:
                cv2.drawContours(frame,[box],0,(0,0,255),2)
            else:
                cv2.drawContours(frame,[box],0,(0,255,0),2)
            msg = '(' + str(xCenter) + ',' + str(yCenter) + ')\n'
        else:
            msg = '( 0,0)\n'
        
        ret = True
        return frame , msg, ret, mask
