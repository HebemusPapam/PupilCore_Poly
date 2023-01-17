# -*- coding: utf-8 -*-
"""
Created on Mon Oct 24 10:23:30 2022
@author: Marion Léger


# REQUIREMENTS
Code designed for Psychopy 2022.2.4 and Python 3.8.
Python packages recquired :
    - numpy
	- matplotlib
    - tobii-research (pip install tobii-research (or py -m pip install ...))
    - Pupil core : 
    	1. pip install zmq msgpack==0.5.6
    	2. copied all of the files form psychopy github "\psychopy-release\psychopy\iohub\devices\eyetracker\hw\pupil_labs\pupil_core" 
    	into the “~\PsychoPy\Lib\site-packages\psychopy\iohub\devices\eyetracker\hw\pupil


# EXPERIMENT
Process image exploration trials in 3 phases :
    1. Fixation point
    2. Image plot : free image exploration
    3. Black background : rest phase

Images to explore are stored in a list that is shuffled before each experiment.
The eye tracking gaze data are recorded during all the experiment.
The experiment strats with a calibration process to read meaningful gaze data with precision.


# INPUT :
    - images to explored stored in the img_path directory
    - cross fixation and background images stored in the rest_fix_path directory

    
# OUTPUT : Data saved in a HDF5 file (Hierarchical Data Format)
    - Eyetracking binocular gaze data for each eyes
    - Event messages + corresponding times to label experimental steps

The HDF5 file is organized as followed:
data_collection/
	* events/
		- LogEvent 
		- MessageEvent
			Device_time			    // Time of the eye-tracker
			Logged_time
			Time				    // time of event, [sec.msec] format, using psychopy timebase
			Text				    // event messages sent during each trials ['TRIAL_START','FIXATION_START','FIXATION_STOP','IMAGE_START','imagename.jpg|png','IMAGE_STOP','REST_START','REST_STOP','TRIAL_END']
	* Eyetracker/
		- BinocularEyeSampleEvent   // gaze data recorded by the eyectracker
			The BinocularEyeSampleEvent event represents the eye position and eye attribute data collected from one frame or reading of an eye tracker device that is recording both eyes of a participant.
			Experiment_id
			Session_id 
			Devide_id = 0
			Event_id			    // number indicating the rank of the nth data saved in the hdf file
			Type
			Device_time [sec]		// time of gaze measurement, in sec.msec format, using the eye-tracker clock
			Logged_time [sec]		// time at which the sample was received in PsychoPy®, in sec.msec format,
			Time        			// time of gaze measurement, in sec.msec format, using PsychoPy clock
			Confidence_interval		----> Not supported by tobii & Pupil Core
			Delay				// The difference between logged_time and time, in sec.msec format
			Filter_id = 0
			R/L_gaze_x/y/z 			// The (x,y,z) gaze location in screen coordinates for the Left/Right eye, in [Display Coordinate Type Units = here Pixel].
			R/L_gaze_z = 0 			----> Not supported by tobii
			L/R_eye_cam_x/y/z 		// The Left/Right x/y/z eye position in the eye trackers 3D coordinate space
			L/R_angle_x 			----> Not supported by tobii -> Pupil Core : phi angle / horizontal rotation of the 3d eye model location in radians. -pi/2 corresponds to looking directly into the eye camera
			L/R_angle_y  			----> Not supported by tobii -> Pupil Core : theta angle / vertical rotation of the 3d eye model location in radians. pi/2 corresponds to looking directly into the eye camera	
			L/R_raw_x/y = 0   		----> Not supported by tobii -> Pupil Core : (x,y) components of the pupil center location in normalized coordinates
			L/R_pupil_measure1 		// Tobii : Left/Right eye pupil diameter in [mm]. Pupil Core : Major axis of the detected pupil ellipse in pixels
			L/R_pupil_mesure1_type
			L/R_pupil_measure2		----> Not supported by tobii -> Pupil Core : Diameter of the detected pupil in mm or None if not available
			L/R_ppd_x,y = 0 		----> Not supported by tobii -> Horizontal/Vertcial pixels per visual degree for this eye position as reported by the eye tracker.
			L/R_velocity_x/y/xy = 0 ----> Not supported by tobii -> Horizontal/Vertcial/2D velocity of the eye at the time of the sample
			Statut 				// Indicates if eye sample contains ‘valid’ data -> 0 = Eye sample is OK. 2 = Right eye data is likely invalid. 20 = Left eye data is likely invalid. 22 = Eye sample is likely invalid.
		
		- BlinkEndEvent 	  		----> Not supported by tobii & Pupil Core
		- BlinkStartEvent 	 		----> Not supported by tobii & Pupil Core
		- FixationEndEvent 	  		----> Not supported by tobii & Pupil Core
		- FixationStartEvent 	  	----> Not supported by tobii & Pupil Core
		
		- MonocularEyeSampleEvent 	----> Not supported by tobii -> Pupil Core same variables as BinocularEyeSampleEvent
							A MonocularEyeSampleEvent represents the eye position and eye attribute data collected from one frame or reading of an eye tracker device 
							that is recoding from only one eye, or is recording from both eyes and averaging the binocular data.
		
		- SaccadeEndEvent 	  		----> Not supported by tobii & Pupil Core
		- SaccadeStartEvent 	    ----> Not supported by tobii & Pupil Core
    
    
# PARAMETERS TO BE SET FOR THE EXPERIMENT :
    - img_path      = image pathway where are stored the experiment's images
    - rest_fix_path =  pathway of the fixation cross & the black background
    - screen_size   = screen resolution [pixel]
    - screen_name   = monitor name that have been set in Psychopy Builder 'Monitor settings and Calibration'
    - t_fix, t_img, t_rest = stimulis duration of the fixation, exploration & rest phase [sec]
    - sampling_tracker     = Sampling rate of the eyetracker [Hz]
   

# EYETRACKER SETUP
Before running the program on PsychoPy several step have to be done on Psychopy software :
1. Create and set monitor info (resolution, monitor width & the distance to the monitor) in PsychopPy Builder section 'Monitor settings and calibration'
2. Verify that the unit of the visual.Window in the Python code is well set to 'pix' in order to obtain gaze data in pixel unit
3. If you want to change the images to observe during the experiment add/remove them from the image directory img_path
4. For Tobii : 
	a. Connect the Tobii eye-tracker to the external processing unit and the processing unit to the PC
	b. Fix the eye-tracker above the screen using a magnetic sticker
	b. Set the eye-tracker dimension on the screen with the Eyetracker Manager of Tobii software : https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-eye-tracker-manager#downloads)
5. For pupil core : https://psychopy.org/api/iohub/device/eyetracker_interface/PupilLabs_Core_Implementation_Notes.html#additional-software-requirements
	a. In the Psychopy code set Pupil Remote IP Address/Port in ioConfig[pupil_remote] (keep default): Defines how to connect to Pupil Capture. See Pupil Capture’s Network API menu to check address and port are correct.
	b. Install Pupil Capture v.2.0 software or newer in your computer	
    c. In pupil Capture software :
        1. Connect the PupilCore glasses to the computer
        2. In the general settings select Pupil dection + detect eye 0 + eye 1
        3. In Calibration set choreography = Screen Marker, gaze mapping = 3D, chose the monitor use to display the experiment.
        4. Print 4 apriltag markers and attaching them at the screen corners. Avoid occluding the screen and leave sufficient white space around the marker squares.
        5. Set the world camera position and resolution to see completly the screen and AprilTag
        6. In Pupil Capture Plugin manager select the pluggins : Network API (check that port = 50020), Time Sync, Surface tracker
    	7. In the Surface tracker plugin : 
            - set april parameters to high resolution + sharpen image
            - define a surface using the markers and align its surface corners with the screen corners as good as possible (you can freeze the image to help)
    	    - rename the surface to the name set in the Surface Name field of the eye tracking project settings ioConfig (default: psychopy_iohub_surface, width = height = 1.0)
        8. Eye camera settings :
            - Set both eyecamera to the same resolution and frame frequency you want
            - Move the eye camera to put your eyes in the image center
            - For both eyes, In Pye3D detector reset the 3D model and rolls your eyes
            - the blue circles of the 3d model must fit your eye shapes and be completly visible IMPORTANT
            - your pupil is well detect if the red circle fit your pupil and is constant and if the blue circle fit well your eye shape
        9. Let the software open and run this program
"""

