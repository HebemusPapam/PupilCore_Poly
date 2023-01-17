# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 13:55:27 2022

@author: Marion Léger

# REQUIREMENTS
Code designed for Psychopy 2022.2.4 and Python 3.8.
Python packages recquired :
    - numpy
	- matplotlib
    - scipy
    - h5py
    - thinker

Visualize gaze data collected during the exploration session recorded by image_exploration.py

The user has the choice between 2 kind of visualization :
    - raw vizualisation of gaze coordinates on the image  with different colors for each hdf file data loaded
    - inter-subjects heat map of gaze data distribution drawn above the image analysed (data concatenation of all hdf file's)

The user also has the choice between displaying the gaze data of right or left eye or the gaze average of both eyes.
The heat map is computed using a 2d histogram of gaze data smoothed by a gausian filter.

# INPUT :
    - images explored during experiments in img_path directory
    - hdf files recorded during the expriments
    
# PARAMETERS TO BE SET :
    - IMG_PATH      = directory where are stored the experiment's images
    - HDF_PATH      = directory where are stored the hdf files recorded
    - FILENAME      = list of hdf files where are stored the gaze data to visualize
    - T_IMG         = duration of the image exploration phase in seconds during the experiments
    - HEATMAP_DETAIL= gaussian blur kerner of the image (higher number = more blur)
    - F_TRACKER_MAX = highest sampling frequency in Hz of the eyetrackers used during FILENAME experiments
"""

################## Import package ##################
from tkinter import ttk
import tkinter as tk

import warnings
import os
import numpy as np
import h5py

import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.colors import ListedColormap


################## Parameters ##################
# experiment data directory and files
PATH = os.getcwd()
IMG_PATH = PATH + '\Gaze_recording\ExplorationImgCoder\img\\'
HDF_PATH = PATH + '\Gaze_recording\ExplorationImgCoder\data\\'
FILENAME =  ['ExploIMG_PupilCore_m_001.hdf5','ExploIMG_Tobii_d_001.hdf5'] # files to visualize
print(PATH,IMG_PATH)

'''
IMG_PATH = 'C:/Users/marion/Documents/Gaze_recording/ExplorationImgCoder/img/'   # pathway of the images used during experiment
HDF_PATH = 'C:/Users/marion/Documents/Gaze_recording/ExplorationImgCoder/data/'  # pathway of the HDF files recorded
FILENAME =  ['ExploIMG_PupilCore_m_001.hdf5','ExploIMG_Tobii_d_001.hdf5'] # files to visualize
'''
# heat map parameters
HEATMAP_DETAIL = 0.04 #0.05 # this will determine the gaussian blur kerner of the image (higher number = more blur)

# parameters useful just to init gaze data array's size which must be above T_IMG*F_TRACKER_MAX
T_IMG = 7           # duration of the image exploration phase in seconds
F_TRACKER_MAX = 120 # highest sampling frequency in Hz of the eyetrackers used during FILENAME experiments


################## Function definitions ##################
def validate():
    """
    Get the user choice made in the widget's menu
    """
    global DATA_CHOICE
    global PLOT_CHOICE
    DATA_CHOICE = w1.get()
    PLOT_CHOICE = w.get()
    win.destroy()

def heatmap(gaze_x, gaze_y, grid, detail):
    """
    Compute a heatmap of gaze data density using a 2d histogram blurred by a gaussian filter

    Parameters
    ----------
    gaze_x : numpy.array of float
        Contain the x gaze data of all hdf files for one specific image reference.
    gaze_y : numpy.array of float
       Contain the y gaze data of all hdf files for one specific image reference.
    grid : tupple
        size of the image reference.
    detail : float
        Coeff. of the gaussian blur kerner.

    Returns
    -------
    H :  numpy.array of float
        Density map of the gaze data distribution.
    """
    # To extend the heat map to the image's border (and not only to the raw gaze border) -> set 2 fake points to the image edges
    gaze_x = np.concatenate((gaze_x,[-img.shape[1]/2,img.shape[1]/2]))
    gaze_y = np.concatenate((gaze_y,[-img.shape[0]/2,img.shape[0]/2]))

    # compute the 2d histogram of gaze distribution (gaze density map)
    hist, x_edges, y_edges = np.histogram2d(gaze_x,gaze_y,bins=grid)

    # smoothing of density map -> gaussian blur kernel as a function of grid size
    filter_h = int(detail * grid[0])
    filter_w = int(detail * grid[1])
    htmp = gaussian_filter(hist.T, sigma=(filter_w, filter_h), order=0)
    return htmp

def heatmap_plot(image_name, image,extent,HM ):
    "display the histogram overlap on the reference image"
    plt.figure()
    plt.title('Heat map '+image_name)
    plt.imshow(image, cmap=plt.cm.gray, extent=extent)
    plt.imshow(HM, cmap=my_cmap, extent=extent, origin='lower')#,interpolation='bilinear')
    plt.axis('off')

def raw_gaze_plot(image_name,x,y,filename,extent,image,win_size):
    fig, ax = plt.subplots()
    ax.set_title('Raw gaze plot : '+image_name)
    ax.plot(x, y, marker='',   # marker='.'
            linewidth=1, markersize=6,
            linestyle='-',fillstyle='full', #linestyle='dashed'
            label=filename)
        
    ax.imshow(image, extent=extent)    
    plt.xlim([-int(win_size[0])/2,int(win_size[0])/2])
    plt.ylim([-int(win_size[1])/2,int(win_size[1])/2])
    ax.axis('on')
    ax.legend()
        
def raw_heatmap_plot(image_name,x,y,FILENAME,extent,image,win_size,cmap):
    # display the histogram overlap on the reference image
    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle("Gaze data visualisation : "+image_name, fontsize=15,fontweight="bold")

    ax1.imshow(image, cmap=plt.cm.gray, extent=extent)
    ax1.imshow(H, cmap=my_cmap, extent=extent, origin='lower')#,interpolation='bilinear')
    ax1.axis('off')
    ax1.set_title('Heat map')

    # plot raw gaze data over reference image      
    ax2.plot(x, y, marker='',linewidth=1, markersize=6,linestyle='-',fillstyle='full',label=FILENAME)
    ax2.imshow(image, extent=[-image.shape[1] /2., image.shape[1] /2., -image.shape[0]/2., image.shape[0]/2.]) # set the coordinate origin to the center
    ax2.axis('on')
    ax2.set_title('Raw gaze plot')
        
    plt.xlim([-int(win_size[0])/2,int(win_size[0])/2])
    plt.ylim([-int(win_size[1])/2,int(win_size[1])/2])
        
def find_first_index(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)][0]


################## Create a transparent color map for heatmap draw ##################
cmap          = plt.cm.jet
my_cmap       = cmap(np.arange(cmap.N))   # Get the colormap colors
my_cmap[:,-1] = np.linspace(0, 1, cmap.N) # Set transparency
my_cmap       = ListedColormap(my_cmap)   # Create new colormap


################## Dialog box to set visualization choice ##################
# config the widget window
win = tk.Tk()  # init the widget
win.geometry('500x100')
win.title('Plot parameters')

# config the box menu data choice
w1 = ttk.Label(win, text = "Select binocular data :")
w1.grid(column = 0,row = 1, padx = 10, pady = 5)
w1 = ttk.Combobox(win, values = ['Left eye', 'Right eye', 'Average both eyes']) #box menu
w1.grid(row=1,column=1,padx=10,pady=5)  # adding to grid
w1.set('Average both eyes')             # default selected option

# config the box menu plot choice
w = ttk.Label(win, text = "Select plot type :")
w.grid(column = 0,row = 2, padx = 10, pady = 5)
w = ttk.Combobox(win, values = ['Heat_map', 'Raw_gaze_plot', 'Both']) #box menu
w.grid(row=2,column=1,padx=10,pady=5)    # adding to grid
w.set('Raw_gaze_plot')                   # default selected option

#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate())
b1.grid(row=2,column=3)
win.mainloop()


################## Search image files used in /IMG_PATH ##################
img_list = []

for f in os.listdir(IMG_PATH):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".jpg",".png"]:
        continue
    img_list.append(f)

nb_image = np.size(img_list)


################## Search for each image the corresponding gaze data in all hdf file loaded  ##################
nb_file  = np.size(FILENAME)
FRAMES   = T_IMG*F_TRACKER_MAX*3

for i in range(nb_image): # LOOP OVER IMAGES

    # --- Init arrays to store gaze data of all hdf files specific to one given image ---#
    #  Init empty 1d data arrays to store gaze data for heat map plot
    gaze_x_htmp = []
    gaze_y_htmp = []

    # Init 2d arrays to store gaze data for raw gaze plot (size=nb_file,nb_sample_per_trials)
    gaze_x_raw = np.empty((FRAMES,nb_file))*np.nan
    gaze_y_raw = np.empty((FRAMES,nb_file))*np.nan

    # ---  load the image to plot --- #
    img  = plt.imread(IMG_PATH+img_list[i])
    img_size = img.shape[0:2] # height, width of the loaded image
    extent = [-img_size[1]/2,img_size[1]/2,-img_size[0]/2,img_size[0]/2] #set the image coordinate origin to the image center

    # --- LOOP OVER FILES --- #
    for s in range(nb_file):

        # --- Import hdf file data --- #
        # Open hierachical element contained in the HDF data file
        f = h5py.File(HDF_PATH+FILENAME[s],'r')

        # Import Experiment gaze data & events
        bino_data = f['data_collection']['events']['eyetracker']['BinocularEyeSampleEvent']  # Access to the Binocular eye Samples of the HDF file
        events    = f['data_collection']['events']['experiment']['MessageEvent']  # access to the binocular gaze data of the HDF file

        # --- Research the event id of the first and last samples recorded during the image exploration phase
        # Research the array index of the image event label
        index_img_labbel = np.where(events['text'].astype('U128') == img_list[i])

        if len(index_img_labbel[0]) != 0 :  # if the data exist for this image ('img_list[i]' exists)                              
            
            # read the time at which the image exploration pahse started
            index_img_labbel = index_img_labbel[0][0]
            t_start_img   = events['text'][index_img_labbel-1].astype('U128').replace('IMAGE_START :','')

            if len(events['event_id'])-1 > index_img_labbel+1: # & if the image exploration has been complete (IMG_STOP exists)

                # read the time at which the image exploration phase stoped
                t_stop_img     = events['text'][index_img_labbel+1].astype('U128').replace('IMAGE_STOP :','')

                # research the index array corresponding in bino_array to the begining and the end of the image exploration
                ind_gaze_stop  = find_first_index(bino_data['time'], lambda e:e> float(t_stop_img))
                ind_gaze_start = find_first_index(bino_data['time'], lambda e:e> float(t_start_img))
                
                # --- Get gaze data for this image exploration according to the user choice of visualization --- #
                if DATA_CHOICE == 'Right eye':
                    img_gaze = np.array([bino_data['right_gaze_x'][ind_gaze_start:ind_gaze_stop], bino_data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]])

                elif DATA_CHOICE == 'Left eye':
                    img_gaze = np.array([bino_data['left_gaze_x'][ind_gaze_start:ind_gaze_stop], bino_data['left_gaze_y'][ind_gaze_start:ind_gaze_stop]])

                elif DATA_CHOICE == 'Average both eyes' :  # compute gaze average between both eyes
                    with warnings.catch_warnings():        # removee RuntimeWarnings from nanmean
                        warnings.simplefilter("ignore", category=RuntimeWarning)
                        avg_gaze_x = np.nanmean(np.array([bino_data['left_gaze_x'][ind_gaze_start:ind_gaze_stop],bino_data['right_gaze_x'][ind_gaze_start:ind_gaze_stop]]), axis=0)
                        avg_gaze_y = np.nanmean(np.array([bino_data['left_gaze_y'][ind_gaze_start:ind_gaze_stop],bino_data['right_gaze_y'][ind_gaze_start:ind_gaze_stop]]), axis=0)
                        img_gaze   = np.array([avg_gaze_x, avg_gaze_y])

                img_gaze = img_gaze.T

                # remove samples with NaN value in one of the (x,y) coordinates = Blink
                img_gaze = img_gaze[~np.isnan(img_gaze).any(axis=1)]

                # --- store gaze data for this hdf file in the arrays with those from others hdf files ---#
                # Heat map: concat with gaze data of others hdf files
                if len(gaze_x_htmp) != 0: 
                    gaze_x_htmp = np.concatenate((gaze_x_htmp, img_gaze[:,0]))
                    gaze_y_htmp = np.concatenate((gaze_y_htmp, img_gaze[:,1]))
                else:
                    gaze_x_htmp = img_gaze[:,0]
                    gaze_y_htmp = img_gaze[:,1]

                # Raw gaze plot: store gaze data in different column for each hdf file
                gaze_x_raw[0:np.size(img_gaze,0),s] = img_gaze[:,0]
                gaze_y_raw[0:np.size(img_gaze,0),s] = img_gaze[:,1]
                
                
    ################## Get the window size used during experiment ##################
    win_size = events['text'][0].astype('U128').replace('ScreenSize=','')
    win_size = win_size.replace('[','')
    win_size = win_size.replace(']','')
    win_size = list(win_size.split(", "))
    
    ################## Heat map plot #######################
    if len(gaze_x_htmp) != 0 and PLOT_CHOICE == 'Heat_map': # if data exist
        # --- Display the histogram overlap on the reference image --- #
        H = heatmap(gaze_x_htmp, gaze_y_htmp, img_size, HEATMAP_DETAIL,cmap)
        heatmap_plot(img_list[i],img,extent,H)

    ################## Raw gaze data plot ##################
    if len(gaze_x_raw) != 0 and PLOT_CHOICE == 'Raw_gaze_plot': # if data exist
        # --- Display raw gaze data overlap on the reference image --- #
        raw_gaze_plot(img_list[i],gaze_x_raw,gaze_y_raw,FILENAME,extent,img,win_size)

    ################## Heat map & raw data subplot #######################
    if len(gaze_x_raw) != 0 and PLOT_CHOICE == 'Both':
        # --- Display raw gaze + heatmap overlap on the reference image --- #
        H = heatmap(gaze_x_htmp, gaze_y_htmp, img_size, HEATMAP_DETAIL)
        raw_heatmap_plot(img_list[i],gaze_x_raw,gaze_y_raw,FILENAME,extent,img,win_size,cmap)
        
