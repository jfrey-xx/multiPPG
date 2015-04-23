
from signal_processing import *
from data import *
from IProcess import *

class ProcessLUV(IProcess):
  """
  Read one green channel, use morlet to get Hz
  """
  def __init__(self, sampling_rate, attach_plot=False):
    """
    attach_plot: enable or disable *all* plots
    """

    # New holder for green channel
    green_chan = SignalBuffer(sampling_rate, window_length = 10, attach_plot=attach_plot, name="green")
    
    # -- filtering?

    # -- applying dwt morlet
    morlet = Morlet(green_chan, window_length=10, attach_plot=attach_plot, name="the green morlet")
    morlet_spec = MorletSpectrum(morlet, attach_plot=attach_plot)

    # extract BPM (max freq), pass-band between 0.6 and 4Hz
    bpm_one = GetMaxX(morlet_spec, nb_values = 1, stop_list = [(0,0.6),(4,-1)])
    bpms_raw = SignalBuffer(window_length=5, input_data=bpm_one, attach_plot=attach_plot, name="BPM history")
    
    IProcess.__init__(self, green_chan, bpm_one, green_chan, attach_plot=attach_plot)
