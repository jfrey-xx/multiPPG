import interface
import video
import argparse

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--webcam',
    help="Webcam number")
  parser.add_argument('--algo',
    help="Algo number")
  args = parser.parse_args()
  
  # no argument triggers GUI, if there is one, thene everything is taken from CLI
  if args.webcam or args.algo:
    if not (args.webcam and args.algo):
      parser.error('Shall you use CLI, you must specify all arguments.')
    else:
      try:
        webcam = int(args.webcam)
        algo= int(args.algo)
      except:
        parser.error('Could not parse arguments as integers.')
      print "Using CLI"
      print "Webcam selected:", webcam
      print "Algo selected:", algo
      video.start_proc(webcam,algo)
  else:
    print "Starting GUI"
    interface.gui()
