import cv2
from Tkinter import *


# fenetre = Tk()
# champ_label = Label(fenetre, text="contenu de notre champ label")
# var_choix = IntVar()
# choix_rouge = Radiobutton(fenetre, text="Camera 0", variable=var_choix, value=0)
# choix_vert = Radiobutton(fenetre, text="Camera 1", variable=var_choix, value=1)
# choix_rouge.pack()
# choix_vert.pack()
# champ_label.pack()
cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

while True :
	ret,im = cap.read()
	cv2.imshow('Mesure physiologique 0',im)
	key = cv2.waitKey(40)
	ret2,im2 = cap2.read()
	cv2.imshow('Mesure physiologique 1',im2)
	key2 = cv2.waitKey(40)
# fenetre.mainloop()
