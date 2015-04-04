import plot
import numpy as np
from locker import *

class DataBuffer():
  """
  Data structure used to hold, process and plot signals. Base class, should not be instanciate directly by users.
  """
  
  def __init__(self, sample_rate, shape, input_data = None, attach_plot = False, name="data"):
    """
    sample_rate: at which rate values will be sent (in Hz).
    shape number of points of the buffer, MUST be a tuple since it can have more than one dimension (eg. (128,128) for a small matrix). NB: must also hold integers.
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
    
    # check that shape has the right format
    if not type(shape) is tuple:
      raise NameError('WrongShapeFormat')

    # empty list for output callback
    self.outputs = []
    # another one for processing callback
    self.callbackClients = []
    
    self.sample_rate = int(sample_rate)
    self.shape = shape
    self.name = name
    
    # init Y / n-dim values to 0
    self.values =  np.zeros(self.shape)
    self.queue_size = self.values.size
    self.ndim = self.values.ndim
    # init labels value to regular range, except if got input_data, in this case mirror data
    if input_data:
      self.labels = input_data.labels
    else:
        self.labels = np.arange(0,self.shape[0])
    
    # ini plot, if any
    if attach_plot:
      self.plot = plot.Plotter(shape, title=self.name)
      self.plot.set_labels(self.labels)
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
      FIXME: unexpected results with multi-dimensional arrays
    """
    self.push_values(np.array([value]), revert = revert)

  def push_values(self, values, revert = False):
    """
    New values for the buffer. We push in turn automatically to every output, if any.
      NB: if the new values are the same size as the old ones, will replace everything
      Warning: should not be called manually exept if "input_data" is None
    
    revert: by default values append to the end of the buffer, set True to append to the beginning
      NB: parameter will be passed to all outputs
      WARNING: unexpected results when incoming values shape and size does not match internal array (ie could shift values toward other dimensions)
    """
    # work temporarily in 1D to update values
    self.values.shape = (self.values.size)
    new_values_orig_shape = values.shape
    values.shape = values.size
    # One goes out, one goes in
    if revert:
      self.values = np.roll(self.values, len(values))
      self.values[0:len(values):] = values
    else:
      self.values = np.roll(self.values, -len(values))
      self.values[-len(values):] = values
    # back to original shape for both arrays
    self.values.shape = self.shape
    values.shape = new_values_orig_shape

    # Trigger external functions if needed
    self.nudge_callback(values, self.values)
    # Update plot data once it's created
    if self.plot:
      self.plot.set_values(self.values)    # Push to output
    for output in self.outputs:
      output.push_values(values, revert=revert)
      
  def set_labels(self, labels, revert = False):
    """
    Set labels (eg X axis), replace data of the plot if any
    FIXME: decide if revert should be at plot level
    """
    self.labels = labels
    if self.plot:
      #if revert:
      #  labels = labels[::-1]
      self.plot.set_labels(self.labels)
      
  def add_callback(self, fun, threaded=False):
    """
    Add a fuction to be called automatically each time values are updated. NB: a more powerful and general case compared to "input_data" mechanism.
    @param fun: function to call
    @param threaded: instead of calling the fuction at /each/ new value, a separate thread is launched and will be waken periodically with an event. Likely to miss data, but handy for heavy computation so the whole program does not lag. A threaded callback will get the whole values of the buffer, not the new samples ; less likely to skip some.
    """
    if threaded:
      mrCall = CallbackLazy(self, fun)
    else:
      mrCall = CallbackNow(self, fun)
    self.callbackClients.append(mrCall)
    
  def nudge_callback(self, new_values, all_values):
    """
    Send message to all registered callback functions. Used for signal processing. Clients will take over or the work will be done by a seperate thread depending of the case -- *This is why the processing is not guaranteed by this class*
    @new_values: what has been change since last call (aimed at CallbackNow)
    @all_values: the whole buffer (aimed at CalbackLazy)
    """
    for client in self.callbackClients:
      client(new_values, all_values)

class SignalBuffer(DataBuffer):
  """
  Contains a 1D signal; possible to play on history size with window_length and to time axis
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
    DataBuffer.__init__(self, sample_rate, (sample_rate*self.window_length,), input_data = input_data, attach_plot = attach_plot, name = name)
    
    self.last_point_time = 0 # in s
    
  def push_values(self, values, **kwargs):
    """
    override DataBuffer.push_values to set axis
    NB: x values accuracy depends on the fact that this function is called at the same frequency as sample_rate
    FIXME: CPU intensive
    """
    # pass values as usual
    DataBuffer.push_values(self, values, **kwargs)
    # update x values
    self.last_point_time = self.last_point_time + 1/float(self.sample_rate)
    first_point_time = self.last_point_time - self.queue_size/float(self.sample_rate)
    labels = np.arange(first_point_time, self.last_point_time, abs(self.last_point_time - first_point_time) / float(self.queue_size))
    DataBuffer.set_labels(self, labels, **kwargs)
    
