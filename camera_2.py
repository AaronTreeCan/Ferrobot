from __future__ import print_function
from PIL import Image as Imgp
from PIL import ImageTk
import threading
import datetime
import imutils
import cv2
import os
from picamera2 import Picamera2, Preview
from imutils.video import VideoStream
import argparse
import time
import RPi.GPIO as GPIO #MUST CONNECT GND LED pin to ic pins. 
import time
import tkinter as tki
#from mttkinter import mtTkinter as tki
import PySimpleGUI as sg
import io
import editor_page
import pages
import camera

class PhotoBoothApp:
    

    def __init__(self, cap):

        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        
        self.vs = camera.cap                    # initialize camera object (as Ras Pi camera)
        self.frame = None               # initialize video frame for continuous video display (set to None initially, will receive frames from camera during operation)
        self.thread = None              # initialize thread object, we need threading to switch between continuous video display and image capturing (initialize as None) 
        self.stopEvent = None           # initialize stop event for the function passed to the thread (this function will be the continuous video display), after stopping we capture the frame, then continue thread
        #self.root = tki.Tk()            # initialize the root window 
        self.root = tki.Toplevel(editor_page.window)
        self.panel = None  

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()
        #editor_page.window.bind("<<newwin>>",new_window)

    def videoLoop(self):
        
        # added try statment here to avoid RuntimeErrors while threading
        
                                                                        
            # keep looping over frames until we are instructed to stop
            while not self.stopEvent.is_set():                          

                
                
                # grab the frame from the video stream and resize it to have a maximum width of 300 pixels
                self.vs = camera.cap                                            
                self.frame = self.vs.capture_array()
                self.frame = imutils.resize(self.frame, width=1080)
                
        
                # OpenCV represents images in BGR order; however PIL
                # represents images in RGB order, so we need to swap
                # the channels, then convert to PIL and ImageTk format
                
                #convert image from opencv to pillow (PIL) format 
                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)     # opencv represents images in BGR order however PIL represents images in RGB order, so we need to swap the channels first
                image = Imgp.fromarray(image) 
                image = ImageTk.PhotoImage(image)



                # if the panel is None, we need to initialize it
                if self.panel is None:     
                    self.panel = tki.Label(image=image)
                    self.panel.image = image
                    self.panel.pack(side="left", padx=10, pady=10)

                else:   # otherwise, simply update the panel
                    self.panel.configure(image=image)
                    self.panel.image = image

        


def run_preview():
    pba = PhotoBoothApp(camera.cap)
    pba.root.mainloop()