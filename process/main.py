import readerLSL
import plot, data
from signal_processing import *
from data import *

if __name__ == "__main__":
  reader = readerLSL.ReaderLSL("PPG")
  assert(reader.nb_streams > 0)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i
  
  # New holder for green channel
  green_chan = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="green")
  fft = FFT(green_chan, window_length = 10, attach_plot=True)
  #filtered = TemporalFilter(green_chan, [(0, 0.6),(4,-1)], attach_plot=True)
  morlet = Morlet(green_chan, window_length=10, attach_plot=True, name="the green morlet")
  morlet_spec = MorletSpectrum(morlet, attach_plot=True)
  max_morlet = GetMaxX(morlet_spec)
  max_fft = GetMaxX(fft)
  slide_avg = RemoveSlidingAverage(green_chan, attach_plot=True)
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    #print timestamp, sample
    # retrieve value for green channel
    green_chan.push_value(sample[0])
    print "max morlet:", max_morlet.values[0], ", max fft:", max_fft.values[0]
