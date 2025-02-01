from PIL import Image
import os
import random
import time
import csv
import socket

HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

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

# List of image paths based on shuffled numbers
image_paths = [
    fr"/home/hits/Documents/GitHub/HITS/Images to Output/page_{num}.png"
    for num in image_numbers
]

current_index = 0  # Tracks the current image index
opened_image = None  # Keeps reference to the currently open PIL Image object
data = []  # To store keypress data
start_time = time.time()  # Start timing

# Function to open and display an image
def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()
    opened_image = Image.open(image_path)
    opened_image.show()

def handle_client(conn):
    global current_index
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            key = data.decode('utf-8')
            if key == "s":
                response = str(image_numbers[current_index])
                show_image(image_paths[current_index])
                current_index += 1
            elif key in ["y", "n"]:
                if current_index < len(image_numbers):
                    response = str(image_numbers[current_index])
                    show_image(image_paths[current_index])
                    current_index += 1
                else:
                    response = "end"
            conn.sendall(response.encode('utf-8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = s.accept()
        handle_client(conn)