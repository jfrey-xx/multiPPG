import data

class Invert(data.DataBuffer):
  """
  Test case: takes a data and revert values. Output: signal buffer.
  """
  def __init__(self, input_signal_buffer, attach_plot = False, name = "invert"):
    self.input_buffer = data.DataBuffer(input_signal_buffer.sample_rate, input_signal_buffer.queue_size, input_data=input_signal_buffer)
    data.DataBuffer.__init__(self, self.input_buffer.sample_rate, self.input_buffer.queue_size, input_data=self.input_buffer, attach_plot = attach_plot, name = name)
    self.input_buffer.add_callback(self)

    
  def __call__(self, data_buffer):
    self.values = self.input_buffer.values * -1
    