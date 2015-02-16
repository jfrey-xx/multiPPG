import cv2
from Tkinter import *

selectCam = Tk()

label = Label(selectCam, text="Selection de la camera")
var_choix =IntVar()
choix_1 = Radiobutton(selectCam, text="Camera 0", variable=var_choix, value=0, command=selectCam.quit)
choix_2 = Radiobutton(selectCam, text="Camera 1", variable=var_choix, value=1, command=selectCam.quit)
choix_1.pack()
choix_2.pack()
label.pack()
selectCam.mainloop()
selectCam.destroy()

cap = cv2.VideoCapture(var_choix.get())

while True :
	ret,im = cap.read()
	cv2.imshow('Mesure physiologique camera %d'%var_choix.get(),im)
	key = cv2.waitKey(40)