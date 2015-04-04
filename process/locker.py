
# An interface between sender and receiver for callback function so it is possible to parallelize computations
# The idea behind: non-blocking call for sender when data is push, blocking for receiver
 
from threading import Thread, Lock

class ICallbackFunction():
    """
    interface for callback mechanism
    @param fun: client's function to be called upon value change
    """
    def __init__(self, caller, fun):
        self.caller = caller
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

    def __call__(self, new_values, all_values):
        """
        Must be redefined by classes that implements
        """
        raise NameError("NotImplementedError")

class CallbackNow(ICallbackFunction):
    """
    Not threaded, pass directly new values -- there will not be loss, but lag/drift are more likely
    """
    def __call__(self, new_values, all_values):
        self.fun(self.caller, new_values)

class CallbackLazy(ICallbackFunction,Thread):
    """
    Threaded, could miss values, will do computations when it could
    FIXME: for sure we could do things to optimize and ensure sync
    """
    def __init__(self, caller, fun):
        # register thread, pass function to upper class
        Thread.__init__(self)
        ICallbackFunction.__init__(self, caller, fun)
        self.daemon = True
        # all the magic is here. Blocking locks for thread, non-blocking for exterior, two of them to sychronize processing.
        self.lockWaiter = Lock() # make local thread wait
        self.lockWaiter.acquire()
        #self.lockIdle = Lock() # locked by local thread once done computations
        self.start()
        # data that be passed between exterior and local threads
        self.data = None
        # a flag set by caller to ensure that run won't process something already seen
        self.new_data = False
        # set by runner, to detect if 
        # TODO: use queue to communicate?
        self.working = False

    def __call__(self, new_values, all_values):
        """
        New values coming, try to tell that to the local thread
        """
        print "Lazy call, try acquire waiter"
        # if we manage to acquire lock (non-blocking call), it means that the run thread could use some data, leave it a message
        if(self.lockWaiter.acquire(False)):
            print "Lazy call, got waiter"
            self.data = all_values
            self.new_data = True
            self.lockWaiter.release()
        else:
            print "lazy call, missing data"
                
    def run(self):
        """
        as soon as we got the opportunity: execute function
        """
        while True:
            print "Lazy run, try to acquire waiter"
            if(self.lockWaiter.acquire()): # blocking
                print "lazy run, got waiter"
                # we are sure nobody will mess up with our data, copy it and run a new job
                data = self.data
                # release immediately, then process if we have new data
                self.lockWaiter.release()
                if self.new_data:
                    self.new_data = False
                    self.fun(self.caller, data)

