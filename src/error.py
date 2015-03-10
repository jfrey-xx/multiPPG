from Tkinter import *
import utility
def webcam_error():
	error = Tk()
	error.resizable(width=False,height=False)
	error.title('Mesure physiologique')
	error.geometry("%dx%d+0+0" % (400, 150))
	error.config(bg=utility.color1)
	error.bind('<Escape>', lambda e: error.quit())
	label_error= Label(cam_frame, text="Select cam")
	error.mainloop()