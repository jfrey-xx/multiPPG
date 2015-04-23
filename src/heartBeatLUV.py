# -*- coding: utf-8 -*-

import video
import cv, cv2
import numpy
from IheartBeat import *

# This algo will try to implement in part the work discribed in [Frédéric Bousefsaf. Mesure sans contact de l’activité cardiaque par analyse du flux vidéo issu d’une caméra numérique : extraction de paramètres physiologiques et application à l’estimation du stress. Signal and Image processing. Université de Lorraine, 2014. French.]
# * extract face
# * stabilize with 1€ filter (new)
# * extract skin pixels
# * convert space to luv
# * extract u component
# * get u from skin pixels

# enable or not separate window to show computations
LUV_DEBUG = True
# we don't get any info about webcam yet, so we'll share one debug window per iteration of the algo for each face
LUV_WINDOW_NAME="LUV_debug"

class heartBeatLUV(IheartBeat):
  def __init__(self, **kwargs):
    self.name = "Luv"
    IheartBeat.__init__(self, kwargs)
        
  def process(self,frame, faces):
    #  region of interest
    fitFace_color = (255, 255, 0)
    # we be filled with mean color of each face
    means = []
    # one ID for each face
    faceN = 0
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
      
      if LUV_DEBUG:
	#cv2.imshow(LUV_WINDOW_NAME+"_"+str(faceN), roi)
	#cv2.imshow(LUV_WINDOW_NAME+"_skinMask_"+str(faceN), skinMask)
	cv2.imshow(LUV_WINDOW_NAME+"_skin_"+str(faceN), skin)
    
      # 8bit style
      # convert to luv
      #roi_luv = cv2.cvtColor(roi, cv.CV_BGR2Luv)
      # Compute average color over skin
      #meanLUV = cv2.mean(roi_luv, mask=skinMask)
      
      # convert to 32F and normalize -- should have less data loss
      roi32F = numpy.array(roi, dtype=numpy.float32)/255.
      # convert to luv
      roi_luv = cv2.cvtColor(roi32F, cv2.cv.CV_BGR2Luv)
      meanLUV = cv2.mean(roi_luv, mask=skinMask)
      
      # get U channel
      means.append(meanLUV[1])
      
      faceN = faceN+1
    # next step: return as a value and make something out of it
    return means

