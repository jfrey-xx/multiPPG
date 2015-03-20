import sys; sys.path.append('../lib/mtKinter') # help python find mtKinter relative to this example program
import mtTkinter as Tkinter # bypass some Tkinter internals to make it complient with threads
import matplotlib.pyplot as plt 
from threading import Thread


class Plotter(Thread):
  """
  Use threads to update regularely a data plot
  FIXME: buggy because of Tkinter (on close and one plot only ??)
  """
  
  def __init__(self, sample_rate, window_length=1, polling_interval=0.1):
    """
    sample_rate: at which rate values will be sent (in Hz). NB: will be cast to int!
    window_length: time length of plot (in seconds)
    polling_interval: will redraw plot every XX seconds
    """
    Thread.__init__(self)
    self.polling_interval = polling_interval
    self.sample_rate = int(sample_rate)
    self.queue_size = self.sample_rate*window_length
    
    # fifo for temporal filter
    self.values =  [0]*self.queue_size
    # for plot: X
    self.x=range(0,self.queue_size)

    self.daemon = True
    self.running = True
    self.start()
    
    
  def run(self):
      # initialize figure
      plt.figure() 
      ln, = plt.plot(self.values)
      plt.ion()
      plt.show()

      while True:
        plt.pause(self.polling_interval)
        if self.running:
          # kinda autoscale
          ymin = min(self.values)
          ymax = max(self.values)
          delta = ymax-ymin
          plt.ylim(ymin-delta-1, ymax+delta+1) # "+1": safeguard in case we got nothing but the same value
          ln.set_ydata(self.values)
          plt.draw()
        else:
          break
      
  def __del__(self):
    self.running = False
    print "del"
        
  def push_value(self, value):
      """
      One new value for the plot
      """
      # One goes out, one goes in
      self.values.pop(0)
      self.values.append(value)
        
    
