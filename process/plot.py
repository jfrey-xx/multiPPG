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
  plots = [] # the object that represents the value (lines or image depending on dimension)
  figures = [] # the whole figue (with axis)
  wins = [] # figure's windows, that won't be used, we keep a ref to prevent system to destroy objects automatically
  def __init__(self):
    Thread.__init__(self)
    global singleton
    assert(PlotLaunch.singleton == False)
    PlotLaunch.singleton = True
    self.daemon = True
    self.start()
    
  def run(self):
    app = QtGui.QApplication([])
    
    # populate plots and figures arrays
    global plots, figures, wins
    for canvas in Plotter.canvass:
        # 1D: a plot
        if canvas.ndim == 1:
            win =  pg.GraphicsWindow(title=canvas.title)
            PlotLaunch.wins.append(win) # keep a ref in mem against garbage collector
            win.resize(WINDOW_WIDTH,WINDOW_HEIGHT)
            fig = win.addPlot(title=canvas.title)
            PlotLaunch.figures.append(fig)
            plot = fig.plot(pen='y')
            PlotLaunch.plots.append(plot)
        # 2D: a raster (an image)
        elif canvas.ndim == 2:
            win = QtGui.QMainWindow()
            imv = pg.ImageView()
            # for an image there is no such separation as win/figure/plot (?), duplicate entries to keep same order
            PlotLaunch.wins.append(win)
            #PlotLaunch.wins.append(imv)
            PlotLaunch.figures.append(imv)
            PlotLaunch.plots.append(imv)
            #imv.show()
            win.setCentralWidget(imv)
            win.resize(WINDOW_WIDTH,WINDOW_HEIGHT)
            win.show()
            win.setWindowTitle(canvas.title)
        else:
            raise NameError("PlotNDimNotSupported")
        
    # Enable antialiasing for prettier plots
    pg.setConfigOptions(antialias=True)
    
    global init
    PlotLaunch.init = True
    QtGui.QApplication.instance().exec_()

  @classmethod
  def update_plot(cls,canvas):
    """
    A Plotter object asks the charming manager to update itself
    @param canvas: instance of Plotter requesting
    """
    # Update plot data once it's created
    if cls.init:
      # 1D plot
      if canvas.ndim == 1:
        plot = cls.plots[canvas.id]
        # do not care about X axis if no info about it
        if  canvas.labels == None:
          plot.setData(canvas.values)
        else:
          plot.setData(y=canvas.values, x=canvas.labels)
        fig = cls.figures[canvas.id]
        fig.enableAutoRange('xy')
      # 2D image
      elif canvas.ndim == 2:
        # Rotate matrix to orientate correctly
        values=np.rot90(canvas.values)
        fig = cls.figures[canvas.id]
        fig.setImage(values)
      else:
         raise NameError("PlotNDimNotSupported")

            
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
    ask PlotLaunch to update values and labels (if any)
    """
    PlotLaunch.update_plot(self)

