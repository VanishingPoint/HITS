from PIL import Image
import os
import random
import time
import csv
import socket
import pandas
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput

HOST = "100.120.18.53"  # Server's hostname or IP address
PORT = 65432  # Port used by the cognitive test server
csv_directory = "/home/hits/Documents/GitHub/HITS/csv_files"  # Folder to save CSV files
file_path = None

def handle_data(data):
    if user_data_received == False:
        response = record_user_data(data)
    elif user_data_received == True and cognitive_test_complete == False:
        response = cognitive_test(data)
    elif cognitive_test_complete == True and balance_test_complete == False:
        response = balance_test() #TODO: Call the balance test function
    elif cognitive_test_complete == True and balance_test_complete == True and eye_track_completed == False:
        response = eye_tracking_test() #TODO: Call the eye track function
    else:
        print("All Tests Complete or Error")
    return response

# Function to append cognitive data starting at column G TODO: Does this work??? No: Use pandas: empty_row = df['G'].isna().idxmax()  # Finds the first NaN (empty) row
# Add data to the first empty row in column G: df.at[empty_row, 'G'] = "New Data"
def append_cognitive_data(cognitive_data):
    """Append cognitive data to the existing user CSV file, starting at column G."""
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Add the cognitive data starting from column G
        writer.writerow(cognitive_data)

# Function to open and display an image
opened_image = None  # Initialize the variable at the global level

def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()  # Close the previous image if it exists
    opened_image = Image.open(image_path)
    opened_image.show()

def record_user_data(data):
    global file_path, user_data_received
    sequence, age, sex, height, drunk = data.split()

    # Generate the CSV filename based on the sequence number and save it in the csv_directory
    file_name = f"{sequence}.csv"
    file_name = file_name[:255].replace(":", "_").replace(" ", "_")
    file_path = os.path.join(csv_directory, file_name)  # Full path to the CSV file, since this is global it defines it everywhere

    # Ensure the directory exists
    os.makedirs(csv_directory, exist_ok=True)

    # Open file in append mode without checking size first
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if os.path.getsize(file_path) == 0:
            writer.writerow(["Sequence", "Age", "Sex", "Height", "Drunk", "Timestamp", "Image Number", "Color", "Word", "Response", "Time Taken"])
        log_data = [sequence, age, sex, height, drunk, time.time()]
        writer.writerow(log_data)

    user_data_received = True
    print("User Data Recorded")
    return("Data Saved")


# Function to handle client connections for the cognitive test
def cognitive_test(key):
    global cognitive_test_complete, cognitive_test_started, image_numbers, current_index, start_time

    if cognitive_test_started == False:
        image_numbers = list(range(1, 17))  # Assuming 16 images
        random.shuffle(image_numbers)

        #TODO: Show instructions to the participant here

        current_index = 0  # Tracks the current image index
        start_time = 0

    # Defining attributes for each image
    image_colour = {
        1: "blue", 2: "green", 3: "red", 4: "yellow", 5: "blue", 6: "green", 7: "red", 8: "yellow", 9: "blue", 10: "green", 
        11: "red", 12: "yellow", 13: "blue", 14: "green", 15: "red", 16: "yellow"}
    image_word = {
        1: "red", 2: "red", 3: "red", 4: "red", 5: "blue", 6: "blue", 7: "blue", 8: "blue", 9: "yellow", 10: "yellow", 
        11: "yellow", 12: "yellow", 13: "green", 14: "green", 15: "green", 16: "green"}

    # List of image paths based on shuffled numbers
    image_paths = [
        fr"/home/hits/Documents/GitHub/HITS/Cognitive/Cognitive Participant Images/page_{num}.png"
        for num in image_numbers
    ]

    end_time = time.time()
    time_taken = end_time - start_time

    if key == "s" and cognitive_test_started == False: 
        # Show the current image
        response = str(image_numbers[current_index])
        show_image(image_paths[current_index])
        start_time = time.time()  # Reset start time for the next image
        current_index += 1
        cognitive_test_started = True
    elif key in ["y", "n"]:
        if current_index < len(image_numbers):
            # Show next image
            response = str(image_numbers[current_index])
            show_image(image_paths[current_index])
            start_time = time.time()  # Reset start time for the next image
            current_index += 1
        else:
            # End the test when all images are shown
            cognitive_test_complete = True
            print("Test completed.")
            response = "end"
    elif key == "Exit":
        cognitive_test_complete = True
        return("Exited")
    else:
        print(f"Invalid key pressed: {key}")
        return "Invalid"
    
    if current_index != 1:
        print("Logging data")
        # Log the data after each keystroke and image
        image_num = image_numbers[current_index - 1]
        colour = image_colour[image_num]
        word = image_word[image_num]
        # Additional data logging here (cognitive data)
        cognitive_data = [image_num, colour, word, key, time_taken]
        append_cognitive_data(cognitive_data)

        print("Finished logging")

    return(response)

def eye_tracking_recording(): #TODO: Set proper cropping, change encoding to increase frame rate
    cam1 = Picamera2(0)
    cam1.start_preview(Preview.QTGL, x=100,y=300,width=400,height=300)

    video_config1= cam1.create_video_configuration()
    cam1.configure(video_config1)

    encoder1 = H264Encoder(10000000)
    output1 = FfmpegOutput('testcam1.mp4') #TODO: Rename

    cam2 = Picamera2(1)
    cam2.start_preview(Preview.QTGL, x=500,y=300,width=400,height=300)

    video_config2 = cam2.create_video_configuration()
    cam2.configure(video_config2)

    encoder2= H264Encoder(10000000)
    output2 = FfmpegOutput('testcam2.mp4') #TODO: Rename

    cam1.start_recording(encoder1, output1)
    cam2.start_recording(encoder2, output2)

    time.sleep(10) #Set recording duration here, 10 seconds set for now

    cam2.stop_recording()
    cam1.stop_recording()

    cam1.stop_preview()
    cam2.stop_preview()

    cam2.stop()
    cam1.stop()


def eye_tracking_test():
    time.sleep(1) #TODO: Do something here
    eye_track_started = True
    #1st show instructions, wait for key to proceed (have to go to main loop to detect)
    #Then show 1st image here
    eye_tracking_recording() #Record the first test (Figure out if we need to pass anything...)
    #Move & Rename files??? Or include logic that knows if it is first run or second run on the recording to name them differently
    #Show instructions and wait for key to proceed (again, need main loop to detect)
    eye_tracking_recording() #record second test here
    #Then we do analysis here (or maybe we should do it during balance)
    #Need to let people restart test
    eye_track_completed = True
    #return(response)


def balance_test():
    time.sleep(1) #TODO: Do something here

response = None
user_data_received = False
cognitive_test_complete = False
cognitive_test_started = False
balance_test_complete = False
balance_test_started = False
eye_track_started = False
eye_track_completed = False

# This cannot be in a function!!
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            response = handle_data(data.decode('utf-8'))

            if not data:
                print("Disconnected from Pi")

            conn.sendall(response.encode('utf-8'))

