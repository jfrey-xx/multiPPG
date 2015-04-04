import sys; sys.path.append('../lib') # help python find libs relative to this script
import data
import scipy
import scipy.fftpack
import numpy as np
import pyscellania_wavelets as pw
from utilities import *

# Takes a DataBuffer as input, makes computations and serve new values through inheritance.
# TODO: optimize memory by sharing input buffer when possible (pointer instead of copy)

class Invert(data.DataBuffer):
  """
  Test case: takes a data and revert values. Output: signal buffer.
  """
  def __init__(self, input_signal_buffer, attach_plot = False, name = "invert"):
    self.input_buffer = data.DataBuffer(input_signal_buffer.sample_rate, input_signal_buffer.shape, input_data=input_signal_buffer)
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, self.input_buffer.shape, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, data_buffer, new_values):
    self.push_values(new_values * -1)
    
class FFT(data.DataBuffer):
  """
  Compute FFT of the signal
  FIXME: 1D only
  """
  def __init__(self, input_signal_buffer, window_length = -1, attach_plot = False, name = "FFT"):
    """
    input_signal_buffer: SignalBuffer type
    window_length: set parameter to extend window length of the signal in the buffer
    """
    if input_signal_buffer.ndim > 1:
      raise NameError("NDimNotHandled")
    # By default input buffer will be 3 times as long as the original signal
    if window_length <= 0:
      window_length = 3 * input_signal_buffer.window_length
    self.input_buffer = data.SignalBuffer(window_length = window_length, input_data=input_signal_buffer)
    
    # FFT is mirrored (nyquist), spectrum will have half the points
    if self.input_buffer.queue_size%2: # odd
      self.nb_points = (self.input_buffer.queue_size + 1) / 2
    else: # even
      self.nb_points = self.input_buffer.queue_size/2 
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, (self.nb_points,), attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)
    
    self.set_labels(scipy.fftpack.fftfreq( self.input_buffer.queue_size, 1./self.sample_rate)[0:self.nb_points])

  def __call__(self, data_buffer, new_values):
    fft=abs(scipy.fft(data_buffer.values))
    self.push_values(fft[0:self.nb_points])

class GetMaxX(data.DataBuffer):
  """
  Return the X indices sorted by Y (max first). Useful with FFT.
    input_data_buffer: DataBuffer type
    nb_values: retains only some values. By default: all
    FIXME: 1D only at the moment
  """
  def __init__(self, input_data_buffer, nb_values = -1, attach_plot = False, name = "max X"):
    if input_data_buffer.ndim > 1:
      raise NameError("NDimNotHandled")
    # init with a copy of input buffer
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, input_data_buffer.shape, input_data=input_data_buffer)
    # default / crop data buffer size if needed
    if nb_values <= 0 or nb_values > input_data_buffer.queue_size:
      nb_values = input_data_buffer.queue_size
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, (nb_values,), attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, data_buffer, new_values):
    # sort input by X then reverse order
    sorted_indices = np.argsort(self.input_buffer.values)[::-1]
    # retrieve values, select 
    sorted_labels = self.input_buffer.labels[sorted_indices]
    # replace values with corresponding subset
    self.push_values(sorted_sabels[0:self.queue_size])

class TemporalFilter(data.SignalBuffer):
  """
  Use iFFT to remove unwanted frequencies
  FIXME: 1D only
  """
  def __init__(self, input_signal_buffer, stop_list, window_length = -1, attach_plot = False, name = "TemporalFilter"):
    """
    input_signal_buffer: SignalBuffer type
    stop_list: list of tuples, frequencies to remove. Eg [(0,4), (20,30), (60,-1)] to low-pass at 60, high-pass at 4 and notch between 20 and 30.
    window_length: set parameter to extend window length of the signal in the buffer
    """
    if input_signal_buffer.ndim > 1:
      raise NameError("NDimNotHandled")
    self.stop_list = stop_list
    # By default input buffer will be same length as the signal
    if window_length <= 0:
      window_length = input_signal_buffer.window_length
      
    # use a DataBuffer type because we store FFT, need fixed X axis (and don't use signal_processing.FFT because we need all points)
    self.input_buffer = data.DataBuffer(input_signal_buffer.sample_rate, (input_signal_buffer.sample_rate*window_length,), input_data=input_signal_buffer)
    self.input_buffer.set_labels(scipy.fftpack.fftfreq(self.input_buffer.queue_size, 1./input_signal_buffer.sample_rate))
    
    data.SignalBuffer.__init__(self, self.input_buffer.sample_rate, input_signal_buffer.window_length, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, data_buffer, new_values):
    # compute FFT over input buffer
    fft = scipy.fft(self.input_buffer.values)
    x = self.input_buffer.labels
    # zero selected frequencies
    for stop in self.stop_list:
      start = stop[0]
      end = stop[1]
      # "-1" code for upper bound
      if end == -1:
        end = np.max(x)
      # zero selected band
      fft[(abs(x) >= start) & (abs(x) <= end)] = 0
    # compute iFFT and push    
    self.push_values(scipy.ifft(fft).real)

class Morlet(data.DataBuffer):
  """
  Compute continous wavelet transform, morlet style
  Warning: too slow for real time, computations are threaded
  """
  def __init__(self, input_signal_buffer, window_length = -1, attach_plot = False, name = "Morlet"):
    """
    input_signal_buffer: SignalBuffer type
    window_length: set parameter to extend window length of the signal in the buffer
    """
    # By default input buffer will be 3 times as long as the original signal + should be next power of two
    if window_length <= 0:
      window_length = 3 * input_signal_buffer.window_length
    # create correct input buffer, with size power of 2      
    input_shape =  (nextPow2(window_length * input_signal_buffer.sample_rate),)
    self.input_buffer = data.DataBuffer(input_signal_buffer.sample_rate, input_shape, input_data = input_signal_buffer)
    
    # first wave to init self DataBuffer
    self.wavelet=pw.Morlet
    self.maxscale=4
    self.notes=16
    self.scaling="log"
    self.cw=self.wavelet(self.input_buffer.values, self.maxscale, self.notes, scaling=self.scaling)
    cwt=self.cw.getdata()

    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, cwt.shape, attach_plot = attach_plot, name = name)

    # init spectrum and freq
    self.spectrum = self.get_spectrum()
    self.freq = self.get_freq()
    # freq... which is our "x" value (label)
    self.set_labels(self.freq)

    self.input_buffer.add_callback(self, threaded=True)

  def get_nb_temporal_points(self):
    """
    Return the number of points of the signal buffer
    """
    return self.input_buffer.queue_size

  def get_spectrum(self):
    """
    Return the average spectrum computed by the wavelet
    """
    scales=self.cw.getscales()
    pwr=self.cw.getpower()
    spectrum=np.sum(pwr,axis=1)/scales # calculate scale spectrum
    return spectrum

  def get_freq(self):
    """
    Return the list of the frequencies computed by the wavelet
    """
    scales=self.cw.getscales()
    # scale frequencies and correct with sample rate
    freq=(self.cw.fourierwl*scales)*self.get_nb_temporal_points()/self.sample_rate
    return freq

  def __call__(self, data_buffer, new_values):
    self.cw=self.wavelet(self.input_buffer.values,self.maxscale,self.notes,scaling=self.scaling)
    values = abs(self.cw.getdata())
    # update spectrum
    self.spectrum = self.get_spectrum()
    # revert to correct order values (or at least the same as the others)
    # FIXME: not working?
    self.push_values(values, revert=True)
