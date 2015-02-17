from pylab import *
import time
import serial

y=[] 
x=[]
port = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=3.0)
i=0
while(1):
	toto = port.read(5)
	if toto != '\n':
		test= float(toto)
		y.append(test/10)
		print test
		x.append(time.time())
		i+=1
		plot(x, y)
		draw()
		show(block=False)
