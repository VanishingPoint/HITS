from PIL import Image
import os
import random
import time
import csv
import socket
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

# List of image numbers (shuffled for randomness)
image_numbers = list(range(1, 31))  # Assuming 30 images
random.shuffle(image_numbers)

# Defining attributes for each image
image_colour = {
    1: "blue", 2: "green", 3: "red", 4: "blue", 5: "green",  6: "green",  7: "blue", 8: "yellow", 9: "red", 10: "green", 
    11: "red", 12: "yellow", 13: "green", 14: "blue", 15: "blue", 16: "yellow", 17: "blue", 18: "green", 19: "red", 20: "yellow", 
    21: "yellow", 22: "red", 23: "red", 24: "yellow", 25: "blue", 26: "blue", 27: "green", 28: "blue", 29: "red", 30: "yellow"}
image_word = {
    1: "red", 2: "green", 3: "blue", 4: "yellow", 5: "blue", 6: "red", 7: "blue", 8: "red", 9: "yellow", 10: "red", 
    11: "green", 12: "yellow", 13: "yellow", 14: "green", 15: "red", 16: "blue", 17: "yellow", 18: "green", 19: "blue", 20: "yellow", 
    21: "green", 22: "green", 23: "red", 24: "blue", 25: "green", 26: "blue", 27: "blue", 28: "yellow", 29: "blue", 30: "red"}
#TODO: Remove these attributes and just bring up the "answer" image that corresponds to the image number


current_index = 0  # Tracks the current image index
opened_image = None  # Keeps reference to the currently open PIL Image object
data = []  # To store keypress data
start_time = time.time()  # Start timing

print("Press 's' to start the randomized image sequence.")
print("Press 'y' or 'n' to open the next image after starting.")
print("Press 'esc' to exit the program.")

# Flag to indicate if the sequence has started
started = False

def on_press(key):
    global started
    try:
        if key.char == 's' and not started:
            started = True
            response = send_keystroke('s')
            print(f"Received image number: {response}")
        elif key.char == 'y' and started:
            response = send_keystroke('y')
            print(f"Received image number: {response}")
        elif key.char == 'n' and started:
            response = send_keystroke('n')
            print(f"Received image number: {response}")
        elif key.char == 'esc':
            print("Exiting program.")
            return False
    except AttributeError:
        pass

# Collect events until released
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()