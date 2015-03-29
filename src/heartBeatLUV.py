# -*- coding: utf-8 -*-

import video # boo! import within an import! no choice if I want to change little
import cv, cv2
import numpy

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

def process(frame):
  #  region of interest
  fitFace_color = (0, 255, 255)
  faces = video.detect_faces_memory(frame)
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
    
    # duplicate region of interest and sho it
    # FIXME: check that len(start:stop) > 0
    roi = frame[fitFace_start[1]:fitFace_stop[1], fitFace_start[0]:fitFace_stop[0]]
    
    skin = video.detectSkin(roi)
    
    if LUV_DEBUG:
      cv.ShowImage(LUV_WINDOW_NAME+"_"+str(faceN), roi)
      cv2.imshow(LUV_WINDOW_NAME+"_skin_"+str(faceN), skin)
      
    # Compute average color over skin
    # wow, lot's of modules and functions to convert roi to matrix to numpy array to get mean color
    meanColor = cv2.mean(numpy.asarray(cv.GetMat(roi)))
    means.append(meanColor)
    
    faceN = faceN+1
  # next step: return as a value and make something out of it
  return means
