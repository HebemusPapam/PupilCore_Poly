library(hdf5r)

### LOAD FILE ###
file ="C:/Users/marion/Documents/ExplorationImgCoder/data/ExploIMG_PupilCore_m_004.hdf5"

#file ="C:/Users/marion/Documents/Pupil_Core/Tests/data/380526_set_pupil_core_2022-11-29_14h34.06.458.hdf5"
df = H5File$new(file, mode="r")

### IMPORT BINOCULAR GAZE DATA ###
# import eyetracker binocular data
BinoData = df[["data_collection/events/eyetracker/BinocularEyeSampleEvent"]]
BinoData = BinoData[]

# IMPORT EXPERIMENT EVENTS
Event = df[["data_collection/events/experiment/MessageEvent"]]
Event = Event[]

### EYETRACKER MONOCULAR EVENTS ### -> EMPTY
MonoData = df[["data_collection/events/eyetracker/MonocularEyeSampleEvent"]]
MonoData = MonoData[]


### BLINK EVENTS ###
# import eyetracker blink end events -> EMPTY
#blinkEnd = df[["data_collection/events/eyetracker/BlinkEndEvent"]]
#blinkEnd = blinkEnd[]

# import eyetracker blink start events -> EMPTY
#blinkStart = df[["data_collection/events/eyetracker/BlinkStartEvent"]]
#blinkStart = blinkStart[]


### FIXATION EVENTS ###
# import eyetracker blink end events -> EMPTY
#fixEnd = df[["data_collection/events/eyetracker/FixationEndEvent"]]
#fixEnd = fixEnd[]

# import eyetracker blink start events -> EMPTY
#fixStart = df[["data_collection/events/eyetracker/FixationStartEvent"]]
#fixStart = fixStart[]


### SACCADE EVENTS ###
# import eyetracker blink end events -> EMPTY
#SaccadeEnd = df[["data_collection/events/eyetracker/SaccadeEndEvent"]]
#SaccadeEnd = SaccadeEnd[]

# import eyetracker blink start events -> EMPTY
#SaccadeStart = df[["data_collection/events/eyetracker/BlinkStartEvent"]]
#SaccadeStart = SaccadeStart[]





