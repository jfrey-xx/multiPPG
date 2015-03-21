import readerLSL
import plot, data, signal_processing
import time

if __name__ == "__main__":
  reader = readerLSL.ReaderLSL("PPG")
  assert(reader.nb_streams > 0)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i
  
  # New holder for green channel
  green_chan = data.SignalBuffer(reader.getSamplingRate(0), attach_plot=True, name="green")
  # Longer history
  data.SignalBuffer(input_data=green_chan, window_length=10, attach_plot=True, name="green_history")
  inverter = signal_processing.Invert(green_chan, attach_plot=True)
  data.SignalBuffer(input_data=inverter, window_length=10, attach_plot=True, name="invert_history")
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    #print timestamp, sample
    # retrieve value for green channel
    green_value = 0
    if len(sample) > 2:
      green_value = sample[1]
    green_chan.push_value(green_value)
