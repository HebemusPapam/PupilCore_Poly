################## Import package ##################
from tkinter import ttk
import tkinter as tk
import math as mt
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
#FILENAME =  ['ExploIMG_PupilCore_m_001.hdf5','ExploIMG_Tobii_d_001.hdf5'] # files to visualize
FILENAME =  ['ExploIMG_PupilCore_m_001.hdf5']

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
    global RADIUS_CHOICE
    global DURATION_CHOICE
    DURATION_CHOICE = 0.001 * float(w3.get())
    RADIUS_CHOICE = float(w2.get())
    DATA_CHOICE = w1.get()
    PLOT_CHOICE = w.get()
    win.destroy()

    
def dispersion_map(time,gaze_x, gaze_y,radius,duration):

    """
    Return a list of cercle (x,y,radius) if the condition is respected
    A circle is created, if the dispersion and time between the points are contained in their respective threshold.
    The function first check if the distance between the point is longer than the radius and then if the time passed is sufficient.
    """
    tobii = 0
    rayon_dispersion = radius
    duration_limit = duration
    x_1 = gaze_x[0,tobii]
    y_1 = gaze_y[0,tobii]
    time_0 = time[tobii][0]
    NaN_count = 0
    cercle= []
    #we search the distance between each point 
    for i  in range(1,len(gaze_x)-2):
        if np.isnan(gaze_x[i,tobii]) or np.isnan(gaze_y[i,tobii]):
            NaN_count+=1
        else:
            x_2 = gaze_x[i,tobii]
            y_2 = gaze_y[i,tobii]
            
            time_1 = time[tobii][i-NaN_count]
            distance = mt.sqrt((x_1-x_2)**2 + (y_1-y_2)**2)
            #Event if the fixation is over (out of the circle)
            if distance > rayon_dispersion : 
                #The dispersion size must have evolved to be considered a fixation
                if rayon_dispersion != radius :
                    #The time between 2 points must be high enough
                    if time_1-time_0 >= duration_limit:
                        cercle.append((x_1,y_1,rayon_dispersion))  #The center of the fixation is saved
                        rayon_dispersion = radius #The dispersion is reset to its default value
                x_1 = x_2
                y_1 = y_2
                time_0=time_1
            elif rayon_dispersion < (radius*2):
                rayon_dispersion = rayon_dispersion * 1.01
    #Condition if the gaze stay in a circle and don't disperse at the end
    if time_1-time_0 >= duration_limit:
        cercle.append((x_1,y_1,rayon_dispersion))  #The center of the fixation is saved

    print("i : ",len(gaze_x)-2," naN :", NaN_count )
    print("cercle : ",cercle)
    return cercle

def dispersion_plot(image_name,cercle,extent,image,win_size,radius):
    fig, ax = plt.subplots()
    ax.set_title('Raw gaze plot : '+image_name)
    for center in cercle :
        print("centre ",center)
        ax.add_artist(plt.Circle((center[0],center[1]),center[2],
                                linewidth = 2, color = 'red',fill=0))
    ax.imshow(image, extent=extent)    
    plt.xlim([-int(win_size[0])/2,int(win_size[0])/2])
    plt.ylim([-int(win_size[1])/2,int(win_size[1])/2])
    ax.axis('on')
    ax.legend()
    plt.show()


def raw_gaze_plot(image_name,x,y,filename,extent,image,win_size):
    fig, ax = plt.subplots()
    ax.set_title('Dispersion gaze plot : '+image_name)
    ax.plot(x, y, marker='',   # marker='.'
            linewidth=1, markersize=6,
            linestyle='-',fillstyle='full', #linestyle='dashed'
            label=filename)
        
    ax.imshow(image, extent=extent)    
    plt.xlim([-int(win_size[0])/2,int(win_size[0])/2])
    plt.ylim([-int(win_size[1])/2,int(win_size[1])/2])
    ax.axis('on')
    ax.legend()
    plt.show()

def Disper_raw_plot(image_name,x,y,filename,extent,image,win_size,cercle):
    fig, ax = plt.subplots()
    ax.set_title('Dispersion gaze plot : '+image_name)
    ax.plot(x, y, marker='',   # marker='.'
            linewidth=1, markersize=6,
            linestyle='-',fillstyle='full', #linestyle='dashed'
            label=filename)
    for center in cercle :
        print("centre ",center)
        ax.add_artist(plt.Circle((center[0],center[1]),center[2],
                                linewidth = 2, color = 'red',fill=0))
    ax.imshow(image, extent=extent)    
    plt.xlim([-int(win_size[0])/2,int(win_size[0])/2])
    plt.ylim([-int(win_size[1])/2,int(win_size[1])/2])
    ax.axis('on')
    ax.legend()
    plt.show()   


