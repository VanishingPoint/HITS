import os
import random
import time
import csv
import socket
import tkinter
from PIL import Image, ImageTk

# This is where Triss is trying to get the fullscreen to work

HOST = "100.120.18.53"  # The server's hostname or IP address
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
opened_image = None  # Keeps reference to the currently open PIL Image object
session_started = False # Flag to indicate if the session has started
session_ended = False  # Flag to indicate if the session has ended
root = None # Global variable to store the root window reference

#TODO: Make the images fullscreen, make the images actually close when the next image is shown
#TODO: We have an instructions page for the proctor, maybe display an instruction page to the participant as well
#TODO: It is possible to have a single extraneous entry in the log file, this is because the scipt logs a single keypress after the last image is shown
#TODO: Score the data

def checkConnection(conn): # this function listens for key presses from the participant and reacts accordingly
    with conn:
        while True:
            data = conn.recv(1024) # Receive data from client, where does this come from?
           
            if not data:
                break
            key = data.decode('utf-8') # Decode the key press

            if session_ended: # Ignore the input if the session has ended
                continue

            if (key == "s" and session_started == False):
                current_index += 1
                response = str(image_numbers[current_index])
                start_time = time.time()  # Start timing
                nextImg() # Show the first image

            elif key in ["y", "n"]: # If the participant responds
                if current_index < len(image_numbers):
                    end_time = time.time()
                    time_taken = end_time - start_time # Compute response time
                    logData(key, time_taken) # Save response
                    current_index += 1
                    response = str(image_numbers[current_index])
                    start_time = time.time()  # Reset start time for the next image
                    nextImg() # Displays next image
                else:
                    response = "end"
                    session_ended = True
                    end_time = time.time()
                    time_taken = end_time - start_time
                    logData(key, time_taken)
                    close_image_window() # Ends test
                    
            elif key == "x":
                close_image_window() # Exits the test
            
            conn.sendall(response.encode('utf-8')) # Sends the response to the client


def logData(key, time_taken): # Log the data
    image_num = image_numbers[current_index]
    colour = image_colour[image_num]
    word = image_word[image_num]
    log_data = [image_num, colour, word, key, time_taken]
    print(f"Logging data: {log_data}")
    with open("cognitive_results.csv", "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(log_data)

def nextImg(): # This function displays the image
    global root, current_index
    pilImage = Image.open(image_paths[current_index]) # Opens the image
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1) # Fullscreen mode? 
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()    
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))

    # Display the image on a black background of a specific size
    canvas = tkinter.Canvas(root, width=w, height=h)
    canvas.pack()
    canvas.configure(background='black')

    # Resize image if it is too big
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth, imgHeight), Image.LANCZOS)

    # Display the image
    image = ImageTk.PhotoImage(pilImage)
    imagesprite = canvas.create_image(w/2, h/2, image=image)

    # Wait for key press in checkConnection function
    root.after(5, checkConnection) 
    root.mainloop()

# This function closes the image
def close_image_window():
    global root
    if root:
        root.destroy()
        root = None

# Starts the server and waits for the participant to connect
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT)) # Bind to the IP and port
    s.listen() # Wait for client
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept() # Accept incoming connection
        print(f"Connected by {addr}")
        if not session_ended:
            nextImg() # Start test

