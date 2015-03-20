import sys; sys.path.append('../lib') # help python find pylsl relative to this example program
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from threading import Thread

# Default windows size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class PlotLaunch(Thread):
  """
  One thread to launch vispy app, try not to instanciate this class twice... Call this after Plotter()
  """
  # one flag to make sure we are the One, another to sync with Plotter
  singleton = False
  init = False
  # different list to make data accesible by Plotter and also juste for the sake of keeping windows ref in memory
  lines = []
  ps = []
  wins = []
  
  def __init__(self):
    Thread.__init__(self)
    global singleton
    assert(PlotLaunch.singleton == False)
    PlotLaunch.singleton = True
    self.daemon = True
    self.start()
    
  def run(self):
    app = QtGui.QApplication([])
    
    # 
    global lines, ps, wins
    for canvas in Plotter.canvass:
        print "New canvas!"
        win =  pg.GraphicsWindow(title=canvas.title)
        win.resize(WINDOW_WIDTH,WINDOW_HEIGHT)
        PlotLaunch.wins.append(win)
        p = win.addPlot(title=canvas.title)
        PlotLaunch.ps.append(p)
        line = p.plot(pen='y')
        PlotLaunch.lines.append(line)
        
    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)
    
    global init
    PlotLaunch.init = True
    QtGui.QApplication.instance().exec_()

class Plotter():
  """
  Use singleton threads to update regularely a data plot
  """
  
  # canvas list for main thread
  canvass = []
  
  def __init__(self, sample_rate, window_length=1, polling_interval=0.1, title="plot"):
    """
    sample_rate: at which rate values will be sent (in Hz). NB: will be cast to int!
    window_length: time length of plot (in seconds)
    polling_interval: will redraw plot every XX seconds
    """
    self.polling_interval = polling_interval
    self.sample_rate = int(sample_rate)
    self.queue_size = self.sample_rate*window_length
    self.title = title
    
    # fifo for temporal filter
    self.values =  [0]*self.queue_size
    
    global canvass
    self.id = len(Plotter.canvass)
    Plotter.canvass.append(self)

  def push_value(self, value):
      """
      One new value for the plot
      """
      # One goes out, one goes in
      self.values.pop(0)
      self.values.append(value)
      # Update plot data once it's created
      if PlotLaunch.init:
        line = PlotLaunch.lines[self.id]
        line.setData(self.values)
        p =  PlotLaunch.ps[self.id]
        p.enableAutoRange('xy') 


        
    
