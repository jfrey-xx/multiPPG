import multiprocessing
from Tkinter import *
import utility
import error
import cv2
import video


value =''

##
# @brief Send to video.start the numero of the cam used.
#  
def sendCam():
    video.start_proc(cam.get(),tab,algo.get())

def actualiseLabel(value):
    print value_label
    value_label.config(text=value)
    

##
# @brief The fonction gui is the starter of the graphic interface
# It's catch the different cam, display the different label or button.
# The button start permit to lunch OpenCv Capture. (call the fonction start of the file video.py)
#  
def gui():
    print "OS : ",utility.system #Print OS
    root = Tk()
    root.resizable(width=False,height=False)
    root.title('Mesure physiologique')
    root.wm_geometry("")
    root.config(bg=utility.color1)
    root.bind('<Escape>', lambda e: root.quit())
    label_frame = Frame(root, borderwidth=1)
    label_frame.config(bg=utility.color1)
    label_frame.pack(side='top')

####################################Title ####################################
    escape_label = Label(label_frame, text="Press ESC to close")
    escape_label.config(font=utility.font_other,bg=utility.color1)
    escape_label.pack(anchor=N)
    global value_label
    value_label = Label(label_frame,text=value)
    value_label.pack()

####################################Select CAM ####################################

    cam_frame = Frame(root,borderwidth=1)
    cam_frame.config(bg=utility.color1)
    cam_frame.pack(side='left')
    label_cam = Label(cam_frame, text="Select cam")
    label_cam.pack()
    label_cam.config(font=utility.font_title,bg=utility.color1)
    global cam
    cam = IntVar()
    #------------------- For LINUX -------------------
    if utility.system == "linux" or utility.system == "linux2":
        global tab
        tab = utility.transWebcamString()
        length=len(tab)
        if not length==0:
            for i in range (0,length):
                choice = Radiobutton(cam_frame, text=tab[length-i-1], variable=cam, value=i, command=None)
                choice.config(font=utility.font_other,bg=utility.color1)
                choice.pack(anchor=W)
        else :
                error.webcam_error()
    #------------------- For Other -------------------
    else :
        isok=True
        i=0
        while isok:
            cap=cv2.VideoCapture(i)
            choice = Radiobutton(cam_frame, text="Camera {0}".format(i-1), variable=cam, value=i-1, command=None)
            choice.config(font=utility.font_other,bg=utility.color1)
            choice.pack(anchor=W)
            isok=cap.isOpened()
            i+=1

    camChoice=cam.get()

#################################### Select Algorithm ####################################
    global algo
    algo = IntVar()

    algo_frame= Frame(root,borderwidth=1)
    algo_frame.config(bg=utility.color1)
    algo_frame.pack(anchor=E)

    algo_label = Label(algo_frame,text="Select an algorithm")
    algo_label.config(font=utility.font_title,bg=utility.color1)
    algo_label.pack(anchor=W)

    algochoice=Radiobutton(algo_frame, text="PPG", variable=algo, value=0, command=None)
    algochoice.config(bg=utility.color1)
    algochoice.pack(anchor=W)

    algochoice=Radiobutton(algo_frame, text="Eularian", variable=algo, value=1, command=None)
    algochoice.config(bg=utility.color1)
    algochoice.pack(anchor=W)

#################################### Button START/STOP ####################################

    button_frame =Frame(root,borderwidth=1)
    button_frame.config(bg=utility.color1)
    button_frame.pack(anchor=SW)

    startbutton=Button(button_frame,width=10,height=1,text='Start Video',command=sendCam)
    stopbutton=Button(button_frame,width=10,height=1,text='Stop', command=video.stop)
    startbutton.config(bg=utility.color1)
    stopbutton.config(bg=utility.color1)
    startbutton.pack()
    stopbutton.pack()
    root.mainloop()