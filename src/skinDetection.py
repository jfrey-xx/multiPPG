import cv
import cv2
import numpy

def detectSkin(frame):

    # min et max de l'espace couleur YCrCb
    # 77 < Cb 127
    # 133 < Cr < 173
    min_YCrCb = numpy.array([0,133,77],numpy.uint8)
    max_YCrCb = numpy.array([255,173,127],numpy.uint8)

    # conversion
    imageYCrCb = cv.CvtColor(frame,frame,cv2.COLOR_BGR2YCR_CB)
    
    # 1 si le pixel est compris entre min et max
    # 0 sinon
    skin = cv.InRange(imageYCrCb,min_YCrCb,max_YCrCb,imageYCrCb)

    return skin