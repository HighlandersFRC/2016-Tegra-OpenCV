import json
import cv2
import numpy as np
#
# A class that contains a function and can be used to create switchable vision functions
#

class visionFile(object): 
    dataPoints = [] 
    visionName = ""
    def __init__(self, data, func, name): 
        self.dataPoints = data
        self.calculateFrame = func
        self.visionName = name

    def calculateFrame(self,frame):
        mask = frame
        ret = True
        data = ""
        return frame, data, ret, mask

    #Updates DataPoints and takes in a python dictionary
    def update(self, data): 
        
        self.dataPoints = data
        
    #updates DataPoints and takes in JSON string describing data points
    def updateByJSON(self,data):
        newData = []
        for element in data:
            if element != 'visionName':
                index = '"'+ element + '"'
                newData.append((element,data[element]))
        dataPoints = newData
    
    def getDataPoints(self):
        return self.dataPoints
    
    def setCalculateFrame(self,func):
        self.calculateFrame = func

    def getCalculateFrame(self):
        return self.calculateFrame

    def setVisionName(self,name):
        self.visionName = name

    def getVisionName(self):
        return self.visionName

    def getJSON(self): 
        data = self.dataPoints
        data["visionName"] = self.visionName
        print "visionFiles",self.visionName
        return json.dumps(data)
    
