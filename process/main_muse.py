
import multiprocessing as mpc
import ctypes
import argparse
import numpy as np

import processDummy, processUfuk, processLUV, processMuse
import readerLSL
import plot

import sys; sys.path.append('../src') # help python find // files relative to this script
import sample_rate
import visualization
import streamerLSL

# from http://stackoverflow.com/a/8090605
def rebin(a, shape):
    sh = shape[0],a.shape[0]//shape[0],shape[1],a.shape[1]//shape[1]
    return a.reshape(sh).mean(-1).mean(1)

def getRealData(spectrArray, xDim, yDim, reader, chan, debug, sizeArray):
  """
  Fetch LSL data, deal with all processing
  """

  # Will trigger plots if any
  plot.PlotLaunch()
  name = "Process " + stream + "_" + str(user_id)

  processor = processMuse.ProcessMuse(reader.getSamplingRate(0), chan, attach_plot=debug)

  values = processor.morlet.values
  values_shape = np.shape(values)
  print "Morlet shape:", values_shape

  # maybe use in the futur to adapt panda world size
  sizeArray[0] = values_shape[0]
  sizeArray[1] = values_shape[1]
  
  # Init the thread that will monitor FPS
  monit = sample_rate.PluginSampleRate(name=name)
  monit.activate()
  start_time = 0
  while True:
    sample, timestamp = reader()
    processor(np.array(sample))
    # compute FPS
    monit()
    if  timestamp != None and timestamp - start_time  > 0.1:
      start_time = timestamp 
      # work on local copy
      vcopy = np.array(processor.morlet.values)
      #print vcopy
      if vcopy.max() == 0:
        continue
      # in case copy went wrong, correct
      vcopy = vcopy.reshape(values_shape)

      # rebin x (frequency), ie reduce with average
      # FIXME: will probably crash with sampling rate different than 220 -- xDim and yDim must be divider of original shape
      vcopy = rebin(vcopy, (xDim, yDim))

      # normalize and "move" in scene
      vcopy *= 1.0/vcopy.max() 
      vcopy = vcopy*250 - 300 

      # copy to shared memory and correct "orientation"
      # (we want low freq on the left and new data in front)
      vcopy = vcopy.reshape(yDim*xDim)
      spectrArray[:] = vcopy[::-1]

def runEnv(spectrArray, xDim, yDim ):
  heartRateVar = mpc.Value('f', 0.0)
  heartRate = mpc.Value('i', 0)
  accel_ang1 = mpc.Value('f', 0)
  accel_ang2 = mpc.Value('f', 0)
  print "===== Init panda ====="
  panda3dObj=visualization.MyTapper(spectrArray, xDim, yDim, heartRate, heartRateVar,  accel_ang1,  accel_ang2)
  print "===== End panda ====="
  while True:
    panda3dObj.step()

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
  print "User ID:", user_id
  print "Debug:", debug
  print "Chan:", chan
  
  # init LSL reader
  reader = readerLSL.ReaderLSL(stream, user_id)
  print "Nb streams found:", reader.nb_streams 
  for i in range(reader.nb_streams):
    print reader.getSamplingRate(i), "Hz for channel", i

  xDim = 20
  yDim = 64 

  spectrArray = mpc.Array('f', range(xDim*yDim))
  sizeArray = mpc.Array('i', [-1,-1])

  print "launch main loop" 
  p = mpc.Process(target=getRealData, args=(spectrArray, xDim, yDim, reader, chan, debug, sizeArray))
  p.start()
  print "end main loop" 

  while sizeArray[0] == -1:
    pass

  print "Got size in main proc:", sizeArray[0], " by ", sizeArray[1]
  # TODO: use info to set xDim / yDim 

  print "init env"
  p_env = mpc.Process(target=runEnv, args=(spectrArray, xDim, yDim))
  p_env.start()

  print "Wait for end..."
  p.join()
  p_env.join()
      
  print('Game Over.')
