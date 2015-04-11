# Utilities for webcam

import cv,cv2
import config

def init(cam):
  """
  Set resolution and FPS -- test for PS eye, trying to push FPS to limits.
  @param cam: camera number
  @return: an OpenCV cap ready to read from
  """
  print "Init webcam:", cam
  cap = cv.CaptureFromCAM(cam)
  # min def, max FPS
  cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_WIDTH, config.WEBCAM_WIDTH)
  cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FRAME_HEIGHT, config.WEBCAM_HEIGHT)
  cv.SetCaptureProperty(cap,cv.CV_CAP_PROP_FPS, config.MAGIC_FPS)
  
  return cap

def getFPS(cap):
  """
  Stub, return the number of FPS of the webcam
  """
  return config.MAGIC_FPS
  
