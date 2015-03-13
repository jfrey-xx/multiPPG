import sys
import utility
import os
from tkMessageBox import *
##
# 
# @brief MessageBox to warn users their is no device
##  
def webcam_error():
	showerror('Webcam', "     No Device Detect\nPlease connect a webcam")
	if utility.system == "linux" or utility.system == "linux2":
		dirs = os.listdir('/dev/v4l/by-id')
		print "List of device : "
		for file in dirs:
			print file ,"\n"
	sys.exit()

def unknown_error():
	showerror('Error', "An Error Occured please try again")

def facedetect_error():
	showinfo('Detection',"Nobody is detect")