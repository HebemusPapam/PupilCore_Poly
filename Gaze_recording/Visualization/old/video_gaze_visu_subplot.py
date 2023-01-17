# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 13:51:16 2022

@author: Marion Léger

Display raw binocular gaze data of the experiment session recorded by image_exploration.py.
The raw data are drawn over the corresponding image.

The user has the choice between displaying the right or left data or the data average of both eyes.
The user can load and subplot several data session. In this case the data will be subploted in different colors for each subject.

"""

################## import package ##################
import h5py
import numpy as np
import os, os.path
import matplotlib.pyplot as plt
import cv2
    
import tkinter as tk
from tkinter import ttk
from imutils.video import FPS


################## PARAMETERS TO SET ##################
VIDEO_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/video/'   # pathway of the images used during experiment
HDF_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/data/' # pathway of the HDF files recorded
FILENAME = ['video_explo_12_001.hdf5']#,'video_explo_12_001.hdf5'] # files to visualize

# parameters useful to determine the number of samples recorded during each trials -> init data array's size
T_VIDEO   = 7      # duration of the image exploration phase in seconds -> must have been the same for all file experiments
F_TRACKER = 60 # sampling frequency of the eyetracker in Hz  -> must have been the same for all file experiments


################## DIALOG BOX TO SELECT VISUALIZATION OPTIONS ##################
def validate(): #function to get the user choice made in the widget's menu
    global m
    m = w.get()   
    win.destroy() 

# config the widget window
win = tk.Tk()           # init the widget
win.geometry('400x100') 
win.title('Choose which gaze data to display')

# config the box menu
choices = ['Left eye', 'Right eye', 'Average both eyes']
w = ttk.Combobox(win, values = choices) #box menu
w.grid(row=1,column=1,padx=10,pady=20)  #adding to grid
w.set('Average both eyes')              #default selected option

#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate())
b1.grid(row=1,column=2)
win.mainloop()


################## SEARCH IMAGE FILES EXPLORED IN /IMG_PATH ##################
video_list = []

for f in os.listdir(VIDEO_PATH):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".mp4"]:
        continue
    video_list.append(f)

nb_video = np.size(video_list)


################## Define color list for plot ##################
nb_file = np.size(FILENAME)
color   = [list(np.random.random(size=3) * 256) * 1 for q in range(nb_file)]
    
    
################## Search for each image the corresponding gaze data in all hdf file loaded  ##################
for i in range(nb_video):
    
    # --- Init 2d arrays that will contain gaze data of all files specific to one given image ---#
    gaze_x_all = np.empty((T_VIDEO*F_TRACKER,nb_file))*np.nan
    gaze_y_all = np.empty((T_VIDEO*F_TRACKER,nb_file))*np.nan
    
    # --- LOOP OVER FILES --- #
    for s in range(nb_file):
        
        # --- Open hierachical element contained in the HDF data file ---#
        f = h5py.File(HDF_PATH+FILENAME[s],'r')
        
        # --- Import Experiment gaze data --- #      
        bino_path = 'data_collection/events/eyetracker/BinocularEyeSampleEvent'
        bino_data = f[bino_path][()]  # Access to the Binocular eye Samples of the HDF file       
        
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
                ind_gaze_stop  = np.where(bino_data['event_id'] == event_id_stop-1)[0][0]
                ind_gaze_start = np.where(bino_data['event_id'] == event_id_label+1)[0][0]
                
                # save the image gaze data for this image exploration according to the user choice of visualization
                if m == 'Right eye':
                    video_gaze = np.array([bino_data['right_gaze_x'][ind_gaze_start:ind_gaze_stop], bino_data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]])
                
                elif m == 'Left eye':
                    video_gaze = np.array([bino_data['left_gaze_x'][ind_gaze_start:ind_gaze_stop], bino_data['left_gaze_y'][ind_gaze_start:ind_gaze_stop]])
                
                elif m == 'Average both eyes' :  # compute gaze average between both eyes      
                    avg_gaze_x = np.nanmean(np.array([bino_data['left_gaze_x'][ind_gaze_start:ind_gaze_stop],bino_data['right_gaze_x'][ind_gaze_start:ind_gaze_stop]]), axis=0)
                    avg_gaze_y = np.nanmean(np.array([bino_data['left_gaze_y'][ind_gaze_start:ind_gaze_stop],bino_data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]]), axis=0)                        
                    video_gaze = np.array([avg_gaze_x, avg_gaze_y])  # img_gaze : column 0 = R/L/avg_gaze_x, 1 = R/L/avg_gaze_y 
                
                video_gaze = np.transpose(video_gaze)
                
                if s == 1:
                    video_gaze = video_gaze+50
                               
                # --- concat with gaze data of hdf files --- #
                gaze_x_all[0:np.size(video_gaze,0),s] = video_gaze[0:420,0]
                gaze_y_all[0:np.size(video_gaze,0),s] = video_gaze[0:420,1]

    
    ############# Load video parameters ###########             
    # --- Open video using cv2 library --- #
    cap = cv2.VideoCapture(VIDEO_PATH+video_list[i])
      
    # --- Get the shape, fps and number of frames in the video --- #
    frames_nb = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps_vid   = round(cap.get(cv2.CAP_PROP_FPS),2)
    frm_delay = 1000/fps_vid
        
    print ("Frames per second : {0}".format(fps_vid))  
    fps_vid = round(fps_vid)
    
    # --- Check raw gaze plot --- #
    # fig, ax = plt.subplots() 
    # plt.title(video_list[i]) 
    # ax.plot(gaze_x_all, gaze_y_all, marker='.',linewidth=1, markersize=6,linestyle='dashed',fillstyle='full') 
    # plt.xlim(-width/2, width/2)
    # plt.ylim(-height/2, height/2)
    
    ############# Prepare gaze data to fit with video frame ###########
    # --- Translate gaze data coordinate to the TopLeft origin coordinate --- #
    gaze_x_vid = gaze_x_all + width/2
    gaze_y_vid = - gaze_y_all + height/2
    
    # fig, ax = plt.subplots() 
    # plt.title(video_list[i]) 
    # ax.plot(gaze_x_vid, gaze_y_vid, marker='.',linewidth=1, markersize=6,linestyle='dashed',fillstyle='full') 

     
    # --- Resample gaze data to video sample freq to plot one sample per video frame --- #
    nb_frames = T_VIDEO*fps_vid  
    if fps_vid < F_TRACKER: # 1. Cas ou F_eyeT > F_video -> F_eyeT doit être un mutliple de F_video     
        m = 0
        step = int(F_TRACKER/fps_vid)
        # init gaze data array of the same size as the nb of video frame
        gaze_resample_x = np.empty((nb_frames,nb_file))*np.nan
        gaze_resample_y = np.empty((nb_frames,nb_file))*np.nan
    
        for k in range(T_VIDEO*fps_vid): # under sample gaze data 
            gaze_resample_x[k,:] = gaze_x_vid[m,:]
            gaze_resample_y[k,:] = gaze_y_vid[m,:]
            m=m+step
            
    elif fps_vid == F_TRACKER:  # 2. Cas ou F_eyeT = F_video : keep same gaze data
        gaze_resample_x = gaze_x_vid
        gaze_resample_y = gaze_y_vid            
    # 2. Cas ou F_eyeT < F_video ????? skip video frame ? or had Nan gaze sample
    
    # fig, ax = plt.subplots() 
    # plt.title(video_list[i]) 
    # ax.plot(gaze_resample_x,gaze_resample_y, marker='.',linewidth=1, markersize=6,linestyle='dashed',fillstyle='full') 
    
    
    ############ Formate gaze data to fit with OpenCv plot function's data format ###########
    # --- For circle gaze plot with OpenCv : store in tupple list gaze's circle center coordinates --- #   
    gaze_dot = [[0] * nb_frames for q in range(nb_file)]  
    for p in range(nb_frames):
        for r in range(nb_file):
            if ~np.isnan(gaze_resample_x[p,r]):
                gaze_dot[r][p] = (round(gaze_resample_x[p,r]),round(gaze_resample_y[p,r]))
            else: gaze_dot[r][p] = (gaze_resample_x[p,r],gaze_resample_y[p,r])
            
        
    
    # --- For gaze path plot with OpenCv : store in an transpose array gaze coordinates --- #
    pts = np.array([gaze_resample_x, gaze_resample_y],np.int32).T
       
    fps = FPS().start()
    
    ################## Play the video frame by frame and plot gaze data ##################
    #create the video window
    cv2.namedWindow(video_list[i], cv2.WINDOW_AUTOSIZE)
              
    # while True: # loop over frames from the video file stream    
    ######## p max = max gaze_resample
    for p in range(nb_frames): # for the time played during the experiment
        fps1 = FPS().start()
        # --- Capture the frame --- #
        flag, frame = cap.read()       
        if not flag: # if no frame grabbed = reached the stream end
            break

        # --- Draw gaze data over video frame for all files --- #
        if p != nb_frames-1 :         
            # if not last video frame : only draw frame's gaze data
            for n in range(nb_file):
                if ~np.isnan(gaze_resample_x[p,n]): # if no blink or data lost
                    # draw the gaze circles over the video frame     
                    cv2.circle(frame,((round(gaze_resample_x[p,n]),
                                       round(gaze_resample_y[p,n]))),
                               radius=10, color=color[n], thickness=-1)
        else:        
            # Last video frame : Draw complete gaze path        
            for n in range(nb_file):
                for point in gaze_dot[n]:
                    if ~np.isnan(point[0]): # if no blink or data lost
                        cv2.circle(frame,point,radius=10, color=color[n], thickness=-1)                          
                cv2.polylines(frame, [pts[n,~pts[n,:,0]<0,:]], isClosed = False, color=color[n], thickness=0, lineType = 4)
            
        # --- Display the resulting frame --- #           
        cv2.imshow(video_list[i],frame)  

        fps1.update()
        fps1.stop()
        delay = frm_delay-fps1.elapsed()
        print(delay)
        print(fps1.elapsed())
                              
        #time.sleep(frm_delay/2000)   
        if cv2.waitKey(round(frm_delay/2)) & 0xFF == ord('q'):
             break
        
        fps.update()
                         
    fps.stop() # stop the timer and display FPS information
    print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    
    cap.release() # release the video capture object
    #cv2.destroyAllWindows() # Closes all the frames