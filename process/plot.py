import sys; sys.path.append('../lib') # help python find mtKinter relative to this example program
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

from threading import Thread


class Plotter(Thread):
  """
  Use threads to update regularely a data plot
  FIXME: buggy because of Tkinter (on close and one plot only ??)
  """
  
  def __init__(self, sample_rate, window_length=1, polling_interval=0.1):
    """
    sample_rate: at which rate values will be sent (in Hz). NB: will be cast to int!
    window_length: time length of plot (in seconds)
    polling_interval: will redraw plot every XX seconds
    """
    Thread.__init__(self)
    self.polling_interval = polling_interval
    self.sample_rate = int(sample_rate)
    self.queue_size = self.sample_rate*window_length
    
    # fifo for temporal filter
    self.values =  [0]*self.queue_size
    # for plot: X
    self.x=range(0,self.queue_size)

    self.app = QtGui.QApplication([])
    
    win = pg.GraphicsWindow(title="Basic plotting examples")
    win.resize(1000,600)
    win.setWindowTitle('pyqtgraph example: Plotting')
    
    self.p6 = win.addPlot(title="Updating plot")
    self.curve = self.p6.plot(pen='y')
    self.data = np.random.normal(size=(10,1000))
    self.ptr = 0
    
    self.daemon = True
    self.running = True
    self.start()
    
    
    
    
  def run(self):
    #QtGui.QApplication.instance().exec_()
    while True:
      pass
      #self.curve.setData(self.data[self.ptr%10])
      #if self.ptr == 0:
      #  self.p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
      #self.ptr += 1


        
  def push_value(self, value):
      """
      One new value for the plot
      """
      #self.curve.setData(self.data[self.ptr%10])
      #if self.ptr == 0:
      #  self.p6.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
      #self.ptr += 1
        
      # One goes out, one goes in
      self.values.pop(0)
      self.values.append(value)
        
    
