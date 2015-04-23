import time
import timeit
from threading import Thread

# try to ease work for main loop
class Monitor(Thread):
        def __init__(self, name=None):
                Thread.__init__(self)
                self.global_nb_samples_out = -1
                self.nb_samples_out = -1

                # Init time to compute sampling rate
                self.tick = timeit.default_timer()
                self.start_tick = self.tick
                self.polling_interval = 10
                self.name = ""

        def run(self):
                while True:
                        # check FPS + listen for new connections
                        new_tick = timeit.default_timer()
                        elapsed_time = new_tick - self.tick
                        current_samples_out = self.global_nb_samples_out
                        print "--" + str(self.name) + "--",
                        print "at t: ", (new_tick - self.start_tick),
                        print "\telapsed_time: ", elapsed_time,
                        print "\tnb_samples_out: ", current_samples_out - self.nb_samples_out,
                        sampling_rate = (current_samples_out - self.nb_samples_out)  / elapsed_time
                        print "\tsampling rate: ", sampling_rate
                        self.tick = new_tick
                        self.nb_samples_out = current_samples_out
                        time.sleep(self.polling_interval)

class PluginSampleRate():
        # @polling_time: will print FPS every xx seconds
        def __init__(self, polling_time=1, name=""):
                """
                name: if set, will be added in output
                """
                self.monit = Monitor()
                self.monit.polling_interval = polling_time
                self.monit.name = name
                
        # update counters value
        def __call__(self):
                self.monit.global_nb_samples_out = self.monit.global_nb_samples_out + 1
        
        # Instanciate "monitor" thread
        def activate(self):
                # daemonize thread to terminate it altogether with the main when time will come
                self.monit.daemon = True
                self.monit.start()

