import sys; sys.path.append('../process')
import plot, data, signal_processing
import time
import numpy as np

# Test our different data structures with radom data

if __name__ == "__main__":
  freq = 100
  # New holder for green channel
  chan = data.SignalBuffer(freq, window_length = 10, attach_plot=True, name="random")
  fft = signal_processing.FFT(chan, window_length = 10, attach_plot=True)
  filtered = signal_processing.TemporalFilter(chan, [(0, 0.6),(4,-1)], attach_plot=True)
  inver = signal_processing.Invert(chan, attach_plot = True)
  maxou = signal_processing.GetMaxX(fft)
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample = np.random.random(1)
    time.sleep(0.010)
    #print timestamp, sample
    # retrieve value for green channel
    chan.push_value(sample)
    print maxou.values
