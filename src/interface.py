import multiprocessing
from Tkinter import *
import utility
import error
import cv2
import video
import re

value =''

##
# @brief Send to video.start the numero of the cam used.
#  
def sendCam():
    video.start_proc(cam.get(),algo.get(),userID.get())

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
    label_frame.pack()

####################################Title ####################################
    escape_label = Label(label_frame, text="Press ESC to close")
    escape_label.config(font=utility.font_other,bg=utility.color1)
    escape_label.pack(anchor=N)

####################################Select CAM ####################################

    cam_frame = Frame(root,borderwidth=5)
    cam_frame.config(bg=utility.color1)
    cam_frame.pack()
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
                # /dev/videoXX may not be sequential, try to extrat dev number
                try:
                    cam_id = re.findall(r'\d+', tab[i])[0]
                except:
                    cam_id = i
                choice = Radiobutton(cam_frame, text=tab[i], variable=cam, value=cam_id, command=None)
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

    algo_frame= Frame(root,borderwidth=5)
    algo_frame.config(bg=utility.color1)
    algo_frame.pack()

    algo_label = Label(algo_frame,text="Select an algorithm")
    algo_label.config(font=utility.font_title,bg=utility.color1)
    algo_label.pack()

    algochoice=Radiobutton(algo_frame, text="Dummy", variable=algo, value=0, command=None)
    algochoice.config(bg=utility.color1)
    algochoice.pack(anchor=W)
    
    algochoice=Radiobutton(algo_frame, text="LUV", variable=algo, value=1, command=None)
    algochoice.config(bg=utility.color1)
    algochoice.pack(anchor=W)
    
    algochoice=Radiobutton(algo_frame, text="Ufuk NG", variable=algo, value=2, command=None)
    algochoice.config(bg=utility.color1)
    algochoice.pack(anchor=W)
    
#################################### Subject ID ####################################
    global userID
    userID_frame= Frame(root,borderwidth=5)
    userID_frame.config(bg=utility.color1)
    userID_frame.pack()
    userID_label = Label(userID_frame,text="User ID")
    userID_label.config(font=utility.font_title,bg=utility.color1)
    userID_label.pack()
    userID = Spinbox(userID_frame, from_=0, to=99)
    userID.pack()
    
#################################### Button START/STOP ####################################

    button_frame =Frame(root,borderwidth=5)
    button_frame.config(bg=utility.color1)
    button_frame.pack()

    startbutton=Button(button_frame,width=10,height=1,text='Start Video',command=sendCam)
    stopbutton=Button(button_frame,width=10,height=1,text='Stop', command=video.stop)
    startbutton.config(bg=utility.color1)
    stopbutton.config(bg=utility.color1)
    startbutton.pack()
    stopbutton.pack()
    root.mainloop()