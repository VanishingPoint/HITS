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

def receive_file(sock, save_path):
    """Receive a file from the server and save it."""
    try:
        with open(save_path, "wb") as file:
            while True:
                data = sock.recv(1024)  # Receive file in chunks
                if not data:
                    break
                file.write(data)
        print(f"File saved as {save_path}")
    except Exception as e:
        print(f"Error receiving file: {e}")

def send_info(participant_information, save_dir="received_csvs"):
    """Send participant information and receive the CSV file."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(participant_information.encode('utf-8'))
            
            # Ensure save directory exists
            os.makedirs(save_dir, exist_ok=True)

            # Define file path for saving the received CSV
            file_name = f"{participant_information}.csv".replace(":", "_").replace(" ", "_")
            save_path = os.path.join(save_dir, file_name)

            # Receive and save the file
            receive_file(s, save_path)
        
        return save_path
    except ConnectionRefusedError:
        print("Connection refused. Retrying...")
        time.sleep(1)
        return send_info(participant_information, save_dir)
    
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

def user_info():
    with ui.column():
        ui.label("Enter the Participant's Information").classes('text-2xl font-bold')
        number = ui.input("Participant's Number").classes("w-64")
        sex = ui.radio(["Male", "Female"]).classes("w-64")
        height = ui.input("Participant's Height in 3 digits [cm]").classes("w-64")
        ui.label("Select the activity:").classes('text-lg')
        activity = ui.select(['Drunk', 'Sober'], value=None)
    
        def submit():
            print("Submit button clicked! S{sex.value} H{height.value} A{activity.value} N{number.value}")
            save_user_info(sex.value, height.value, activity.value, number.value)
            ui.notify("User Info Saved!", color="green")

        ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")

with content:
    user_info()
ui.run()