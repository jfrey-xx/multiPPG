import multiprocessing
import error
import sys
import cv2
import cv
import heartBeatPPG, heartBeatDummy
import numpy
import interface
import streamerLSL
import sample_rate

HAAR_CASCADE_PATH = "../sources/haarcascades/haarcascade_frontalface_alt.xml"
e = multiprocessing.Event()
p = None
cascade = cv2.CascadeClassifier(HAAR_CASCADE_PATH)

# number of values sent to streamer, ie number of persons x RGBA ... bold move to say only one at the moment
LSL_NB_CHANNELS = 4
LSL_SAMPLE_RATE = 30 # 30 FPS... maybe not, FIXME: find a reliable way to discover webcam FPS

# set "1" to track face every frame, 2 every two frames and so on
TRACKING_RATE=5
frame_count = 0

##
 # @brief detect_face use the cascade to calculate the square of the faces
 # @param frame The window create by OpenCV
 # @return faces This table contain the different square. 
 # The nomber of square depend of the number of users see by the webcam
 #  
def detect_faces(frame):
    global frame_count
    faces = ()
    if not frame_count % TRACKING_RATE:
        # convert frame to cv2 format, and to B&W to speedup processsing (this cv/cv2 mix drives me crazy)
        # FIXME: prone to bug if webcam already B&W
        gray = cv2.cvtColor(numpy.array(cv.GetMat(frame)), cv2.COLOR_BGR2GRAY)

        try:
            # NB: CV_HAAR_SCALE_IMAGE more optimized than CV_HAAR_DO_CANNY_PRUNING
            faces = cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=2, flags=cv.CV_HAAR_SCALE_IMAGE, minSize=(100, 100))
        except cv.error:
            error.unknown_error()

        # lenght = len(faces) # Nomber of faces on camera
        for (x,y,w,h) in faces:
            cv.Rectangle(frame, (x,y), (x+w,y+h), 255)
            cv.Rectangle(frame, (x+w/2, y+h/6), (x+w/2, y+h/6), (0, 0, 255), 2)
    frame_count = frame_count + 1
    return faces

# def getNbFaces():
#     return nbface


##
# @brief The fonction detect the skin with the color
# @param frame The window create by OpenCV
# @return skin The table with the value of the skin
# 
def detectSkin(frame):

    # min et max de l'espace couleur YCrCb
    # 77 < Cb 127
    # 133 < Cr < 173
    min_YCrCb = numpy.array([0,133,77],numpy.uint8)
    max_YCrCb = numpy.array([255,173,127],numpy.uint8)

    # conversion

    min_YCrCb= cv.fromarray(min_YCrCb,True)
    max_YCrCb= cv.fromarray(max_YCrCb,True)
    print "[Detect skin] Max : ",max_YCrCb
    print "[Detect skin] Min : ",min_YCrCb
    imageYCrCb = cv.CvtColor(frame,frame,cv2.COLOR_BGR2YCR_CB)
    print "[Detect skin] image : ",imageYCrCb
    
    # 1 si le pixel est compris entre min et max
    # 0 sinon
    skin = cv.InRange(imageYCrCb,min_YCrCb,max_YCrCb,imageYCrCb)
    print "[Detect skin] skin : ",skin
    return skin




##
# @brief The fonction start allows the begining of the capture by OpenCV
# @param cam The number of the webcam must be used
#  
def start(e,cam,tab,algo):
    WINDOW_NAME="Camera {0}".format(tab[cam])
    global cap
    cap = cv.CaptureFromCAM(cam)
    cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
    r = [0, 0]
    g = [0, 0]
    b = [0, 0]

    # Init network streamer
    streamer = streamerLSL.StreamerLSL(LSL_NB_CHANNELS,LSL_SAMPLE_RATE)

    # Init the thread that will monitor FPS
    monit = sample_rate.PluginSampleRate()
    monit.activate()

    while(True):
        
        # init streamed value with default (make a tuple out of it, as with dummy)
        values = [0] * LSL_NB_CHANNELS,

        # careful to what is caught, block to big could occult genuine bugs (I'm not saying I mispelled a variable, of course not!)
        try:
            frame = cv.QueryFrame(cap)
            # nbface = len(faces) #Pour les calculs a venir
        except Exception : # V4L error ... [TODO] VIDIOC_DQBUF
            error.webcam_error()
            break

######################## Algo CHOICE #########################
        if algo == 0:
            print "Algo : PPG"
            toto='coucou'
            sendToInterface(toto)
            # skin = detectSkin(frame)
            # heartBeatPPG.ppgFunction(r, g, b, face, frame)
        if algo == 1:
            print "Algo : Eularian"
        if algo == 2:
            #print "Algo : Dummy"
            #sendToInterface("dummy") # what 4?
            values = heartBeatDummy.process(frame)
        
        # TODO: adapt values size to NB_CHANNELS
        streamer(values)

        # compute FPS
        monit()

        # delay when we show frame so that algo could add information
        cv.ShowImage(WINDOW_NAME, frame)

######################## Wait KEY #########################
        key = cv.WaitKey(20) & 0xFF
        if key == 27: # 27 = ESC
            cv.DestroyWindow(WINDOW_NAME)
            e.clear()
            break


def start_proc(cam,tab,algo):
    global p
    p = multiprocessing.Process(target=start, args=(e,cam,tab,algo))
    p.start()


def stop():
    cv.DestroyWindow(WINDOW_NAME)
    e.set()
    p.join()
    
def sendToInterface(test):
    interface.actualiseLabel(test)
