from PIL import Image
import os
import socket
import time
from pynput import keyboard
from nicegui import app, ui
import random

HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65433  # The port used by the server for the main menu in particular
content = ui.column()

image_numbers = list(range(0, 17)) #image 0 is explination, others are answers corresponding to the participant images

image_paths = [
    # fr"/Users/test/Documents/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Triss
    # fr"C:\Users\richy\Downloads\cognitive\images\cognitive_page_{num}.png" # Richard
     fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png" # Chanel
    for num in image_numbers
]

opened_image = None
started = False
ended = False
completed = False

def send_keystroke(key):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(key.encode('utf-8'))
            data = s.recv(1024)
            print(f"Server response: {data.decode('utf-8')}")
        return data.decode('utf-8')
    except ConnectionRefusedError:
        print("Connection refused. Retrying...")
        time.sleep(1)
        return send_keystroke(key)

def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()
    opened_image = Image.open(image_path)
    opened_image.show()

def on_press(key):
    global started, ended, completed
    print(f"starting cases: started = {started}, ended = {ended}, completed = {completed}") # it stops here the second time this runs
    try:
        if key.char == 's' and not started:
            started = True
            print("Test started.")
            # Show the first image
            response = send_keystroke(key.char)
            print(f"Sending key stroke: {key.char}")
            print(f"Received image number: {response}")
            show_image(image_paths[int(response)])
            print("came back from show image for instructions")
        elif (key.char == 'y' or key.char == 'n') and started:
            # Send the 'y' or 'n' response to the server
            print("sent key:", key)
            response = send_keystroke(key.char)
            print(f"received key response {response}")
            if (response == 'end'):
                print("Test Complete")
                ended = True
                completed = True
            else:
                print(f"Received image number: {response}")
                print(f"Next image: {image_numbers[response]}")
                show_image(image_paths[int(response)])  # Show the next randomized image
        elif key.char == 'e':
            print("Exiting program.")
            ended = True
            completed = False
              # Allows the user to exit the test if 'e' is pressed, false flag indicates incomplete test
        else:
                print("Invalid Input")
                
    except AttributeError:
        pass
    print ("exiting cases")
    return 0

# Run cognitive test once user info is submitted
def run_cognitive_test():
    global started, image_numbers, completed
    print("Press 's' to start the randomized image sequence.")
    print("Press 'y' or 'n' to open the next image after starting.")
    print("Press 'e' to exit the program.")

    # Show the explanation image first (cognitive_page_0)
    show_image(image_paths[0])

    while not completed:
        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()
            print(f"After listener: started={started}, ended={ended}, completed={completed}")

    print("loop exited")

with content:
    run_cognitive_test()

ui.run()
