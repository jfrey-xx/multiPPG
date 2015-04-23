
import argparse
import numpy as np
import processDummy, processUfuk, processLUV
import readerLSL
import plot

# algo 0: processDummy
# algo 1: processLUV
# algo 2: processUfuk

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--stream', default='PPG',
    help="Stream type (default: PPG)")
  parser.add_argument('--algo', default=0,
    help="Algo number (default: 0)")
  parser.add_argument('--user-id', default=0,
    help="User ID (default: 0)")
  parser.add_argument('-d', '--debug', dest='debug', action='store_true',
    help="Enable debug mode")
  parser.set_defaults(debug=False)
  args = parser.parse_args()
  
  try:
    algo = int(args.algo)
    user_id = int(args.user_id)
  except:
    parser.error('Could not parse arguments as integers.')
  stream = args.stream
  debug = args.debug

  print "Stream type:", stream
  print "Algo:", algo
  print "User ID:", user_id
  print "Debug:", debug
  
  # init LSL reader
  reader = readerLSL.ReaderLSL(stream, user_id)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i

  # check/create algo pipeline
  if algo == 0:
    processor = processDummy.ProcessDummy(reader.getSamplingRate(0), attach_plot=debug)
  elif algo == 1:
    processor = processLUV.ProcessLUV(reader.getSamplingRate(0), attach_plot=debug)
  elif algo == 2:
    processor = processUfuk.ProcessUfuk(reader.getSamplingRate(0), attach_plot=debug)
  else:
    raise NameError('AlgoNotFound')
      
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    ret = processor(np.array(sample))
    print ret