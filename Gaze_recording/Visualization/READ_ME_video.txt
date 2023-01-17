To visualize gaze data collected during the visual perception experiment 'video_exploration.py'
run the python program 'mpv_video_visualization.py'.

This program overlaps the gaze data collected over video frames using the mpv video player 
and the video frame timing file recorded during 'video_exploration.py'.


The mpv player is used to play the video frames and obtain the frame count.
Depending on the video frame count we search the time at which this frame t1 and the next one t2 have been ploted 
in the frame_timing text file.
We overlap to the mpv video frame the gaze data collected between this 2 times.


# REQUIREMENTS
  * Python 3.8  -> https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe
  * Python IDE to run the program as Spyder  -> https://docs.spyder-ide.org/3/installation.html
  * Python libraries:
    - PIL
    - numpy
    - cv2
    - h5py
    - thinker
    - mpv :
        1. pip install python-mpv==0.3.1
        2. https://sourceforge.net/projects/mpv-player-windows/files/libmpv/
        extract lastest zip of libmpv on the same directory as this program

# INPUT :
    - video explored during experiment in VIDEO_PATH directory
    - hdf files recorded during the expriments
    - frame_timing.txt files in which are stored the video frame timing
    
# PARAMETERS TO BE SET :
    - VIDEO_PATH    = directory where are stored the experiment's videos
    - FRAME_PATH    = directory where are stored the experiment's video frame timing files
    - HDF_PATH      = directory where are stored the hdf files recorded
    - FILENAME      = list of hdf files where are stored the gaze data to visualize
    - R             = diameter/2 of the gaze cross visualization (must be pair)
"""