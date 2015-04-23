
from signal_processing import *

class IProcess():
  """
  Interface for processing algo
  """
  def __init__(self, input_chan, bpm_chan, confidence_idx_chan, attach_plot=False):
    """
    Should be called by sub-class after its pipeline has been initiated
    
    input_chan: new values will be pushed to it
    bpm_chan: output channel of the algorithm, smoothing will be computed
    confidence_idx_chan: one particular chan upon which the confidence channel will be computed. NB: we "backport" such feature from Bousefsaf to other algo
    """
    print "start process"

    self.input_chan = input_chan
    # confidence index: derivative on 0.5s window of raw signal
    #deriv = Derivative(green_chan, window_length=0.5, attach_plot=True)
    self.conf_idx = CondidenceIndex(confidence_idx_chan, window_length=10, attach_plot=attach_plot)
    # discard impossible values
    bpms_discard = BPMSmoother(bpm_chan, window_length=10, attach_plot=attach_plot, name="discard BPMs")
    # and... smooth truely values with a sliding window
    self.bpms = SlidingAverage(bpms_discard, sliding_window=10, window_length=10, attach_plot=attach_plot, name="BPMs sliding average")
          
  def __call__(self, values):
    """
    Update pipeline with new values, return a tuble with BPM, confidence_idx
    """
    self.input_chan.push_values(values)
    return    self.bpms.values[-1],self.conf_idx.values[-1]
    #green_chan.push_value(sample[1])
