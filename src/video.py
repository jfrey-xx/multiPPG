# -*- coding: utf-8 -*-

import sys; sys.path.append('../lib') # help python find 1€ filter relative to this example program
import multiprocessing
import error
import sys
import cv2
import cv
import heartBeatDummy, heartBeatLUV, heartBeatUfukNG
import numpy
import interface
import streamerLSL
import sample_rate
import timeit
import OneEuroFilter
import webcam
import config

# NB: this module is process safe, but not thread safe (eg face detection)

HAAR_CASCADE_PATH = "../external/haarcascades/haarcascade_frontalface_alt.xml"
e = multiprocessing.Event()
p = None
cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

# help face detection to keep track of TRACKING_RATE
frame_count = 0

# Init later when we'll know about FPS
euro_filters = None

def init_euro_filters(nbUers, fps):
  """
  using 1 euro filter to stabilize head
  @param fps: in Hz, sample rate of webcam
  FIXME: one person at the moment
  """
  euro1_config = {
      'freq': fps, # Hz
      'mincutoff': 0.01,
      'beta': 0.01,
      'dcutoff': 1.0
      }
  global euro_filters
  # init filters, X/Y/W/H per persson
  euro_filters = [OneEuroFilter.OneEuroFilter(**euro1_config) for _ in range(4)]

# keeps track of face detection status
detected_faces = [0]

##
 # @brief detect_face use the cascade to calculate the square of the faces
 # @param frame The window create by OpenCV
 # @return faces This table contain the different square. 
 # The nomber of square depend of the number of users see by the webcam -- capped by maximum set
 #  
def detect_faces(frame):
    global frame_count, detected_faces
    faces = ()
    if not frame_count % config.TRACKING_RATE:
        # convert frame to cv2 format, and to B&W to speedup processsing (this cv/cv2 mix drives me crazy)
        # FIXME: prone to bug if webcam already B&W
        gray = cv2.cvtColor(numpy.array(cv.GetMat(frame)), cv2.COLOR_BGR2GRAY)

        try:
            # NB: CV_HAAR_SCALE_IMAGE more optimized than CV_HAAR_DO_CANNY_PRUNING
            faces = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=2, flags=cv.CV_HAAR_SCALE_IMAGE, minSize=(100, 100))
        except cv.error:
            error.unknown_error()
    if len(faces) > 0:
        faces = faces[0:config.NB_FACES]
        detected_faces = [1]
    # set detection flag to false only if we actually tried something
    elif not frame_count % config.TRACKING_RATE:
        detected_faces = [0]
    frame_count = frame_count + 1
    return faces

# one static variable to remember last faces in case of tracking disruption, one small patch by default
last_faces = [[0,0,128,128]]

def detect_faces_memory(frame):
  """
  same as detect_faces, remember last position of faces in case there's not detected in some frames
  FIXME: only one face
  """
  global last_faces
  faces = detect_faces(frame)
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
  # eye candy to know when tracking is off
  for (x,y,w,h) in last_faces:
    cv.Rectangle(frame, (x,y), (x+w,y+h), fitFace_color)
    
  return last_faces

def detect_faces_filter(frame):
  """
  Use 1euro filter to stabilize frames
  FIXME: handle only one face
  """
  tick = timeit.default_timer()
  faces = detect_faces_memory(frame) # will at least return one face
  
  if len(faces) > 0 and euro_filters != None:
    # smooth x,y,w,h in first face
    k = min(len(euro_filters), len(faces[0]))
    for i in range(k):
      faces[0][i] = int(round(euro_filters[i](faces[0][i],tick)))
     
  return faces
  
# def getNbFaces():
#     return nbface


##
# @brief The fonction detect the skin with the color
# @param frame The window create by OpenCV (ov2 format)
# @return skin The table with the value of the skin (ov2 format)
# 
# FIXME: prone to bug if webcam already B&W
def detectSkin(frame):
    # convert frame to HSV
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
    # apply blur to remove noise
    frame_hsv = cv2.GaussianBlur(frame_hsv,(5,5),0)
    # TODO: check more complicated (and smoothed) methods: http://www.pyimagesearch.com/2014/08/18/skin-detection-step-step-example-using-python-opencv/
    
    # min et max de l'espace couleur YCrCb
    # Y > 80
    # 77 < Cb 127
    # 133 < Cr < 173
    min_YCrCb = numpy.array([80,133,77],numpy.uint8)
    max_YCrCb = numpy.array([255,173,127],numpy.uint8)
    
    skin = cv2.inRange(frame_hsv, min_YCrCb, max_YCrCb)

    return skin

