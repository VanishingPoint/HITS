import socket
import os
import time
from PIL import Image
from pynput import keyboard
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# Define paths and images
base_path = r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images\menu_"
image_numbers = list(range(0, 6))  # 0 to 5 for 6 images
image_paths = [f"{base_path}{i}.png" for i in image_numbers]

# Setup for plot
current_i = 0  # Tracks the current image index

def setup_plot():
    global fig, ax, img_display
    fig, ax = plt.subplots()  # Create the figure and axis for the plot
    ax.axis("off")  # Hide axes initially
    img_display = ax.imshow(mpimg.imread(image_paths[current_i]))  # Display the first image
    plt.show(block=False)

def update_image():
    global current_i
    img_display.set_data(mpimg.imread(image_paths[current_i]))  # Update the image data
    plt.draw()  # Ensure the plot updates after changing the image

def send_keystroke(key):
    HOST = "127.0.0.1"  # Server address
    PORT = 65432  # The port used by the server
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

def increment_and_show_next_image():
    global current_i
    current_i += 1
    if current_i < len(image_paths):
        update_image()  # Show the next image
        print(f"Image {current_i} displayed.")
    else:
        print("End of image sequence.")

def on_press(key):
    global current_i
    try:
        if key.char == 'c':
            if current_i == 0:
                increment_and_show_next_image()
            else:
                response = send_keystroke('c')
                print(f"Received response: {response}")
                increment_and_show_next_image()
        elif key.char == 'b':  # Go back to previous image
            if current_i > 0:
                current_i -= 1
                update_image()
                print(f"Image {current_i} shown.")
        elif key.char == 'esc':
            print("Exiting program.")
            return False  # Exit program
    except AttributeError:
        pass  # Ignore other keys

def main():
    setup_plot()

    # Start listening for keyboard input
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    plt.show()  # Keep the plot window open

if __name__ == "__main__":
    main()
