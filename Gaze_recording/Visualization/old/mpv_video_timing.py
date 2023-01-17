# -*- coding: utf-8 -*-
"""
Created on Mon Dec  5 10:45:57 2022

@author: Marion Léger

# REQUIREMENTS
Code designed for Psychopy 2022.2.4 and Python 3.8.
Python packages recquired :
    - numpy
	- matplotlib
    - cv2
    - h5py
    - thinker
    - mpv :
        1. pip install python-mpv==0.3.1
        2. https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
        extract lastest zip of libmpv on the same directory as this program

Visualize gaze data collected during the exploration session recorded by video_exploration_timing.py
by overlaping the gaze data collected over video frame.

This program uses the mpv player to play the video frames and obtain the frame count.
Depending on the video frame count we search the time at which this frame t1 and the next one t2 have been ploted 
in the frame_timing text file.
We overlap to the mpv video frame the gaze data collected between this 2 times.

# INPUT :
    - video explored during experiment in VIDEO_PATH directory
    - hdf files recorded during the expriments
    - frame_timing.txt files in which are stored the video frame timing
    
# PARAMETERS TO BE SET :
    - VIDEO_PATH    = directory where are stored the experiment's videos
    - FRAME_PATH    = directory where are stored the experiment's video frame timing files
    - HDF_PATH      = directory where are stored the hdf files recorded
    - FILENAME      = list of hdf files where are stored the gaze data to visualize
    - R             = diameter/2 of the gaze cross visualization (must be pair)
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
EXPERIMENT_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/'
VIDEO_PATH = EXPERIMENT_PATH + 'video/'        # directory pathway of the videos used during experiment
FRAME_PATH = EXPERIMENT_PATH + 'frame_timing/' # directory pathway of the frame timing txt files
HDF_PATH   = EXPERIMENT_PATH + 'data/'         # directory pathway of the HDF files recorded
FILENAME = 'video_explo_Tobii_M_4_poisson.mp4.hdf5' #'video_explo_PupilCore_m_001_poisson.mp4.hdf5' # hdf5 file to visualize
R = 10 # diameter/2 of the gaze cross visualization (must be pair)


################## function definition ################## 
def validate(w1):
    "Get the user choice made in the widget's menu"
    global DATA_CHOICE
    global VIDEO_NAME
    DATA_CHOICE = w1.get()
    win.destroy()     

def find_first_index(lst, condition):
    """Return the 1st element's index in the list lst 
    which validates the condition"""
    return [i for i, elem in enumerate(lst) if condition(elem)][0]

# def find_nearest(array, value):
#     """ Return the index of the array's element
#     that is closer to the value""" 
#     array = np.asarray(array)
#     idx = (np.abs(array - value)).argmin()
#     return idx

def gaze_overlap(x,y):
    """ Create a transparent image overlay of size=(video.width,video.height)
    which contains multiple crosses at gaze positions (xi,yi)"""
    global width, height, R
    D = R*2+1 # cross diameter
          
    # create transparent Image
    img = Image.new('RGBA',(width, height),(255, 255, 255, 0))
    d = ImageDraw.Draw(img)
    
    # create crosses at each gaze position (xi,yi)    
    for u in range(len(x)):
        if ~(np.isnan(x[u]) or np.isnan(y[u])): # if gaze data is not NaN
            d.line([(x[u]-D/2, y[u]), (x[u]+D/2, y[u])], fill ="red", width = 3) #horizontal line
            d.line([(x[u], y[u]-D/2), (x[u], y[u]+D/2)], fill ="red", width = 3) #vertical line
    
    d.line([(1381-D/2, 566), (1381+D/2, 566)], fill ="red", width = 3) #horizontal line
    d.line([(1381, 566-D/2), (1381, 566+D/2)], fill ="red", width = 3) #vertical line
    
    return img

def reset_overlap():
    """ Create a transparent image overlay of size=(video.width,video.height)
    which contains multiple crosses at gaze positions (xi,yi)"""
    global width, height          
    # create transparent Image
    img = Image.new('RGBA', (width, height),  (255, 255, 255, 0))
    return img

def plot_frame_gaze_2(frame_count):
    """"For a given video frame display at elapsed_ms time
    overlay on it the elapsed_ms time on Top Left
    and the gaze cross position overlay """
    
    #player.osd_msg1=f"{elapsed_ms/1000.0:.3f}" # Update elapsed_ms msg
    
    # Find the times at which the curent video frame and the next one have been fliped during the experiment  
    #frame_ind = find_first_index(frame_time_array[:,2], lambda e:e>= elapsed_ms/1000)   
    #frame_ind = frame_count-1
    
    # search in the frame timing txt file the line of the current frame displayed
    frame_ind = np.where(frame_time_array[:,0] == frame_count)
    
    # compute x,y mpv correction for full screen
    mt = player.osd_dimensions['mt']
    ml = player.osd_dimensions['ml']
        
    if len(frame_ind[0]) != 0:  # if this frame has been dropped in Psychopy
        frame_ind = frame_ind[0][0]
        
        # search for the time at which the current frame has been displayed in the experiment
        t1 = frame_time_array[frame_ind,1]
        # search for the time at which the next frame has been displayed in the experiment
        t2 = frame_time_array[frame_ind+1,1]
        
        # find the corresponding gaze data collected between these 2 times = gaze data collected for the curent frame
        ind1 = find_first_index(gaze[:,0], lambda e:e>= t1)
        ind2 = find_first_index(gaze[:,0], lambda e:e>= t2)-1
        
        x = gaze[ind1:ind2,1]
        y = gaze[ind1:ind2,2]
              
        # Create an overlay image with cross at gaze positions to plot over the video
        image = gaze_overlap(x,y)
    
    else: #if the current frame has been dropped in psychopy experiment
        # remove previous frame gaze overlap
        image = reset_overlap()
    
    overlay.update(image, pos=(ml, mt)) #update the overlap image on the video display
   
     
