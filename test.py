import cv2
from Tkinter import *
import os.path

selectCam = Tk()
selectCam.resizable(width=False, height=False)
selectCam.title('Choix webcam')
selectCam.geometry('{}x{}'.format(200, 70))
selectCam.bind('<Escape>',exit)
label = Label(selectCam, text="Selection de la camera")
var_choix =IntVar()
i=0
while os.path.exists("/dev/video%d"%i):
	choix = Radiobutton(selectCam, text="Camera %d"%i, variable=var_choix, value=i, command=selectCam.quit)
	choix.pack()
	i+=1
label.pack()
selectCam.mainloop()
selectCam.destroy()

cap = cv2.VideoCapture(var_choix.get())
while go :
	ret,im = cap.read()
	cv2.imshow('Mesure physiologique camera %d'%var_choix.get(),im)
	key = cv2.waitKey(40)
	print key
	if key== 1048603 or key==27:
		cv2.destroyAllWindows()
		break

	