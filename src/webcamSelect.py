import cv2
from Tkinter import *
import os.path
def camSelect():
	selectCam = Tk()
	selectCam.resizable(width=False, height=False)
	selectCam.title('Choix webcam')
	selectCam.bind('<Escape>',exit)
	label = Label(selectCam, text="Selection de la camera")
	cam =IntVar()
	i=0
	while os.path.exists("/dev/video%d"%i):
		choix = Radiobutton(selectCam, text="Camera {0}".format(i), variable=cam, value=i, command=selectCam.quit)
		choix.pack()
		i+=1
	label.pack()
	selectCam.geometry('{}x{}'.format(200, 50+10*i))
	selectCam.mainloop()
	selectCam.destroy()
	return cam.get()

def test():
	print "coucou"	

def main():
	cam = camSelect()
	cap = cv2.VideoCapture(cam)
	# cap.set(3,1020) # set(ID, valeur), ou ID=3 pour la largeur et ID=4 pour la hauteur.
	# cap.set(4,940)
	while True:
		ret,img = cap.read()
		height, width = img.shape[:2]
		cv2.putText(img, "Press ESC to close", (5, 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,0,0))
		cv2.putText(img, "Press s to begin process", (5, 40), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,0,0))
		cv2.imshow('Mesure physiologique camera : {0}'.format(cam),img)
		key = cv2.waitKey(10)& 0xFF
		# print key #affiche la valueur de la touche enfoncée
		if key==27:	
			cv2.destroyAllWindows()
			break
			cap.release()
		if key == ord('s'):
			test()


if __name__ == '__main__':
		main()	