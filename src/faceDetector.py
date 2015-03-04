# #!/usr/bin/env python
# # -*- coding: utf-8 -*-

# import cv2, math
# import numpy as np

# cv2.namedWindow("preview")
# vc = cv2.VideoCapture(0)

# if vc.isOpened(): # try to get the first frame
#     rval, frame = vc.read()
# else:
#     rval = False

# while rval:
#     cv2.imshow("preview", frame)
#     rval, frame = vc.read()

#     hc = cv2.CascadeClassifier("/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml")
#     faces = hc.detectMultiScale(frame)
#     for face in faces:
#         cv2.rectangle(frame, (face[0], face[1]), (face[0] + face[2], face[0] + face[3]), (255, 0, 0), 3)

#     key = cv2.waitKey(20)
#     if key == 27: # exit on ESC
#         break

#! /usr/bin/env python
#-*- coding: utf-8 -*-
 
# Python binding for OpenCV
import cv2
 
HAAR_CASCADE_PATH = "../sources/haarcascades/haarcascade_frontalface_alt.xml"
CAMERA_INDEX = 1
WINDOW_NAME = "Real time face detection with Python and OpenCV"
 
# def detect_faces(image):
#     """
#     Detect face(s) in an image.
#     """
#     faces = []
#     return faces
 
def detector(feed,frame):
    # Point of entry in execution mode
    # cv.NamedWindow(WINDOW_NAME, cv.CV_WINDOW_AUTOSIZE)
    # cam = cv.CaptureFromCAM(CAMERA_INDEX)
    storage = cv2.cv.CreateMemStorage()
    cascade = cv2.cv.Load(HAAR_CASCADE_PATH)
    faces = []
    while True: 
        detected = cv2.HaarDetectObjetcs(image, cascade, storage)
        if detected:
            for (x,y,w,h),n in detected:
                faces.append((x,y,w,h))
        for (x,y,w,h) in faces:
            cv2.Rectangle(feed, (x,y), (x+w,y+h), 255)
 
        cv2.ShowImage(frame, feed)