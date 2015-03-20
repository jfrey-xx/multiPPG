# download LSL and pylsl from https://code.google.com/p/labstreaminglayer/
# Eg: ftp://sccn.ucsd.edu/pub/software/LSL/SDK/liblsl-Python-1.10.2.zip
# put in "lib" folder (same level as user.py)
import sys; sys.path.append('../lib') # help python find pylsl relative to this example program

from pylsl import StreamInfo, StreamOutlet

# Use LSL protocol to broadcast data using one stream for EEG and one stream for AUX
class StreamerLSL():
	# From IPlugin
        def __init__(self, nb_channels, sample_rate):
                self.nb_channels = nb_channels
                self.sample_rate = sample_rate
                # TODO: as many stream as we got algo
		kinect_stream = "kinect_data"
                kinect_id = "kinect_id1"
		
		# Create a new stream
		info_kinect = StreamInfo(kinect_stream, 'PPG', self.nb_channels,self.sample_rate,'float32',kinect_id);
		
		# make outlets
		self.outlet_kinect = StreamOutlet(info_kinect)
	    
	# send channels values
        # sample: list of float values
	def __call__(self, sample):
                # FIXME: in fact we receive a list of tuples
		self.outlet_kinect.push_sample(list(sample[0]))

