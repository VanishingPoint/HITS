from PIL import Image
import os
import random
import time
import csv
import socket

# This is the one that actually works, need the pi plugged in and remote into the pi
# Software: tiger vnc viewer, need pi and computer to be on the same network
# pi to monitor - need that cable I bought - locker 
# run the one on the pi first

HOST = "100.120.18.53" # "127.0.0.1"  # this allows me to run both scripts on same device?  # "100.120.18.53"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

#TODO: Replace this when switching to local wifi

# List of image numbers (shuffled for randomness)
image_numbers = list(range(1, 17))  # Assuming 15 images
random.shuffle(image_numbers)

# Defining attributes for each image
image_colour = {
    1: "blue", 2: "green", 3: "red", 4: "yellow", 5: "blue",  6: "green",  7: "red", 8: "yellow", 9: "blue", 10: "green", 
    11: "red", 12: "yellow", 13: "blue", 14: "green", 15: "red", 16: "yellow"}
image_word = {
    1: "red", 2: "red", 3: "red", 4: "red", 5: "blue", 6: "blue", 7: "blue", 8: "blue", 9: "yellow", 10: "yellow", 
    11: "yellow", 12: "yellow", 13: "green", 14: "green", 15: "green", 16: "green"}

# List of image paths based on shuffled numbers
image_paths = [
    fr"/home/hits/Documents/GitHub/HITS/Cognitive/Cognitive Participant Images/page_{num}.png"
    for num in image_numbers
]

current_index = 0  # Tracks the current image index
opened_image = None  # Keeps reference to the currently open PIL Image object (delete)
start_time = time.time()  # Start timing
session_ended = False  # Flag to indicate if the session has ended

# Function to open and display an image (delete)
def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()
    opened_image = Image.open(image_path)
    opened_image.show()

#TODO: Make the images fullscreen, make the images actually close when the next image is shown
#TODO: We have an instructions page for the proctor, maybe display an instruction page to the participant as well
#TODO: It is possible to have a single extraneous entry in the log file, this is because the scipt logs a single keypress after the last image is shown

def handle_client(conn):
    global current_index, start_time, session_ended
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            key = data.decode('utf-8') # sending data from pi to computer using sockets - really basic protocol - only sends binary data, 
            # This automatically turns the text into binary so you can send it
            # The scoring and timing happens on the pi
            # Client sends the start to the pi, then pi only sends the image index to the client
            # Do as much as possible on the pi
            if session_ended:
                continue
            end_time = time.time()
            time_taken = end_time - start_time
            if key == "s": #TODO: Display an image with instructions to the participant until s pressed, allow for proctor to exit ("page 0")
                response = str(image_numbers[current_index])
                show_image(image_paths[current_index])
                start_time = time.time()  # Reset start time for the next image
                current_index += 1
            elif key in ["y", "n"]:
                if current_index < len(image_numbers):
                    response = str(image_numbers[current_index])
                    show_image(image_paths[current_index])
                    start_time = time.time()  # Reset start time for the next image
                    current_index += 1
                else:
                    response = "end"
                    session_ended = True
            # Log the data
            image_num = image_numbers[current_index - 1]
            colour = image_colour[image_num]
            word = image_word[image_num]
            log_data = [image_num, colour, word, key, time_taken]
            print(f"Logging data: {log_data}")
            with open("cognitive_results.csv", "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(log_data)
            conn.sendall(response.encode('utf-8'))

# (delete)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        handle_client(conn)

#TODO: Score the data