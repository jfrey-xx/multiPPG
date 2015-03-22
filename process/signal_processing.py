import data
import scipy
import scipy.fftpack

# Takes a DataBuffer as input, makes computations and serve new values through inheritance.

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