from PIL import Image
import os
import random
import time
import csv
import socket

HOST = "100.120.18.53"  # Server's hostname or IP address
PORT_MAIN = 65433  # Port used by the main menu server
PORT_COGNITIVE = 65432  # Port used by the cognitive test server
session_ended = False  # Flag to indicate if the session has ended
csv_directory = "/home/hits/Documents/GitHub/HITS/csv_files"  # Folder to save CSV files

# Function to decode the message into user info
def decode_message(message):
    """Decode the message SbHnnnAbNnnnnn into its components."""
    print(message)
    sex = "Female" if message[1] == "1" else "Male"  # Sx -> 1 is female, 0 is male
    height = int(message[3:6])  # Hnnn -> height in cm
    activity = "Drunk" if message[7] == "1" else "Sober"  # Ax -> 1 is drunk, 0 is sober
    participant_number = int(message[9:len(message)])  # b -> participant number
    return sex, height, activity, participant_number

# Function to append cognitive data starting at column F
def append_cognitive_data(file_path, cognitive_data):
    """Append cognitive data to the existing user CSV file, starting at column F."""
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Add the cognitive data starting from column F
        writer.writerow(cognitive_data)

# Function to track cognitive data (image number, color, word, key, time taken)
def track_cognitive_data():
    image_numbers = list(range(1, 17))  # Assuming 16 images
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
    start_time = time.time()  # Start timing
    session_ended = False  # Flag to indicate if the session has ended

    return image_numbers, image_colour, image_word, image_paths, current_index, start_time, session_ended

# Function to open and display an image
opened_image = None  # Initialize the variable at the global level

def show_image(image_path):
    global opened_image  # Use the global opened_image variable
    if opened_image:
        opened_image.close()  # Close the previous image if it exists
    opened_image = Image.open(image_path)
    opened_image.show()

# Function to handle client connections for the main menu
def handle_main_menu_client(conn_main):
    data = conn_main.recv(1024).decode('utf-8')  # Receive the message
    sex, height, activity, number = decode_message(data)
    print(f"Received: {sex}, {height}, {activity}, {number}")
    file_name = f"{sex}_{height}_{activity}_{number}.csv"
    file_path = os.path.join(csv_directory, file_name)

    # Store participant info in CSV
    with open(file_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Sex", "Height", "Activity", "Participant Number", "Test Result"])
        writer.writerow([sex, height, activity, number, ""])  # First row with header

    conn_main.sendall("Information saved!".encode('utf-8'))  # Acknowledge the received info
    conn_main.close()

# Main function to run the server
def run_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_main:
        s_main.bind((HOST, PORT_MAIN))
        s_main.listen()
        print(f"Main menu server started on {HOST}:{PORT_MAIN}")

        while True:
            conn_main, addr_main = s_main.accept()
            print(f"Connected by {addr_main}")
            handle_main_menu_client(conn_main)
            break  # Break after handling the main menu client

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_cognitive:
        s_cognitive.bind((HOST, PORT_COGNITIVE))
        s_cognitive.listen()
        print(f"Cognitive test server started on {HOST}:{PORT_COGNITIVE}")

        while True:
            conn_cognitive, addr_cognitive = s_cognitive.accept()
            print(f"Connected by {addr_cognitive}")

            # Handle cognitive testing
            image_numbers, image_colour, image_word, image_paths, current_index, start_time, session_ended = track_cognitive_data()

            show_image(image_paths[current_index])  # Show first image
            while not session_ended:
                data = conn_cognitive.recv(1024).decode('utf-8')
                if data in ['y', 'n']:
                    print(f"Received keypress: {data}")
                    # Add logic to process cognitive responses
                    # Add any other logic needed for handling the test
                elif data == 'e':
                    print("Ending the test session.")
                    session_ended = True
                    break

            conn_cognitive.close()

# Start the server
run_server()
