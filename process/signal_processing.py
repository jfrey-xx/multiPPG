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

  def __call__(self, all_values, new_values):
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

  def __call__(self, all_values, new_values):
    fft=abs(scipy.fft(all_values))
    self.push_values(fft[0:self.nb_points])

class GetMaxX(data.DataBuffer):
  """
  Return the X indices sorted by Y (max first). Useful with FFT.
    input_data_buffer: DataBuffer type
    nb_values: retains only some values. By default: all
    FIXME: 1D only at the moment
    stop_list: tuples of intervals to ignore (see TemporalFilter help)
  """
  def __init__(self, input_data_buffer, nb_values = -1, stop_list = [], attach_plot = False, name = "max X"):
    if input_data_buffer.ndim > 1:
      raise NameError("NDimNotHandled")
    self.stop_list = stop_list
    # init with a copy of input buffer
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, input_data_buffer.shape, input_data=input_data_buffer)
    # we have to dublicate manually labels now -- here it's the same dimensions, that's okay
    self.input_buffer.set_labels(input_data_buffer.labels)
    # default / crop data buffer size if needed
    if nb_values <= 0 or nb_values > input_data_buffer.queue_size:
      nb_values = input_data_buffer.queue_size
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, (nb_values,), attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, all_values, new_values):
    x = self.input_buffer.labels
    # zero selected frequencies
    for stop in self.stop_list:
      start = stop[0]
      end = stop[1]
      # "-1" code for upper bound
      if end == -1:
        end = np.max(x)
      # zero selected band
      all_values[(abs(x) >= start) & (abs(x) <= end)] = 0
    # sort input by X then reverse order
    sorted_indices = np.argsort(all_values)[::-1]
    # retrieve values, select 
    sorted_labels = self.input_buffer.labels[sorted_indices]
    # replace values with corresponding subset
    self.push_values(sorted_labels[0:self.queue_size])

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

  def __call__(self, all_values, new_values):
    # compute FFT over input buffer
    fft = scipy.fft(all_values)
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
    freq=1/(self.cw.fourierwl*scales)*self.sample_rate
    return freq

  def __call__(self, all_values, new_values):
    self.cw=self.wavelet(all_values,self.maxscale,self.notes,scaling=self.scaling)
    values = abs(self.cw.getdata())
    # update spectrum
    self.spectrum = self.get_spectrum()
    # revert to correct order values (or at least the same as the others)
    # FIXME: not working?
    self.push_values(values, revert=True)

class MorletSpectrum(data.DataBuffer):
  """
  1D signal out of Mr Morlet
  @param morlet: Morlet class
  """
  def __init__(self, morlet, attach_plot = False, name = "morlet spectrum"):
    shape = (len(morlet.get_spectrum()),)
    data.DataBuffer.__init__(self, morlet.sample_rate, shape, attach_plot = attach_plot, name = name)
    self.set_labels(morlet.get_freq())
    morlet.add_callback(self)
    # FIXME: not great *at all* to have a direct ref...
    self.morlet = morlet

  def __call__(self, all_values, new_values):
    values = self.morlet.get_spectrum()
    self.push_values(values)

class RemoveSlidingAverage(data.DataBuffer):
    """
    sustract to the average of the input to current sample
    cf. @Bousefsaf2014
    """
    def __init__(self, input_data_buffer, attach_plot = False, name = "sliding average"):
      self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, input_data_buffer.shape, input_data=input_data_buffer)
      data.DataBuffer.__init__(self, self.input_buffer.sample_rate, self.input_buffer.shape, attach_plot = attach_plot, name = name)
      self.input_buffer.add_callback(self)

    def __call__(self, all_values, new_values):
      """
      a mean over input buffer and a push and we're good
      """
      new_values = new_values - np.mean(all_values)
      self.push_values(new_values)

class Derivative(data.DataBuffer):
  """
  Use numpy.diff to compute firt order derivative
  """
  def __init__(self, input_data_buffer, window_length = -1, attach_plot = False, name = "Derivative"):
    # By default input buffer will be 1s long
    if window_length <= 0:
      window_length = 1
    # FIXME: should ceil a bit everywhere like that probably
    shape = (np.ceil(input_data_buffer.sample_rate*window_length),)
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, shape, input_data=input_data_buffer)
    
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, shape, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, all_values, new_values):
    x = self.input_buffer.labels
    dx =  x[-1] - x[0]# np.diff(x)
    dy = np.diff(all_values)
    df = dy/dx
    self.push_values(df)

