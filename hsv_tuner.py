
import cv2
import numpy as np
import time
import argparse

import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# http://lxml.de/tutorial.html
from lxml import etree


class set_camera_defaults():
   def __init__(self, device, exposure_time):

      self.device = device
      self.exposure_time = exposure_time
      self.v4l = "/usr/bin/v4l2-ctl"

      # Select's the specified camera
      device_setting = "--device=/dev/video{0}".format(self.device)

      # The camera must be set to manual exposure before we set
      # the exposure time below.
      manual_exp_setting = "--set-ctrl=exposure_auto={0}".format(1)

      # Set width and height
      focus_auto = "--set-fmt-video=width=1920,height=1080,pixelformat=1"
      command = "{0} {1} {2}".format(self.v4l, device_setting, focus_auto)
      os.system(command)

      # Set width and height
      focus_auto = "--set-fmt-video=width=1920,height=1080,pixelformat=1"
      command = "{0} {1} {2}".format(self.v4l, device_setting, focus_auto)
      os.system(command)

      self.C920_FOCAL_RATIO = 0.61744858
      self.cap = cv2.VideoCapture(self.device)
      self.frame_wid = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
      self.frame_hgt = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)

      self.focal_len = self.C920_FOCAL_RATIO * self.frame_wid

      _, self.frame = self.cap.read()

      # Millisecond exposure time
      if (self.exposure_time == -1):
         exp_setting = "--set-ctrl=exposure_absolute={0}".format(5)
         #print "Use default exposure time {0}".format(exp_setting)
      else:
         exp_setting = "--set-ctrl=exposure_absolute={0}".format(self.exposure_time)

      command = "{0} {1} {2}".format(self.v4l, device_setting, manual_exp_setting)
      os.system(command)
      command = "{0} {1} {2}".format(self.v4l, device_setting, exp_setting)
      os.system(command)

      # Turn off auto focus
      focus_auto = "--set-ctrl=focus_auto=0"
      command = "{0} {1} {2}".format(self.v4l, device_setting, focus_auto)
      os.system(command)

      # Set focus depth to infinity
      focus_infinite = "--set-ctrl=focus_absolute=0"
      command = "{0} {1} {2}".format(self.v4l, device_setting, focus_infinite)
      os.system(command)

      # Set width and height
      focus_auto = "--set-fmt-video=width=1920,height=1080,pixelformat=1"
      command = "{0} {1} {2}".format(self.v4l, device_setting, focus_auto)
      os.system(command)


   def get_cap(self):
      return self.cap

class tune_hsv():
   # @todo: Add UI to select camera device (/dev/video#)
   def __init__(self, ui, device, exposure_time, show_result):
      self.ui = ui
      self.device = device
      self.exposure_time = exposure_time
      self.app_name = 'hsv_tuner'
      self.app_ver = 1
      self.cfg_fname = 'hsv_settings.xml'
      self.show_result = show_result
      self.hue = 60
      self.sat = 60
      self.val = 60
      self.hue_tol = 60
      self.sat_tol = 60
      self.val_tol = 60
      self.noise_filter = False
      self.noise_filter_mask = False
      self.refPt = []
      self.have_selection = False
      self.print_selection = False
      self.MAX_UINT = 255
      self.CHECK_SIZE = 100
      self.MAX_HUE = 180
      self.morph_size = 3
      # FOV (field field view) = .5 image width image width / (2 * tan (FOV ? 2)
      # focal length = image width / (2 * tan (FOV ? 2)
      self.C920_FOCAL_RATIO = 0.61744858

      self.restore_settings()

      # Must set camera values AFTER first read because the first read resets
      # the camera settings!
      cd = set_camera_defaults(self.device, self.exposure_time)
      self.cap = cd.get_cap()

      self.frame_wid = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
      self.frame_hgt = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
      self.focal_len = self.C920_FOCAL_RATIO * self.frame_wid

      #self.cap.set(cv2.cv.CV_CAP_PROP_EXPOSURE, .5)
