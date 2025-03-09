# This script runs the main menu and all of the tests in separate functions 
# It is for use by the test proctor on a laptop
# Written by Chanel 
# TODO: Change UI image so that 'c' is used since 's' makes it think I want to save the image
# TODO: Change UI image for that 'b' is used for back since 'esc' doesn't work
# Eyemovementtest_screen to display image to pi screen

# Import Librairies
import time
import socket
import os
from pynput import keyboard
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Define the base path for the images
base_path = r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images\menu_"

# List of image numbers (0 to 5 for 6 images)
image_numbers = list(range(0, 6)) 

# Construct the image paths dynamically using the base path and image numbers
image_paths = [f"{base_path}{i}.png" for i in image_numbers]

current_index = 0  # Tracks the current image index
ended = False  # Flag to indicate whether results have been calculated

def setup_plot():  # Initialize the plot to display images
    global fig, ax, img_display
    fig, ax = plt.subplots()  # Create the figure and axis for the plot
    ax.axis("off")  # Hide axes initially
    img_display = ax.imshow(mpimg.imread(image_paths[current_index]))  # Display the first image
    plt.show(block=False)  # Show the figure window without blocking the script

def update_image():  # Function to display the current image
    global current_index
    img_display.set_data(mpimg.imread(image_paths[current_index]))  # Update the image data
    plt.draw()  # Ensure the plot updates after changing the image

def run_test_1():  # Test 1 function: COGNITIVE
    
    HOST = "100.120.18.53"  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    def send_keystroke(key):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(key.encode('utf-8'))
                data = s.recv(1024)
            return data.decode('utf-8')
        except ConnectionRefusedError:
            print("Connection refused. Retrying...")
            time.sleep(1)
            return send_keystroke(key)

    current_index = 0  # Tracks the current image index
    

    print("Press 's' to start the randomized image sequence.")
    print("Press 'y' or 'n' to open the next image after starting.")
    print("Press 'esc' to exit the program.")

    #TODO: Maybe remove these prints if we are displaying an image that contains the same info

    image_numbers = list(range(0, 17)) #image 0 is explination, others are answers corresponding to the participant images

    # List of image paths based on shuffled numbers
    image_paths = [
        # Triss's Laptop Path fr"/Users/test/Documents/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png"
        fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png"
        for num in image_numbers
    ]
    #NOTE: This is the path to the images on my computer, you will need to change this to the path on your computer
    #TODO should always display cognitive_page_0 first as it displays the instructions

    def show_image(image_path):
        # global opened_image
        opened_image = None  # Keeps reference to the currently open PIL Image object

        if opened_image:
            opened_image.close()
        opened_image = Image.open(image_path)
        opened_image.show()

    #TODO:Make the images close (it doesnt work rn)

    show_image(image_paths[0]) #show the explination image

    # Flag to indicate if the sequence has started
    started = False

    def on_press(key):
        global started
        try:
            if key.char == 'c' and not started:
                started = True
                response = send_keystroke('c')
                print(f"Received image number: {response}")
                show_image(image_paths[int(response)])
            elif key.char == 'y' and started:
                response = send_keystroke('y')
                print(f"Received image number: {response}")
                if response != "end":
                    show_image(image_paths[int(response)])
            elif key.char == 'n' and started:
                response = send_keystroke('n')
                print(f"Received image number: {response}")
                if response != "end":
                    show_image(image_paths[int(response)])
            elif key.char == 'esc':
                print("Exiting program.")
                return False

        except AttributeError:
            pass

    # Collect events until released
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

        print("Test 1 complete.")
        increment_and_show_next_image()

def run_test_2():  # Test 2 function
    print("Running Test 2...")
    time.sleep(2)  # Simulate running the test (e.g., processing time)
    print("Test 2 complete.")
    increment_and_show_next_image()

def run_test_3():  # Test 3 function
    print("Running Test 3...")
    time.sleep(2)  # Simulate running the test (e.g., processing time)
    print("Test 3 complete.")
    increment_and_show_next_image()

def run_test_4():  # Test 4 function
    print("Running Test 4...")
    time.sleep(2)  # Simulate running the test (e.g., processing time)
    print("Test 4 complete.")
    increment_and_show_next_image()

def increment_and_show_next_image(): # Function to increment the index and show the next image
    global current_index
    current_index += 1
    if current_index < len(image_paths):
        update_image()  # Show the next image
        print(f"Image {current_index} displayed.")
    else:
        print("End of image sequence.")

def on_press(key):  # Function to handle key presses
    global current_index, ended
    if not ended:
        try:
            if key.char == 'c':  # Execute one of the test functions based on current index
                if current_index == 0:
                    increment_and_show_next_image()
                elif current_index == 1:
                    run_test_1()  # Run Test 1 if the current index is 1
                elif current_index == 2:
                    run_test_2()  # Run Test 2 if the current index is 2
                elif current_index == 3:
                    run_test_3()  # Run Test 3 if the current index is 3
                elif current_index == 4:
                    run_test_4()  # Run Test 4 if the current index is 4
            elif key.char == 'b':  # Go back to the previous image
                if current_index > 0:
                    current_index -= 1
                    update_image()
                    print(f"Image {current_index} shown.")
        except AttributeError:
            pass  # Ignore other keys

def main():
    setup_plot()

    # Start the keyboard listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # Start listening for keyboard input

    plt.show()  # Keep the plot window open and interactive

if __name__ == "__main__":
    main()
