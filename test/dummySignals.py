 
import sys; sys.path.append('../src') # help python find pylsl relative to this example program
from streamerLSL import *
import sample_rate
import time
from Tkinter import *
from threading import Thread

# main params
nbPlayers = 3
FPS=30

class GUI(Thread):
  def __init__(self):
    Thread.__init__(self)
    self.init = False
    self.daemon = True
    
    self.BMPs = []
    self.idx = []
    self.detections = []
    
    self.start()
    
  def run(self):
    self.master = Tk()
    
    # init cursors
    for i in range(nbPlayers):
      w = Label(self.master, text="Player " + str(i))
      w.pack()
      self.BMPs.append(Scale(self.master, from_=50, to=200, orient=HORIZONTAL, label="BPM"))
      self.BMPs[-1].pack()
      self.idx.append(Scale(self.master, from_=-100, to=100, orient=HORIZONTAL, label="idx"))
      self.idx[-1].pack()
      self.detections.append(Scale(self.master, from_=-1, to=1, orient=HORIZONTAL, label="detection"))
      self.detections[-1].pack()
      
    self.w = Scale(self.master, from_=0, to=100, orient=HORIZONTAL)
    #self.w.pack()

    self.w2 = Scale(self.master, from_=0, to=100, orient=HORIZONTAL)
    #self.w2.pack()
    
    self.init = True
    mainloop()
                                 

# init LSL streams
streamerDetections = []
streamerBPMs = []
for i in range(nbPlayers):
  streamerDetections.append(StreamerLSL(1,FPS,"detection",i))
  streamerBPMs.append(StreamerLSL(2,FPS,"BPM",i))

# init monitor and GUI
monit = sample_rate.PluginSampleRate(name="dummy")
monit.activate()
gui=GUI()

while True:
  monit()
  # Once GUI is set, push values to all streams
  if gui.init:
    for i in range(nbPlayers):
      #print "player", i
      bpm = gui.BMPs[i].get()
      idx = gui.idx[i].get()
      detection = gui.detections[i].get()
      #print "BPM:", bpm, ", idx:", idx, ", detection:", detection
      streamerDetections[i]([detection])
      streamerBPMs[i]([idx,bpm])
  time.sleep((1./FPS))