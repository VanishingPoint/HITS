from PIL import Image
import os
import socket
import time
from pynput import keyboard

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
opened_image = None  # Keeps reference to the currently open PIL Image object

print("Press 's' to start the randomized image sequence.")
print("Press 'y' or 'n' to open the next image after starting.")
print("Press 'esc' to exit the program.")

#TODO: Maybe remove these prints if we are displaying an image that contains the same info

image_numbers = list(range(0, 17)) #image 0 is explination, others are answers corresponding to the participant images

# List of image paths based on shuffled numbers
image_paths = [
    fr"/Users/test/Documents/HITS/Cognitive Proctor Images/cognitive_page_{num}.png"
    for num in image_numbers
]
#NOTE: This is the path to the images on my computer, you will need to change this to the path on your computer
#TODO should always display cognitive_page_0 first as it displays the instructions

def show_image(image_path):
    global opened_image
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
        if key.char == 's' and not started:
            started = True
            response = send_keystroke('s')
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