import multiprocessing
import error
import sys
# import cv2
import cv
import heartBeatPPG
import numpy

HAAR_CASCADE_PATH = "../sources/haarcascades/haarcascade_frontalface_alt.xml"
e = multiprocessing.Event()
p = None

##
 # @brief detect_face use the cascade to calculate the square of the faces
 # @param frame The window create by OpenCV
 # @return faces This table contain the different square. 
 # The nomber of square depend of the number of users see by the webcam
 #  
def detect_faces(frame):
    storage = cv.CreateMemStorage()
    cascade = cv.Load(HAAR_CASCADE_PATH)
    faces = []
    try:
        detected = cv.HaarDetectObjects(frame, cascade, storage, 1.2, 2,cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))
    except cv.error:
        unknown_error()
    if detected:
        for (x,y,w,h),n in detected:
            faces.append((x,y,w,h))
    # lenght = len(faces) # Nomber of faces on camera
    for (x,y,w,h) in faces:
        cv.Rectangle(frame, (x,y), (x+w,y+h), 255)
        cv.Rectangle(frame, (x+w/2, y+h/6), (x+w/2, y+h/6), (0, 0, 255), 2)
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
    print max_YCrCb
    print min_YCrCb
    imageYCrCb = cv.CvtColor(frame,frame,cv2.COLOR_BGR2YCR_CB)
    print imageYCrCb
    
    # 1 si le pixel est compris entre min et max
    # 0 sinon
    skin = cv.InRange(imageYCrCb,min_YCrCb,max_YCrCb,imageYCrCb)

    return skin




##
# @brief The fonction start allows the begining of the capture by OpenCV
# @param cam The number of the webcam must be used
#  
def start(e,cam):
    WINDOW_NAME="Camera {0}".format(cam+1)
    global cap
    cap = cv.CaptureFromCAM(cam)
    cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
    r = [0, 0]
    g = [0, 0]
    b = [0, 0]
    while(True):
        try:
            frame = cv.QueryFrame(cap)
            faces = detect_faces(frame)
            # nbface = len(faces) #Pour les calculs a venir
            cv.ShowImage(WINDOW_NAME, frame)
            skin = detectSkin(frame)
            key = cv.WaitKey(20) & 0xFF
            if key == 27: # 27 = ESC
                cv.DestroyWindow(WINDOW_NAME)
                e.clear()
                break
            if key == 115 : # 115 = s
                heartBeatPPG.ppgFunction(r, g, b, face, frame)
        except cv.error:
            error.webcam_error()

def start_proc(cam):
    global p
    p = multiprocessing.Process(target=start, args=(e,cam))
    p.start()


def stop():
    e.set()
    p.join()
    
