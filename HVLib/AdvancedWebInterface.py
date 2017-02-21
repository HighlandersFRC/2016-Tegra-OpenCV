import cv2
from flask import Flask, Response, render_template,request, send_from_directory,redirect,url_for
from cv2 import *
import sys
sys.path.append('vision')
from hvlib import * 
import time
import os
import json
import novision
import ast

visionOptions = [] # contains strings of data that correspond to the names of available vision files 


visionFiles = [novision.novision(),novision.novision(),novision.novision()]
cameraStrings = ["cam_zero","cam_zero","cam_zero"]
masks =[False,False,False]
availableCameras = ['off']
#get the video capture object

cameras = {'cam_zero':None,'cam_one': None, 'cam_two':None,"off":None }
logo = open('assets/Logo.png','rb').read()
socket = send.send('roboRIO-4499-frc.local',5801)
socket.connect()

for i in range(0,3):
    try:
        capture = cv2.VideoCapture(int(i)) 
        capture.set(3,320)# width 320
        capture.set(4,240)# height 240
        if capture != None and capture.isOpened():
            cap = threadedCamera.USBCamera(capture).start()
            cap.set_capture_index(i)
            if i ==0:
                cameras['cam_zero'] = cap
		cap.set_capture_time(5)
                availableCameras.append("cam_zero")
            elif i ==1:
                #cap.set_capture_time(200)
                cameras['cam_one'] = cap
                availableCameras.append("cam_one")
            elif i ==2:
                cameras['cam_two'] = cap
                availableCameras.append("cam_two")
    except:
        print ("No Camera Present") 
selectedFrame = -1

#create webpage
app = Flask(__name__)
# The gen function needs to yield the image that will be displayed
def checkAllCamerasOff():
    for i in cameraStrings:
        if i != "off":
            return False
    return True

def gen(index): 
    lastTime = time.time()
    while True:	
        camera = cameras[cameraStrings[index]]
        frame = None
        deltaTime = time.time() - lastTime
        #print 1/deltaTime
        lastTime = time.time()
        if camera == None:
            frame = logo
            yield (b'--frame\r\n'b'Content-Type: image/png\r\n\r\n' + frame + b'\r\n')
        else:
            #frame = cameras[cameraStrings[index]].read() 
            frame,data,ret,mask = visionFiles[index].calculateFrame(cameras[cameraStrings[index]])
            if len(data) > 0:
                socket.send(data)
            if masks[index]:
                frame = mask
            frame = cv2.imencode('.jpg',frame,[int(IMWRITE_JPEG_QUALITY),50])[1].tostring() 
            yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#default route
@app.route('/')
def index():
   return render_template('AdvancedWebInterface.html')

