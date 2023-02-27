################## Import package ##################
from tkinter import ttk
import tkinter as tk
import math as mt
import warnings
import os
import numpy as np
import h5py
import platform
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.colors import ListedColormap
import pandas


################## Parameters ##################
# experiment data directory and files
PATH = os.getcwd()
#print(PATH)
if platform.system() == 'Windows' :
    IMG_PATH = PATH + '\Gaze_recording\ExplorationImgCoder\img\\'
    HDF_PATH = PATH + '\Gaze_recording\ExplorationImgCoder\data\\'
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

    
def dispersion_map(time,gaze_x, gaze_y,radius,duration,participant, image):

    """
    Return a list of fixation : cercle (x,y,radius) if the conditions are respected
    A circle is created, if the dispersion and time between the points are contained in their respective threshold.
    The function first check if the distance between the point is longer than the radius and then if the time passed is sufficient.
    """
    rayon_dispersion = radius
    duration_limit = duration
    x_1 = gaze_x[0]
    y_1 = gaze_y[0]
    time_0 = time[0]
    cercle= []
    points_in_fixation = [[x_1,y_1]]
    middle_fix = []
    #we search the distance between each point 
    for i in range(1,len(gaze_x)-2):
        if np.isnan(gaze_x[i])==False:
            x_2 = gaze_x[i]
            y_2 = gaze_y[i]
            time_1 = time[i]
            distance = mt.sqrt((x_1-x_2)**2 + (y_1-y_2)**2)
            #Event if the fixation is over (out of the circle)
            if distance > rayon_dispersion : 
                #The dispersion size must have evolved to be considered a fixation
                if rayon_dispersion != radius :
                    #The time between 2 points must be high enough
                    if time_1-time_0 >= duration_limit:
                        middle_fix = middle_calcul(points_in_fixation)
                        cercle.append((middle_fix[0],middle_fix[1],rayon_dispersion,time_0,time_1-time_0))  #The center of the fixation is saved
                        rayon_dispersion = radius #The dispersion is reset to its default value

                points_in_fixation = [[x_1,x_2]] #reset the points in a fixation 
                x_1 = x_2
                y_1 = y_2
                time_0=time_1

            elif rayon_dispersion < (radius*3):
                points_in_fixation.append([x_2,y_2])
                rayon_dispersion = rayon_dispersion * 1.01
    #Condition if the gaze stay in a circle and don't disperse at the end
    if time_1-time_0 >= duration_limit:
        middle_fix = middle_calcul(points_in_fixation)
        cercle.append((middle_fix[0],middle_fix[1],rayon_dispersion,time_0,time_1-time_0))  #The center of the fixation is saved
    Save_fixation(cercle,participant,image) 
    return cercle

def middle_calcul(points):
    """Fonction qui retourne les coordonées du centre d'une succession de points"""
    sum_x =0
    sum_y =0
    for point in points:
        sum_x += point[0]
        sum_y += point[1]
    return [sum_x/len(points),sum_y/len(points)]



#Fonction qui affiche les fixations sur l'image
def dispersion_plot(time,image_name,x,y,cercle,extent,image,win_size): 
    """Fonction qui affiche les fixations sur l'image"""
    fig, ax = plt.subplots(2,sharex=False, sharey=False) 

    #Pour la 1ere image 
    ax[0].set_title('Dispersion gaze plot : '+image_name)
    for center in cercle :
        #print("centre ",center)
        ax[0].add_artist(plt.Circle((center[0],center[1]),center[2],linewidth = 2, fill=0 ))#,color = 'red'

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
    

def Save_fixation(cercle,participant,image):
    #on ajoute le nom et numéro du participant de l'éxperience 
    participant = participant.split('_')
    nom = participant[2] + ' n° ' + participant[3][0:len(participant[3])-5]
    #on transforme le tableau en dataframe afin d'être sauvegardé
    Cercle_array = np.array(cercle,dtype=[('Fixation_x','<i1'),('Fixation_y','<i1'),('rayon','<f2'),('Time Start','<f2'),('Duration','<f2')])
    FIXATION_INFORMATION = pandas.DataFrame(Cercle_array, columns=['Fixation_x','Fixation_y','rayon','Time Start','Duration'])
    #FIXATION_INFORMATION.insert(0, 'INFORMATIONS', pandas.Series([nom,image], index=[0,1]))
    #print(FIXATION_INFORMATION)
    with pandas.ExcelWriter(nom + '.xlsx', mode="a", engine="openpyxl", if_sheet_exists="overlay", ) as xls:
        FIXATION_INFORMATION.to_excel(xls, sheet_name=image, index=True,)
    


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
                        gaze_time = np.array(bino_data['time'][ind_gaze_start:ind_gaze_stop])
                        img_gaze   = np.array([avg_gaze_x, avg_gaze_y,gaze_time])
                
                #get all the value of time for each gaze and each image
                
                img_gaze = img_gaze[~np.isnan(img_gaze).any(axis=1)]
            
       

        ################## Get the window size used during experiment ##################
        win_size = events['text'][0].astype('U128').replace('ScreenSize=','')
        win_size = win_size.replace('[','')
        win_size = win_size.replace(']','')
        win_size = list(win_size.split(", "))

        ################## Dispersion map plot #######################
        if len(img_gaze[0]) != 0 and PLOT_CHOICE == 'Dispersion_map': # if data exist
            # --- Display the histogram overlap on the reference image --- #
            List_Circle = dispersion_map(img_gaze[2],img_gaze[0],img_gaze[1],RADIUS_CHOICE,DURATION_CHOICE,FILENAME[s],img_list[i])
            #def dispersion_map(time,gaze_x, gaze_y,radius,duration,participant, image
            dispersion_plot(img_gaze[2],img_list[i],img_gaze[0],img_gaze[1],List_Circle,extent,img,win_size)
            

        ################## Raw gaze data plot ##################
        if len(img_gaze[0]) != 0 and PLOT_CHOICE == 'Raw_gaze_plot': # if data exist
            # --- Display raw gaze data overlap on the reference image --- #
            raw_gaze_plot(img_gaze[2],img_list[i],img_gaze[0],img_gaze[1],FILENAME,extent,img,win_size)
           
        
        ################## Dispersion map & raw data subplot #######################
        if len(img_gaze[0]) != 0 and PLOT_CHOICE == 'Both':
            # --- Display raw gaze + heatmap overlap on the reference image --- #
            List_Circle = dispersion_map(img_gaze[2],img_gaze[0],img_gaze[1],RADIUS_CHOICE,DURATION_CHOICE,FILENAME[s],img_list[i])
            Disper_raw_plot(img_gaze[2],img_list[i],img_gaze[0],img_gaze[1],FILENAME[s],extent,img,win_size,List_Circle) 
         
          

        
    