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

# Function to open and display an image
opened_image = None  # Initialize the variable at the global level

def show_image(image_path):
    global opened_image  # Use the global opened_image variable
    if opened_image:
        opened_image.close()  # Close the previous image if it exists
    opened_image = Image.open(image_path)
    opened_image.show()

# Function to handle client connections for the main menu
def handle_main_menu_client(conn_main, addr):
    global session_ended
    with conn_main:
        print(f"Connected by {addr} (Main Menu)")

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
                    writer.writerow(["Sex", "Height (cm)", "Activity", "Participant Number", "Timestamp", "Image Number", "Color", "Word", "Response", "Time Taken"])
                log_data = [sex, height, activity, participant_number, time.time()]
                writer.writerow(log_data)

            # Send back the received message as the response
            conn_main.sendall(message.encode('utf-8'))  # Send the received message back to the proctor

            return file_path  # Return the file path for use in the cognitive test

# Function to handle client connections for the cognitive test
def handle_cognitive_test(conn_cognitive, file_path):
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

    with conn_cognitive:
        print(f"Connected by {addr_cognitive}")
        while True:
            
            data_available = False

            while not data_available:
                data = conn_cognitive.recv(1024)
                if data:
                    data_available = True

            #if not data:
                #print("not data break trip")
                #break


            key = data.decode('utf-8')

            # Check if session has ended
            if session_ended == True:
                print("Session ended.")
                break

            end_time = time.time()
            time_taken = end_time - start_time

            print(f"Key Recieved: {key}") #Debug print

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
                    conn_cognitive.sendall(response.encode('utf-8'))
                    #not Sure the above line is correct - Triss
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
            append_cognitive_data(file_path, cognitive_data)

            print("finished logging")

            conn_cognitive.sendall(response.encode('utf-8'))
            print("sent response")

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
            file_path = handle_main_menu_client(conn_main, addr_main)  # Handle main menu client and get file path
            
            conn_cognitive, addr_cognitive = s_cognitive.accept()  # Accept cognitive test connection
            handle_cognitive_test(conn_cognitive, file_path)  # Handle cognitive test client with file path
            print("finished calling handle_cognitive_test") # it stops here
            #It should'nt be reaching the line above until the test is finished... the while true is not working???
            #We either troubleshoot the loop or conditionally run the setup portion of the function and loop calling the function.
            #Chaging the loop condition did not work. Perhaps it is hitting a break statement?? Will try option 2