################## Import package ##################
import os
import os.path

from psychopy import gui, visual, core, logging, clock
from numpy.random import  shuffle
from psychopy.hardware import keyboard

import psychopy.iohub as io
import numpy as np


################## Parameters ##################
expSetting ={
  "img_path": "img/",                # pathway of the experiment's images to explore
  "rest_fix_path": "img_fix_rest/",  # pathway of fixation cross & the black background
  "screen_size": [2560, 1080], # screen resolution [pixel]
  "screen_name": 'Dell1',      # name of the monitor set in PsychoPy builder
  "screen_frame": 60.0,        # monitor refresh frequency [Hz]
  # WARNINGS duration of stimulus must be t_stimulus = alpha*1/Fe_screen to display for complete monitor frame refresh
  # exemple t = 1/60 * 300 frames = 5.0sec
  "t_fix": 5.0,  # duration in [sec] of fixation stimulis,
  "t_img": 300,  # duration in frame of image stimulis
  "t_rest":300,  # duration in frame of black rest screen
}

################## Function definitions ##################
def stimuli_display(frame_stim, stimuli, window, start_event, stop_event):
    """
        Display stimuli (fixation cross + black screen) for a certain amount of frame periods computed
        according to the monitor frame rate; start_event & stop_event are texts labelling the stimuli's start and end
        they are stored with the experiment time in the HDF event file
    """
    for frame_n in range(1,frame_stim+1): # For each frame
        stimuli.draw() # draw the image at each frame
        window.flip()  # synchronisation to the screen frame refresh
    
        if frame_n == 1: # if first frame send start event label to the HDF file
            ioServer.sendMessageEvent(text=start_event)

        if frame_n == frame_stim:  # if last frame to display send stop event label to the HDF file
            ioServer.sendMessageEvent(text=stop_event)

        test_escape() # if user pressed escape quit program


