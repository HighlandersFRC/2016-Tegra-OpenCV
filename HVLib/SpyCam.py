import cv2
from flask import Flask, Response, render_template,request, send_from_directory,redirect,url_for
from cv2 import *
import sys
sys.path.insert(0,'../HVLib')
import threadedCamera 
import time
import wiringpi


wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(18,wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)

wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)


global sliderValue
sliderValue = 0

# get the video capture object
capture = VideoCapture(0)

capture.set(3,320)# width 320
capture.set(4,240)# height 240

# creates a threadedCamera object which threads the system improving perfomance
cap = threadedCamera.USBCamera(capture).start()

#create webpage
app = Flask(__name__)

# The gen function needs to yield the image that will be displayed
def gen(): 
    last_time = 0 
    while True:
        global sliderValue
        wiringpi.pwmWrite(18,sliderValue)
        print 1/(time.time()-last_time)
        last_time = time.time()
        frame = cap.read()  
        frame = cv2.imencode('.jpg',frame,[int(IMWRITE_JPEG_QUALITY),50])[1].tostring() 
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


#default route
@app.route('/')
def index():
   return render_template('UserWebInterface.html')

#special route that allows for the feed to be streamed
@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/updateValues')
def updateValues():
    global sliderValue
    sliderValue = request.args.get('sliderValue',-1,type=int)
    return ('',204) 


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5800,threaded = True)

cap.stop()
capture.release()

