# download LSL and pylsl from https://code.google.com/p/labstreaminglayer/
# Eg: ftp://sccn.ucsd.edu/pub/software/LSL/SDK/liblsl-Python-1.10.2.zip
# put in "lib" folder (same level as user.py)
import sys; sys.path.append('../lib') # help python find pylsl relative to this example program

from pylsl import StreamInlet, resolve_stream

# Use LSL protocol read PPG data stream -- buffer set to 5s max to avoid huge shift because in case of delay
class ReaderLSL():
  """
  Will raise error if do not find stream type or ID
  """
  def __init__(self, stream_type='PPG', stream_id=None, buflen=5):
    """
    stream_type: LSL type of the stream to check
    stream_id: will select specifically one stream based on its name "[stream_type]_[stream_id]"
    """
    # first resolve said stream type on the network
    streams = resolve_stream('type',stream_type)
    self.nb_streams = 0
    
    if len(streams) < 1:
      raise NameError('LSLTypeNotFound')
      
    print "Detecting", len(streams), stream_type, "streams"
    
    # create inlets to read from each stream
    self.inlets = []
    # retrieve also corresponding StreamInfo for future uses (eg sampling rate)
    self.infos = []
    
    for stream in streams:
      inlet = StreamInlet(stream, max_buflen=buflen)
      info = inlet.info()
      # if an ID is specified, will look only for it, otherwise add everything
      if stream_id is not None:
	if info.name() == stream_type + "_" + str(stream_id):
	  # check that there is a unique stream with this name to stop right there any ambiguity
	  if self.nb_streams > 0:
	    raise NameError('LSLDuplicateStreamName')
	  else:
	    self.inlets.append(inlet)
	    self.infos.append(info)
	    self.nb_streams = self.nb_streams + 1
      else:
	self.inlets.append(inlet)
	self.infos.append(info)
	self.nb_streams = self.nb_streams + 1
    
    if stream_id and self.nb_streams < 1:
      raise NameError('LSLStreamNameNotFound')
    
    # init list of samples
    self.samples = [] * self.nb_streams

  # retrieve samples from network
  def __call__(self):
    """
    get new samples
    FIXME return only sample of last inlets
    """
    i=0
    for inlet in self.inlets:
      sample,timestamp = inlet.pull_sample()
    return sample,timestamp

  def getSamplingRate(self, index):
    """
    return sampling rate of given index stream (in Hz, -1 if stream does not exist)
    """
    if index < self.nb_streams and index >= 0:
      return self.infos[index].nominal_srate()
    else:
      return -1