# - MAIN -#
################## SEARCH IMAGE FILES EXPLORED IN /IMG_PATH ##################
video_list = []
for f in os.listdir(VIDEO_PATH):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".mp4"]:
        continue
    video_list.append(f)
    
nb_video = np.size(video_list)
    
    
################## Dialog box to set visualization choice ##################
# config the widget window
win = tk.Tk()
win.geometry('500x70')
win.title('Plot parameters')

# config the box menu data choice
w1 = ttk.Label(win, text = "Select binocular data :")
w1.grid(column = 0,row = 1, padx = 10, pady = 5)
w1 = ttk.Combobox(win, values = ['Left eye', 'Right eye', 'Average both eyes','Monocular']) #box menu
w1.grid(row=1,column=1,padx=10,pady=5)  # adding to grid
w1.set('Average both eyes')             # default selected option

#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate(w1))
b1.grid(row=2,column=2)
win.mainloop()


################## Open the HDF file and load gaze and event data  ##################
# --- Open hierachical element contained in the HDF data file ---#
f = h5py.File(HDF_PATH+FILENAME,'r')

# --- Search the video played during the file experiment --- "
split = FILENAME.replace('.hdf5','').split('_')
video = split[len(split)-1]

# --- Import Experiment events --- #
events_path = 'data_collection/events/experiment/MessageEvent'
events      = f[events_path][()]  # access to the binocular gaze data of the HDF file

# --- Import gaze data mono or binocular --- #
if DATA_CHOICE == 'Monocular':
    MONO_PATH = 'data_collection/events/eyetracker/MonocularEyeSampleEvent'
    data = f[MONO_PATH][()]  # Access to the Binocular eye Samples of the HDF file
else :
    BINO_PATH = 'data_collection/events/eyetracker/BinocularEyeSampleEvent'
    data = f[BINO_PATH][()]  # Access to the Binocular eye Samples of the HDF file

# --- Import left and right gaze data or average and gaze data time --- #
if   DATA_CHOICE == 'Right eye':
    gaze = np.array([data['time'], data['right_gaze_x'], data['right_gaze_y']]).T
elif DATA_CHOICE == 'Left eye':
    gaze = np.array([data['time'], data['left_gaze_x'], data['left_gaze_y']]).T
elif DATA_CHOICE == 'Average both eyes' :  # compute gaze average between both eyes      
    avg_gaze_x = np.nanmean(np.array([data['left_gaze_x'],data['right_gaze_x']]), axis=0)
    avg_gaze_y = np.nanmean(np.array([data['left_gaze_y'],data['right_gaze_y']]), axis=0)                        
    gaze = np.array([data['time'], avg_gaze_x, avg_gaze_y]).T  # img_gaze : column 0 = R/L/avg_gaze_x, 1 = R/L/avg_gaze_y 


################## Open the txt file and load video frame timing data  ##################
fp = open(FRAME_PATH+FILENAME.replace('.hdf5','.txt'), "r")

# skip video info and look for frame timing data lines
for l_no, line in enumerate(fp):
    if ' ** Per Frame Video Playback Data ** ' in line: #search the nb of this line
        break

# load from the txt file the frame timing data into an array
frame_time_array = np.loadtxt(FRAME_PATH+FILENAME.replace('.hdf5','.txt'), skiprows=l_no+2, dtype='str')
frame_time_array = frame_time_array.astype(np.float)


################## Get video resolution ##################
cap = cv2.VideoCapture(VIDEO_PATH+video)
width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# --- Translate gaze data coordinate to the TopLeft video origin coordinate --- #
gaze[:,1] = gaze[:,1] + width/2
gaze[:,2] = - gaze[:,2] + height/2

################## plot raw gaze data over reference video ##################
# --- mpv player settings --- #
player = mpv.MPV()
player.loop = False
player.fullscreen = False

# --- create the image overlap to plot over the mpv video --- #
overlay = player.create_image_overlay()
frame_count = 0

### properties access to mpv player ###
# --- each time a frame video is played by mpv : subplot gaze overlap --- #
@player.property_observer('time-pos') 
def time_observer(_name, value):
    global frame_count
    # Here, _value is either None if nothing is playing or a float
    # containing fractional seconds since the beginning of the file.
    if value: # if a frame is played
       # elapsed_ms  = int(value*1000.0) #get the time of this frame
        frame_count = frame_count+1 # increase the frame counter
        plot_frame_gaze_2(frame_count) # overlay gaze crosses to the frame video    

# --- shortcuts during video playing --- #            
@player.on_key_press('s')
def my_s_binding():
    pillow_img = player.screenshot_raw()
    pillow_img.save('screenshot.png')

@player.on_key_press('esc')
def my_q_binding():
    global is_running
    is_running=False
    player.seek(100,reference="absolute-percent")
    print("'Quit' request acknowledged")


# --- start playing the video --- #
player.play(VIDEO_PATH+video)
player.wait_until_playing()
print(frame_count)
