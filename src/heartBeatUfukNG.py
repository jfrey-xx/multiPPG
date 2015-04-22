# -*- coding: utf-8 -*-
import sys; sys.path.append('../process') # help python find // files relative to this script
import video
import cv, cv2
import numpy
from IheartBeat import *
# from process
from data import *
from utilities import *
import plot

# enable or not separate window to show computations
DEBUG = True
# we don't get any info about webcam yet, so we'll share one debug window per iteration of the algo for each face
WINDOW_NAME="UFUKNG_debug"

# FIXME: WIP, at the moment return RGB, could compute orthogonal vector here

class heartBeatUfukNG(IheartBeat):
  def __init__(self, fps, *args, **kwargs):
    self.name = "Ufuk NG"
    self.fps = fps
    IheartBeat.__init__(self, args, kwargs)
    # buffers for the 3 components -- FIXME: only one face
    self.R_chan = SignalBuffer(sample_rate=fps, window_length=3)
    self.G_chan = SignalBuffer(sample_rate=fps, window_length=3)
    self.B_chan = SignalBuffer(sample_rate=fps, window_length=3)
    
  def process(self, frame, faces):
    #  region of interest
    fitFace_color = (255, 255, 0)
    # one ID for each face
    faceN = 0
    
    meanRGB = []
    
    # Now we can play with faces color!
    for (x,y,w,h) in faces:
      # narrower rectangle for effective face, show in green
      fitFace_start = (x, y)
      fitFace_stop =  (x+w, y+h)
      cv.Rectangle(frame, fitFace_start, fitFace_stop, fitFace_color, 2)
      
      # duplicate region of interest and show it
      # FIXME: check that len(start:stop) > 0
      roi = frame[fitFace_start[1]:fitFace_stop[1], fitFace_start[0]:fitFace_stop[0]]
      
      # conver roi to cv2
      roi = numpy.asarray(cv.GetMat(roi))
      # extract mask and skin
      skinMask = video.detectSkin(roi)
      skin = cv2.bitwise_and(roi, roi, mask = skinMask)
      
      if DEBUG:
	cv2.imshow(WINDOW_NAME+"_skin_"+str(faceN), skin)
      
      meanRGB = cv2.mean(roi, mask=skinMask)
      
      # get U channel
      self.R_chan.push_value(meanRGB[0])
      self.G_chan.push_value(meanRGB[1])
      self.B_chan.push_value(meanRGB[2])
      
      faceN = faceN+1
      break # we're rude, don't care about more than 1 face
    
    # detrend
    #R_detrend = detrend(self.R_chan.values)
    #G_detrend = detrend(self.G_chan.values)
    #B_detrend = detrend(self.B_chan.values)
    
    # formula 2, aka algo from "Shadinrakar et al, used to stretch the RGB signal and combine the three color channels to give stronger resultant signal"
    
    #X1 = R_detrend - G_detrend
    #X2 = R_detrend + G_detrend - 2*B_detrend
    #X1 = X1 - np.mean(X1)
    #X2 = X2 - np.mean(X2)
    #X2 = (np.std(X1)/np.std(X2))*X2
    #HB = X1 - X2
    #HB = HB / np.std(HB)
    
    # next step: return as a value and make something out of it
    return meanRGB

