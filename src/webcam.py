# Utilities for webcam

import cv,cv2

# everybody's a PSeye
MAGIC_FPS = 125

def init(cam):
  """
  Set resolution and FPS -- test for PS eye, trying to push FPS to limits.
  @param cam: camera number
  @return: an OpenCV cap ready to read from
  """
  print "Init webcam:", cam
  cap = cv.CaptureFromCAM(cam)
  # min def, max FPS
  cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_WIDTH, 320)
  cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_HEIGHT, 240)
  cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FPS, 1000)
  
  return cap

def getFPS(cap):
  """
  Stub, return the number of FPS of the webcam
  """
  return MAGIC_FPS
  