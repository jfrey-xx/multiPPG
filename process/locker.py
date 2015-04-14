
# An interface between sender and receiver for callback function so it is possible to parallelize computations
# The idea behind: non-blocking call for sender when data is push, blocking for receiver
 
from threading import Thread, Lock
import numpy as np

class ICallbackFunction():
    """
    interface for callback mechanism
    @param fun: client's function to be called upon value change
    """
    def __init__(self, fun):
        self.fun = fun

    #def register_sender(self,sender_function):
    #    """
    #    Set function of the sender
    #    """
    #    pass

    #def register_receiver(self, receiver):
    #    """
    #    Set function to be called by receiver
    #   """
    #   pass

    def __call__(self, all_values, new_values):
        """
        Must be redefined by classes that implements
        """
        raise NameError("NotImplementedError")

class CallbackNow(ICallbackFunction):
    """
    Not threaded, pass directly new values -- there will not be loss, but lag/drift are more likely
    """
    def __call__(self, all_values, new_values):
        self.fun(all_values, new_values)

class CallbackLazy(ICallbackFunction,Thread):
    """
    Threaded, could miss values, will do computations when it could
    FIXME: for sure we could do things to optimize and ensure sync
    """
    def __init__(self, fun):
        # register thread, pass function to upper class
        Thread.__init__(self)
        ICallbackFunction.__init__(self, fun)
        self.daemon = True
        # all the magic is here. Blocking locks for thread, non-blocking for exterior, two of them to sychronize processing.
        self.lockWaiter = Lock() # make local thread wait
        self.lockWaiter.acquire()
        #self.lockIdle = Lock() # locked by local thread once done computations
        # data that be passed between exterior and local threads
        self.new_values = None
        self.all_values = None
        # a flag set by caller to ensure that run won't process something already seen
        self.new_data = False
        # set by runner, to detect if 
        # TODO: use queue to communicate?
        self.working = False
        self.start()

    def __call__(self, all_values, new_values):
        """
        New values coming, try to tell that to the local thread
        """
        #print "Lazy call, try acquire waiter"
        # if we manage to acquire lock (non-blocking call), it means that the run thread could use some data, leave it a message
        if True: #(self.lockWaiter.acquire(False)):
            #print "Lazy call, got waiter"
            self.all_values = all_values
            self.new_values = new_values
            self.new_data = True
            #self.lockWaiter.release()
            pass
        else:
            print "lazy call, missing data"
                
    def run(self):
        """
        as soon as we got the opportunity: execute function
        """
        while True:
            #print "Lazy run, try to acquire waiter"
            if True:  # blocking
                #print "lazy run, got waiter"
                # release immediately, then process if we have new data
                #self.lockWaiter.release()
                if True:
                    self.working = True
                    # we are sure nobody will mess up with our data, copy it and run a new job
                    all_values = self.all_values
                    new_values = self.new_values
                    # give some time to the data to come
                    if all_values is not None and new_values is not None:
                        self.new_data = False
                        self.fun(all_values, new_values)
                        self.working = False

