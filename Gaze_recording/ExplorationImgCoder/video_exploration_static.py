#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Mon Oct 24 10:23:30 2022
@author: Marion Léger

# REQUIREMENTS
Code designed for Psychopy 2022.2.4 and Python 3.8.
Python packages recquired :
    - numpy
    - time
    - matplotlib
    - tobii-research (pip install tobii-research (or py -m pip install ...))
    - Pupil core : 
        1. pip install zmq msgpack==0.5.6
        2. copied all of the files form psychopy github "\psychopy-release\psychopy\iohub\devices\eyetracker\hw\pupil_labs\pupil_core" 
        into the “~\PsychoPy\Lib\site-packages\psychopy\iohub\devices\eyetracker\hw\pupil

# EXPERIMENT        
This script plays a video file using visual.MovieStim2, records timing information 
about each video frame displayed and save it in a txt file in the directory frame_timing/.

Gaze data of eyetracker Tobii or PupilCore are recorded during the video display and saved in a hdf file.
The experiment strats with a calibration process to read meaningful gaze data with precision.


# INPUT :
    - video to play stored in the video_path directory
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


# OUTPUT : Frame timing in a text file 
The frame timing section can be opened by a program like LibreOffice Calc.
Select 'tabs' as the column delimiter.

Example Results File Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 ** Video Info **
Video File:
    Name: 	./jwpIntro.mp4
    Frame Count: 	145
    Width: 	320
    Height: 240
    FPS: 	25.0
Video Display:
    Window Resolution: 	[1920 1080]
    Window Fullscreen: 	True
    Drawn Size: 	[ 320.  240.]

 ** Column Definitions **
frame_num:	The frame index being displayed. Range is 1 to video frame count.
frame_flip_time:	The time returned by win.flip() for the current frame_num.
playback_duration:	current frame_flip_time minus the first video frame_flip_time.

 ** Per Frame Video Playback Data **
frame_num	frame_flip_time	playback_duration
[...]
15	3.284598	0.628544
16	3.334647	0.678593
17	3.367943	0.711889
18	3.401261	0.745207
19	3.451266	0.795213
20	3.484598	0.828544
[...]

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
        3. In Calibration set chorography = Screen Marker, gaze mapping = 3D, chose the monitor use to display the experiment.
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

from psychopy import gui, visual, core, logging, event, constants, clock
from psychopy.hardware import keyboard
import psychopy.iohub as io

from numpy.random import  shuffle
import numpy as np
import cv2

from psychopy import prefs
prefs.hardware['audioLib'] = ['PTB']

################## Experiment parameters ##################
expSetting ={
  "video_path": "video/",                # pathway of the experiment's images to explore
  "rest_fix_path": "img_fix_rest/",  # pathway of fixation cross & the black background
  "screen_size": [2560, 1080], # screen resolution [pixel]
  "screen_name": 'Dell1',      # name of the monitor set in PsychoPy builder
  "screen_frame": 60.0,        # monitor refresh frequency [Hz]
  # WARNINGS duration of stimulus must be t_stimulus = alpha*1/Fe_screen to display for complete monitor frame refresh
  # exemple t = 1/60 * 300 frames = 5sec
  "t_fix": 5.0,  # Set duration [sec] of fixation stimulis
  "t_rest":5.0,  # duration in frame of black rest screen
}


################## Function definitions ##################
def stimuli_display(frame_stim, stimuli, window, start_event, stop_event):
    """
        Display stimuli (fixation cross + black screen) for a certain amount of frame periods computed
        according to the monitor frame rate; start_event & stop_event are texts labelling the stimuli's start and end
        they are stored with the experiment time in the HDF event file
    """
    for frame_n in range(1,frame_stim+1): # For exactly frame_stim frames
        if frame_n == 1: # if first frame send start event label to the HDF file
            ioServer.sendMessageEvent(text=start_event)

        stimuli.draw() # draw the image at each frame
        window.flip()  # synchronisation to the frame refresh

        if frame_n == frame_stim:
            ioServer.sendMessageEvent(text=stop_event)

        test_escape()    # if user pressed escape quit program

def test_escape():
    """ if user pressed escape quit program """
    if defaultKeyboard.getKeys(keyList=["escape"]):
        core.quit()

def getVideoFilePath():
    videopath = expSetting['video_path']
    if not os.path.exists(videopath):
        raise RuntimeError("Video File could not be found:" + videopath)
    return videopath

def getResultsFilePath():
    _vdir = "frame_timing/"
    _results_file = u'%s_%s_%s_%s_%s.txt' % (expInfo['exp_name'],
        TRACKER, expInfo['participant'], expInfo['session'],video_name)
    return os.path.join(_vdir, _results_file)

