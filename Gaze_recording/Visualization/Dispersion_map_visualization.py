################## Import package ##################
from tkinter import ttk
import tkinter as tk
import math as mt
import warnings
import os
from cv2 import line
import numpy as np
import h5py
import platform
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.colors import ListedColormap
import pandas
import Methode_I_DT as IDT
import Methode_I_VT as IVT


################## Parameters ##################
# experiment data directory and files
PATH = os.getcwd()
if platform.system() == 'Windows' :
    IMG_PATH = PATH + '\Gaze_recording\ExplorationImgCoder\img\\'
    #IMG_PATH = 'D:\Cours\IESE4\PupilCore_POLYTECH\PupilCore_Poly\Gaze_recording\ExplorationImgCoder\img\\'
    HDF_PATH = PATH + '\Gaze_recording\ExplorationImgCoder\data\\'
    #HDF_PATH = 'D:\Cours\IESE4\PupilCore_POLYTECH\PupilCore_Poly\Gaze_recording\ExplorationImgCoder\data\\'

elif platform.system() == 'Darwin':
    IMG_PATH = PATH + '/Gaze_recording/ExplorationImgCoder/img/'
    HDF_PATH = PATH + '/Gaze_recording/ExplorationImgCoder/data/'


#FILENAME =  ['ExploIMG_PupilCore_m_001.hdf5','ExploIMG_Tobii_d_001.hdf5'] # files to visualize
FILENAME =  ['ExploIMG_PupilCore_m_001.hdf5']

# parameters useful just to init gaze data array's size which must be above T_IMG*F_TRACKER_MAX
T_IMG = 7           # duration of the image exploration phase in seconds
F_TRACKER_MAX = 120 # highest sampling frequency in Hz of the eyetrackers used during FILENAME experiments

# Defining the dataframe which will contain all the informations about the fixations
FIXATION_INFORMATION = pandas.DataFrame()
SACCADE_INFORMATION = pandas.DataFrame()
INFORMATION = pandas.DataFrame()

################## Function definitions ##################
def validate_win():
    """
    Get the user choice made in the widget's menu
    """
    global DATA_CHOICE
    global PLOT_CHOICE
    global METHOD_CHOICE
    
    DATA_CHOICE = data_choice.get()
    PLOT_CHOICE = plot_choice.get()
    METHOD_CHOICE = method_choice.get()
    win.destroy()

def validate_win_dis():
    """
    Get the user choice made in the widget's menu
    """
        
    global RADIUS_CHOICE
    global DURATION_CHOICE
        
    RADIUS_CHOICE = float(radius_choice.get())
    DURATION_CHOICE = 0.001 * float(duration_choice.get())
    win_dis.destroy()

def validate_win_vel():
    """
    Get the user choice made in the widget's menu
    """
        
    global THRESOLD_SPEED
        
    THRESOLD_SPEED = float(thresold_speed.get())
    win_vel.destroy()

def dispersion_plot(time,image_name,x,y,cercle,extent,image,win_size):
    fig, ax = plt.subplots(2,sharex=False, sharey=False)
    ax[0].set_title('Raw gaze plot : '+image_name)
    for center in cercle :
        ax[0].add_artist(plt.Circle((center[0],center[1]),center[2],linewidth = 2, fill=0 ,color = 'red'))

    ax[0].imshow(image, extent=extent)    
    ax[0].set_xlim([-int(win_size[0])/2,int(win_size[0])/2])
    ax[0].set_ylim([-int(win_size[1])/2,int(win_size[1])/2])

    #Pour la 2eme image : 
    ax[1].set_title('Dispersion gaze plot : '+image_name)
    ax[1].plot(time,x,label='x')
    ax[1].plot(time,y,label='y')
    #plt.plot(time,x,label='x')
    #plt.plot(time,y,label='y')
   
    #Plot des deux images dans une 
    ax[1].axis('on')
    ax[1].legend()
    ax[0].axis('on')
    ax[0].legend()
    plt.show()

