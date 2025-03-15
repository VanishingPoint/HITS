from PIL import Image
import os
import socket
import time
from pynput import keyboard
from nicegui import app, ui
from nicegui.events import KeyEventArguments

HOST = "100.120.18.53"  # The server's hostname or IP address for the pi
PORT = 65433  # The port used by the server for main menu in particular
content = ui.column()

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
    
def save_user_info(sex, height, activity, number, append=False):
    if sex.value == "Female":
            participant_sex = "1"
    elif sex.value == "Male":
            participant_sex = "0"
    participant_height = str(height.value)  
    participant_activity = str(activity.value) # change to binary
    participant_number = str(number.value)
    participant_info = f"S{participant_sex}H{participant_height}A{participant_activity}N{participant_number})"
    print(f"User Info Saved as {participant_info}")
    send_info(participant_info)

def user_info():
    with ui.column():
        ui.label("Enter the Participant's Information").classes('text-2xl font-bold')
        number = ui.input("Participant's Number").classes("w-64")
        sex = ui.radio(["Male", "Female"], value="Other").classes("w-64")
        height = ui.input("Participant's Height in 3 digits [cm]").classes("w-64")
        ui.label("Select the activity:").classes('text-lg')
        activity = ui.select(['Drunk', 'Sober'], value=None)
    
        def submit():
            save_user_info(sex.value, height.value, activity.value, number.value)
            ui.notify("User Info Saved!", color="green")

        ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")

ui.label("Hello, NiceGUI!").classes('text-2xl font-bold')  # Test if something is rendering
ui.run()