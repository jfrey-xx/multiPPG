import readerLSL
import plot, data
from signal_processing import *
from data import *

if __name__ == "__main__":
  reader = readerLSL.ReaderLSL("PPG")
  assert(reader.nb_streams > 0)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i
  
  global_window_length = 5
  
  # New holder for green channel
  #red_chan = SignalBuffer(reader.getSamplingRate(0), window_length = global_window_length, attach_plot=True, name="red")
  #green_chan = SignalBuffer(reader.getSamplingRate(0), window_length = global_window_length, attach_plot=True, name="green")
  #blue_chan = SignalBuffer(reader.getSamplingRate(0), window_length = global_window_length, attach_plot=True, name="blue")
  
  # 3 channels of 5 seconds
  rgb_shape = 3,reader.getSamplingRate(0)*global_window_length
  rgb_chan = Data2DBuffer(reader.getSamplingRate(0), rgb_shape)
  
  rgb_detrend = Detrend2D(rgb_chan)
  rgb_ortho =  OrthogonalRGB(rgb_detrend, attach_plot=True, name="rgb_detrend_ortho")
  
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    #red_chan.push_value(sample[0])
    #green_chan.push_value(sample[1])
    #blue_chan.push_value(sample[2])
    rgb_chan.push_values(np.array(sample))
