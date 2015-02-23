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

def main():
	cam = camSelect()
	cap = cv2.VideoCapture(cam)
	root = Tk()

	# Sers seulement pour se reperer
	root.config(bg='blue')


	root.resizable(width=False,height=False)
	root.title('Mesure physiologique camera : {0}'.format(0))
	root.bind('<Escape>', lambda e: root.quit())

	# Frame of the selection of measure (RIGHT)
	cal_fram = Frame(root, borderwidth=1)
	cal_fram.pack(side="right")
	select_label = Label(cal_fram, text="Selection du calcul")
	select_label.config(font=font_title)
	select_label.pack(side="top")
	cal = 0
	measure = Radiobutton(cal_fram, text="Rythme Cardiaque", variable=cal, value=1)
	measure.config(font=font_other)
	measure.pack(side="right")
	# Frame of key description(TOP)
	label_frame = Frame(root, borderwidth=1)
	label_frame.pack(anchor=W)
	escape_label = Label(label_frame, text="Press ESC to close")
	escape_label.config(font=font_title)
	escape_label.pack(side="top")
	lmain = Label(root)
	lmain.pack()

	def show_frame():
		_, frame = cap.read()
		frame = cv2.flip(frame, 1)
		cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
		img = Image.fromarray(cv2image)
		imgTK = ImageTk.PhotoImage(image=img)
		lmain.imgTK = imgTK
		lmain.configure(image=imgTK)
		lmain.after(10, show_frame)
	show_frame()
	root.mainloop()

if __name__ == '__main__':
		main()	