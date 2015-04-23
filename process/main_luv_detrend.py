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
  green = SignalBuffer(reader.getSamplingRate(0), window_length = 10, attach_plot=True, name="green")

  green_detrend = Detrend1D(green, fast=True, attach_plot=False, name="green detrend fast")
  # -- testing FFT
  #fft = FFT(green_chan, window_length = 10, attach_plot=True)
  filtered_detrend = TemporalFilterFFT(green_detrend, [(0, 0.6),(4,-1)], attach_plot=True, name="detrend filtered fft")

  #filtered = TemporalFilterFFT(green, [(0, 0.6),(4,-1)], attach_plot=True, name="filtered fft")

  #filtered_butter = BandPassFilterButterworth(green, 0.6, 4, attach_plot=True, name="filtered butter")
  filtered_detrend_butter = BandPassFilterButterworth(green_detrend, 0.6, 4, attach_plot=True, name="filtered detrend butter")
  #max_fft = GetMaxX(fft)

  # -- applying dwt morlet
  # FIXME: check sample rate
  #morlet = Morlet(filtered, window_length=10, attach_plot=False, name="the green morlet")
  #morlet_spec = MorletSpectrum(morlet, attach_plot=True)
  #max_fft = GetMaxX(fft)

  # extract BPM (max freq), pass-band between 0.6 and 4Hz
  #bpm_one = GetMaxX(morlet_spec, nb_values = 1, stop_list = [(0,0.6),(4,-1)])
  #bpms_raw = SignalBuffer(window_length=5, input_data=bpm_one, attach_plot=True, name="BPM history")
  
  ## testing normalization
  #slide_avg = RemoveSlidingAverage(green_chan, attach_plot=False)
  #norm = Invert(slide_avg, attach_plot=True)
  #fft_norm = FFT(norm, window_length = 10, attach_plot=True, name="fft norm")
  #morlet_norm = Morlet(norm, window_length=10, attach_plot=True, name="the green morlet norm")
  #morlet_spec_norm = MorletSpectrum(morlet_norm, attach_plot=True, name="morlet spec norm")
  #max_morlet_norm = GetMaxX(morlet_spec_norm)
  #max_fft_norm = GetMaxX(fft_norm)

  # confidence index: derivative on 0.5s window of raw signal
  #deriv = Derivative(green_chan, window_length=0.5, attach_plot=True)
  #conf_idx = CondidenceIndex(green, window_length=10, attach_plot=True)
  # smooth BPM: discard impossible values
  #bpms_smooth = BPMSmoother(bpms_raw, window_length = 5, attach_plot=True, name="ultimate smoother")
  
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    #print timestamp, sample
    # retrieve value for green channel
    green.push_value(sample[0])
    #print "max morlet:", max_morlet.values[0], ", max fft:", max_fft.values[0]
    #print "Norm -- max morlet:", max_morlet_norm.values[0], ", max fft:", max_fft_norm.values[0]

    #print "bpm:", bpm_one.values[0]
    #print "bpm smoothed:", bpms_smooth.values[0]