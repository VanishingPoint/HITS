import tkinter as tk
from tkinter import Label
import os
import random
import time
import csv
import socket
from PIL import Image, ImageTk

HOST = "10.0.0.223"  # "127.0.0.1"  # This allows me to run both scripts on the same device
PORT = 65432  # The port used by the server

# List of image numbers (shuffled for randomness)
image_numbers = list(range(1, 17))  # Assuming 16 images
random.shuffle(image_numbers)

# Defining attributes for each image
image_colour = {
    1: "blue", 2: "green", 3: "red", 4: "yellow", 5: "blue", 6: "green", 7: "red", 8: "yellow",
    9: "blue", 10: "green", 11: "red", 12: "yellow", 13: "blue", 14: "green", 15: "red", 16: "yellow"
}
image_word = {
    1: "red", 2: "red", 3: "red", 4: "red", 5: "blue", 6: "blue", 7: "blue", 8: "blue",
    9: "yellow", 10: "yellow", 11: "yellow", 12: "yellow", 13: "green", 14: "green", 15: "green", 16: "green"
}

# List of image paths based on shuffled numbers
image_paths = [
    fr"C:\Users\richy\Documents\Git\HITS\Cognitive\Cognitive Participant Images\cognitive_participant_page_{num}.png"
    for num in image_numbers
]

current_index = 0  # Tracks the current image index
start_time = time.time()  # Start timing
session_ended = False  # Flag to indicate if the session has ended

# Setting up tkinter window
root = tk.Tk()
root.title("Cognitive Test")

# Create a label to display images
image_label = Label(root)
image_label.pack()

# Function to open and display an image
def show_image(image_path):
    global image_label  # Ensure that image_label is accessible
    image = Image.open(image_path)
    
    # Set a fixed size for the image (e.g., 600x400 or smaller based on your preference)
    max_width = 1300
    max_height = 1000
    
    image.thumbnail((max_width, max_height))  # This keeps the aspect ratio intact while resizing
    
    # Convert to PhotoImage and display it
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo  # Keep a reference to avoid garbage collection

# Display the first image on startup
show_image(fr"C:\Users\richy\Documents\Git\HITS\Cognitive\Cognitive Participant Images\cognitive_participant_page_0.png")

# Function to handle socket communication
def handle_client(conn, addr):  # Add addr as a parameter
    global current_index, start_time, session_ended
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            key = data.decode('utf-8')
            if session_ended:
                continue
            end_time = time.time()
            time_taken = end_time - start_time
            if key == "s":
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

# Function to start the server and listen for connections
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()  # addr is now returned here
            handle_client(conn, addr)  # Pass addr to handle_client

# Function to toggle full-screen mode
def toggle_fullscreen(event=None):
    # Toggle the fullscreen state
    current_state = root.attributes('-fullscreen')
    root.attributes('-fullscreen', not current_state)

# Function to handle the escape key to exit fullscreen
def exit_fullscreen(event=None):
    root.attributes('-fullscreen', False)

# Bind the Escape key to exit full-screen mode
root.bind('<Escape>', exit_fullscreen)

# Set the window to full-screen by default when the application starts
root.attributes('-fullscreen', True)

# Running the server in a separate thread so the tkinter GUI stays responsive
import threading
server_thread = threading.Thread(target=start_server)
server_thread.daemon = True
server_thread.start()

# Start tkinter main loop
root.mainloop()

