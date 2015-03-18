
import video # boo! import within an import! no choice if I want to change little
import cv

# one static variable to remember last faces in case of tracking disruption, one dot by default
# TODO: should be handled by video.detect_faces
last_faces = [0,0,1,1]

def process(frame):
  global last_faces
  print "got it"
  faces = video.detect_faces(frame)
  # by default: greet color for faces
  fitFace_color = (0, 255, 0)
  print faces
  if faces != []:
    last_faces = faces
  else:
    # "red" flag
    fitFace_color = (0, 255, 255)
    
  # Now we can play with faces color!
  for (x,y,w,h) in last_faces:
    # narrower rectangle for effective face, show in green
    fitFace_start = (x+w/4, y+h/6)
    fitFace_stop =  (x+3*w/4, y+5*h/6)
    cv.Rectangle(frame, fitFace_start, fitFace_stop, fitFace_color, 2)