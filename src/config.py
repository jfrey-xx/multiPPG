
# well set FPS and LSL sample late for the whole program, whatever the webcam.
MAGIC_FPS = 30
WEBCAM_WIDTH = 640
WEBCAM_HEIGHT = 480

# set "1" to track face every frame, 2 every two frames and so on
TRACKING_RATE=5

# max number of values sent to streamer for PPG vallues
# FIXME: varying depending on algo
LSL_PPG_NB_CHANNELS = 3

# max number of values sent to streamer per face for tracking (x,y,w,h)
LSL_FACE_NB_CHANNELS = 4

# Number of users max per cam
# FIXME: bold move to say only one at the moment
NB_FACES=1