def find_first_index(lst, condition):
    return [i for i, elem in enumerate(lst) if condition(elem)][0]
################## Search image files used in /IMG_PATH ##################
img_list = []

for f in os.listdir(IMG_PATH):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".jpg",".png"]:
        continue
    img_list.append(f)

nb_image = np.size(img_list)

################## Dialog box to set visualization choice ##################
# config the widget window
win = tk.Tk()  # init the widget
win.geometry('500x140')
win.title('Plot parameters')

# config the duration thresold
w3 = ttk.Label(win, text = "Minimum fixation duration (ms) :")
w3.grid(column = 0,row = 4, padx = 10, pady = 5)
w3 = ttk.Entry(win)
w3.insert(0,"150") #Valeur du temps
w3.grid(row=4,column=1,padx=10,pady=5)  # adding to grid

# config the dispersion radius
w2 = ttk.Label(win, text = "Maximum fixation dispersion:")
w2.grid(column = 0,row = 3, padx = 10, pady = 5)
w2 = ttk.Entry(win)
w2.insert(0,"30") #Valeur du rayon
w2.grid(row=3,column=1,padx=10,pady=5)  # adding to grid

# config the box menu data choice
w1 = ttk.Label(win, text = "Select binocular data :")
w1.grid(column = 0,row = 1, padx = 10, pady = 5)
w1 = ttk.Combobox(win, values = ['Left eye', 'Right eye', 'Average both eyes']) #box menu
w1.grid(row=1,column=1,padx=10,pady=5)  # adding to grid
w1.set('Average both eyes')             # default selected option

# config the box menu plot choice
w = ttk.Label(win, text = "Select plot type :")
w.grid(column = 0,row = 2, padx = 10, pady = 5)
w = ttk.Combobox(win, values = ['Dispersion_map', 'Raw_gaze_plot', 'Both']) #box menu
w.grid(row=2,column=1,padx=10,pady=5)    # adding to grid
w.set('Both')                   # default selected option



#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate())
b1.grid(row=3,column=3)
win.mainloop()

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
    gaze_time = np.empty((FRAMES,nb_file))*np.nan
    gaze_time_xy = [0,0]
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
                
                #get all the value of time for each gaze and each image
                
                gaze_time = np.array(bino_data['time'][ind_gaze_start:ind_gaze_stop])
                gaze_time = gaze_time.T
                # remove samples with NaN value in one of the (x,y) coordinates = Blink
                count = 0
                index_NaN=[]
                for element in img_gaze :
                    if np.isnan(element).any():
                        index_NaN.append(count)
                    count=count+1 #we seek the index of the NaN value
                # remove samples trough their index, can remove the associate temporal data
                np.delete(img_gaze,index_NaN)
                np.delete(gaze_time,index_NaN)
                gaze_time_xy[s] = gaze_time
                """
                img_gaze = img_gaze[~np.isnan(img_gaze).any(axis=1)]
                
                print("Time ", gaze_time,"\n","IMG : ", img_gaze,"\n")
                print("Time ", len(gaze_time),"\n","IMG : ", len(img_gaze),"\n")
                """
                # --- store time data for this hdf file in the arrays with those from others hdf files ---#

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

    ################## Dispersion map plot #######################
    if len(gaze_x_raw) != 0 and PLOT_CHOICE == 'Dispersion_map': # if data exist
        # --- Display the histogram overlap on the reference image --- #
       List_Circle = dispersion_map(gaze_time_xy,gaze_x_raw,gaze_y_raw,RADIUS_CHOICE,DURATION_CHOICE)
       dispersion_plot(img_list[i],List_Circle,FILENAME,extent,img,win_size)

    
    ################## Raw gaze data plot ##################
    if len(gaze_x_raw) != 0 and PLOT_CHOICE == 'Raw_gaze_plot': # if data exist
        # --- Display raw gaze data overlap on the reference image --- #
        raw_gaze_plot(img_list[i],gaze_x_raw,gaze_y_raw,FILENAME,extent,img,win_size)
    
    ################## Dispersion map & raw data subplot #######################
    if len(gaze_x_raw) != 0 and PLOT_CHOICE == 'Both':
        # --- Display raw gaze + heatmap overlap on the reference image --- #
        List_Circle = dispersion_map(gaze_time_xy,gaze_x_raw,gaze_y_raw,RADIUS_CHOICE,DURATION_CHOICE)
        Disper_raw_plot(img_list[i],gaze_x_raw,gaze_y_raw,FILENAME,extent,img,win_size,List_Circle)
    