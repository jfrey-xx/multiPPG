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
  red_chan = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="red")
  #green_chan = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="green")
  #blue_chan = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="blue")
  
  red_detrend = Detrend(red_chan, attach_plot=True, name="red detrend")
  red_detrend4 = Detrend4(red_chan, attach_plot=True, name="red detrend")
  #green_detrend = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="green detrend")
  #blue_detrend = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="blue detrend")
 
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    red_chan.push_value(sample[0])
    #green_chan.push_value(sample[1])
    #blue_chan.push_value(sample[2])

