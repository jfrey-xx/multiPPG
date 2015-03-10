import os
import error
from string import maketrans
import sys
from sys import platform as system

# system represente l OS 
# 
# if _platform == "linux" or _platform == "linux2":
    # linux
# elif _platform == "darwin":
    # OS X
# elif _platform == "win32":
    # Windows...
# 
# 

font_title=('arial', 12)#,'italic')
font_other=('arial', 10)#,'bold')

color1='#AED9FA'
color_erreur ='#ff8282'

##
 # @brief This fonction catch webcam name and makes ergonomic
 #  Webcam must be compatible with video4linux 
 # @return A table with the different webcam's name
 #
def transWebcamString():
    path = '/dev/v4l/by-id'
    tab = []
    if not os.path.exists(path):
        return tab
    else :
        dirs = os.listdir(path)
        chain = str()
        i=0
        for file in dirs:
            chain = file
            table = maketrans('_',' ')
            chain=chain.translate(table, ' ')
            chain=chain.replace('usb-','')
            chain=chain.replace('-video-index0','')
            if i==0:
            	chain=chain.replace(' ','')
            tab.append(chain)  
            i+=1
        return tab