#special route that allows for the feed to be streamed
#These routes are for the various vision feeds that will be coming into the system
@app.route('/video_zero')
def video_zero():
    return Response(gen(0),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_one')
def video_one():
    return Response(gen(1),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_two')
def video_two():
    return Response(gen(2),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/frame_query')
def frame_query():
    data = visionFiles[selectedFrame].dataPoints
    data["visionName"] = visionFiles[selectedFrame].visionName
    data["camera"] = cameraStrings[selectedFrame]
    return Response(json.dumps(data))

# This is a route that will communicate between the server and the client
@app.route('/updateValues')
def updateValues(): 
    global selectedFrame
    global visionFiles

    action = request.args.get('action',-1,type=int)
    
    if action == 0: # update Values
        frameStats = request.args.get("frameStats","",type = str)
        frameDict = ast.literal_eval(frameStats) 
        (visionFiles[selectedFrame]).update(frameDict)
        print ("Updated VisionValues","SelectedFrame: ", selectedFrame)

    elif action == 1:# changeFrame
        selectedFrame = request.args.get("selectedFrame",-1,type=int)
        print ("ChangedFrame to: ", selectedFrame, visionFiles[selectedFrame])
    
    elif action == 2: # changeVision
        selectedVision = request.args.get("selectedVision","novision",type=str)
        visionFiles[selectedFrame] = getVisionFileObj(selectedVision)
        print ("Changed Vision to: ", visionFiles[selectedFrame])
    
    elif action == 4: # saveVisionFile
        name = request.args.get("saveAs","unknown",type=str)
        saveGlobaConfig(name)
    
    elif action == 5: # save global settings
        saveAs = request.args.get('saveAs','unknown',type=str)
        saveGlobalConfig(saveAs)

    elif action == 6: # reload global settings / load global settings
        pageConfig = request.args.get('pageConfig',"default",type=str)
        loadPageConfiguration("saves/pages/" + pageConfig + ".json")
    elif action == 7: # swtich camera
        global cameraStrings
        cameraStrings[selectedFrame] = request.args.get('camera','cam_zero',type=str)
    elif action == 8: # toggle mask on/off
        global masks
        masks[selectedFrame] = not masks[selectedFrame]
    
    return ('',204) 

#This is used to load up the vision files when requested by the client
#Loading should be only done when a specic vision File is needed
@app.route('/loadVisionFiles')
def loadVisionFiles():
    toReturn = '['
    for f in os.listdir("vision"):
        if f[-3:] == ".py":
            moduleName = f[:len(f)-3]
            toReturn = toReturn +'{ "visionName": "'+ moduleName +'" }, '
            visionOptions.append(moduleName)
    toReturn = toReturn[:len(toReturn)-2] + ']'
    return Response(toReturn)

@app.route('/loadCameras')
def loadCameras():
    return json.dumps(availableCameras)

@app.route('/loadGlobalConfigFiles')
def loadGlobalConfigFiles():
    toReturn = '['
    for f in os.listdir("saves/pages"):
        if f[-5:] == ".json":
            fileName = f[:len(f)-5]
            toReturn = toReturn + '{ "fileName": "' + fileName +'" }, '
    toReturn = toReturn[:len(toReturn)-2] + ']' 
    return Response(toReturn)

def getVisionFileObj(name):
    sys.path.append('vision')
    module = __import__(name)
    klass = getattr(module,name) # this is why file and class names must match
    instance = klass() 
    return instance


# loads the global page from a json string
def loadPageConfiguration(path):
    global visionFiles
    f = open(path,'r')
    jsonString = f.read() 
    data = json.loads(jsonString)
    f.close()
    
    #set the cameras to the proper locations
    cameraStrings[0] = data['frame_zero_cam']
    cameraStrings[1] = data['frame_one_cam']
    cameraStrings[2] = data['frame_two_cam']
     
    
    #setup objects for the visionFiles array
    visionFiles[0] = getVisionFileObj(data['frame_zero_vision']['visionName'])
    visionFiles[0].update(ast.literal_eval(str(data['frame_zero_vision'])))
    
    visionFiles[1] = getVisionFileObj(data['frame_one_vision']['visionName'])
    visionFiles[1].update(ast.literal_eval(str(data['frame_one_vision'])))
    
    visionFiles[2] = getVisionFileObj(data['frame_two_vision']['visionName'])
    visionFiles[2].update(ast.literal_eval(str(data['frame_two_vision'])))
    print (visionFiles[0],visionFiles[1],visionFiles[2])

def saveGlobalConfig(name):
    f = open('saves/pages/' + name + '.json','w+')
    f.write(getSaveJSON())
    f.close()

# returns a JSON string describing the global page configuration
def getSaveJSON():
    data = {}
    
    data["frame_zero_cam"] = cameraStrings[0]
    data["frame_zero_vision"] = json.loads(visionFiles[0].getJSON())
    
    data["frame_one_cam"] = cameraStrings[1]
    data["frame_one_vision"] = json.loads(visionFiles[1].getJSON())
    
    data["frame_two_cam"] = cameraStrings[2]
    data["frame_two_vision"] = json.loads(visionFiles[2].getJSON())
    
    temp = json.dumps(data)
    
    return temp

# This function prevents page caching and improve relibility of system
@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    loadPageConfiguration("saves/pages/default.json")
    app.run(host='0.0.0.0',port=5800,threaded = True)

capture.release()