def removeExistingResultsFile():
    # delete existing results file of same name (if exists)
    rfpath = getResultsFilePath()
    if os.path.exists(rfpath):
        try:
            os.remove(rfpath)
        except Exception:
            pass

def storeVideoFrameInfo(flip_time, frame_num):
    global first_flip_time, last_count, last_frame_time
    
    if video_results is not None:
        movie_playback_dur = 0
        
        if first_flip_time == 0:
            video_results.append(
                "frame_num\tframe_flip_time\tplayback_duration\n")
            first_flip_time = flip_time
        
        if last_frame_time > 0:
            movie_playback_dur = flip_time - first_flip_time
        
        last_frame_time = flip_time 
        video_results_data.append((frame_num, flip_time, movie_playback_dur))


def createResultsFile(file_name):
    if video_results is not None:
        cap = cv2.VideoCapture(file_name)
        total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
        with open(getResultsFilePath(), 'a') as f:
            print("Saving Frame Timing Results to: %s" % (getResultsFilePath()))

            f.write(" ** Video Info ** \n")
            f.write("Video File:\n")
            f.write("\tName:\t{0}\n".format(video_name))
            f.write("\tFrame Count:\t{0}\n".format(total_frame_count))
            f.write("\tWidth:\t{0}\n".format(width))
            f.write("\tHeight:\t{0}\n".format(height))
            f.write("\tFPS:\t{0}\n".format(mov.getFPS()))

            f.write("Video Display:\n")
            f.write("\tWindow Resolution:\t{0}\n".format(win.size))
            f.write("\tWindow Fullscreen:\t{0}\n".format(win._isFullScr))
            f.write("\tDrawn Size:\t{0}\n".format(mov.size))


def saveVideoFrameResults():
    if video_results is not None:
        with open(getResultsFilePath(), 'a') as f:

            f.write("\n ** Column Definitions ** \n")
            f.write("frame_num:\tThe frame index being displayed. Range is 1 to video frame count.\n")
            f.write("frame_flip_time:\tThe time returned by win.flip() for the current frame_num.\n")
            f.write("playback_duration:\tcurrent frame_flip_time minus the first video frame_flip_time.\n")
            f.write("\n ** Per Frame Video Playback Data ** \n")
            f.writelines(video_results)
            for vfd in video_results_data:
                f.write("%.0f\t%.6f\t%.6f\t\n"%vfd)
        del video_results[: ]

def getVideoFiles(video_path):
    video_list = []
    for f in os.listdir(video_path):
        ext = os.path.splitext(f)[1]
        if ext.lower() not in [".mp4"]:
            continue
        video_list.append(f)
    return video_list


################## DEFINE THE SESSION & DATA INFO ##################
expInfo = {
    'exp_name' : 'video_explo', # label of the experiment
    'participant': '1',      # number of the participant set in the dialog box
    'session': '001'}        # number of the session set in the dialog box

# Show participant info dialog for setting
dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title='Session settings')
if dlg.OK is False:
    core.quit()  # user pressed cancel quit program

# Show a choice menu to define the eye-tracker used
myDlg = gui.Dlg(title="EyeTracker settings")
myDlg.addField('EyeTracker:', choices=["Tobii", "PupilCore"])
trackerType = myDlg.show()  # show dialog and wait for OK or Cancel
if dlg.OK is False:
    core.quit()  # user pressed cancel quit program
TRACKER = trackerType[0]

# Search video files in video directory
video_list = getVideoFiles(expSetting["video_path"])
nb_trial   = np.size(video_list)
shuffle(video_list)  # randomize the video order

# Set data filename and directory
_thisDir = os.path.dirname(os.path.abspath(__file__)) # actual path
os.chdir(_thisDir)                                    # change the curent working directory
filename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (expInfo['exp_name'],
           TRACKER, expInfo['participant'], expInfo['session'])
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not to the data file


################## Initilization routine components ##################
# --- Setup the Window --- #
win = visual.Window(
    size=expSetting["screen_size"],
    fullscr=True,
    screen=0,
    winType = 'pyglet',
    monitor=expSetting["screen_name"],
    useFBO = True,
    units='pix')
win.mouseVisible = False

# --- Fixation point image --- #
FixCross = visual.ImageStim(
    win = win,
    units='height',
    image=expSetting['rest_fix_path']+'Target.bmp',
    size=(0.05, 0.05))


# --- Rest black background --- #
Background = visual.ImageStim(
    win=win,
    units='height',
    image=expSetting['rest_fix_path']+'black.jpg',
    size=(3,3))