##
# @brief The fonction start allows the begining of the capture by OpenCV
# @param cam The number of the webcam must be used
#  
def start(e,cam,algo,userID):
    WINDOW_NAME="Camera ID" + str(cam)
    cap = webcam.init(cam)
    
    cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
    
    fps = webcam.getFPS(cap)
    print "FPS:", fps
    
    # init smooth tracking
    init_euro_filters(config.NB_FACES,fps)
    
    # Init network streamer for PPG values
    streamerPPG = streamerLSL.StreamerLSL(config.LSL_PPG_NB_CHANNELS*config.NB_FACES,fps,"PPG",userID)
    # Same for face tracking
    streamerFace = streamerLSL.StreamerLSL(config.LSL_FACE_NB_CHANNELS*config.NB_FACES,fps,"face",userID)
    # Whether or not face is detected
    streamerDetection = streamerLSL.StreamerLSL(config.NB_FACES,fps,"detection",userID)
    
    algoHR = None
    
    ######################## Algo CHOICE #########################
    if algo == 0:
	algoHR = heartBeatDummy.heartBeatDummy()
    elif algo == 1:
	algoHR = heartBeatLUV.heartBeatLUV()
    elif algo == 2:
	algoHR = heartBeatUfukNG.heartBeatUfukNG(config.MAGIC_FPS)
    else:
	print "Error: unknown algorithm"
	return

    monit_name = "cam" +  str(cam) + "_algo" + str(algo) + "_user" + str(userID)
    # Init the thread that will monitor FPS
    monit = sample_rate.PluginSampleRate(name=monit_name)
    monit.activate()

    while(True):
        
        # init streamed value with default (make a tuple out of it, as with dummy)
        values = [0] * config.LSL_PPG_NB_CHANNELS,

        # careful to what is caught, block to big could occult genuine bugs (I'm not saying I mispelled a variable, of course not!)
        try:
            frame = cv.QueryFrame(cap)
            # nbface = len(faces) #Pour les calculs a venir
        except Exception : # V4L error ... [TODO] VIDIOC_DQBUF
            error.webcam_error()
            break
        
        faces = detect_faces_filter(frame)
        values = algoHR.process(frame,faces)

        # PPG -- clamp values to lsl channels number
        lsl_values = numpy.zeros(config.LSL_PPG_NB_CHANNELS)
        k = min(config.LSL_PPG_NB_CHANNELS, len(values))
        for i in range(k):
	  lsl_values[i] = values[i]
        streamerPPG(lsl_values)
        
        # FACES -- clamp values as well, flatten face detection
        lsl_faces = numpy.zeros(config.LSL_FACE_NB_CHANNELS)
        flat_faces = [item for sublist in faces for item in sublist] # lsl doesn't go well with list of list
        k = min(config.LSL_FACE_NB_CHANNELS, len(flat_faces))
        for i in range(k):
	  lsl_faces[i] = flat_faces[i]
        streamerFace(lsl_faces)
        
         # DETECTION -- clamp values as well, flatten face detection
        lsl_detection = numpy.zeros(config.NB_FACES)
        k = min(config.NB_FACES, len(detected_faces))
        for i in range(k):
	  lsl_detection[i] = detected_faces[i]
        streamerDetection(lsl_detection)

        # compute FPS
        monit()

        # delay when we show frame so that algo could add information
        cv.ShowImage(WINDOW_NAME, frame)

######################## Wait KEY #########################
        key = cv.WaitKey(1) & 0xFF
        if key == 27: # 27 = ESC
            cv.DestroyWindow(WINDOW_NAME)
            e.clear()
            break


def start_proc(cam,algo,userID):
    try:
      userID = int(userID)
    except:
      print "Error: could not parse userID -- ", userID
      return
    
    print "Webcam selected:", cam
    print "Algo selected:", algo
    print "User ID:", userID
      
    global p
    p = multiprocessing.Process(target=start, args=(e,cam,algo,userID))
    p.start()

def stop():
    # FIXME: it's not how you stop background threads
    cv.DestroyWindow(WINDOW_NAME)
    e.set()
    p.join()
    
