import sys; sys.path.append('../lib'); sys.path.append('../process') # help python find libs relative to this script
import numpy as np
import pyscellania_wavelets as pw
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import readerLSL
import threading
import data
from  utilities import *

app = QtGui.QApplication([])

imv = pg.ImageView()
imv.show()

wavelet=pw.Morlet
maxscale=4
notes=16
scaling="linear" #or "linear"

reader = readerLSL.ReaderLSL("PPG")
green_chan = data.DataBuffer(reader.getSamplingRate(0), (nextPow2(reader.getSamplingRate(0)*10),))

def updateplot():
  NA = green_chan.values
  # Wavelet transform the data
  cw=wavelet(NA,maxscale,notes,scaling=scaling)
  cwt=cw.getdata()
  scales = cw.getscales()
  power = cw.getpower()
  y = cw.fourierwl*scales
  print "shape cwt:", cwt.shape
  print "nscales:", cw.nscale
  print "four:", cw.fourierwl
  print "scales:", scales
  print "power:", power
  print "y:", y
  # Rotate matrix for plot
  cwt=np.rot90(cwt)
  imv.setImage(abs(cwt))
  #imv.autoRange()
  
def poll_data():
  while True:
    sample, timestamp = reader()
    green_chan.push_value(sample, revert=True)
  
poller = threading.Thread(target=poll_data)
poller.setDaemon(True)
poller.start()

timer = QtCore.QTimer()
timer.timeout.connect(updateplot)
timer.start(100)

QtGui.QApplication.instance().exec_()
