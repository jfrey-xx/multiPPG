import plot
import numpy as np

class DataBuffer():
  """
  Data structure to hold, process and plot signals. Base class, should not be instanciate diretctly.
  """
  
  def __init__(self, sample_rate, queue_size, attach_plot = False, name="data"):
    """
    sample_rate: at which rate values will be sent (in Hz).
    queue_size: number of points of the buffer
    plot: attach a plot or not
    name: used as title for the plot
    """
    
    self.sample_rate = int(sample_rate)
    self.queue_size = int(queue_size)
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
    One new value for the buffer.
    """
    # One goes out, one goes in
    self.values = np.roll(self.values, -1)
    self.values[-1] = value
    # Update plot data once it's created
    if self.plot:
      self.plot.set_values(self.values)

class SignalBuffer(DataBuffer):
  """
  Contains signals
  """
  
  def __init__(self,  sample_rate, window_length=1, input_data = None, attach_plot = False, name = "signal"):
    """
    sample_rate: at which rate values will be sent (in Hz).
    window_length: time length of signal buffer (in seconds)
    plot: attach a plot or not
    name: used as title for the plot
    """
    DataBuffer.__init__(self, sample_rate, sample_rate*window_length, attach_plot = attach_plot, name = name)