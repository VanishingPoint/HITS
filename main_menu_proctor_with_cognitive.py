from PIL import Image
import os
import socket
import time
from pynput import keyboard
from nicegui import app, ui
from nicegui.events import KeyEventArguments

HOST = "100.120.18.53"  # The server's hostname or IP address
PORT = 65433  # The port used by the server for main menu in particular
content = ui.column()

# Function to send user information
def send_info(participant_information):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(participant_information.encode('utf-8'))
            data = s.recv(1024)
        return data.decode('utf-8')
    except ConnectionRefusedError:
        print("Connection refused. Retrying...")
        time.sleep(1)
        return send_info(participant_information)

# Function to save user information
def save_user_info(sex, height, activity, number, append=False):
    if sex == "Female":
        participant_sex = "1"
    elif sex == "Male":
        participant_sex = "0"
    if activity == 'Drunk':
        participant_activity = "1"
    else:
        participant_activity = "0"
    participant_height = str(height)
    participant_number = str(number)
    participant_info = f"S{participant_sex}H{participant_height}A{participant_activity}N{participant_number}"
    print(f"User Info Saved as {participant_info}")
    send_info(participant_info)

# Function for user input interface in NiceGUI
def user_info():
    with ui.column():
        ui.label("Enter the Participant's Information").classes('text-2xl font-bold')
        number = ui.input("Participant's Number").classes("w-64")
        sex = ui.radio(["Male", "Female"]).classes("w-64")
        height = ui.input("Participant's Height in 3 digits [cm]").classes("w-64")
        ui.label("Select the activity:").classes('text-lg')
        activity = ui.select(['Drunk', 'Sober'], value=None)

        def submit():
            print(f"Submit button clicked! S{sex.value} H{height.value} A{activity.value} N{number.value}")
            save_user_info(sex.value, height.value, activity.value, number.value)
            ui.notify("User Info Saved!", color="green")
            # After saving user info, run the cognitive test code
            run_cognitive_test()

        ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")

# Cognitive test variables and logic
HOST_COGNITIVE = "100.120.18.53"
PORT_COGNITIVE = 65432

image_numbers = list(range(0, 17))  # image 0 is explanation, others are answers
image_paths = [
    fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png"
    for num in image_numbers
]
opened_image = None
started = False
current_index = 0

def send_keystroke(key):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST_COGNITIVE, PORT_COGNITIVE))
            s.sendall(key.encode('utf-8'))
            data = s.recv(1024)
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

# Run cognitive test once user info is submitted
def run_cognitive_test():
    global started
    print("Press 's' to start the randomized image sequence.")
    print("Press 'y' or 'n' to open the next image after starting.")
    print("Press 'e' to exit the program.")

    show_image(image_paths[0])  # Show the explanation image

    def on_press(key):
        global started
        try:
            if key.char == 's' and not started:
                started = True
                # Send 's' to start the test (or the initial image)
                response = send_keystroke('s')
                print(f"Starting the test, received response: {response}")
                # Display the first random image after 's' is pressed
                show_image(image_paths[int(response)])
            elif key.char == 'y' and started:
                # Send 'y' and display the next image after starting
                response = send_keystroke('y')
                print(f"Received response for 'y': {response}")
                if response != "end":
                    show_image(image_paths[int(response)])  # Show the next image
            elif key.char == 'n' and started:
                # Send 'n' and display the next image after starting
                response = send_keystroke('n')
                print(f"Received response for 'n': {response}")
                if response != "end":
                    show_image(image_paths[int(response)])  # Show the next image
            elif key.char == 'e':
                print("Exiting program.")
                return False  # Stop listening for events (exit)
        except AttributeError:
            pass  # Handle non-character keys

    # Collect events until released
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Start NiceGUI app
with content:
    user_info()

ui.run()
