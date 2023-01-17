##### Visual perception experiment #####

# REQUIREMENTS

  * PsychoPy v2022.2.4: to load and run the Python program on it -> https://www.psychopy.org/download.html
  * Python 3.8          -> https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe
  * Python packages:
	- numpy
	- matplotlib
  * Tobii python library : tobii-research -> pip install tobii-research (or py -m pip install ...)
  * Pupil core :
	1. pip install zmq msgpack==0.5.6
	2. copied all of the files form psychopy github "\psychopy-release\psychopy\iohub\devices\eyetracker\hw\pupil_labs\pupil_core" -> https://github.com/psychopy/psychopy/tree/dev/psychopy/iohub/devices/eyetracker/hw/pupil_labs/pupil_core
	into the directory on your PC “~\Programs\PsychoPy\Lib\site-packages\psychopy\iohub\devices\eyetracker\hw\pupil_labs\pupil_core"


# EXPERIMENT : Visual perception

Process free image/video exploration in 3 phases:
    1. Fixation point 
    2. Image/Video : free image/video exploration
    3. Black background : rest phase

Images/videos to explore are stored in a list that is shuffled before each experiment.
The gaze data are recorded during all the experiment.
The experiment starts with a calibration process to read meaningful gaze data with precision.


# EYE TRACKER SETUP

Before running the program on PsychoPy several step have to be done on Psychopy software :
1. Create and set monitor info (resolution, monitor width & the distance to the monitor) in PsychopPy Builder section 'Monitor settings and calibration'
2. Verify that the unit of the visual.Window in the Python code is well set to 'pix' in order to obtain gaze data in pixel unit
3. If you want to change the images to observe during the experiment put them in the image directory
4. For Tobii : 
	a. Connect the Tobii eye-tracker to the external processing unit and the processing unit to the PC
	b. Fix the eye-tracker above the screen using a magnetic sticker
	b. Set the eye-tracker dimension on the screen with the Eyetracker Manager of Tobii : https://www.tobii.com/products/software/applications-and-developer-kits/tobii-pro-eye-tracker-manager#downloads)
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
        9. Let the software open and run the python program

# EXPERIMENT PARAMETERS TO BE SET
expSetting:
    * img_path      = image pathway where are stored the experiment's images
    * rest_fix_path = pathway of the fixation cross & the black background images
    * screen_size   = screen resolution [pixel]
    * screen_name   = monitor name that have been set in Psychopy Builder 'Monitor settings and Calibration'
    * screen_frame  = monitor refresh frequency [Hz]
    * t_fix, t_img, t_rest = stimulis duration of the fixation, exploration & rest phase [sec]


# WARNING
* The coordinate origin of the window is set to the screen center (0,0) meaning that gaze data are recorded with this specific origin cordinate.
* As the unit of the window is set to pixel gaze data recorded are also in pixel units.


# OUTPUT
Output data are saved in a HDF5 file (Hierarchical Data Format):
    * Gaze data = binocular gaze data are supported for Tobii device and Monocular + Binocular for Pupil Core
    * Event messages = experimental labels + corresponding times

The HDF5 file is organized as followed:
data_collection/
	* condition_variables
	* events/
		- LogEvent 
		- MessageEvent
			Device_time			// Time of the eye-tracker
			Logged_time
			Time				// time of event, [sec.msec] format, using psychopy timebase
			Text				// event messages sent during each trials ['TRIAL_START','FIXATION_START','FIXATION_STOP','IMAGE_START','imagename.jpg|png','IMAGE_STOP','REST_START','REST_STOP','TRIAL_END']
	* Eyetracker/
		- BinocularEyeSampleEvent               // gaze data recorded by the eyectracker
			The BinocularEyeSampleEvent event represents the eye position and eye attribute data collected from one frame or reading of an eye tracker device that is recording both eyes of a participant.
			
			Experiment_id
			Session_id 
			Devide_id = 0
			Event_id			// number indicating the rank of the nth data saved in the hdf file
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
			L/R_velocity_x/y/xy = 0		----> Not supported by tobii -> Horizontal/Vertcial/2D velocity of the eye at the time of the sample
			Statut 				// Indicates if eye sample contains ‘valid’ data -> 0 = Eye sample is OK. 2 = Right eye data is likely invalid. 20 = Left eye data is likely invalid. 22 = Eye sample is likely invalid.
		
		- BlinkEndEvent 	  		----> Not supported by tobii & Pupil Core
		- BlinkStartEvent 	 		----> Not supported by tobii & Pupil Core
		- FixationEndEvent 	  		----> Not supported by tobii & Pupil Core
		- FixationStartEvent 	  		----> Not supported by tobii & Pupil Core
		
		- MonocularEyeSampleEvent 		----> Not supported by tobii -> Pupil Core same variables as BinocularEyeSampleEvent
							A MonocularEyeSampleEvent represents the eye position and eye attribute data collected from one frame or reading of an eye tracker device 
							that is recoding from only one eye, or is recording from both eyes and averaging the binocular data.
		
		- SaccadeEndEvent 	  		----> Not supported by tobii & Pupil Core
		- SaccadeStartEvent 	  		----> Not supported by tobii & Pupil Core
	* Keyboard
		- KeyboardInputEvent
	* Mouse
		- MouseInputEvent
	* Pstbox
	* Serial
	* Wintab
	* Experiment_meta_data
	* Session_meta_data
	* Class_table_mapping

# Additional output for video_exploration : Video frame timing in a text file 
This file stores the time at which each video frame was been displayed on the monitor.

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
frame_num	frame_flip_time	playback_duration	frame_num_dx
[...]
15	3.284598	0.628544
16	3.334647	0.678593
17	3.367943	0.711889
18	3.401261	0.745207
19	3.451266	0.795213
20	3.484598	0.828544
[...]
