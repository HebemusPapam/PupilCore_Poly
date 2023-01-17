# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 10:45:57 2022

@author: marion
"""

import os
os.environ["PATH"] = os.path.dirname(__file__) + os.pathsep + os.environ["PATH"]

#!/usr/bin/env python3
from PIL import Image, ImageDraw
import mpv

import h5py
import numpy as np
import os, os.path
import cv2
    
import tkinter as tk
from tkinter import ttk

################## PARAMETERS TO SET ##################
VIDEO_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/video/' # pathway of the videos used during experiment
HDF_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/data/' # pathway of the HDF files recorded
FILENAME = ['video_explo_12_001.hdf5'] # hdf5 files to visualize

################## function definition ################## 
def validate():
    "Get the user choice made in the widget's menu"
    global DATA_CHOICE
    DATA_CHOICE = w1.get()
    win.destroy()     

def find_first_index(lst, condition):
    """Return the 1st element's index in the list lst 
    which validates the condition"""
    return [i for i, elem in enumerate(lst) if condition(elem)][0]

def find_nearest(array, value):
    """ Return the index of the array's element
    that is closer to the value""" 
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def create_PIL_cross(R):
    "Create a (R+1+R) sized transparent cross image"
    diameter = 2*R+1 # cross diameter
    w, h = diameter, diameter # overlay image size = cross size
      
    # creating new Image object
    img = Image.new('RGBA', (w, h),  (255, 255, 255, 0))
      
    # create 2 lines on image -> cross
    d = ImageDraw.Draw(img)  
    d.line([(0, h/2), (w, h/2)], fill ="red", width = 3) #horizontal line
    d.line([(w/2, 0), (w/2, h)], fill ="red", width = 3) #vertical line
    return img


def gaze_sum_up_image(x,y):
    """ Create a transparent image overlay of size=(video.width,video.height)
    which contains multiple crosses at gaze positions (xi,yi)"""
    global width, height, R
    D = R*2+1            # cross diameter
    w, h = width, height # overlay image size = video size
          
    # creating new Image object
    img = Image.new('RGBA', (w, h),  (255, 255, 255, 0))
    d = ImageDraw.Draw(img)     
    
    # origin cross to test the overlay image position on video
    # should be top left
    d.line([(0-D/2, 0), (+D/2, 0)], fill ="red", width = 3)
    d.line([(0, -D/2), (0, +D/2)], fill ="red", width = 3)
    
    # create crosses at each gaze position (xi,yi)    
    for u in range(len(x)):
        if ~(np.isnan(x[u]) or np.isnan(y[u])): # if gaze data is not NaN
            d.line([(x[u]-D/2, y[u]), (x[u]+D/2, y[u])], fill ="red", width = 3) #horizontal line
            d.line([(x[u], y[u]-D/2), (x[u], y[u]+D/2)], fill ="red", width = 3) #vertical line
    return img


def plot_frame_gazes(elapsed_ms):
    """"For a given video frame display at elapsed_ms time
    overlay on it the elapsed_ms time on Top Left
    and the gaze cross position overlay """
    global frm_delay#, transpose_gaze, overlay, video_duration
    
    player.osd_msg1=f"{elapsed_ms/1000.0:.3f}" # Update elapsed_ms msg
    
    # Find the gaze data recorded between the current frame displaying and the next one
    idx_frame      = find_nearest(transpose_gaze[:,2],elapsed_ms/1000)
    idx_next_frame = find_nearest(transpose_gaze[:,2],(elapsed_ms+frm_delay)/1000)
    
    x = transpose_gaze[idx_frame:idx_next_frame,0]
    y = transpose_gaze[idx_frame:idx_next_frame,1]
        
    # x,y correction for full screen
    mt = player.osd_dimensions['mt']
    ml = player.osd_dimensions['ml']
    
    # Set the overlay over the video frame with TOP Left origin
    #if idx_frame == idx_next_frame:
        #image = gaze_sum_up_image(transpose_gaze[:,0],transpose_gaze[:,1])
    #else:
        # Create an overlay image with cross at gaze positions
    image = gaze_sum_up_image(x,y)
    
    overlay.update(image, pos=(ml, mt))
    #print(idx_next_frame-idx_frame)

    
    
################## Dialog box to set visualization choice ##################
# config the widget window
win = tk.Tk()
win.geometry('500x50')
win.title('Plot parameters')

# config the box menu data choice
w1 = ttk.Label(win, text = "Select binocular data :")
w1.grid(column = 0,row = 1, padx = 10, pady = 5)
w1 = ttk.Combobox(win, values = ['Left eye', 'Right eye', 'Average both eyes','Monocular']) #box menu
w1.grid(row=1,column=1,padx=10,pady=5)  # adding to grid
w1.set('Average both eyes')             # default selected option

#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate())
b1.grid(row=1,column=3)
win.mainloop()

################## SEARCH IMAGE FILES EXPLORED IN /IMG_PATH ##################
video_list = []

for f in os.listdir(VIDEO_PATH):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".mp4"]:
        continue
    video_list.append(f)

nb_video = np.size(video_list)


################## Search for each video the corresponding gaze data in all hdf file loaded  ##################
nb_file  = np.size(FILENAME)
for i in range(1):
    i=1  
    # --- LOOP OVER FILES --- #
    for s in range(nb_file):
        
        # --- Open hierachical element contained in the HDF data file ---#
        f = h5py.File(HDF_PATH+FILENAME[s],'r')
        
        if DATA_CHOICE == 'Binocular':
            # Import Experiment gaze data
            MONO_PATH = 'data_collection/events/eyetracker/MonocularEyeSampleEvent'
            data = f[MONO_PATH][()]  # Access to the Binocular eye Samples of the HDF file
        else :
            # Import Experiment gaze data
            BINO_PATH = 'data_collection/events/eyetracker/BinocularEyeSampleEvent'
            data = f[BINO_PATH][()]  # Access to the Binocular eye Samples of the HDF file

        # --- Import Experiment events --- #
        events_path = 'data_collection/events/experiment/MessageEvent'
        events      = f[events_path][()]  # access to the binocular gaze data of the HDF file       
                
        # --- Research the event id of the first and last samples recorded during the image exploration phase
        # Research the event_array's index of the curent image processed's = 'img_list[i]'
        index_video_labbel = np.where(events['text'].astype('U128') == video_list[i])
        
        if len(index_video_labbel[0]) != 0 :  # if the data exist for this image ('img_list[i]' exists)                                    
            index_video_labbel = index_video_labbel[0][0]
            
            if len(events['event_id'])-1 > index_video_labbel+1: # & if the image exploration has been complete (IMG_STOP exists)
               
                # Find the event id of START_IMAGE and STOP_IMAGE labels        
                event_id_label = events['event_id'][index_video_labbel]           
                event_id_stop  = events['event_id'][index_video_labbel+1]
                  
                # --- Get gaze data for this image exploration --- #                       
                # research the index array corresponding in bino_array to the begining and the end of the image exploration        
                ind_gaze_stop  = find_first_index(data['event_id'], lambda e:e> event_id_stop)
                ind_gaze_start = find_first_index(data['event_id'], lambda e:e> event_id_label)
                
                # save the image gaze data for this image exploration according to the user choice of visualization
                if DATA_CHOICE == 'Right eye':
                    video_gaze = np.array([data['right_gaze_x'][ind_gaze_start:ind_gaze_stop], data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]]).T
                
                elif DATA_CHOICE == 'Left eye':
                    video_gaze = np.array([data['left_gaze_x'][ind_gaze_start:ind_gaze_stop], data['left_gaze_y'][ind_gaze_start:ind_gaze_stop]]).T
                
                elif DATA_CHOICE == 'Average both eyes' :  # compute gaze average between both eyes      
                    avg_gaze_x = np.nanmean(np.array([data['left_gaze_x'][ind_gaze_start:ind_gaze_stop],data['right_gaze_x'][ind_gaze_start:ind_gaze_stop]]), axis=0)
                    avg_gaze_y = np.nanmean(np.array([data['left_gaze_y'][ind_gaze_start:ind_gaze_stop],data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]]), axis=0)                        
                    video_gaze = np.array([avg_gaze_x, avg_gaze_y]).T  # img_gaze : column 0 = R/L/avg_gaze_x, 1 = R/L/avg_gaze_y 
                
                gaze_time     = np.array(data['time'][ind_gaze_start:ind_gaze_stop])
                video_t_start = events['time'][index_video_labbel]
                
                time_recale = gaze_time - video_t_start


    ################## plot raw gaze data over reference video ##################
    # --- Get video fps --- #
    cap = cv2.VideoCapture(VIDEO_PATH+video_list[i])
    width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frames    = cap.get(cv2.CAP_PROP_FRAME_COUNT) # count the number of frames
    fps_vid   = cap.get(cv2.CAP_PROP_FPS)
    frm_delay = 1000/fps_vid
     
    # calculate duration of the video
    # video_duration = round(frames/fps_vid)

    # --- Translate gaze data coordinate to the TopLeft video origin coordinate --- #
    transpose_gaze_x = video_gaze[:,0] + width/2
    transpose_gaze_y = - video_gaze[:,1] + height/2
    transpose_gaze   = np.array([transpose_gaze_x,transpose_gaze_y,time_recale]).T
    
    # --- mpv player settings --- #
    player = mpv.MPV()
    player.loop = False
    player.fullscreen = False
    
    # --- create the cross image pattern for gaze visualisation --- #
    R = 10
    cross_img = create_PIL_cross(R)
    overlay   = player.create_image_overlay()
    
    # Property access, these can be changed at runtime
    @player.property_observer('time-pos')
    def time_observer(_name, value):
        # Here, _value is either None if nothing is playing or a float
        # containing fractional seconds since the beginning of the file.
        if value:
            elapsed_ms=int(value*1000.0)
            plot_frame_gazes(elapsed_ms)
            
                
    @player.on_key_press('s')
    def my_s_binding():
        pillow_img = player.screenshot_raw()
        pillow_img.save('screenshot.png')
        
    @player.on_key_press('0')
    def my_0_binding():
        global LAST_FRAME_T
        LAST_FRAME_T = 0
        player.time_pos=0
        plot_frame_gazes(0)
    
    @player.on_key_press('q')
    def my_q_binding():
        global is_running
        is_running=False
        player.seek(100,reference="absolute-percent")
        print("'Quit' request acknowledged")

    # --- start playing the video --- #
    player.play(VIDEO_PATH+video_list[i])
    player.wait_until_playing()
              