def raw_gaze_plot(time,image_name,x,y,filename,extent,image,win_size):
    """Fonction qui affiche les points de regard sur l'image"""
    fig, ax = plt.subplots(2,sharex=False, sharey=False)

    #Pour la 1ere image : 
    ax[0].set_title('Raw gaze plot : '+image_name)
    ax[0].plot(x, y, marker='',   # marker='.'
            linewidth=1, markersize=6,
            linestyle='-',fillstyle='full', #linestyle='dashed'
            label=filename)
        
    ax[0].imshow(image, extent=extent)    
    ax[0].set_xlim([-int(win_size[0])/2,int(win_size[0])/2])
    ax[0].set_ylim([-int(win_size[1])/2,int(win_size[1])/2])

    #Pour la 2eme image : 
    ax[1].set_title('Raw gaze plot : '+image_name)
    ax[1].plot(time,x,label='x')
    ax[1].plot(time,y,label='y')
    #plt.plot(time,x,label='x')
    #plt.plot(time,y,label='y')
   
    #Plot des deux images dans une 
    ax[1].axis('on')
    ax[1].legend()
    ax[0].axis('on')
    ax[0].legend()
    plt.show()

def Disper_raw_plot(time,image_name,x,y,filename,extent,image,win_size,cercle):
    """Fonction qui affiche les points de regard sur l'image"""
    fig, ax = plt.subplots(2,sharex=False, sharey=False)
    ax[0].set_title('Dispersion & Raw gaze plot : '+image_name)
    ax[0].plot(x, y, marker='',   # marker='.'
            linewidth=1, markersize=6,
            linestyle='-',fillstyle='full', #linestyle='dashed'
            label=filename)
    for center in cercle :
        ax[0].add_artist(plt.Circle((center[0],center[1]),center[2],
                                linewidth = 2, fill=0 ,color = 'blue'))
    ax[0].imshow(image, extent=extent)    
    ax[0].set_xlim([-int(win_size[0])/2,int(win_size[0])/2])
    ax[0].set_ylim([-int(win_size[1])/2,int(win_size[1])/2])

    #Pour la 2eme image : 
    ax[1].set_title('Dispersion & Raw gaze plot : '+image_name)
    ax[1].plot(time,x,label='x')
    ax[1].plot(time,y,label='y')
    #plt.plot(time,x,label='x')
    #plt.plot(time,y,label='y')
   
    #Plot des deux images dans une 
    ax[1].axis('on')
    ax[1].legend()
    ax[0].axis('on')
    ax[0].legend()
    plt.show() 

