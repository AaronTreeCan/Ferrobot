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
import PySimpleGUI as sg
import io
import editor_page
import pages
import printer
import numpy as np
import parse
sdi = 5
clk = 6
le = 26
oe = 16
clock = 1000
GPIO.setwarnings(False)


final_image = []
extracted_image = []
CAMERA_CONNECTED = False
stopevent_flag = threading.Event()
capture_flag = threading.Event()
cap = Picamera2() 
# set camera parameters
cap.options["quality"] = 100
cap.options["compress_level"] = 0
cap.options["resolution"] = (1080,720)
cap.options["framerate"] = 20

import time
#config = vs.create_preview_configuration({"size" : (7800,5700), "format": "RGB888"})
config = cap.create_preview_configuration({"size" : (1080,720), "format": "RGB888"}) #quick processing
#config = cap.create_preview_configuration({"size" : (720,480)}) #quick processing

    # start camera
cap.configure(config)
cap.set_controls({"AfTrigger": 0, "AnalogueGain": 1.0, "AwbEnable": 0, "AfMode": 0, "AfSpeed":1})
#cap.start()
#preview_checkbox = sg.Checkbox("Activate preview", default=start_preview, enable_events=False, key="_preview_mode_")

# This subroutine moves the camera to a predefined position and takes an
# image. Both a camera and a printer must be connected for this to work
# properly. It returns the image taken.

def adjust_exposure(exposure_time):
    expT = exposure_time
    with cap.controls as controls:
        controls.ExposureTime = int(expT * 1000000)          # adjust camera exposure time based on the user input, the exposure should be in microseconds
    import time


def adjust_exposure2(expT):
    with cap.controls as controls:
        controls.ExposureTime = int(expT * 1000000)          # adjust camera exposure time based on the user input, the exposure should be in microseconds
    import time
    
def adjust_focus():
    cap.autofocus_cycle()

def adjust_res(X_res, Y_res):
    cap.options["resolution"] = (X_res, Y_res)
    config = cap.create_preview_configuration({"size" : (X_res,Y_res), "format": "RGB888"})
    cap.configure(config)

def take_image(file_path):
    global final_image

    cap.start()
    cap.autofocus_cycle()
    frame = cap.capture_array()    
    

    frame = imutils.resize(frame, width=720)
    final_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # opencv represents images in BGR order however PIL represents images in RGB order, so we need to swap the channels first
    image = Imgp.fromarray(final_image) 
    
    bio = io.BytesIO()
    image.save(bio, format= 'PNG')
    imgbytes = bio.getvalue()
    print(type(imgbytes))
    

    #final_image = ImageTk.PhotoImage(image) 
    image.save(file_path, format='JPEG')
    cap.stop()
    return imgbytes

def take_multiple_images(file_path, cam_coords, add_ind, all_images):
    
    print(cam_coords)
    for i in range(len(cam_coords)-add_ind):
        i+=add_ind
        print(i)
        x_coord = cam_coords[i][0] - parse.CAMERA_X
        y_coord = cam_coords[i][1] - parse.CAMERA_Y
        if i>0:
            prev_x_coord = cam_coords[i-1][0] - parse.CAMERA_X
            prev_y_coord = cam_coords[i-1][1] - parse.CAMERA_Y
        print([x_coord, y_coord])

        
        printer.realtime_goto((x_coord, y_coord))

        if i == 0:
            del_time = np.sqrt(x_coord*x_coord + y_coord*y_coord)/parse.MOVE_SPEED*100
        else:
            del_time = np.sqrt((prev_x_coord-x_coord)*(prev_x_coord-x_coord) + (prev_y_coord-y_coord)*(prev_y_coord-y_coord))/parse.MOVE_SPEED*100
            
        time.sleep(del_time)
        this_file_path = file_path[:-3] + '_' + str(i) + '.jpg'
        this_image = take_image(this_file_path)
        all_images.append(this_image)
        editor_page.window['-IMAGE-'].update(data=all_images[len(all_images)-1])
        pages.viewport.render_old_capture(x_coord + parse.CAMERA_X, y_coord + parse.CAMERA_Y)

    return all_images, len(all_images)-1

def display_previous_image(all_images, cur_ind):
    if cur_ind > 0:
        cur_ind = cur_ind - 1
        editor_page.window['-IMAGE-'].update(data=all_images[cur_ind])
    else:
        pages.debug_terminal.debug_log("This is the first image")
    return cur_ind 

def display_next_image(all_images, cur_ind):
    if cur_ind < len(all_images)-1:
        cur_ind = cur_ind + 1
        editor_page.window['-IMAGE-'].update(data=all_images[cur_ind])
    else:
        pages.debug_terminal.debug_log("This is the last image")
    return cur_ind 

def cleanup_camera():
    if CAMERA_CONNECTED:  # If a camera is connected, release it and end the cv2 scripts.
        cap.release()
        cv2.destroyAllWindows()

def show_preview():
    global stopevent_flag
    stopevent_flag = not stopevent_flag
    cap.start()
    while not stopevent_flag:       
        capture_frame()
        time.sleep(0.1)


""" def open_preview_window():
    global window2
    layout = [[sg.Image(size=(720, 480), key='-NEW_IMAGE-')]]
    window2 = sg.Window("Second Window", layout, size=(420, 420),finalize=True, modal=True)
    choice = None
    while True:
        event, values = window2.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
    window2.close() """



def capture_frame(): 
    global final_image  
    global extracted_image  
    frame = cap.capture_array()
    extracted_image = frame   
    frame = imutils.resize(frame, width=720, height = 480)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # opencv represents images in BGR order however PIL represents images in RGB order, so we need to swap the channels first
    image = Imgp.fromarray(image) 
    #bio = io.BytesIO()
    #image.save(bio, format= 'PNG')
    #imgbytes = bio.getvalue()
    final_image = ImageTk.PhotoImage(image) 

def videoloop():
    
    panel=None

    frame = cap.capture_array()
    frame = imutils.resize(frame, width=1080)
    final_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # opencv represents images in BGR order however PIL represents images in RGB order, so we need to swap the channels first
    final_image = Imgp.fromarray(final_image) 
    final_image = ImageTk.PhotoImage(final_image) 
    
     
    if panel is None:
        print(stopevent_flag)     
        panel = tki.Label(image=final_image)
        panel.image = final_image
        panel.pack(side="left")

    else:   # otherwise, simply update the panel
        panel.configure(image=final_image)
        panel.image = final_image