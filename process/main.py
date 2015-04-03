import readerLSL
import plot, data, signal_processing

if __name__ == "__main__":
  reader = readerLSL.ReaderLSL("PPG")
  assert(reader.nb_streams > 0)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i
  
  # New holder for green channel
  green_chan = data.SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="green")
  fft = signal_processing.FFT(green_chan, window_length = 10, attach_plot=True)
  filtered = signal_processing.TemporalFilter(green_chan, [(0, 0.6),(4,-1)], attach_plot=True)
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    #print timestamp, sample
    # retrieve value for green channel
    green_chan.push_value(sample)
