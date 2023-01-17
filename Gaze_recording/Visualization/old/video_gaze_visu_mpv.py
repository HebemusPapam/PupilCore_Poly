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
VIDEO_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/video/'   # pathway of the images used during experiment
HDF_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/data/' # pathway of the HDF files recorded
FILENAME = ['video_explo_12_001.hdf5'] # files to visualize

LAST_FRAME_T = 0

################## DIALOG BOX TO SELECT VISUALIZATION OPTIONS ##################
# --- function definition --- # 
def validate():
    """
    Get the user choice made in the widget's menu
    """
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
    "create a (R+1+R) sized transparent cross image"
    R = 10*2+1  # diameter = R+1+R
    w, h = width, height
          
    # creating new Image object
    img = Image.new('RGBA', (w, h),  (255, 255, 255, 0))
          
    # create line image
    d = ImageDraw.Draw(img)
    d.line([(0, R/2), (R, R/2)], fill ="red", width = 3)
    d.line([(R/2, 0), (R/2, R)], fill ="red", width = 3)
        
    for u in range(len(x)):
        if ~(np.isnan(x[u]) or np.isnan(y[u])):
            d.line([(x[u]-R/2, y[u]), (x[u]+R/2, y[u])], fill ="red", width = 3)
            d.line([(x[u], y[u]-R/2), (x[u], y[u]+R/2)], fill ="red", width = 3)
    return img

# callback, when mpv frame changes
def plot_nearest_gaze(elapsed_ms):
        
    # Update 'level1" msg
    player.osd_msg1=f"{elapsed_ms/1000.0:.3f}"
        
    # x,y correction for full screen
    mt=player.osd_dimensions['mt'] # y-correction black band
    ml=player.osd_dimensions['ml'] # x-correction black band
        
    idx = find_nearest(transpose_gaze[:,2],elapsed_ms/1000)
           
    x = transpose_gaze[idx,0]
    y = transpose_gaze[idx,1]
        
    if idx is None or np.isnan(x) or np.isnan(y):
        overlay.update(cross_img, pos=(-R-1,-R-1))
        
    else:
        x = int(ml + x - R)
        y = int(mt + y - R)
        overlay.update(cross_img, pos=(x,y))
            
    
def plot_lastest_gazes(elapsed_ms):
    
    global LAST_FRAME_T
    # Update 'level1" msg
    player.osd_msg1=f"{elapsed_ms/1000.0:.3f}"
    
    # x,y correction for full screen
    mt=player.osd_dimensions['mt'] # y-correction black band
    ml=player.osd_dimensions['ml'] # x-correction black band
    
    idx_current = find_nearest(transpose_gaze[:,2],elapsed_ms/1000)
    idx_last    = find_nearest(transpose_gaze[:,2],LAST_FRAME_T/1000)

    x = transpose_gaze[idx_last:idx_current,0]
    y = transpose_gaze[idx_last:idx_current,1]
    
    # if idx_current-idx_last == 0:
    #     #image = gaze_sum_up_image(transpose_gaze[:,0],transpose_gaze[:,1])
    # else :
    image = gaze_sum_up_image(x,y)
    
    overlay.update(image, pos=(ml - R +1,mt - R +1))
    
    #(current_elapsed_ms/1000.0-LAST_FRAME_T/1000)
    print(idx_current-idx_last)
    LAST_FRAME_T = elapsed_ms

def plot_frame_gazes(elapsed_ms):
    
    global frm_delay
    # Update 'level1" msg
    player.osd_msg1=f"{elapsed_ms/1000.0:.3f}"
    
    # x,y correction for full screen
    mt=player.osd_dimensions['mt'] # y-correction black band
    ml=player.osd_dimensions['ml'] # x-correction black band
    
    idx_frame = find_nearest(transpose_gaze[:,2],elapsed_ms/1000)
    idx_next_frame   = find_nearest(transpose_gaze[:,2],(elapsed_ms+frm_delay)/1000)

    x = transpose_gaze[idx_frame:idx_next_frame,0]
    y = transpose_gaze[idx_frame:idx_next_frame,1]
    
    # if idx_next_frame == 0:
    #     overlay.update(cross_img, pos=(-R-1,-R-1))
    # else :
    image = gaze_sum_up_image(x,y)
    overlay.update(image, pos=(ml-R, mt-R))
    
    #(current_elapsed_ms/1000.0-LAST_FRAME_T/1000)
    print(idx_next_frame-idx_frame)

     
################## Dialog box to set visualization choice ##################
# config the widget window
win = tk.Tk()  # init the widget
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
    # --- Init 2d arrays that will contain gaze data of all files specific to one given image ---#
    # gaze_x_all = np.empty((T_VIDEO*F_TRACKER,nb_file))*np.nan
    # gaze_y_all = np.empty((T_VIDEO*F_TRACKER,nb_file))*np.nan
    
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
    fps_vid   = cap.get(cv2.CAP_PROP_FPS)
    frm_delay = 1000/fps_vid

    # --- Translate gaze data coordinate to the TopLeft origin coordinate --- #
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
        plot_lastest_gazes(0)
    
    @player.on_key_press('q')
    def my_q_binding():
        global is_running
        is_running=False
        player.seek(100,reference="absolute-percent")
        print("'Quit' request acknowledged")

    # --- start playing the video --- #
    player.play(VIDEO_PATH+video_list[i])
    player.wait_until_playing()
              