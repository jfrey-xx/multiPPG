
from signal_processing import *
from data import *
from IProcess import *

class ProcessUfuk(IProcess):
  """
  Read RGB, use detrend + orthogonal vector as described in original article
  """
  def __init__(self, sampling_rate, attach_plot=False):
    """
    attach_plot: enable or disable *all* plots
    """
    self.name = "Ufuk"
    
    # 5s because original detrend is slow
    global_window_length = 5
    
    # 3 channels of 5 seconds
    rgb_shape = 3,sampling_rate*global_window_length
    rgb_chan = Data2DBuffer(sampling_rate, rgb_shape)
    rgb_detrend = Detrend2D(rgb_chan)
    rgb_ortho =  OrthogonalRGB(rgb_detrend, attach_plot=attach_plot, name="rgb_detrend_ortho")
    
    # -- applying dwt morlet
    morlet = Morlet(rgb_ortho, window_length=global_window_length, attach_plot=attach_plot, name="the green morlet")
    morlet_spec = MorletSpectrum(morlet, attach_plot=attach_plot)
    
    # extract BPM (max freq), pass-band between 0.6 and 4Hz
    bpm_one = GetMaxX(morlet_spec, nb_values = 1, stop_list = [(0,0.6),(4,-1)])
    bpms_raw = SignalBuffer(window_length=5, input_data=bpm_one, attach_plot=attach_plot, name="BPM history")
    
    IProcess.__init__(self, rgb_ortho, bpm_one, rgb_ortho, 3, attach_plot=attach_plot)

    
