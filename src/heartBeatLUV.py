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


# one static variable to remember last faces in case of tracking disruption, one dot by default
# TODO: should be handled by video.detect_faces
last_faces = [[0,0,128,128]]

def process(frame):
  global last_faces
  # TODO: use filter ala One Euro Filter to stabilize tracking
  faces = video.detect_faces(frame)
  # by default: greet color for faces
  fitFace_color = (0, 255, 0)
  if faces != ():
    last_faces = faces
  else:
    # "red" flag
    fitFace_color = (0, 255, 255)
  # we be filled with mean color of each face
  means = []
  # one ID for each face
  faceN = 0
  # Now we can play with faces color!
  for (x,y,w,h) in last_faces:
    # narrower rectangle for effective face, show in green
    fitFace_start = (x+w/4, y+h/6)
    fitFace_stop =  (x+3*w/4, y+5*h/6)
    cv.Rectangle(frame, fitFace_start, fitFace_stop, fitFace_color, 2)
    
    # duplicate region of interest and sho it
    # FIXME: check that len(start:stop) > 0
    roi = frame[fitFace_start[1]:fitFace_stop[1], fitFace_start[0]:fitFace_stop[0]]
    
    # Compute average color
    # wow, lot's of modules and functions to convert roi to matrix to numpy array to get mean color
    meanColor = cv2.mean(numpy.asarray(cv.GetMat(roi)))
    means.append(meanColor)
    
    faceN = faceN+1
  # next step: return as a value and make something out of it
  return means

