from vispy import app, scene
from threading import Thread
import numpy as np

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

class PlotLaunch(Thread):
  """
  One thread to launch vispy app, try not to instanciate this class twice...
  """
  init = False
  def __init__(self):
    Thread.__init__(self)
    global init
    assert(PlotLaunch.init == False)
    PlotLaunch.init = True
    self.daemon = True
    self.start()
    
  def run(self):
    for canvas in Plotter.canvass:
      canvas.show()
    app.run()

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
    
    # init canvas, add to main list
    self.canvas = scene.SceneCanvas(size=(WINDOW_WIDTH, WINDOW_HEIGHT), keys='interactive', title=self.title)
    global canvass
    Plotter.canvass.append(self.canvas)
    
    # init content: one line
    self.pos = np.empty((self.queue_size, 2), np.float32)
    self.pos[:, 0] = np.linspace(0, WINDOW_WIDTH, self.queue_size)
    self.pos[:, 1] = np.random.normal(scale=50, loc=30, size=self.queue_size)
    self.line = scene.visuals.Line(pos=self.pos, parent=self.canvas.scene)

  def push_value(self, value):
      """
      One new value for the plot
      """
      # One goes out, one goes in
      self.values.pop(0)
      self.values.append(value)
      # update once line created by new thread
      if self.line != None:
        # convert to numpy array
        values_np = np.array(self.values)
        ymin = min(values_np)
        ymax = max(values_np)
        delta = ymax-ymin+1
        # autoscale and invert axis
        values_np = (values_np - ymin)
        values_np = values_np * (WINDOW_HEIGHT/delta) * -1 + WINDOW_HEIGHT
        #values_np = (values_np - ymin) * (WINDOW_HEIGHT/delta) * (-1) 
        
        self.pos[:, 1] = values_np
        self.line.set_data(self.pos)
        

        
    
