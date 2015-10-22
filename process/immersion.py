import visualization
import numpy as np
from threading import Thread

# let's go virtual 
class World(Thread):
  def __init__(self, values):
    Thread.__init__(self)
    self.values = values
    values_shape = np.shape(values)
    print "World input shape:", values_shape 
    self.xDim = values_shape[0]
    self.yDim = values_shape[1]

  def run(self):
    "Launching World"
    panda3dObj=visualization.MyTapper(self.values, self.xDim, self.yDim)
    while True:
      panda3dObj.step()

class Immersion():
  # @polling_time: will print FPS every xx seconds
  def __init__(self, values):
    """
    name: if set, will be added in output
    """
    self.world = World(values)
    
  # update counters value
  def __call__(self):
    pass
        
  # Instanciate "monitor" thread
  def activate(self):
   self.world.daemon = True
   self.world.start()