def Save_fixation(Fixation,participant,image):
    #on ajoute le nom et numéro du participant de l'éxperience 
    participant = participant.split('_')
    nom = participant[2] + ' n° ' + participant[3][0:len(participant[3])-5]

    #on transforme le tableau en dataframe afin d'être sauvegardé
    Fixation_array = np.array(Fixation,dtype=[('Fixation_x (px)','<i1'),('Fixation_y (px)','<i1'),('rayon (px)','<f4'),('Time Start (s)','<f4'),('Duration (s)','<f4')])
    FIXATION_INFORMATION = pandas.DataFrame(Fixation_array, columns=['Fixation_x (px)','Fixation_y (px)','rayon (px)','Time Start (s)','Duration (s)'])

    if os.path.isfile(nom + ' fixation.xlsx'):
        with pandas.ExcelWriter(nom + ' fixation.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace", ) as xls:
            FIXATION_INFORMATION.to_excel(xls, sheet_name=image, index=True,)
    else:
        FIXATION_INFORMATION.to_excel(nom + ' fixation.xlsx', sheet_name=image, index=True,)

def Save_Saccade(Saccade,participant,image):
    #on ajoute le nom et numéro du participant de l'éxperience 
    participant = participant.split('_')
    nom = participant[2] + ' n° ' + participant[3][0:len(participant[3])-5]
    
    #on transforme le tableau en dataframe afin d'être sauvegardé
    Saccade_array = np.array(Saccade,dtype=[('Type',np.unicode_, 16), ('X_start (px)','<i1'), ('Y_start (px)','<i1'), ('X_end (px)','<i1'), ('Y_end (px)','<i1'),('Time Start (s)','<f4'),('Time End (s)','<f4'),('Duration (s)','<f4')])
    SACCADE_INFORMATION = pandas.DataFrame(Saccade_array, columns=['Type','X_start (px)','Y_start (px)','X_end (px)','Y_end (px)','Time Start (s)','Time End (s)','Duration (s)'])

    if os.path.isfile(nom + ' saccade.xlsx'):
        with pandas.ExcelWriter(nom + ' saccade.xlsx', mode="a", engine="openpyxl", if_sheet_exists="replace", ) as xls:
            SACCADE_INFORMATION.to_excel(xls, sheet_name=image, index=True,)
    else:
        SACCADE_INFORMATION.to_excel(nom + ' saccade.xlsx', sheet_name=image, index=True,)

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
win.geometry('600x150')
win.title('Plot parameters')
Row = 1

# config the box menu data choice
data_choice = ttk.Label(win, text = "Select binocular data :")
data_choice.grid(column = 0,row = Row, padx = 10, pady = 5)
data_choice = ttk.Combobox(win, values = ['Left eye', 'Right eye', 'Average both eyes']) #box menu
data_choice.grid(row=Row,column=1,padx=10,pady=5)  # adding to grid
data_choice.set('Average both eyes')             # default selected option

# config the box menu plot choice
Row += 1
plot_choice = ttk.Label(win, text = "Select plot type :")
plot_choice.grid(column = 0,row = Row, padx = 10, pady = 5)
plot_choice = ttk.Combobox(win, values = ['None', 'Dispersion_plot', 'Raw_gaze_plot', 'Both']) #box menu
plot_choice.grid(row=Row,column=1,padx=10,pady=5)    # adding to grid
plot_choice.set('None')                   # default selected option

# config the box menu methode choice
Row += 1
method_choice = ttk.Label(win, text = "Select method :")
method_choice.grid(column = 0,row = Row, padx = 10, pady = 5)
method_choice = ttk.Combobox(win, values = ['Dispersion', 'Velocity']) #box menu
method_choice.grid(row=Row,column=1,padx=10,pady=5)    # adding to grid
method_choice.set('Velocity')                   # default selected option

#config the validation button
b1=tk.Button(win,text="Submit", command=lambda: validate_win())
b1.grid(row=Row,column=3)
win.mainloop()

if METHOD_CHOICE == 'Dispersion':
    # config the widget window
    win_dis = tk.Tk()  # init the widget
    win_dis.geometry('600x100')
    win_dis.title('Plot parameters')
    Row = 1

    # config the dispersion radius
    Row += 1
    radius_choice = ttk.Label(win_dis, text = "Maximum fixation dispersion:")
    radius_choice.grid(column = 0,row = Row, padx = 10, pady = 5)
    radius_choice = ttk.Entry(win_dis)
    radius_choice.insert(0,"150") #Valeur du rayon
    radius_choice.grid(row=Row,column=1,padx=10,pady=5)  # adding to grid

    # config the duration thresold
    Row += 1
    duration_choice = ttk.Label(win_dis, text = "Minimum fixation duration (ms) :")
    duration_choice.grid(column = 0,row = Row, padx = 10, pady = 5)
    duration_choice = ttk.Entry(win_dis)
    duration_choice.insert(0,"200") #Valeur du temps
    duration_choice.grid(row=Row,column=1,padx=10,pady=5)  # adding to grid

    #config the validation button
    b1=tk.Button(win_dis,text="Submit", command=lambda: validate_win_dis())
    b1.grid(row=Row,column=3)
    win_dis.mainloop()

elif METHOD_CHOICE == 'Velocity':
    # config the widget window
    win_vel = tk.Tk()  # init the widget
    win_vel.geometry('600x100')
    win_vel.title('Plot parameters')
    Row = 1

    # config the thresoldspeed
    Row += 1
    thresold_speed = ttk.Label(win_vel, text = "Minimum thresoldspeed (px/s) :")
    thresold_speed.grid(column = 0,row = Row, padx = 10, pady = 5)
    thresold_speed = ttk.Entry(win_vel)
    thresold_speed.insert(0,"1000") #Valeur de ref
    thresold_speed.grid(row=Row,column=1,padx=10,pady=5)  # adding to grid

    #config the validation button
    b1=tk.Button(win_vel,text="Submit", command=lambda: validate_win_vel())
    b1.grid(row=Row,column=3)
    win_vel.mainloop()

################## Search for each image the corresponding gaze data in all hdf file loaded  ##################
nb_file  = np.size(FILENAME)
FRAMES   = T_IMG*F_TRACKER_MAX*3

# --- LOOP OVER FILES --- #
for s in range(nb_file):

    # --- Import hdf file data --- #
    # Open hierachical element contained in the HDF data file
    f = h5py.File(HDF_PATH+FILENAME[s],'r')
 
    # Init 2d arrays to store gaze data for raw gaze plot (size=nb_file,nb_sample_per_trials)
    gaze_x_raw = np.empty((FRAMES,nb_file))*np.nan
    gaze_y_raw = np.empty((FRAMES,nb_file))*np.nan
    gaze_time_xy = np.empty((FRAMES,nb_file))*np.nan
    # Import Experiment gaze data & events
    bino_data = f['data_collection']['events']['eyetracker']['BinocularEyeSampleEvent']  # Access to the Binocular eye Samples of the HDF file
    events    = f['data_collection']['events']['experiment']['MessageEvent']  # access to the binocular gaze data of the HDF file

    
    for i in range(nb_image): # LOOP OVER IMAGES
            # ---  load the image to plot --- #
        img  = plt.imread(IMG_PATH+img_list[i])
        img_size = img.shape[0:2] # height, width of the loaded image
        extent = [-img_size[1]/2,img_size[1]/2,-img_size[0]/2,img_size[0]/2] #set the image coordinate origin to the image center

        # --- Research the event id of the first and last samples recorded during the image exploration phase
        # Research the array index of the image event label
        index_img_labbel = np.where(events['text'].astype('U128') == img_list[i])

        if len(index_img_labbel[0]) != 0 :  # if the data exist for this image ('img_list[i]' exists)                              
            
            # read the time at which the image exploration phase started
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
                        gaze_time = np.array(bino_data['time'][ind_gaze_start:ind_gaze_stop])
                        img_gaze   = np.array([avg_gaze_x, avg_gaze_y,gaze_time])
                
                #get all the value of time for each gaze and each image
                
                img_gaze = img_gaze[~np.isnan(img_gaze).any(axis=1)]
            
       

        ################## Get the window size used during experiment ##################
        win_size = events['text'][0].astype('U128').replace('ScreenSize=','')
        win_size = win_size.replace('[','')
        win_size = win_size.replace(']','')
        win_size = list(win_size.split(", "))

        ################## Raw gaze data plot ##################
        if len(img_gaze[0]) != 0 and PLOT_CHOICE == 'Raw_gaze_plot': # if data exist
            # --- Display raw gaze data overlap on the reference image --- #
            raw_gaze_plot(img_gaze[2],img_list[i],img_gaze[0],img_gaze[1],FILENAME,extent,img,win_size)
            

        ################## Dispersion map plot #######################
        elif len(img_gaze[0]) != 0 and (PLOT_CHOICE == 'Dispersion_plot' or PLOT_CHOICE == 'Both' or PLOT_CHOICE == 'None'): # if data exist
            # --- Display the histogram overlap on the reference image --- #
            if METHOD_CHOICE == 'Dispersion':
                Fixation,Saccade = IDT.Choix_Methode_Dispersion("Salvucci",img_gaze[2],img_gaze[0],img_gaze[1],RADIUS_CHOICE,DURATION_CHOICE)
            elif METHOD_CHOICE == 'Velocity':
                Fixation,Saccade = IVT.Velocity(THRESOLD_SPEED,img_gaze[0],img_gaze[1],img_gaze[2])
            
            Save_fixation(Fixation,FILENAME[s],img_list[i])
            Save_Saccade(Saccade,FILENAME[s],img_list[i])

            if PLOT_CHOICE == 'Dispersion_plot':
                dispersion_plot(img_gaze[2],img_list[i],img_gaze[0],img_gaze[1],Fixation,extent,img,win_size)
            elif PLOT_CHOICE == 'Both':
                Disper_raw_plot(img_gaze[2],img_list[i],img_gaze[0],img_gaze[1],FILENAME[s],extent,img,win_size,Fixation) 
            else:
                pass
