import plot
import numpy as np

class DataBuffer():
  """
  Data structure to hold, process and plot signals
  """
  
  def __init__(self, sample_rate, window_length=1, attach_plot = False, name="data"):
    """
    sample_rate: at which rate values will be sent (in Hz). NB: will be cast to int!
    window_length: time length of plot (in seconds)
    plot: attach a plot or not
    name: used as title for the plot
    """
    
    self.sample_rate = int(sample_rate)
    self.queue_size = self.sample_rate*window_length
    self.name = name
    
    # fifo for temporal filter
    self.values =  np.zeros(self.queue_size)
    
    # ini plot, if any
    if attach_plot:
      self.plot = plot.Plotter(title=self.name)
    else:
      self.plot = None

  def push_value(self, value):
    """
    One new value for the buffer
    """
    # One goes out, one goes in
    self.values = np.roll(self.values, -1)
    self.values[-1] = value
    # Update plot data once it's created
    if self.plot:
      self.plot.set_values(self.values)
