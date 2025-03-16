from PIL import Image
import os
import socket
import time
from pynput import keyboard
from nicegui import app, ui
from nicegui.events import KeyEventArguments

HOST = "100.120.18.53"  # The server's hostname or IP address for the pi
PORT_main = 53433  # Port for user info
PORT_cog = 53432  # Port for cognitive test responses
content = ui.column()

def send_info(participant_information):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT_main))
            s.sendall(participant_information.encode('utf-8'))
            data = s.recv(1024)
        return data.decode('utf-8')
    except ConnectionRefusedError:
        print("Connection refused. Retrying...")
        time.sleep(1)
        return send_info(participant_information)
    
def save_user_info(sex, height, activity, number):
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
    show_menu()

def user_info():
    content.clear()
    with content:
        ui.label("Enter the Participant's Information").classes('text-2xl font-bold')
        number = ui.input("Participant's Number").classes("w-64")
        sex = ui.radio(["Male", "Female"]).classes("w-64")
        height = ui.input("Participant's Height in 3 digits [cm]").classes("w-64")
        ui.label("Select the activity:").classes('text-lg')
        activity = ui.select(['Drunk', 'Sober'], value=None)
    
        def submit():
            save_user_info(sex.value, height.value, activity.value, number.value)
            ui.notify("User Info Saved!", color="green")

        ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")

def show_menu():
    content.clear()
    with content:
        ui.image("C:/Users/chane/Desktop/HITS/HITS/Main Menu Proctor Images/menu_0.png")
        ui.button("Back", on_click=user_info).classes("text-lg bg-gray-500 text-white p-2 rounded-lg")
        ui.button("Next", on_click=start_sequence).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")

# --- NiceGUI Image Display with Interactive Buttons ---
image_numbers = list(range(0, 17))  # Ensure cognitive_page_0 is first
image_paths = [
    fr"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images/cognitive_page_{num}.png"
    for num in image_numbers
]

current_image = ui.image(image_paths[0])  # Start with explanation image
started = False

# Buttons initially hidden until test starts
yes_button = ui.button("Yes", on_click=lambda: next_image('y')).style("display: none;")
no_button = ui.button("No", on_click=lambda: next_image('n')).style("display: none;")

def send_keystroke(key):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT_cog))
            s.sendall(key.encode('utf-8'))
            data = s.recv(1024)
        return data.decode('utf-8')
    except ConnectionRefusedError:
        print("Connection refused. Retrying...")
        time.sleep(1)
        return send_keystroke(key)

def start_sequence():
    global started
    content.clear()
    with content:
        ui.image(image_paths[0])
        yes_button.style("display: inline-block;")
        no_button.style("display: inline-block;")
    
    if not started:
        started = True
        response = send_keystroke('s')
        if response.isdigit():
            current_image.set_source(image_paths[int(response)])

def next_image(response_key):
    if started:
        response = send_keystroke(response_key)
        if response.isdigit():
            current_image.set_source(image_paths[int(response)])
        elif response == "end":
            ui.notify("Sequence Ended")
            # Display menu_1.png after the sequence ends
            current_image.set_source("C:/Users/chane/Desktop/HITS/HITS/Main Menu Proctor Images/menu_1.png")

def exit_program():
    ui.notify("Exiting Program")
    ui.stop()

with content:
    user_info()

ui.run()
