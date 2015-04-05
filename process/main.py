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
  
  # -- testing FFT
  #fft = FFT(green_chan, window_length = 10, attach_plot=True)
  #filtered = TemporalFilter(green_chan, [(0, 0.6),(4,-1)], attach_plot=True)
  #max_fft = GetMaxX(fft)

  # -- applying dwt morlet
  # FIXME: check sample rate
  morlet = Morlet(green_chan, window_length=10, attach_plot=False, name="the green morlet")
  morlet_spec = MorletSpectrum(morlet, attach_plot=True)
  #max_fft = GetMaxX(fft)

  # extract BPM (max freq)
  bpm_one = GetMaxX(morlet_spec, nb_values = 1)
  bpms_raw = SignalBuffer(window_length=5, input_data=bpm_one, attach_plot=True, name="BPM history")
  # put in buffer
  
  # confidence index: derivative on 0.5s window of raw signal
  deriv = Derivative(green_chan, window_length=0.5, attach_plot=True)


  ## testing normalization
  #slide_avg = RemoveSlidingAverage(green_chan, attach_plot=False)
  #norm = Invert(slide_avg, attach_plot=True)
  #fft_norm = FFT(norm, window_length = 10, attach_plot=True, name="fft norm")
  #morlet_norm = Morlet(norm, window_length=10, attach_plot=True, name="the green morlet norm")
  #morlet_spec_norm = MorletSpectrum(morlet_norm, attach_plot=True, name="morlet spec norm")
  #max_morlet_norm = GetMaxX(morlet_spec_norm)
  #max_fft_norm = GetMaxX(fft_norm)

  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    #print timestamp, sample
    # retrieve value for green channel
    green_chan.push_value(sample[0])
    #print "max morlet:", max_morlet.values[0], ", max fft:", max_fft.values[0]
    #print "Norm -- max morlet:", max_morlet_norm.values[0], ", max fft:", max_fft_norm.values[0]

    print "bpm:", bpm_one.values[0]
