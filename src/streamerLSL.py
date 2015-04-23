# download LSL and pylsl from https://code.google.com/p/labstreaminglayer/
# Eg: ftp://sccn.ucsd.edu/pub/software/LSL/SDK/liblsl-Python-1.10.2.zip
# put in "lib" folder (same level as user.py)
import sys; sys.path.append('../lib') # help python find pylsl relative to this example program

from pylsl import StreamInfo, StreamOutlet

# WARNING: streamerLSL.StreamerLSL() should be created before  plot.PlotLaunch() is called otherwise won't appear (??)

# Use LSL protocol to broadcast data using one stream for EEG and one stream for AUX
class StreamerLSL():
	# From IPlugin
        def __init__(self, nb_channels, sample_rate, channel_type, ID):
	  """
	  nb_channnels: max number of channels
	  sample_rate: in Hz
	  channel_type: serve as identifier, eg 'PPG" or 'face'
	  ID: unique identifier associated to this stream
	    TODO: check uniqueness
	  """
	  stream_name = channel_type + "_" + str(ID)
	  print "Creating stream:", stream_name, "of type:", channel_type
	  # TODO: use cam/algo for unique id
	  stream_id = stream_name
	  
	  # Create a new stream
	  info_kinect = StreamInfo(stream_name, channel_type, nb_channels, sample_rate,'float32', stream_id);
	  
	  # make outlets
	  self.outlet_kinect = StreamOutlet(info_kinect)
	    
	# send channels values
        # sample: list of float values (one per face)
	def __call__(self, sample):
		self.outlet_kinect.push_sample(sample)

