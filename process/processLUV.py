
from signal_processing import *
from data import *
from IProcess import *

class ProcessLUV(IProcess):
  """
  Read one U channel, detrend, butterworth, use morlet to get Hz
  """
  def __init__(self, sampling_rate, attach_plot=False):
    """
    attach_plot: enable or disable *all* plots
    """
    self.name = "LUV"
    
    # New holder for u channel
    u_chan = SignalBuffer(sampling_rate, window_length = 10, attach_plot=attach_plot, name="u")
    
    # filtering
    u_detrend = Detrend1D(u_chan, fast=True, attach_plot=attach_plot, name="u detrend fast")
    filtered_detrend = BandPassFilterButterworth(u_detrend, 0.6, 4, attach_plot=attach_plot, name="u detrend filtered butter")
    # or FFT version
    #filtered_detrend = TemporalFilterFFT(u_detrend, [(0, 0.6),(4,-1)], attach_plot=attach_plot, name="u detrend filtered fft")

    # -- applying dwt morlet
    morlet = Morlet(filtered_detrend, window_length=10, attach_plot=attach_plot, name="the green morlet")
    morlet_spec = MorletSpectrum(morlet, attach_plot=attach_plot)

    # extract BPM (max freq), pass-band between 0.6 and 4Hz
    bpm_one = GetMaxX(morlet_spec, nb_values = 1, stop_list = [(0,0.6),(4,-1)])
    bpms_raw = SignalBuffer(window_length=5, input_data=bpm_one, attach_plot=attach_plot, name="BPM history")
    
    IProcess.__init__(self, u_chan, bpm_one, u_chan, 1, attach_plot=attach_plot)
