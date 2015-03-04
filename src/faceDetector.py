#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cv2, math
import numpy as np

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False

while rval:
    cv2.imshow("preview", frame)
    rval, frame = vc.read()

    hc = cv2.CascadeClassifier("/usr/share/opencv/haarcascades/haarcascade_frontalface_alt2.xml")
    faces = hc.detectMultiScale(frame)
    for face in faces:
        cv2.rectangle(frame, (face[0], face[1]), (face[0] + face[2], face[0] + face[3]), (255, 0, 0), 3)

    key = cv2.waitKey(20)
    if key == 27: # exit on ESC
        break