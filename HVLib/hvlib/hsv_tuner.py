
import cv2
import os

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

def main():
   default = set_camera_defaults(1,100)
   cap = default.get_cap()

   while True:
      ret, frame = cap.read()
      cv2.imshow("Capture",frame)

      ch = 0xFF & cv2.waitKey(1)
      if ch == 27:
          break




if __name__ == '__main__':
   main()
