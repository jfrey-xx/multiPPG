import plot
import numpy as np

class DataBuffer():
  """
  Data structure used to hold, process and plot signals. Base class, should not be instanciate directly by users.
  """
  
  def __init__(self, sample_rate, queue_size, input_data = None, attach_plot = False, name="data"):
    """
    sample_rate: at which rate values will be sent (in Hz).
    queue_size: number of points of the buffer
    input_data: which buffer the data comes from; will register automatically. Must be subclass of DataBuffer
    plot: attach a plot or not
    name: used as title for the plot
    """
    
    # check input data type and register if needed
    if input_data:
      if not issubclass(input_data.__class__, DataBuffer):
        print "ERROR: instance", input_data.__class__, "is not a subclass of DataBuffer"
        raise NameError('IncompatibleInputData')
      else:
        input_data.add_output(self)
    
    # empty list for output callback
    self.outputs = []
    # another one for processing callback
    self.functions = []
    
    self.sample_rate = int(sample_rate)
    self.queue_size = int(queue_size)
    self.name = name
    
    # init Y values to 0
    self.values =  np.zeros(self.queue_size)
    # init X value to regular range, except if got input_data, in this case mirror data
    if input_data:
      self.values_x = input_data.values_x
    else:
      self.values_x = np.arange(0,self.queue_size)
    
    # ini plot, if any
    if attach_plot:
      self.plot = plot.Plotter(title=self.name)
      self.plot.set_x_values(self.values_x)
    else:
      self.plot = None
   
  def add_output(self, output_data):
    """
    Register a new output stream
    """
    self.outputs.append(output_data)
    
  def push_value(self, value, revert = False):
    """"
    Ease  single value push, pass it to push_values()
    
    revert: by default values append to the end of the buffer, set True to append to the beginning
      NB: parameter will be passed to all outputs
    """
    self.push_values(np.array([value]), revert = revert)

  def push_values(self, values, revert = False):
    """
    New values for the buffer. We push in turn automatically to every output, if any.
      NB: if the new values are the same size as the old ones, will replace everything
      Warning: should not be called manually exept if "input_data" is None
    
    revert: by default values append to the end of the buffer, set True to append to the beginning
      NB: parameter will be passed to all outputs
    """
    # One goes out, one goes in
    if revert:
      self.values = np.roll(self.values, len(values))
      self.values[0:len(values):] = values
    else:
      self.values = np.roll(self.values, -len(values))
      self.values[-len(values):] = values
    # Trigger external functions if needed
    self.nudge_callback(values)
    # Update plot data once it's created
    if self.plot:
      self.plot.set_values(self.values)
    # Push to output
    for output in self.outputs:
      output.push_values(values, revert=revert)
      
  def set_x_values(self, x_values, revert = False):
    """
    Set X points, replace axis of the plot if any
    FIXME: decide if revert should be at plot level
    """
    self.values_x = x_values
    if self.plot:
      #if revert:
      #  x_values = x_values[::-1]
      self.plot.set_x_values(self.values_x)
      
  def add_callback(self, fun):
    """
    Add a fuction to be called automatically each time values are updated. NB: a more powerful and general case compared to "input_data" mechanism.
    """
    self.functions.append(fun)
    
  def nudge_callback(self, new_values):
    """
    Send message to all registered callback functions. Used for signal processing
    """
    for fun in self.functions:
      fun(self, new_values)

class SignalBuffer(DataBuffer):
  """
  Contains a signal; possible to play on history size with window_length and to time axis
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
    self.window_length = window_length
    DataBuffer.__init__(self, sample_rate, sample_rate*self.window_length, input_data = input_data, attach_plot = attach_plot, name = name)
    
    self.last_point_time = 0 # in s
    
  def push_values(self, values, **kwargs):
    """
    override DataBuffer.push_values to set axis
    FIXME: CPU intensive
    """
    # pass values as usual
    DataBuffer.push_values(self, values, **kwargs)
    # update x values
    self.last_point_time = self.last_point_time + len(values)/float(self.sample_rate)
    first_point_time = self.last_point_time - self.queue_size/float(self.sample_rate)
    x_values = np.arange(first_point_time, self.last_point_time, abs(self.last_point_time - first_point_time) / float(self.queue_size))
    DataBuffer.set_x_values(self, x_values, **kwargs)
    