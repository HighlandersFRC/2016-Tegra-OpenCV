import cv2
from flask import Flask, Response, render_template
from cv2 import *
import sys
import time
from hvlib import threadedCamera, recordedCamera


# get the video capture object
capture = VideoCapture(0)

capture.set(3,320)# width 320
capture.set(4,240)# height 240

# creates a threadedCamera object which threads the system improving perfomance
cap = threadedCamera.USBCamera(capture).start()

# creates an object that will handle setting up the video recording
rec = recordedCamera.recordedCamera("").start()

# create webpage
app = Flask(__name__)

# The gen function needs to yield the image that will be displayed
def gen(): 
    last_time = 0 
    while True: 
        print (1/(time.time()-last_time))
        last_time = time.time()
        frame = cap.read()
        rec.write(frame)# This line tells the camera object to write the frame to the video
        frame = cv2.imencode('.jpg',frame,[int(IMWRITE_JPEG_QUALITY),50])[1].tostring()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

#default route
@app.route('/')
def index():
    return render_template('BasicWebStream.html')

#special route that allows for the feed to be streamed
@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5800,threaded = True)

capture.release()

