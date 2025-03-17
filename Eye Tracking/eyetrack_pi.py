import time
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import time

#TODO:Display instructions, display calibration, display two dots, trigger this from client
#Feed videos into interpreter, get gaze data, score, send score
# 2 dots on screen then call this to make videos, get paths in HITS_eyetracking to process videos

# Initialize the cameras
left_camera = Picamera2(0)
right_camera = Picamera2(1)

encoder = H264Encoder(10000000)

left_camera.start()
right_camera.start()


print("Cameras Init")

# Configure the cameras
#left_camera.configure(left_camera.create_video_configuration())
#right_camera.configure(right_camera.create_video_configuration())

#TODO: Figure out the right config values for the quality and framerate that is best

# Start recording
left_camera.start_recording(encoder,output=FfmpegOutput("/home/pi/Left.mp4"))
right_camera.start_recording(encoder,output=FfmpegOutput("/home/pi/Right.mp4"))

print("recording")

# Record for 120 seconds
time.sleep(120)

# Stop recording
left_camera.stop_recording()
right_camera.stop_recording()

print("end recording")

# Close the cameras
left_camera.close()
right_camera.close()

left_camera.stop()
right_camera.stop()
#NOTE: If we cannot process the videos on the pi, we can "stream" the videos using a socket.
