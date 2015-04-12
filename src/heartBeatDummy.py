
import video # boo! import within an import! no choice if I want to change little
import cv, cv2
import numpy
from IheartBeat import *

class heartBeatDummy(IheartBeat):
  def __init__(self):
    print "Starting Dummy"
    
  def process(self, frame):
    #  region of interest
    fitFace_color = (0, 255, 255)
    faces = video.detect_faces_filter(frame)
    # we be filled with mean color of each face
    means = []
    # one ID for each face
    faceN = 0
    # Now we can play with faces color!
    for (x,y,w,h) in faces:
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
      # get green channel
      means.append(meanColor[1])
      
      faceN = faceN+1
    # next step: return as a value and make something out of it
    return means

