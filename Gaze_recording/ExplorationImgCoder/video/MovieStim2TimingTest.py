#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 ** IMPORTANT: Review the software and hardware details saved by this program
   before sending the file to anyone. You must be comfortable with a 3rd party
   viewing the computer details being reported.

This script plays a video file using visual.MovieStim2, records timing
information about each video frame displayed, as well as information about
the computer software and hardware used to run the script.

The hope is that this script can be used to further understand what is,
and is not, working with MovieStim2, and provide information that may help
determine the root cause of any issues found.

The following variables control what video is played during the test as well as
other configuration settings:
"""

#   Test Config.

# Relative path (from this scripts folder) for the video clip to be played .
video_name = r'./vaisseau.mp4'

# If False, no audio tracks will be played.
INCLUDE_AUDIO_TRACK = True

# Size of the PsychoPy Window to create (in pixels).
WINDOW_SIZE = [1280, 720]

# If True, WINDOW_SIZE is ignored and a full screen PsychoPy Window is created.
USE_FULLSCREEN_WINDOW = False

# On systems with > 1 screen, the index of the screen to open the win in.
SCREEN_NUMBER = 0

# If the video frame rate is less than the monitor's refresh rate, then there
# will be some monitor retraces where the video frame does not change. In
# this case, SLEEP_IF_NO_FLIP = True will cause the script to sleep for 1 msec.
# If False, the video playback loop does not insert any sleep times.
SLEEP_IF_NO_FLIP = True

# If True, data about each process running on the computer when this script
# is executed is saved to the results file. Set to False if you do not want
# this information saved. If a string, processes with that name are saved
SAVE_PER_PROCESS_DATA = 'python.exe'

# If you do not want any results file saved at all, set this to None, otherwise
# keep it as an empty list.
video_results = []
#
"""
[ .. script docs continued ..]

A results file is saved in the same folder as the video file that was played.
The results file name is:

[video_name]_frame_timing.txt

video_name is the file name of the video played, with '.' replaced with '_'.

The results file contains several sections of information, the
last of which is the actual tab delimited video frame timing data.

The frame timing section can be opened by a program like LibreOffice Calc.
Select 'tabs' as the column delimiter.

Example Results File Output
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 ** Video Info **
Video File:
    Name: 	./jwpIntro.mp4
    Frame Count: 	145.0
    Width: 	320.0
    Height: 	240.0
    FPS (Format, Requested): 	(25.0, None)
    Play Audio Track: 	True
Video Display:
    Window Resolution: 	[1920 1080]
    Window Fullscreen: 	True
    Drawn Size: 	[ 320.  240.]
    Refresh Rate (reported / calculated): 	60 / 59.9989858627

 ** System Info **
    OS:
        Name: Windows-7-6.1.7601-SP1
    Computer Hardware:
        CPUs (cores / logical): (4, 8)
        System Memory:
            Available: 7.3G
            Used: 8.6G
            Total: 16.0G
            Percent: 54.2
            Free: 7.3G
    Python:
        exe: C:\\Anaconda\\python.exe
        version: 2.7.7 |Anaconda 2.1.0 (64-bit)| (default, Jun 11 2014, 10: 40: 02) [MSC v.1500 64 bit (AMD64)]
    Packages:
        numpy: 1.9.0
        pyglet: 1.2alpha1
        cv2: 2.4.9
        PsychoPy: 1.81.03
    Graphics:
        shaders: True
        opengl:
            version: 4.4.0 NVIDIA 344.11
            vendor: NVIDIA Corporation
            engine: GeForce GTX 580/PCIe/SSE2
            Max vert in VA: 1048576
            extensions:
                GL_ARB_multitexture: True
                GL_EXT_framebuffer_object: True
                GL_ARB_fragment_program: True
                GL_ARB_shader_objects: True
                GL_ARB_vertex_shader: True
                GL_ARB_texture_non_power_of_two: True
                GL_ARB_texture_float: True
                GL_STEREO: False
    Processes: [Only Saved if SAVE_PER_PROCESS_DATA = True]

        [Each user accessible process running on the computer will be output]
        [Example output for 3 processes: ]

        15187:
            num_threads: 3
            exe: C:\\Program Files (x86)\\Notepad++\\notepad++.exe
            name: notepad++.exe
            cpu_percent: 0.0
            cpu_affinity: [0, 1, 2, 3, 4, 5, 6, 7]
            memory_percent: 0.176239720445
            num_ctx_switches: pctxsw(voluntary=5220262, involuntary=0)
            ppid: 4648
            nice: 32
        16656:
            num_threads: 11
            exe: C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe
            name: chrome.exe
            cpu_percent: 0.0
            cpu_affinity: [0, 1, 2, 3, 4, 5, 6, 7]
            memory_percent: 0.200959182049
            num_ctx_switches: pctxsw(voluntary=136232, involuntary=0)
            ppid: 8588
            nice: 32
        16688:
            num_threads: 17
            exe: C:\\Anaconda\\python.exe
            name: python.exe
            cpu_percent: 75.1
            cpu_affinity: [0, 1, 2, 3, 4, 5, 6, 7]
            memory_percent: 0.786193630842
            num_ctx_switches: pctxsw(voluntary=76772, involuntary=0)
            ppid: 12912
            nice: 32

 ** Column Definitions **

