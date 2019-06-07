import numpy as np
import cv2 as cv #OpenCv is used for image processing
import tkinter as tk #tkinter is used for GUI
import datetime
from PIL import Image,ImageTk #Pillow is used for numpy arrays on images.

#Set up GUI
window = tk.Tk()  # Makes main window
window.wm_title("Background substraction") 
window.config(background="#FFFFFF")
imageFrame = tk.Frame(window, width=1000, height=800)
imageFrame.grid(row=0, column=0, padx=10, pady=2)

#Threshold value, default is 30, but can go from 0 to 100, depending on the light in the image, can be controlled with an slider.
thrvalue=30;

#starts capturing video and get's first frame from the video, this frame is used later a background reference.
#A new frame can be chosen using a button.
#This frame is the original background, if the background is set, any objects that enters the background is highlighted in color, while the background remains black and white.
cap = cv.VideoCapture(0)
_, frame = cap.read()
temp = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
gray = cv.cvtColor(temp, cv.COLOR_BGR2GRAY)

def show_frame():
    global gray2
    _, frame = cap.read()
    color2 = cv.cvtColor(frame, cv.COLOR_BGR2RGB) #Original image from the camera
    gray2 = cv.cvtColor(color2, cv.COLOR_BGR2GRAY) #New gray image to find the difference between live frames and the set frame.

    mask = cv.absdiff(gray,gray2)
    mask = cv.GaussianBlur(mask, (5, 5), 0)
    sliderChange()
    ret, thr = cv.threshold(mask, thrvalue, 255, cv.THRESH_BINARY) #thrValue is used to have the objects in a binary setting.

    kernel = np.ones((4, 4), np.uint8)

    #The next lines are to modified the image so that it can be used more easily with our contours code and the watershed algorithm
    cls = cv.morphologyEx(thr, cv.MORPH_CLOSE, kernel)

    bgl = cv.dilate(cls, None, iterations=4)
    ret, bg = cv.threshold(bgl, 1, 128, 1)
    marker2 = cls + bg
    marker2 = marker2 + 1
    unk = cv.subtract(bg, cls)
    marker2[unk == 255] = 0
    mark8 = np.int32(marker2)

    m = cv.watershed(color2, mark8) #by using the dilatation and the morphology Ex, a shape of the main object can be obtained, if this shape is used in the watershed algorithm
                                    #the watershed will transform the background to black and will get the foreground.
    m = cv.convertScaleAbs(m)
    ret, last = cv.threshold(m, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)

    contours, hierarchy = cv.findContours(cls, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    if len(contours) != 0:
        gray2 = cv.cvtColor(gray2, cv.COLOR_GRAY2BGR)
        c = max(contours, key=cv.contourArea)
        cv.drawContours(mask, c, -1, 255, -1)
        gray2[last == 0] = color2[last == 0]

        M = cv.moments(cls)
        centroidx = int(M['m10'] / M['m00'])
        centroidy = int(M['m01'] / M['m00'])
        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])

        mark8[centroidy, centroidx] = 255
        mark8[extLeft[1], extLeft[0]] = 255
        mark8[extRight[1], extRight[0]] = 255
        mark8[extTop[1], extTop[0]] = 255
        mark8[extBot[1], extBot[0]] = 255

    #The video is displayed in the two display on the GUI
    img1 = Image.fromarray(color2)
    imgtk1 = ImageTk.PhotoImage(image=img1)
    img2 = Image.fromarray(gray2)
    imgtk2 = ImageTk.PhotoImage(image=img2)
    display1.imgtk = imgtk1  # Shows frame for display 1
    display1.configure(image=imgtk1)
    display2.imgtk = imgtk2  # Shows frame for display 2
    display2.configure(image=imgtk2)
    window.after(10, show_frame)

#Updates gray variable to have the new background.
def backgroundSnapshot():
    _, frame = cap.read()
    global gray
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

#Saves the photo from the modified image on the main folder.
def saveSnapshot():
    temp= cv.cvtColor(gray2,cv.COLOR_BGR2RGB)
    cv.imwrite(datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.png',temp)
    
#Gets the value of the slider to update thrValue
def sliderChange():
    global thrvalue
    thrvalue=sl.get()

#Adds labels, video displays and buttons to a grid control.
lb1=tk.Label(imageFrame,text="Original Video")
lb1.grid(row=0, column=0, padx=10, pady=2)
lb2 = tk.Label(imageFrame,text="Background Filter")
lb2.grid(row=0, column=1)
display1 = tk.Label(imageFrame)
display1.grid(row=1, column=0)  # Display 1
display2 = tk.Label(imageFrame)
display2.grid(row=1, column=1)  # Display 2
bkgndBtn=tk.Button(imageFrame,text="Set background", command = backgroundSnapshot)
bkgndBtn.grid(row=2, column=0)
saveBtn=tk.Button(imageFrame,text="Save image",command=saveSnapshot)
saveBtn.grid(row=2,column=1)
sl=tk.Scale(imageFrame,from_=0,to=100,tickinterval=5,orient=tk.HORIZONTAL,length=450)
sl.grid(row=3,column=0)
sl.set(30)
lb3 = tk.Label(imageFrame,text="By: Angel Espinoza")
lb3.grid(row=3, column=1)

show_frame()  # Display
window.mainloop()  # Starts GUI