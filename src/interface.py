import multiprocessing
from Tkinter import *
import utility
import error
import cv2
import video

##
# @brief Send to video.start the numero of the cam used.
#  
def envoiCam():
    video.start_proc(cam.get())
##
# @brief The fonction gui is the starter of the graphic interface
# It's catch the different cam, display the different label or button.
# The button start permit to lunch OpenCv Capture. (call the fonction start of the file video.py)
#  
def gui():
    print utility.system #Print OS
    root = Tk()
    root.resizable(width=False,height=False)
    root.title('Mesure physiologique')
    root.geometry("%dx%d+0+0" % (400, 150))
    root.config(bg=utility.color1)
    root.bind('<Escape>', lambda e: root.quit())
    label_frame = Frame(root, borderwidth=1)
    label_frame.config(bg=utility.color1)
    label_frame.pack(side='top')


    escape_label = Label(label_frame, text="Press ESC to close")
    escape_label.config(font=utility.font_title,bg=utility.color1)
    escape_label.pack(anchor=N)
    cam_frame = Frame(root,borderwidth=1)
    cam_frame.config(bg=utility.color1)
    cam_frame.pack(side='left')
    label_cam = Label(cam_frame, text="Select cam")
    label_cam.pack()
    label_cam.config(font=utility.font_title,bg=utility.color1)
    global cam
    cam = IntVar()
    ###################For LINUX###################
    if utility.system == "linux" or utility.system == "linux2":
        global tab
        tab = utility.transWebcamString()
        if not len(tab)==0:
            for i in range (0,len(tab)):
                print tab[i]
                choice = Radiobutton(cam_frame, text=tab[i], variable=cam, value=i, command=None)
                choice.config(font=utility.font_other,bg=utility.color1)
                choice.pack(anchor=W)
        else :
                error.webcam_error()
    ###################For WINDOWS###################
    else :
        isok=True
        while isok:
            cap=cv2.VideoCapture(i)
            choice = Radiobutton(cam_frame, text="Camera {0}".format(i-1), variable=cam, value=i-1, command=None)
            choice.config(font=utility.font_other,bg=utility.color1)
            choice.pack(anchor=W)
            isok=cap.isOpened()

    camChoice=cam.get()
    button_frame =Frame(root,borderwidth=1)
    button_frame.config(bg=utility.color1)
    button_frame.pack(side='right')


    startbutton=Button(button_frame,width=10,height=1,text='Start Video',command=envoiCam)
    stopbutton=Button(button_frame,width=10,height=1,text='Stop', command=video.stop)
    startbutton.config(bg=utility.color1)
    stopbutton.config(bg=utility.color1)
    startbutton.pack()
    stopbutton.pack()

    root.mainloop()