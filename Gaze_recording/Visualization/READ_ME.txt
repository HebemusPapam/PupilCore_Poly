### heat_map.py & raw_gaze_plot.py ###

# REQUIREMENTS

  * Python 3.8  -> https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe
  * Python IDE to run the program as Spyder  -> https://docs.spyder-ide.org/3/installation.html
  * Python libraries:
	- h5py 3.7.0 
	- numpy
	- os
	- matplotlib
	- tkinter
	- scipy


# RAW GAZE PLOT 

Display raw binocular gaze data of the experiment session recorded by image_exploration.py.
The raw data are drawn over the corresponding image.

The user has the choice between displaying the right or left data or the data average of both eyes.
The user can load and subplot several data session. In this case the data will be subploted in different colors for each subject.

# HEAT MAP

Compute and display the inter subjects heat map by concatenating all subject's data loaded.
The heat map is computed using a 2d histogram smoothed by a gausian filter.


# PARAMETERS TO BE SET
	- IMG_PATH  = pathway of the images used during session's experiment (must be exactly the same as the ones used during experiment)
	- HDF_PATH  = pathway of the hdf files recorded during experiment
	- FILENAME  = list of hdf files containing gaze data to display
	- T_IMG     = duration of the image exploration phase in seconds -> must have been the same for all file experiments
	- F_TRACKER = sampling frequency of the eyetracker in Hz  -> must have been the same for all file experiments


# BEFORE RUNNING
1.Set in FILENAME the list of hdf files to display.
2.Put in the directory IMG_PATH all the images used during the experiments to visualize.


# WARNINGS 
  * In PsychoPy the coordinate origin was the image center and here in python it's the top left corner
    so the image plot is extent to set the cordinate origin to the image center too.