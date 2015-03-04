from Tkinter import *
import cv2
import webcamSelect
import faceDetector
import interface
from PIL import Image, ImageTk
import os.path
font_title=('courier', 12,'bold')
font_other=('courier', 10,'bold')
def main():

	cam = webcamSelect.camSelect()
	cap = cv2.VideoCapture(cam)
	feed =cap.read()
	# faces = cv2.QueryFrame(cam)
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
		return frame
	frame = show_frame()
	root.bind('<b>', lambda e: faceDetector.detector(feed,frame))

	root.mainloop()

if __name__ == '__main__':
		main()	