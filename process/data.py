import plot
import numpy as np

class DataBuffer():
  """
  Data structure to hold, process and plot signals. Base class, should not be instanciate diretctly.
  """
  
  def __init__(self, sample_rate, queue_size, input_data = None, attach_plot = False, name="data"):
    """
    sample_rate: at which rate values will be sent (in Hz).
    queue_size: number of points of the buffer
    input_data: which buffer the data comes from; will register automatically. Must be of the same type.
    plot: attach a plot or not
    name: used as title for the plot
    """
    
    # check input data type and register if needed
    if input_data:
      if self.__class__.__name__ != input_data.__class__.__name__:
        print "ERROR: instance", self.__class__.__name__, "differs from input_data:", input_data.__class__.__name__
        raise NameError('IncompatibleInputData')
      else:
        input_data.add_output(self)
        
    # empty list for output callback
    self.outputs = []
    
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
   
  def add_output(self, output_data):
    """
    Register a new output stream
    """
    self.outputs.append(output_data)
    
  def push_value(self, value):
    """
    One new value for the buffer. We push in turn automatically to every output, if any.
    Warning: should not be called manually exept if "input_data" is None
    """
    # One goes out, one goes in
    self.values = np.roll(self.values, -1)
    self.values[-1] = value
    # Update plot data once it's created
    if self.plot:
      self.plot.set_values(self.values)
    # Push to output
    for output in self.outputs:
      output.push_value(value)

class SignalBuffer(DataBuffer):
  """
  Contains signals
  """
  
  def __init__(self, sample_rate=-1, window_length=1, input_data = None, attach_plot = False, name = "signal"):
    """
    input_data: which buffer the data comes from will register automatically to input plot. 
    sample_rate: at which rate values will be sent (in Hz). Must be set if input_data == None. Will be ignored if input_data is set.
    window_length: time length of signal buffer (in seconds)
    plot: attach a plot or not
    name: used as title for the plot
    """
    if not input_data and sample_rate <= 0: 
      print "ERROR: no input_data set and sample rate not given or negative."
      raise NameError('NoSampleRate')
    elif input_data:
      sample_rate = int(input_data.sample_rate)
        
    DataBuffer.__init__(self, sample_rate, sample_rate*window_length, input_data = input_data, attach_plot = attach_plot, name = name)