mov = visual.MovieStim(
    win,
    pos=[0,0],
    noAudio=False,
    loop=False)

################## SETUP INPUT DEVICES ##################
# Setup eyetracking
ioConfig = {}

if TRACKER == 'Tobii':
    ioConfig['eyetracker.hw.tobii.EyeTracker'] = {
        'name': 'tracker',
        'model_name': '',
        'serial_number': '',
        'runtime_settings': {'sampling_rate': 60.0}}

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
ioServer        = io.launchHubServer(window=win, experiment_code='ExploIMG', session_code=str(expInfo['session']), datastore_name=filename, **ioConfig)
eyetracker      = ioServer.getDevice('tracker') #Returns the ioHubDeviceView that has a matching name
defaultKeyboard = keyboard.Keyboard(backend='iohub') # create a default keyboard (e.g. to check for escape)

# RUN CALIBRATION
eyetracker.runSetupProcedure()

ioServer.sendMessageEvent(text='ScreenSize='+str(expSetting["screen_size"]))
ioServer.sendMessageEvent(text='ScreenFrame='+str(expSetting["screen_frame"]))

# set the eyetracker connectionand recording
eyetracker.setConnectionState(True)
eyetracker.setRecordingState(True)

################## EXPERIMENT ROUTINE ##################
# --- LOOP OVER TRIALS --- #
for trial in range(nb_trial):
    ioServer.sendMessageEvent("TRIAL_START")
    
    # -- 1. Fixation phase -- #
    ioServer.sendMessageEvent("FIXATION_START")
    FixCross.draw()
    win.flip()
    
    # - start a static period where the movie component is updated to avoid time-processing operations - #
    ISI = clock.StaticPeriod(screenHz=expSetting["screen_frame"], win=win)
    ISI.start(expSetting["t_fix"])  # start a period of t_fix duration  [sec]
    
    # Init parameters of the video to play during the curent trial
    video_name = video_list[trial-1]
    mov.setMovie(expSetting['video_path']+video_name)  #load the video in the stim component
    mov.size   = mov.frameSize

    # globals for frame timing computing
    video_results = []
    video_results_data = []
    first_flip_time = 0
    last_count      = 0
    last_frame_time = 0
    
    removeExistingResultsFile() # if frame timing file already exist deleted it
    createResultsFile(expSetting['video_path']+video_name) # create a frame timing file
        
    ISI.complete()  # finish the t_fix duration, taking into account one 60Hz frame
    ioServer.sendMessageEvent("FIXATION_STOP")
    
    # --- 1. Fixation phase --- #
    # Draw fixation point during (frameFix) nb of frames (-> t=tFix)
    #stimuli_display(frame_fix, FixCross, win, "FIXATION_START", "FIXATION_STOP")

    # Start the movie stim by preparing it to play
    ioServer.sendMessageEvent(video_name)
    ioServer.sendMessageEvent('MOVIE_START')
    frame = mov.play()
    
    while mov.status != constants.FINISHED:
        
        frame = mov.draw() # load video frame
        if frame :
            frame_count = mov.frameIndex # get the video frame index
            frame_time  = win.flip()     # flip to display on the window & get flip time
    
            if frame_count != last_count:
                last_count = frame_count #update the previous frame index
                storeVideoFrameInfo(frame_time, frame_count)
    
        # process keyboard input
        if event.getKeys('q'):   # quit
            break
        elif event.getKeys('s'):  # play/start
            mov.play()
        elif event.getKeys('p'):  # pause
            mov.pause()
    
    # stop movie playing
    mov.stop()
    ioServer.sendMessageEvent('REST_START')

    # -- 3. Rest phase -- #
    Background.draw()
    win.flip()
    
    # start a static period to save frame timg file and avoid time-processing operations #
    ISI = clock.StaticPeriod(screenHz=expSetting["screen_frame"], win=win)
    ISI.start(expSetting["t_rest"])  # start a period of t_fix duration  [sec]
    saveVideoFrameResults() # save video frames timing data 
    
    ISI.complete()  # finish the t_fix duration, taking into account one 60Hz frame
    ioServer.sendMessageEvent("REST_STOP")
    
    # Draw black background during (frameRest) nb of frames (-> t=tRest)
    #stimuli_display(frame_rest, Background, win, "REST_START", "REST_STOP")


################## END ROUTINE ##################
# stop eyetracker record and connection
eyetracker.setRecordingState(False) 
eyetracker.setConnectionState(False)

# close window and program
#win.flip()
ioServer.quit()
win.close()
core.quit()
