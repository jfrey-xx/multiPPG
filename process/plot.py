import sys; sys.path.append('../lib') # help python find pylsl relative to this example program
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from threading import Thread
import data

# Default windows size
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class PlotLaunch(Thread):
  """
  One thread to launch vispy app, try not to instanciate this class twice... Call this after Plotter()
  TODO: better mechanism for make a singleton out of this class
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
  Use singleton threads to update regularely a data plot.
  Handle automatically up to 2 dimensions.
  """
  
  # canvas list for main thread
  canvass = []
  
  def __init__(self, shape, title="plot"):
    """
    shape: tuple that contains the dimensions of the plot
    """
    self.title = title
    self.values = np.zeros(shape) # aka "y" for 1D
    self.ndim = len(shape)
    self.labels = None # aka "x" for 1D
     
    # register itself to global canvas list
    global canvass
    self.id = len(Plotter.canvass)
    Plotter.canvass.append(self)

  def set_values(self, values):
    """
    Update plot values
    """
    self.values = values
    self.update_plot_values()
  
  def set_labels(self, labels):
    """
    update labels (eg X axis for 1D)
    """
    self.labels = labels
    self.update_plot_values()

  def update_plot_values(self):
    """
    update values and labels (if any)
    """
    # Update plot data once it's created
    if PlotLaunch.init:
      line = PlotLaunch.lines[self.id]
      # do not care about X axis if no info about it
      if  self.labels == None:
        line.setData(self.values)
      else:
        line.setData(y=self.values, x=self.labels)
      p =  PlotLaunch.ps[self.id]
      p.enableAutoRange('xy')
      
