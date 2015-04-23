
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
  parser.add_argument('--stream',
    help="Stream type, eg 'PPG'")
  parser.add_argument('--algo',
    help="Algo number")
  parser.add_argument('--user-id',
    help="User ID")
  args = parser.parse_args()
  
  if not (args.stream and args.algo and args.user_id):
    parser.error('You must specify all arguments.')
  else:
    try:
      algo = int(args.algo)
      user_id = int(args.user_id)
    except:
      parser.error('Could not parse arguments as integers.')
    stream = args.stream

  print "Stream type:", stream
  print "Algo:", algo
  print "User ID:", user_id
  
  # init LSL reader
  reader = readerLSL.ReaderLSL(stream, user_id)
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i

  # check/create algo pipeline
  if algo == 0:
    processor = processDummy.ProcessDummy(reader.getSamplingRate(0))
  elif algo == 1:
    processor = processUfuk.ProcessUfuk(reader.getSamplingRate(0))
  elif algo == 2:
    processor = processLUV.ProcessLUV(reader.getSamplingRate(0))
  else:
    raise NameError('AlgoNotFound')
      
  # Will trigger plots if any
  plot.PlotLaunch()
  
  while True:
    sample, timestamp = reader()
    ret = processor(np.array(sample))
    print ret