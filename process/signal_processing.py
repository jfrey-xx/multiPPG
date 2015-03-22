import data
import scipy
import scipy.fftpack
import numpy as np

# Takes a DataBuffer as input, makes computations and serve new values through inheritance.
# TODO: optimize memory by sharing input buffer when possible (pointer instead of copy)

class Invert(data.DataBuffer):
  """
  Test case: takes a data and revert values. Output: signal buffer.
  """
  def __init__(self, input_signal_buffer, attach_plot = False, name = "invert"):
    self.input_buffer = data.DataBuffer(input_signal_buffer.sample_rate, input_signal_buffer.queue_size, input_data=input_signal_buffer)
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, self.input_buffer.queue_size, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, data_buffer, new_values):
    self.push_values(new_values * -1)
    
class FFT(data.DataBuffer):
  """
  Compute FFT of the signal
  """
  def __init__(self, input_signal_buffer, window_length = -1, attach_plot = False, name = "FFT"):
    """
    input_signal_buffer: SignalBuffer type
    window_length: set parameter to extend window length of the signal in the buffer
    """
    # By default input buffer will be 3 times as long as the original signal
    if window_length <= 0:
      window_length = 3 * input_signal_buffer.window_length
    self.input_buffer = data.SignalBuffer(window_length = window_length, input_data=input_signal_buffer)
    
    # FFT is mirrored (nyquist), spectrum will have half the points
    if self.input_buffer.queue_size%2: # odd
      self.nb_points = (self.input_buffer.queue_size + 1) / 2
    else: # even
      self.nb_points = self.input_buffer.queue_size/2 
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, self.nb_points, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)
    
    self.set_x_values(scipy.fftpack.fftfreq( self.input_buffer.queue_size, 1./self.sample_rate)[0:self.nb_points])

  def __call__(self, data_buffer, new_values):
    fft=abs(scipy.fft(data_buffer.values))
    self.push_values(fft[0:self.nb_points])

    
class GetMaxX(data.DataBuffer):
  """
  Return the X indices sorted by Y (max first). Useful with FFT.
    input_data_buffer: DataBuffer type
    nb_values: retains only some values. By default: all
  """
  def __init__(self, input_data_buffer, nb_values = -1, attach_plot = False, name = "max X"):
    # init with a copy of input buffer
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, input_data_buffer.queue_size, input_data=input_data_buffer)
    # default / crop data buffer size if needed
    if nb_values <= 0 or nb_values > input_data_buffer.queue_size:
      nb_values = input_data_buffer.queue_size
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, nb_values, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, data_buffer, new_values):
    # sort input by X then reverse order
    sorted_indices = np.argsort(self.input_buffer.values)[::-1]
    # retrieve values, select 
    sorted_x_values = self.input_buffer.values_x[sorted_indices]
    # replace values with corresponding subdet
    self.push_values(sorted_x_values[0:self.queue_size])

