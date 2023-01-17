# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 14:16:45 2022

@author: Marion Léger

Export binocular gaze data (x,y) and pupil size from hdf files recorded by image_exploration.py
Store for each image explored : gaze_x, gaze_y and pupil size for all hdf file loaded in 3 separated .txt file
The first column of txt file data is the time vector of the experiment image exploration in [sec]
and the following columns are corresponding data (gaze_x or gaze_y or pupil size) for each hdf file loaded

"""

################## Import package ##################
import warnings
import os

import tkinter as tk
from tkinter import ttk

import numpy as np
import h5py


################## Parameters ##################
# experiment data directory
IMG_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/img/'   # image pathway used during experiment
HDF_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/data/'  # pathway of the HDF files recorded
FILENAME = ['ExploIMG_M_004.hdf5','ExploIMG_M_001.hdf5']          # hdf files for data export

# file text directory
PUPIL_PATH = 'C:/Users/marion/Documents/Data/pupil_size/'    # pathway where save the pupil size data
GAZE_PATH  = 'C:/Users/marion/Documents/Data/raw_gaze_data/' # pathway where save the gaze data

# parameters useful to determine the number of samples recorded during each trials
T_IMG     = 7    # duration of the image exploration phase in seconds -> must have been the same for all file experiments
F_TRACKER = 60   # sampling frequency of the eyetracker in Hz  -> must have been the same for all file experiments
FRAMES    = T_IMG*F_TRACKER-1


################## Function definitions ##################
def save_data(header,data,decimal_nb,txt_filename):
    """
    Save the data array in a text file named txt_filename with the string array label as header
    float data are rounded with n decimal

    Parameters
    ----------
    header : str list
        Contain the header of data array ['time'; 'filename1'; 'filename2'; ...]
        Will be store in the 1st row of text file
    data : numpy.array of float
       Contain time vector and binocular data (gaze_x/gaze_y/pupil_size)
       of all hdf files for one specific image
    decimal_nb : int
        decimal number for data to store in the text file
    txt_filename : str
        filename of text file

    Returns
    -------
    None.
    """
    txt_data =  np.row_stack((np.array(header), np.round(data,decimal_nb)))
    np.savetxt(txt_filename, txt_data, delimiter=" ", fmt="%-15s") #data are saved as string with right justify

    print('data exported to file'+txt_filename)

def validate(): #
    """
    Get the user choice made in the widget's menu

    Returns
    -------
    None.
    """
    global CHOICE
    CHOICE = w.get()
    win.destroy()


################## Dialog box to set visualization choice ##################
# config the widget window
win = tk.Tk()           # init the widget
win.geometry('400x100')
win.title('Choose which gaze data to display')

# config the box menu data choice
choices = ['left_eye', 'right_eye', 'eyes_average']
w = ttk.Combobox(win, values = choices) #box menu
w.grid(row=1,column=1,padx=10,pady=20)  #adding to grid
w.set('eyes_average')              #default selected option

#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate())
b1.grid(row=1,column=2)
win.mainloop()


################## Search image files used in /IMG_PATH ##################
img_list = []

for f in os.listdir(IMG_PATH): # research for each file in IMG_PATH directory if it's an image and save its name
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".jpg",".png"]:
        continue
    img_list.append(f)

nb_image = np.size(img_list)


################## Search for each image the corresponding binocular data in all hdf file loaded  ##################
time     = np.arange(0,T_IMG-1*1/F_TRACKER,(1/F_TRACKER))
nb_file  = np.size(FILENAME)


with warnings.catch_warnings(): # removee RuntimeWarnings from nanmean
    warnings.simplefilter("ignore", category=RuntimeWarning)
    
    for i in range(nb_image): # LOOP OVER IMAGES
    
        # --- Init 2d arrays that will contain gaze data of all files specific to one given image ---#
        gaze_x_all = np.empty((FRAMES,nb_file+1))*np.nan
        gaze_y_all = np.empty((FRAMES,nb_file+1))*np.nan
        pupil_all  = np.empty((FRAMES,nb_file+1))*np.nan
    
        label = ['time']
    
        for s in range(nb_file): # LOOP OVER FILES
    
            # --- Import hdf file data --- #
            # Open hierachical element contained in the HDF data file
            f = h5py.File(HDF_PATH+FILENAME[s],'r')
    
            # Import Experiment gaze data
            BINO_PATH = 'data_collection/events/eyetracker/BinocularEyeSampleEvent'
            bino_data = f[BINO_PATH][()]  # Access to the Binocular eye Samples of the HDF file
    
            # Import Experiment events
            EVENT_PATH = 'data_collection/events/experiment/MessageEvent'
            events      = f[EVENT_PATH][()]  # access to the binocular gaze data of the HDF file
    
            # --- Research the event id of the first and last samples recorded during the image exploration phase
            # Research the event_array's index of the curent image processed's = 'img_list[i]'
            index_img_labbel = np.where(events['text'].astype('U128') == img_list[i])
    
            if len(index_img_labbel[0]) != 0 :  # if the data exist for this image
                index_img_labbel = index_img_labbel[0][0]
    
                if len(events['event_id'])-1 > index_img_labbel+1: # if the image exploration has been complete
    
                # Find the event id of START_IMAGE and STOP_IMAGE labels
                    #event_id_start = events['event_id'][index_img_labbel-1]
                    event_id_label = events['event_id'][index_img_labbel]
                    event_id_stop  = events['event_id'][index_img_labbel+1]
    
                    # --- Get gaze data for this image exploration --- #
                    # research the index array corresponding in bino_array to the begining and the end of the image exploration
                    ind_gaze_stop  = np.where(bino_data['event_id'] == event_id_stop-1)[0][0]
                    ind_gaze_start = np.where(bino_data['event_id'] == event_id_label+1)[0][0]
    
                    # save the image gaze data for this image exploration according to the user choice of visualization
                    if CHOICE == 'right_eye':
                        img_gaze   = np.array([bino_data['right_gaze_x'][ind_gaze_start:ind_gaze_stop], bino_data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]])
                        pupil_size = bino_data['right_pupil_measure1'][ind_gaze_start:ind_gaze_stop]
    
                    elif CHOICE == 'left_eye':
                        img_gaze = np.array([bino_data['left_gaze_x'][ind_gaze_start:ind_gaze_stop], bino_data['left_gaze_y'][ind_gaze_start:ind_gaze_stop]])
                        pupil_size = bino_data['left_pupil_measure1'][ind_gaze_start:ind_gaze_stop]
    
                    elif CHOICE == 'eyes_average' :  # compute gaze average between both eyes
                        avg_gaze_x = np.nanmean(np.array([bino_data['left_gaze_x'][ind_gaze_start:ind_gaze_stop],bino_data['right_gaze_x'][ind_gaze_start:ind_gaze_stop]]), axis=0)
                        avg_gaze_y = np.nanmean(np.array([bino_data['left_gaze_y'][ind_gaze_start:ind_gaze_stop],bino_data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]]), axis=0)
                        img_gaze   = np.array([avg_gaze_x, avg_gaze_y])  # img_gaze : column 0 = R/L/avg_gaze_x, 1 = R/L/avg_gaze_y
                        pupil_size = np.nanmean(np.array([bino_data['left_pupil_measure1'][ind_gaze_start:ind_gaze_stop],bino_data['right_pupil_measure1'][ind_gaze_start:ind_gaze_stop]]), axis=0)
    
                    img_gaze = img_gaze.T
    
                    # concat with other files data of other subjects
                    gaze_x_all[0:np.size(img_gaze,0),s+1]  = img_gaze[:,0]
                    gaze_y_all[0:np.size(img_gaze,0),s+1]  = img_gaze[:,1]
                    pupil_all[0:np.size(pupil_size,0),s+1] = pupil_size
    
                    # add image name to the header of the textfile
                    label = np.append(label,FILENAME[s].split('.',1)[0])
    
        ############## EXPORT RAW GAZE DATA AND PUPIL SIZE IN .txt FILE ######
        if ~np.isnan(np.nanmean(pupil_all)): #if one of the hdf file contain data for img_list[i]
    
            # add time vector to binocular data
            gaze_x_all[:,0] = time
            gaze_y_all[:,0] = time
            pupil_all[:,0]  = time
    
            # set text file's titles
            pupil_filename = PUPIL_PATH + img_list[i] + '_pupil_size_' + CHOICE + '.txt'
            x_filename = GAZE_PATH + img_list[i] + '_gaze_x_' + CHOICE + '.txt'
            y_filename = GAZE_PATH + img_list[i] + '_gaze_y_' + CHOICE + '.txt'
    
            # save and export raw gaze x,y and pupil size
            save_data(label,pupil_all,5,pupil_filename)
            save_data(label,gaze_x_all,5,x_filename)
            save_data(label,gaze_y_all,5,y_filename)
