import multiprocessing
import error
import cv2
import cv

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
    detected = cv.HaarDetectObjects(frame, cascade, storage, 1.2, 2, \
                                    cv.CV_HAAR_DO_CANNY_PRUNING, (100,100))
    if detected:
        for (x,y,w,h),n in detected:
            faces.append((x,y,w,h))
    # lenght = len(faces) # Nomber of faces on camera
    for (x,y,w,h) in faces:
        cv.Rectangle(frame, (x,y), (x+w,y+h), 255)
    return faces

# def getNbFaces():
#     return nbface

##
# @brief The fonction start allows the begining of the capture by OpenCV
# @param cam The number of the webcam must be used
#  
def start(e,cam):
    WINDOW_NAME="Camera {0}".format(cam+1)
    print WINDOW_NAME
    global cap
    cap = cv.CaptureFromCAM(cam)
    cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
    while(True):
        frame = cv.QueryFrame(cap)
        faces = detect_faces(frame)
        nbface = len(faces) #Pour les calculs a venir
        cv.ShowImage(WINDOW_NAME, frame)
        key = cv.WaitKey(20) & 0xFF
        if key == 27: # 27 = ESC
            cv.DestroyWindow(WINDOW_NAME)
            e.clear()
            break

def start_proc(cam):
    global p
    p = multiprocessing.Process(target=start, args=(e,cam))
    p.start()


def stop():
    e.set()
    p.join()
    
