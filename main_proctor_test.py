import datetime
import csv
import random
from pathlib import Path
from nicegui import app, ui

# Set up the folder containing images
folder = Path(r"C:\Users\chane\Desktop\HITS\HITS\niceGUI Images")
files = sorted(f.name for f in folder.glob('image_*.png'))
cognitive_files = sorted(f.name for f in folder.glob('cognitive_page_*.png'))
random.shuffle(cognitive_files)  # Shuffle cognitive images
csv_file_path = None  # Global variable

# State tracking
state = {'index': 0, 'cognitive_index': 0}

# Create a container to hold UI elements
content = ui.column()

def save_user_info(name, sex, age, height, activity):
    global csv_file_path
    folder_path = Path(r"C:\Users\chane\Desktop\HITS\HITS\csv_files")
    folder_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    csv_file_path = folder_path / f"{name.replace(' ', '_')}_{timestamp}.csv"
    
    with open(csv_file_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Sex", "Age", "Height", "Activity"])
        writer.writerow([name, sex, age, height, activity])
    print(f"User Info Saved to {csv_file_path}")

def load_page(page_function):
    content.clear()
    with content:
        page_function()

def opening_screen():
    with ui.column():
        ui.image(f'/images/{files[0]}').style("width: 60vw;")
        ui.button("Enter Participant's Information", on_click=lambda: load_page(user_info))

def user_info():
    with ui.column():
        ui.label("Enter the Participant's Information").classes('text-2xl font-bold')
        name = ui.input("Participant's Full Name")
        sex = ui.radio(["Male", "Female", "Other"], value="Other")
        age = ui.input("Participant's Age")
        height = ui.input("Participant's Height [cm]")
        activity = ui.select(['Drunk', 'Sober', 'Soccer'])
        
        def submit():
            save_user_info(name.value, sex.value, age.value, height.value, activity.value)
            ui.notify("User Info Saved!", color="green")
            load_page(main_menu)
        
        ui.button("Save and Continue", on_click=submit)

def update_image():
    if state['index'] == 0:
        image.set_source(f'/images/{files[0]}')
    elif state['index'] == 1:
        image.set_source(f'/images/{files[1]}')
    elif state['index'] == 2:
        image.set_source(f'/images/{cognitive_files[state["cognitive_index"]]}')
    elif state['index'] == 3:
        image.set_source(f'/images/{files[2]}')

def next_image():
    if state['index'] == 1:
        state['index'] = 2
        state['cognitive_index'] = 0
    elif state['index'] == 2 and state['cognitive_index'] < len(cognitive_files) - 1:
        state['cognitive_index'] += 1
    elif state['index'] == 2 and state['cognitive_index'] == len(cognitive_files) - 1:
        state['index'] = 3
    update_image()

def main_menu():
    global image
    with ui.column():
        image = ui.image(f'/images/{files[1]}').style("width: 60vw;")
        ui.button("Next", on_click=next_image)

def cognitive_test():
    """Test 1: Stroop Test"""
    ui.label("Test 1: Stroop Test").classes("text-2xl font-bold")
    ui.image("assets/test1.png").classes("w-64 h-auto")  # Replace with actual image
    ui.label("Read the color, not the word!").classes("text-lg")

    ui.button("Next Test", on_click=lambda: load_page(test_2)).classes("text-lg")
    ui.button("Back to Main Menu", on_click=lambda: load_page(main_menu)).classes("text-lg")

# Add static file serving
app.add_static_files('/images', folder)

# Start with the opening screen
with content:
    opening_screen()

ui.run()
