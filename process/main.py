import readerLSL
import plot
import time

if __name__ == "__main__":
  reader = readerLSL.ReaderLSL("PPG")
  assert(reader.nb_streams > 0)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i
    
  harry = plot.Plotter(reader.getSamplingRate(0))
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    print timestamp, sample
    # retrieve value for green channel
    green_value = 0
    if len(sample) > 2:
      green_value = sample[1]
    harry.push_value(green_value)
