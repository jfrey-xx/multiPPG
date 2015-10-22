
from signal_processing import *
from data import *
from IProcess import *

class ProcessMuse(IProcess):
  """
  Process EEG data
  """
  def __init__(self, sampling_rate, chan=0, attach_plot=False):
    """
    attach_plot: enable or disable *all* plots
    """
    self.name = "Muse"

    # New holder for green channel
    EEG_chan = SignalBuffer(sampling_rate, window_length = 10, attach_plot=attach_plot, name="rawEEG")
    
    self.morlet = Morlet(EEG_chan, window_length=10, attach_plot=attach_plot, name="the green morlet")
    morlet_spec = MorletSpectrum(self.morlet, attach_plot=attach_plot)

    # bypass IProcess.__init
    self.nb_values = 1
    self.input_chan = EEG_chan

    # yeah, it's the name used by IProcess to return values
    #self.bpms = SlidingAverage(bpms_discard, sliding_window=10, window_length=10, attach_plot=attach_plot, name="BPMs sliding average")

  def __call__(self, values):
    """
    bypass IProcess call
    """

    # some more steps against failure
    nb_incoming_values = -1
    try:
      nb_incoming_values = len(values)
    except:
      print "WARNING: recovering failure, could not assess length of values: ", values
    
    # if < 0 we just recovered from failure, won't raise exception but will not push further values
    if nb_incoming_values >= 0:
      if nb_incoming_values < self.nb_values:
        raise NameError('ProcessNotEnoughValues')
      else:
        self.input_chan.push_values(values[0:self.nb_values])
    
    # Todo: 3D show
