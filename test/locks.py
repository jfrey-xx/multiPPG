
# trying to make threads communicate, based on http://stackoverflow.com/q/3409593
 
import signal, threading, time

class Listener(threading.Thread):

    def __init__(self, ide):        
        super(Listener, self).__init__()
        self.ide = ide
        self.lock = threading.Lock()

    def run(self):                
        print "Listener", self.ide, "started, waiting for lock..."
        self.lock.acquire()
        print "Got lock", self.ide
        self.lock.release()
        print "Listener released lock", self.ide

if __name__ == "__main__": 
    listener1 = Listener(1)
    listener1.lock.acquire()
    listener1.start()

    listener2 = Listener(2)
    listener2.lock.acquire()
    listener2.start()
    print '* PAUSE'

    print '* RELEASE lock 2'
    listener2.lock.release()
    print 'waiting for thread 2 end'
    listener2.join()

    print '* RELEASE lock 1'
    listener1.lock.release()
    print 'waiting for thread 1 to end'
    listener1.join()

    print('* DONE')
