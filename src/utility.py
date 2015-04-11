import os
import error
from string import maketrans
import sys
from sys import platform as system

import re

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]


font_title=('arial', 12)#,'italic')
font_other=('arial', 10)#,'bold')

color1='#AED4FA'
color_erreur ='#ff8282'

##
 # @brief This fonction catch webcam name and makes ergonomic
 #  Webcam must be compatible with video4linux 
 # NB: taken from http://www.zarvox.org/shortlog/static/recorder.py
 # @return A table with the different webcam's name
 #
def transWebcamString():
	"""Lets the user pick an external video device to use from /dev/video*"""
	videodevs = ["/dev/" + x for x in os.listdir("/dev/") if x.startswith("video") ]
	
	if len(videodevs) == 1:
		print "Found exactly one video device; using", videodevs[0]
		return videodevs[0]
	if len(videodevs) == 0:
		raise Exception("Found zero video devices - try plugging in a webcam and checking for /dev/video0?")
 
	# Do ridiculous ioctl stuff to extract the name of the device.
	# Here be dragons.
	import fcntl
	_IOC_NRBITS   =  8
	_IOC_TYPEBITS =  8
	_IOC_SIZEBITS = 14
	_IOC_DIRBITS  =  2
 
	_IOC_NRSHIFT = 0
	_IOC_TYPESHIFT =(_IOC_NRSHIFT+_IOC_NRBITS)
	_IOC_SIZESHIFT =(_IOC_TYPESHIFT+_IOC_TYPEBITS)
	_IOC_DIRSHIFT  =(_IOC_SIZESHIFT+_IOC_SIZEBITS)
 
	_IOC_NONE = 0
	_IOC_WRITE = 1
	_IOC_READ = 2
	def _IOC(direction,type,nr,size):
		return (((direction)  << _IOC_DIRSHIFT) |
			((type) << _IOC_TYPESHIFT) |
			((nr)   << _IOC_NRSHIFT) |
			((size) << _IOC_SIZESHIFT))
	def _IOR(type, number, size):
		return _IOC(_IOC_READ, type, number, size)
	def _IOW(type, number, size):
		return _IOC(_IOC_WRITE, type, number, size)
 
	sizeof_struct_v4l2_capability = (16 + 32 + 32 + 4 + 4 + 16)
	VIDIOC_QUERYCAP = _IOR(ord('V'),  0, sizeof_struct_v4l2_capability)
 
	import array
	import struct
	emptybuf = " " * (16 + 32 + 32 + 4 + 4 + 16) # sizeof(struct v4l2_capability)
	buf = array.array('c', emptybuf)
	cameranames = []
	for dev in videodevs:
		camera_dev = open(dev, "rw")
		camera_fd = camera_dev.fileno()
		fcntl.ioctl(camera_fd, VIDIOC_QUERYCAP, buf, 1)
		#print buf[16:48]
		cameranames.append(buf[16:48].tostring())
		bus_info = buf[48:80].tostring()
		camera_dev.close()
	
	chooseargs = ["%s - %s" % (videodevs[i], cameranames[i]) for i in xrange(len(videodevs))]
	chooseargs.sort(key=natural_keys)
	return chooseargs