[INSERT: Description of each column of the video playback data saved.]

 ** Per Frame Video Playback Data **
frame_num	frame_flip_time	playback_duration	frame_num_dx	dropped_count

[INSERT: One row for each frame displayed during video playback]

[...]
15	3.284598	0.628544	1	1	0.000254	0.005486	0.033325	0.033325	23.865
16	3.334647	0.678593	1	1	0.000258	0.015530	0.050049	0.050049	23.578
17	3.367943	0.711889	1	1	0.000286	0.008799	0.033296	0.033296	23.880
18	3.401261	0.745207	1	1	0.000260	0.002137	0.033318	0.033318	24.154
19	3.451266	0.795213	1	1	0.000264	0.012135	0.050006	0.050006	23.893
20	3.484598	0.828544	1	1	0.000268	0.005463	0.033331	0.033331	24.139
[...]
"""

from psychopy import visual, core, event, constants

getTime = core.getTime
import time, os, numpy as np
import cv2

# Globals
last_frame_ix = -1
last_frame_time = 0
first_flip_time = 0
video_results_data = []

def getVideoFilePath():
    videopath = os.path.normpath(os.path.join(os.getcwd(), video_name))
    if not os.path.exists(videopath):
        raise RuntimeError("Video File could not be found:" + videopath)
    return videopath

def getResultsFilePath():
    _vdir, _vfile = os.path.split(getVideoFilePath())
    _results_file = u'%s_frame_timing.txt' % (_vfile.replace('.', '_'))
    return os.path.join(_vdir, _results_file)

def removeExistingResultsFile():
    # delete existing results file of same name (if exists)
    rfpath = getResultsFilePath()
    if os.path.exists(rfpath):
        try:
            os.remove(rfpath)
        except Exception:
            pass

def initProcessStats():
    try:
        import psutil

        for proc in psutil.process_iter():
            proc.cpu_percent()
    except Exception:
        pass

def storeVideoFrameInfo(flip_time, frame_num):
    global first_flip_time, last_frame_time, last_frame_ix
    if video_results is not None:
        movie_playback_dur = 0
        fps = 0

        if first_flip_time == 0:
            video_results.append(
                "frame_num\tframe_flip_time\tplayback_duration\tfps\n")
            first_flip_time = flip_time

        # manually check for dropped movie frames
        last_frame_ix = frame_num

        # calculate inter movie frame interval etc.
        if last_frame_time > 0:
            movie_playback_dur = flip_time - first_flip_time
            fps = last_frame_ix / movie_playback_dur

        last_frame_time = flip_time
        video_results_data.append((frame_num, flip_time, movie_playback_dur, fps))

def createResultsFile():
    if video_results is not None:
        with open(getResultsFilePath(), 'a') as f:
            print("Saving Frame Timing Results to: %s" % (getResultsFilePath()))

            f.write(" ** Video Info ** \n")
            f.write("Video File:\n")
            f.write("\tName:\t{0}\n".format(video_name))
            f.write("\tFrame Count:\t{0}\n".format(total_frame_count))
            mov_duration = total_frame_count/mov_fps
            f.write("\tVideo Duration:\t{0}\n".format(mov_duration))
            f.write("\tWidth:\t{0}\n".format(width))
            f.write("\tHeight:\t{0}\n".format(height))
            f.write("\tFPS:\t{0}\n".format(mov.getFPS()))

            f.write("Video Display:\n")
            f.write("\tWindow Resolution:\t{0}\n".format(win.size))
            f.write("\tWindow Fullscreen:\t{0}\n".format(win._isFullScr))
            f.write("\tDrawn Size:\t{0}\n".format(mov.size))
            f.write("\tRefresh Rate (reported / calculated):\t{0} / {1}\n".format(win.winHandle._screen.get_mode().rate,
                                                                                  win.getActualFrameRate()))

def saveVideoFrameResults():
    if video_results is not None:
        with open(getResultsFilePath(), 'a') as f:
            video_results_array = np.asarray(video_results_data, dtype=np.float32)
            playback_duration = video_results_array[-1][2]

            f.write("\n ** Video Playback Stats ** \n")
            f.write("Playback Time: %.3f\n"%(playback_duration))

            f.write("\n ** Column Definitions ** \n")
            f.write("frame_num:\tThe frame index being displayed. Range is 1 to video frame count.\n")
            f.write("frame_flip_time:\tThe time returned by win.flip() for the current frame_num.\n")
            f.write("playback_duration:\tcurrent frame_flip_time minus the first video frame_flip_time.\n")
            f.write("fps:\tEquals playback_duration / current frame_num.\n")
            f.write("\n ** Per Frame Video Playback Data ** \n")
            f.writelines(video_results)
            for vfd in video_results_data:
                f.write("%.0f\t%.6f\t%.6f\t%.3f\n"%vfd)
        del video_results[: ]

if __name__ == '__main__':
    removeExistingResultsFile()
    
    expSetting ={
      "video_path": "video/",                # pathway of the experiment's images to explore
      "rest_fix_path": "img_fix_rest/",  # pathway of fixation cross & the black background
      "screen_size": [2560, 1080], # screen resolution [pixel]
      "screen_name": 'Dell1',      # name of the monitor set in PsychoPy builder
      "screen_frame": 60.0,        # monitor refresh frequency [Hz]
      "t_fix": 3,  # Set duration [sec] of fixation stimulis
      "t_video": 7,  # Set duration [sec] of image stimulis
      "t_rest": 2,} # Set duration [sec] of black rest screen

    win = visual.Window(
    size=expSetting["screen_size"],
    fullscr=True,
    screen=0,
    winType='pyglet',
    monitor=expSetting["screen_name"],
    color=[0,0,0], colorSpace='rgb',
    blendMode='avg',
    useFBO=True,
    units='pix')
    win.mouseVisible = False

    # Create your movie stim.
    mov = visual.MovieStim(win, getVideoFilePath(),
                            flipVert=False,
                            flipHoriz=False)
    
    VIDEO_PATH = 'C:/Users/marion/Documents/ExplorationImgCoder/video/vaisseau.mp4'
    cap = cv2.VideoCapture(VIDEO_PATH)
    global total_frame_count, mov_fps, width, height
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    mov_fps   = int(cap.get(cv2.CAP_PROP_FPS))
    width     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height    = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    initProcessStats()

    # Start the movie stim by preparing it to play
    globalClock = core.Clock()
    
    dt1 = getTime()
    display_frame = mov.play()
    draw_dur = getTime() - dt1

    while mov.status != constants.FINISHED:
        # Only flip when a new frame should be displayed. Can significantly reduce
        # CPU usage. This only makes sense if the movie is the only /dynamic/ stim
        # displayed.
        if display_frame:
            ft1 = getTime()
            ftime = win.flip()
            frame_count = mov.frameIndex
            storeVideoFrameInfo(ftime, frame_count)
            print(frame_count)

        # Drawn movie stim again. Updating of movie stim frames as necessary
        # is handled internally.
        dt1 = getTime()
        display_frame = mov.draw()

        # Check for action keys.....
        for key in event.getKeys():
            if key in ['escape', 'q']:
                mov.status = constants.FINISHED
                break

    createResultsFile()
    mov.stop()
    saveVideoFrameResults()

    core.quit()

win.close()
core.quit()
