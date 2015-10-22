
import argparse
import numpy as np

import processDummy, processUfuk, processLUV, processMuse
import readerLSL
import plot

import sys; sys.path.append('../src') # help python find // files relative to this script
import sample_rate
import streamerLSL

# algo 0: processDummy
# algo 1: processLUV
# algo 2: processUfuk
# algo 3: processMuse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--stream', default='PPG',
    help="Stream type (default: PPG)")
  parser.add_argument('--algo', default=3,
    help="Algo number (default: 3)")
  parser.add_argument('--user-id', default=0,
    help="User ID (default: 0)")
  parser.add_argument('-d', '--debug', dest='debug', action='store_true',
    help="Enable debug mode")
  parser.add_argument('--chan', default=0,
    help="Chan number to process, depending algo (default: 0)")
  parser.set_defaults(debug=False)
  args = parser.parse_args()
  
  try:
    algo = int(args.algo)
    user_id = int(args.user_id)
  except:
    parser.error('Could not parse arguments as integers.')
  stream = args.stream
  debug = args.debug
  chan = args.chan

  print "Stream type:", stream
  print "Algo:", algo
  print "User ID:", user_id
  print "Debug:", debug
  print "Chan:", chan
  
  # init LSL reader
  reader = readerLSL.ReaderLSL(stream, user_id)
  print "Nb streams found:", reader.nb_streams 
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i
  
  # At the moment only one algo for EEG, number 3
  if algo == 3:
    processor = processMuse.ProcessMuse(reader.getSamplingRate(0), chan, attach_plot=debug)
  else:
    raise NameError('AlgoNotFound')
      
  # FIXME: parameters for output channel
  fps = reader.getSamplingRate(0) 

  # Will trigger plots if any
  plot.PlotLaunch()
  
  name = "Process " + stream + "_" + str(user_id)
  # Init the thread that will monitor FPS
  monit = sample_rate.PluginSampleRate(name=name)
  monit.activate()
  
  while True:
    sample, timestamp = reader()
    processor(np.array(sample))
    # compute FPS
    monit()
