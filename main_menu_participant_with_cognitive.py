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

# Function to append user info with cognitive data
def append_cognitive_data(file_path, cognitive_data):
    """Append cognitive data to the existing user CSV file."""
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(cognitive_data)

# Function to handle client connections for the main menu
def handle_main_menu_client(conn_main, addr):
    global session_ended
    with conn_main:
        print(f"Connected by {addr_main} (Main Menu)")
        
        while True:
            data = conn_main.recv(1024)
            if not data:
                break
            message = data.decode('utf-8') 
            if session_ended:
                continue
            
            sex, height, activity, participant_number = decode_message(message)
            
            # Generate the CSV filename based on the message and save it in the csv_directory
            file_name = f"{message}.csv"
            file_name = file_name[:255].replace(":", "_").replace(" ", "_")
            file_path = os.path.join(csv_directory, file_name)  # Full path to the CSV file

            # Ensure the directory exists
            os.makedirs(csv_directory, exist_ok=True)

            # Open file in append mode without checking size first
            with open(file_path, "a", newline="") as csvfile:
                writer = csv.writer(csvfile)
                if os.path.getsize(file_path) == 0:
                    writer.writerow(["Sex", "Height (cm)", "Activity", "Participant Number", "Timestamp"])
                log_data = [sex, height, activity, participant_number, time.time()]
                writer.writerow(log_data)

            # Cognitive part: Track image number, color, word, and response time
            cognitive_data = track_cognitive_data()
            append_cognitive_data(file_path, cognitive_data)

            # Send back the received message as the response
            conn.sendall(message.encode('utf-8'))  # Send the received message back to the proctor

# Function to handle client connections for the cognitive test
def handle_cognitive_client(conn_cognitive, addr):
    with conn_cognitive:
        print(f"Connected by {addr_cognitive} (Cognitive Test)")

        # Send instructions or start logic here
        session_ended = False
        while not session_ended:
            data = conn_cognitive.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')

            # Call functions related to cognitive testing logic here
            cognitive_data = track_cognitive_data()
            # For example, you can append the cognitive data or respond based on input
            conn_cognitive.sendall(message.encode('utf-8'))  # Respond with some message

# Function to track cognitive data (image number, color, word, key, time taken)
def track_cognitive_data():
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
    start_time = time.time()  # Start timing
    session_ended = False  # Flag to indicate if the session has ended
    
        # Function to open and display an image
    def show_image(image_path):
        global opened_image
        if opened_image:
            opened_image.close()
        opened_image = Image.open(image_path)
        opened_image.show()

    def handle_client(conn_cognitive):
        global current_index, start_time, session_ended
        with conn_cognitive:
            print(f"Connected by {addr_cognitive}")
            while True:
                data = conn_cognitive.recv(1024)
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
                append_cognitive_data()
                conn_cognitive.sendall(response.encode('utf-8'))
                
# Main server code
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_main:
    s_main.bind((HOST, PORT_MAIN))
    s_main.listen()
    print(f"Server listening on {HOST}:{PORT_MAIN}")
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_cognitive:
        s_cognitive.bind((HOST, PORT_COGNITIVE))
        s_cognitive.listen()
        print(f"Server listening on {HOST}:{PORT_COGNITIVE}")
        
        while True:
            conn_main, addr_main = s_main.accept()  # Accept main menu connection
            handle_main_menu_client(conn_main, addr_main)  # Handle main menu client
            
            conn_cognitive, addr_cognitive = s_cognitive.accept()  # Accept cognitive test connection
            handle_cognitive_client(conn_cognitive, addr_cognitive)  # Handle cognitive test client
