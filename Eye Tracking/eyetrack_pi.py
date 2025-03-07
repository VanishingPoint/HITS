import time
from picamera2 import Picamera2

#TODO:Display instructions, display calibration, display two dots, trigger this from client
#Feed videos into interpreter, get gaze data, score, send score
# 2 dots on screen then call this to make videos, get paths in HITS_eyetracking to process videos

# Initialize the cameras
left_camera = Picamera2(0)
right_camera = Picamera2(1)

# Configure the cameras
left_camera.configure(left_camera.create_video_configuration())
right_camera.configure(right_camera.create_video_configuration())

#TODO: Figure out the right config values for the quality and framerate that is best

# Start recording
left_camera.start_recording("Left.h264")
right_camera.start_recording("Right.h264")

# Record for 120 seconds
time.sleep(120)

# Stop recording
left_camera.stop_recording()
right_camera.stop_recording()

# Close the cameras
left_camera.close()
right_camera.close()

#NOTE: If we cannot process the videos on the pi, we can "stream" the videos using a socket.