def image_display(frame_stim, stimuli, window, img_name):
    """
        Display image to explore for a certain amount of frame periods
        img_name is a text labelling the name of the image stored with the experiment time in the HDF event file
    """
    for frame_n in range(1,frame_stim+1):
        stimuli.draw()         # draw the image at each frame
        ftime = window.flip()  # synchronisation to the frame refresh
        
        if frame_n == 1: # if first frame send start event to the HDF file with the time flip time
            ioServer.sendMessageEvent(text='IMAGE_START :'+str(round(ftime,5)))
            ioServer.sendMessageEvent(text=img_name)
            
        if frame_n == frame_stim: # if last frame send stop event to the HDF file with the time flip time
            ioServer.sendMessageEvent(text='IMAGE_STOP :'+str(round(ftime,5)))

        test_escape()    # if user pressed escape quit program


def test_escape():
    """ if user pressed escape quit program """
    if defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()


################## DEFINE THE SESSION & DATA INFO ##################
expInfo = {
    'exp_name' : 'ExploIMG', # label of the experiment
    'participant': '1',      # number of the participant set in the dialog box
    'session': '001'}        # number of the session set in the dialog box

# Show participant info dialog for setting #
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title='Session settings')
if dlg.OK is False: # user pressed cancel quit program
    core.quit()

# Show a choice menu to define the eye-tracker used
myDlg = gui.Dlg(title="EyeTracker settings")
myDlg.addField('EyeTracker:', choices=["Tobii", "PupilCore"])
trackerType = myDlg.show()
if dlg.OK is False: # user pressed cancel quit program
    core.quit()
TRACKER = trackerType[0]


# Set data filename and directory #
_thisDir = os.path.dirname(os.path.abspath(__file__)) # actual path
os.chdir(_thisDir)                                    # change the curent working directory
filename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (expInfo['exp_name'],TRACKER, expInfo['participant'], expInfo['session'])
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not to the data file


################## Search images in image directory ##################
img_list = []
for f in os.listdir(expSetting["img_path"]):
    ext = os.path.splitext(f)[1]
    if ext.lower() not in [".jpg",".png"]:
        continue
    img_list.append(f)

shuffle(img_list) # randomize the list of image
nb_trial = np.size(img_list)


################## Initilization routine components ##################
# Setup the Window #
win = visual.Window(
    size = expSetting["screen_size"],
    fullscr = True,
    screen = 0,
    winType = 'pyglet',
    monitor = expSetting["screen_name"],
    useFBO = True,
    units = 'pix')
win.mouseVisible = False

# Fixation point image
FixCross = visual.ImageStim(
    win = win,
    units='height',
    image=expSetting['rest_fix_path']+'Target.bmp',
    size=(0.05, 0.05))

