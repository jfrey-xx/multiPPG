 
class IheartBeat():
  """
  Interface for the different heartBeat algorithm, methods should be overriden
  """
  def __init__(self, *args, **kwargs):
    print "start algo",
    if self.name:
      print self.name
 
  def process(self, frame):
    print "processing..."
  