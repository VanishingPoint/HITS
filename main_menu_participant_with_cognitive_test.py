from PIL import Image
import os
import random
import time
import csv
import socket

HOST = "100.120.18.53"  # Server's hostname or IP address
PORT_MAIN = 65433  # Port used by the main menu server
# PORT_COGNITIVE = 65432  # Port used by the cognitive test server
session_ended = False  # Flag to indicate if the session has ended
csv_directory = "/home/hits/Documents/GitHub/HITS/csv_files"  # Folder to save CSV files
# Function to open and display an image
opened_image = None  # Initialize the variable at the global level
file_name = "S1H999A1N9.csv"
file_path = os.path.join(csv_directory, file_name)  # Full path to the CSV file
def show_image(image_path):
    global opened_image  # Use the global opened_image variable
    if opened_image:
        opened_image.close()  # Close the previous image if it exists
    opened_image = Image.open(image_path)
    opened_image.show()

# Function to handle client connections for the cognitive test
def handle_cognitive_test(conn_main, file_path):
    global session_ended
    image_numbers = list(range(1, 17))  # Assuming 16 images
    random.shuffle(image_numbers)

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

    current_index = 0  # Tracks the current image index
    start_time = time.time()  # Start timing
    session_ended = False  # Flag to indicate if the session has ended

    with conn_main:
        print(f"Connected by {addr_main}")
        while True:
            
            print("top of while true")

            data_available = False

            conn_main.settimeout(5)  # Set a 5-second timeout

            while not data_available:
                try:
                    data = conn_main.recv(1024)
                    if not data:  # Handle empty messages
                        print("Empty data received, breaking out of loop.")
                        # break
                        continue # new
                    print(f"Data received: {data}")
                    data_available = True
                except socket.timeout:
                    print("No data received, retrying...")

            #if not data: # this is the way it should be done but the new way is more informative
                #print("not data break trip")
                #break

            key = data.decode('utf-8')

            if not key or key not in {"s", "y", "n"}:  # Ignore blank input and invalid keys
                print(f"Invalid or blank key pressed: '{key}'")
                continue

            if session_ended:
                print("Session ended.")
                break

            end_time = time.time()
            time_taken = end_time - start_time

            print(f"Key Received: {key}") # Debug print

            if key == "s": 
                # Show the current image
                response = str(image_numbers[current_index])
                show_image(image_paths[current_index])
                start_time = time.time()  # Reset start time for the next image
                current_index += 1
            elif key in ["y", "n"]:
                if current_index < len(image_numbers):
                    response = str(image_numbers[current_index])
                    # Show next image
                    show_image(image_paths[current_index])
                    start_time = time.time()  # Reset start time for the next image
                    current_index += 1
                else:
                    # End the test when all images are shown
                    session_ended = True
                    print("Test completed.")
                    response = "end"
                    conn_main.sendall(response.encode('utf-8'))
                    break  # Exit the loop after all images are shown
            else:
                print(f"Invalid key pressed: {key}")
            
            print("logging data")
            # Log the data after each keystroke and image
            image_num = image_numbers[current_index - 1]
            colour = image_colour[image_num]
            word = image_word[image_num]
            # Additional data logging here (cognitive data)
            cognitive_data = [image_num, colour, word, key, time_taken]
            print(f"{cognitive_data}")
            print("finished logging")
            conn_main.sendall(response.encode('utf-8')) # why is this here a second time? -Chanel
            print("sent response")

# Main server code
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s_main:
    s_main.bind((HOST, PORT_MAIN))
    s_main.listen()
    print(f"Server listening on {HOST}:{PORT_MAIN}")
    
    while True:
        conn_main, addr_main = s_main.accept()  # Accept cognitive test connection
        handle_cognitive_test(conn_main, file_path)  # Handle cognitive test client with file path
        print("finished calling handle_cognitive_test") # it stops here