#      self.cap.set(cv2.cv.CV_CAP_PROP_FOURCC, "H264")
      #self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1920)
      #self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 1080) 
      #self.cap.set(cv2.cv.CV_CAP_PROP_FPS, 30) 

      #self.cap.set(3, 1280)
      #self.cap.set(4, 720)

      # Create two named windows
      cv2.namedWindow('frame', cv2.WINDOW_AUTOSIZE)
      cv2.namedWindow('mask', cv2.WINDOW_NORMAL)
      cv2.namedWindow('check', cv2.WINDOW_AUTOSIZE)

      cv2.moveWindow('frame', 1, 1)
      cv2.moveWindow('mask', 710, 0)
      cv2.resizeWindow('mask', 410, 650)
      cv2.moveWindow('check', 500, 530)

      if (self.show_result):
         cv2.namedWindow('res', cv2.WINDOW_NORMAL)
         cv2.moveWindow('res', 1, 530)

      # create a check image with a green pixels
      self.check = np.zeros((self.CHECK_SIZE, self.CHECK_SIZE, 3), np.uint8)

      #print "-----"
      #w = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
      #h = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
      #print "camera capture: width={0}, height={1}".format(w, h)
      #print "-----"

      #self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 640.0)
      #print "-----"
      #self.cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 480.0)
      #print "-----"
            
      #w = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
      #h = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
      #print "camera capture: width={0}, height={1}".format(w, h)
      #print "-----"

   def click_in_frame(self, event, x, y, flags, param):
      if event == cv2.EVENT_LBUTTONDOWN:
         self.refPt = [(x, y)]
         self.refPt.append((x + 1, y + 1))
         self.have_selection = True
         self.print_selection = True

   def get_angle_to_tgt(self, x, y):
      yaw_angle_rad = np.arctan ( (x - (self.frame_wid/2) + 0.5) / self.focal_len )
      pitch_angle_rad = -1 * np.arctan ( (y - (self.frame_hgt/2) + 0.5) / self.focal_len )

      yaw_angle, pitch_angle = np.degrees([ yaw_angle_rad, pitch_angle_rad ])

      print "ANGLES TO TARGET: yaw={0},({1}), pitch={2}({3})".format(yaw_angle, yaw_angle_rad, pitch_angle, pitch_angle_rad)

   def tune(self):
      # Initialize the slider controls for setting hsv & tolerances using CV UI primitives
      self.create_cv_ui()

      cv2.setMouseCallback('frame', self.click_in_frame)

      while(1):
         # define range of blue color in HSV
         lower_bound = np.array([max(0, self.hue - self.hue_tol),
             			max(0, self.sat - self.sat_tol), 
				max(0, self.val - self.val_tol)])
         upper_bound = np.array([min (self.MAX_HUE, self.hue + self.hue_tol),
		 		min (self.MAX_UINT, self.sat + self.sat_tol),
		 		min (self.MAX_UINT, self.val + self.val_tol)])

         # Take each frame
         _, self.frame = self.cap.read()

         # Convert BGR to HSV
         self.hsv_noisy = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

         if (self.noise_filter):
            # Apply noise filter to color image
            # self.hsv = cv2.fastNlMeansDenoisingColored(self.hsv_noisy, None, 10, 10, 7, 21)
            self.hsv = cv2.fastNlMeansDenoisingColored(self.hsv_noisy, None, 3, 3, 5, 15)
         else:
            self.hsv = self.hsv_noisy

         # Threshold HSV image to get bounded values
         mask_noisy = cv2.inRange(self.hsv, lower_bound, upper_bound)

         if (self.noise_filter_mask):
            self.mask = cv2.fastNlMeansDenoising(mask_noisy, None, 20, 7, 21)
         elif (self.morph_size):
            kernel = np.ones((self.morph_size, self.morph_size), np.uint8);
            self.mask = cv2.morphologyEx(mask_noisy, cv2.MORPH_CLOSE, kernel)
            self.mask = cv2.morphologyEx(mask_noisy, cv2.MORPH_OPEN, kernel)
         else:
            self.mask = mask_noisy

         # Draw selection rectangle if one exists
         if self.have_selection:
            if self.print_selection:
                w = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
                h = self.cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
                print "camera capture: width={0}, height={1}".format(w, h)

                x = self.cap.get(cv2.cv.CV_CAP_PROP_EXPOSURE)
                print "camera capture: CV_CAP_PROP_{0}={1}".format('EXPOSURE', x)

                x = self.cap.get(cv2.cv.CV_CAP_PROP_MODE)
                print "camera capture: CV_CAP_PROP_{0}={1}".format('MODE', x)

                x = self.cap.get(cv2.cv.CV_CAP_PROP_FOURCC)
                print "camera capture: CV_CAP_PROP_{0}={1}".format('FOURCC', x)

                x, y = self.refPt[0]
                print "frame: shape={0}, size={1}, Pixel at ({2},{3})".format(
                    str(self.frame.shape), self.frame.size, x, y)
                hh, ss, vv = self.hsv[y, x]
                cv2.setTrackbarPos('Hue', 'mask', hh)
                cv2.setTrackbarPos('Saturation', 'mask', ss)
                cv2.setTrackbarPos('Value', 'mask', vv)
                b = self.frame.item(y, x, 0)
                g = self.frame.item(y, x, 1)
                r = self.frame.item(y, x, 2)

                self.check[:,:] = (b, g, r)

                print "hsv = ({0},{1},{2})".format(hh, ss, vv)
                print "bgr = ({0},{1},{2})".format(b, g, r)

                self.get_angle_to_tgt(x, y)

                # print "mask: shape={0}, size={1}".format(str(self.mask.shape), self.mask.size)
                self.print_selection = False
            cv2.rectangle(self.frame, self.refPt[0], self.refPt[1], (0, self.MAX_UINT, 0), 2)

         # show raw image 
         cv2.imshow('frame', self.frame)

         # show HSV filtered bit mask image
         cv2.imshow('mask', self.mask)

         # show check color window
         cv2.imshow('check', self.check)

         if (self.show_result):
            # Bitwise-AND mask and original image
            self.res = cv2.bitwise_and(self.frame, self.frame, mask = self.mask)
            cv2.imshow('res', self.res)

         key = cv2.waitKey(10) & 0xFF
         if key == ord('q'):
            break
         elif key == ord('0'):
            self.morph_size = 0
         elif key == ord('7'):
            self.morph_size = 7
         elif key == ord('6'):
            self.morph_size = 6
         elif key == ord('5'):
            self.morph_size = 5
         elif key == ord('4'):
            self.morph_size = 4
         elif key == ord('3'):
            self.morph_size = 3
         elif key == ord('2'):
            self.morph_size = 2


      self.cap.release()
      cv2.destroyAllWindows()

      # Save settings as XML
      self.save_settings()

   def create_cv_ui(self):
     # Create slider to set HUE
     cv2.createTrackbar("Hue", 'mask', self.hue, self.MAX_HUE, self.change_hsv_hue)

     # Create slider to set SATURATION
     cv2.createTrackbar("Saturation", 'mask', self.sat, self.MAX_UINT, self.change_hsv_sat)

     # Create slider to set VALUE
     cv2.createTrackbar("Value", 'mask', self.val, self.MAX_UINT, self.change_hsv_val)

     # Create slider to set HUE TOLERANCE
     cv2.createTrackbar("Hue (tol)", 'mask', self.hue_tol, (self.MAX_HUE / 2) + 1, self.change_hsv_hue_tol)

     # Create slider to set SATURATION TOLERANCE
     cv2.createTrackbar("Saturation (tol)", 'mask', self.sat_tol, (self.MAX_UINT / 2) + 1, self.change_hsv_sat_tol)

     # Create slider to set VALUE TOLERANCE
     cv2.createTrackbar("Value (tol)", 'mask', self.val_tol, (self.MAX_UINT / 2) + 1, self.change_hsv_val_tol)

   def change_hsv_hue(self, value):
      self.hue = value

   def change_hsv_sat(self, value):
      self.sat = value

   def change_hsv_val(self, value):
      self.val = value

   def change_hsv_hue_tol(self, value):
      self.hue_tol = value

   def change_hsv_sat_tol(self, value):
      self.sat_tol = value

   def change_hsv_val_tol(self, value):
      self.val_tol = value

   def restore_settings(self):
      tree = etree.parse(self.cfg_fname)
      root = tree.getroot()

      #print (etree.tostring(root, pretty_print=True))

      app = root.find('app')
      if int(app.get('version')) == 1:
          self.restore_settings_v1(root)
      else:
          print "Ignoring config file {:} because version not supported.".format(self.cfg_fname)

   def restore_settings_v1(self, root):
      hsv = root.find('hsv')
      self.hue = int(hsv.get('h'))
      self.sat = int(hsv.get('s'))
      self.val = int(hsv.get('v'))

      hsv_tol = root.find('hsv_tol')
      self.hue_tol = int(hsv_tol.get('h'))
      self.sat_tol = int(hsv_tol.get('s'))
      self.val_tol = int(hsv_tol.get('v'))

   def save_settings(self):

      root = etree.Element("root")
      root.set("name", self.app_name)

      app = etree.SubElement(root, "app")
      app.set("name", self.app_name)
      app.set("version", str(self.app_ver))

      camera = etree.SubElement(root, "camera")
      camera.set("device", str(self.device))
      camera.set("exposure_time", str(self.exposure_time))

      hsv = etree.SubElement(root, "hsv")
      hsv.set("h", str(self.hue))
      hsv.set("s", str(self.sat))
      hsv.set("v", str(self.val))

      hsv_tol = etree.SubElement(root, "hsv_tol")
      hsv_tol.set("h", str(self.hue_tol))
      hsv_tol.set("s", str(self.sat_tol))
      hsv_tol.set("v", str(self.val_tol))

      #print (etree.tostring(root, pretty_print=True))

      cfg = open(self.cfg_fname, 'w')
      cfg.write(etree.tostring(root, pretty_print=True))
      cfg.close

		
def main():

   # @todo: translate USB camera devices output form lsusb to /dev/video# values
   parser = argparse.ArgumentParser(description='Tuner for HSV values for a camera.')
   parser.add_argument('-c', '--camera', type=int, default=0,
                    help='An integer corresponding to /dev/video#, # is the desired camera.')
   parser.add_argument('-e' , '--exposure', type=int, default=-1,
                    help='Camera exposure time in milliseconds.')
   parser.add_argument('-r', '--result', type=bool, default=False,
                    help='Show result frame showing original image anded with mask.')

   args = parser.parse_args()

   ui = False

   tuner = tune_hsv(ui, device = args.camera, exposure_time = args.exposure, show_result = args.result)

   tuner.tune()

if __name__ == '__main__':
   main()
