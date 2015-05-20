
from signal_processing import *

class IProcess():
  """
  Interface for processing algo
  """
  def __init__(self, input_chan, bpm_chan, confidence_idx_chan, nb_values, attach_plot=False):
    """
    Should be called by sub-class after its pipeline has been initiated
    
    input_chan: new values will be pushed to it
    bpm_chan: output channel of the algorithm, smoothing will be computed
    confidence_idx_chan: one particular chan upon which the confidence channel will be computed. NB: we "backport" such feature from Bousefsaf to other algo
    
    nb_values: number of values needed for the algorithm to perform, will raise error if not enough values are givent to  __call__ is different
    """
    
    if self.name:
      print "start process", self.name
    else:
      print "start process"
    
    self.nb_values = nb_values
    
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
    
    TODO: will grab the first nb_values, could not select particular indexes
    FIXME: hotfix in case something went wrong with pushed values
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
        
    # convert from Hz to BPM
    return    self.bpms.values[-1]*60,self.conf_idx.values[-1]