class CondidenceIndex(data.DataBuffer):
  """
  Very specific, implements confidence index described by Bousefsaf2015 (derivative and some log)
  """
  def __init__(self, input_data_buffer, window_length = 1, attach_plot = False, name = "Confidence index"):
    # the alorithm work on 2x0.5 time windom, we want an even number
    np_points = input_data_buffer.sample_rate
    if np_points%2: # odd
      np_points += 1
    shape_input = (np_points,)
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, shape_input, input_data=input_data_buffer)
    
    shape = (np.ceil(input_data_buffer.sample_rate*window_length),)
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, shape, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, all_values, new_values):
    half = len(all_values)/2
    s = 0
    for i in range (half):
      # TODO: for sure in one numpy insrtuction we could do that
      s+=np.abs(all_values[i+half]-all_values[i])
    value=(10-np.log(s)**3)*10
    self.push_value(value)

class BPMSmoother(data.DataBuffer):
  """
  Simple algo to discard unrealistic values, check adjacent values
  FIXME: may need perfect sync because of points number
  """
  def __init__(self, input_data_buffer, window_length = 1, attach_plot = False, name = "smoother"):
    # the alorithm work on 5 time points
    shape_input = 5,
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, shape_input, input_data=input_data_buffer)
    
    shape = (np.ceil(input_data_buffer.sample_rate*window_length),)
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, shape, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

  def __call__(self, all_values, new_values):
    # take the middle, previous and next points, average if diff greater than 10 for direct neighbors, and 18 for the next 
    m = all_values[2]
    mp = all_values[1]
    mn = all_values[3]
    mpp = all_values[0]
    mnn = all_values[4]
    if abs(m-mp) > 10/60. or abs(m-mn) > 10/60.:
        m = (mp+mn)/2
    if abs(m-mpp) > 18/60. or abs(m-mnn) > 18/60.:
        m = (mpp+mnn)/2
    all_values[2]=m
    value = m
    self.push_value(value)

class Detrend1D(data.DataBuffer):
  """
  Apply detrending algo to data in row
  NB: threaded
  """
  def __init__(self, input_data_buffer, window_length = -1, attach_plot = False, name = "Detrend"):
  
    if input_data_buffer.ndim != 1:
      raise NameError("NDimNotHandled")
    
    if window_length < 0:
      shape = input_data_buffer.shape
    else:
      nb_samples = np.ceil(input_data_buffer.sample_rate*window_length)
      shape = nb_samples,
    
    self.input_buffer = data.DataBuffer(input_data_buffer.sample_rate, shape, input_data=input_data_buffer)
    data.DataBuffer.__init__(self, input_data_buffer.sample_rate, shape, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self,threaded=True)

  def __call__(self, all_values, new_values):
    """
    we need to detrend all values
    """
    self.push_values(detrend(all_values))
    
class Detrend2D(data.Data2DBuffer):
  """
  Apply detrending algo to data in row
  NB: threaded
  """
  def __init__(self, input_data_buffer, window_length = -1, attach_plot = False, name = "Detrend"):
  
    if input_data_buffer.ndim != 2:
      raise NameError("NDimNotHandled")
    
    if window_length < 0:
      shape = input_data_buffer.shape
    else:
      nb_samples = np.ceil(input_data_buffer.sample_rate*window_length)
      shape = input_data_buffer.shape[0],nb_samples,
    
    self.input_buffer = data.Data2DBuffer(input_data_buffer.sample_rate, shape, input_data=input_data_buffer)
    data.Data2DBuffer.__init__(self, input_data_buffer.sample_rate, shape, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self,threaded=True)

  def __call__(self, all_values, new_values):
    """
    we need to detrend all values
    """
    for i in range(len(all_values)):
      all_values[i] = detrend(all_values[i])
    self.push_values(all_values)
    
    