# Image to observe -> set resolution pixel in the routine for each one
ImageRnd = visual.ImageStim(
    win=win,
    units='pix',
    image='sin')

# Rest black background
Background = visual.ImageStim(
    win=win,
    units='height',
    image=expSetting['rest_fix_path']+'black.jpg',
    size=(3,3))


################## SETUP INPUT DEVICES ##################
# Setup eyetracking
ioConfig = {}

if TRACKER == 'Tobii':
    ioConfig['eyetracker.hw.tobii.EyeTracker'] = {
        'name': 'tracker',
        'model_name': '',
        'serial_number': '',
        'runtime_settings': {'sampling_rate': 60.0}} # sampling frequency of the eye tracker [Hz]

elif TRACKER == 'PupilCore':
    ioConfig['eyetracker.hw.pupil_labs.pupil_core.EyeTracker'] = {
        'name': 'tracker',
        'runtime_settings': {
            'pupillometry_only': False,
            'surface_name': 'psychopy_iohub_surface',
            'gaze_confidence_threshold': 0.6,
            'pupil_remote': {
                'ip_address': '127.0.0.1',
                'port': 50020.0,
                'timeout_ms': 1000.0,},
            'pupil_capture_recording': {
                'enabled': True,
                'location': '',}}}

# Setup iohub keyboard
ioConfig['Keyboard'] = dict(use_keymap='psychopy')


################## START THE IOHUB SERVER TO COMMUNICATE WITH THE EYETRACKER ##################
# return a iohub.client.ioHubConnection object that is used to access iohub device’s events
ioServer        = io.launchHubServer(window=win, experiment_code='image_explo', session_code=str(expInfo['session']), datastore_name=filename, **ioConfig)
eyetracker      = ioServer.getDevice('tracker') #Returns the ioHubDeviceView that has a matching name
defaultKeyboard = keyboard.Keyboard(backend='iohub') # create a default keyboard (e.g. to check for escape)


################## EXPERIMENT ROUTINE ##################
# RUN CALIBRATION
eyetracker.runSetupProcedure()

ioServer.sendMessageEvent(text='ScreenSize='+str(expSetting["screen_size"]))
ioServer.sendMessageEvent(text='ScreenFrame='+str(expSetting["screen_frame"]))

# set the eyetracker connection and start recording
eyetracker.setConnectionState(True)
eyetracker.setRecordingState(True)

# --- loop over trails --- #
for trial in range(nb_trial):
    ioServer.sendMessageEvent("TRIAL_START")

    # -- 1. Fixation phase -- #
    ioServer.sendMessageEvent("FIXATION_START")
    FixCross.draw()
    win.flip()
    
    # - start a static period where the image component is updated to avoid time-processing operations - #
    ISI = clock.StaticPeriod(screenHz=expSetting["screen_frame"], win=win)
    ISI.start(expSetting["t_fix"])  # start a period of t_fix duration  [sec]
    
    # Init parameters of the image to draw during the curent trial
    img_filename = expSetting['img_path']+img_list[trial-1]
    #img = plt.imread(img_filename)
    ImageRnd.setImage(img_filename)             #load the image in the stim component
    #ImageRnd.size = (img.shape[1],img.shape[0]) #set the component size
    
    ISI.complete()  # finish the t_fix duration, taking into account one 60Hz frame
    ioServer.sendMessageEvent("FIXATION_STOP")

    # -- 1. Fixation phase -- #
    #stimuli_display(expSetting['t_fix'], FixCross, win, "FIXATION_START", "FIXATION_STOP")

    # -- 2. Free image exploration phase -- #
    # Draw the image to explore during (frameImg) nb of frames (-> t=tImg)
    image_display(expSetting['t_img'], ImageRnd, win, "{0}".format(img_list[trial-1]))

    # -- 3. Rest phase -- #
    # Draw black background during (frameRest) nb of frames (-> t=tRest)
    stimuli_display(expSetting['t_rest'], Background, win, "REST_START", "REST_STOP")

    ioServer.sendMessageEvent("TRIAL_STOP")


# --- END ROUTINE = EXPERIMENT CLOSING --- #
# Stop eyeTracker record and close the connexion
eyetracker.setRecordingState(False)
if eyetracker:
    eyetracker.setConnectionState(False) # end the eyetracker connexion
    
win.flip()
ioServer.quit()
win.close()
core.quit()
