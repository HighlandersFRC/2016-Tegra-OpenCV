import cv2
from flask import Flask, Response, render_template
from cv2 import *
import sys 
import time
from hvlib import threadedCamera
capture = VideoCapture(0)

capture.set(3,320)
capture.set(4,240)
cap = threadedCamera.USBCamera(capture).start()
# Notice how the capture object is now place in the USB camera object which Threads the feed

app = Flask(__name__)


def gen(): 
    last_time = 0 
    while True: 
        print (1/(time.time()-last_time))
        last_time = time.time()
        frame = cap.read()  
        frame = cv2.imencode('.jpg',frame,[int(IMWRITE_JPEG_QUALITY),50])[1].tostring()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('BasicWebStream.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5800,threaded = True)

capture.release()

