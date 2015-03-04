from Tkinter import *
import cv2
from PIL import Image, ImageTk
import os.path
font_title=('courier', 12,'bold')
font_other=('courier', 10,'bold')
def camSelect():
	selectCam = Tk()
	selectCam.config(bg='#AED9FA')
	selectCam.resizable(width=False, height=False)
	selectCam.title('webcam choice')
	selectCam.bind('<Escape>',exit)
	label = Label(selectCam, text="Select cam")
	label.config(font=font_title,bg='#AED9FA')
	label.pack()
	cam =IntVar()
	isok=True
	i=1
	while isok:
		cap=cv2.VideoCapture(i)
		isok=cap.isOpened()
		choix = Radiobutton(selectCam, text="Camera {0}".format(i-1), variable=cam, value=i-1, command=selectCam.quit)
		choix.config(font=font_other,bg='#AED9FA')
		choix.pack()
		i+=1
	selectCam.geometry('{}x{}'.format(200, 50+10*i))
	selectCam.mainloop()
	selectCam.destroy()
	return cam.get()
