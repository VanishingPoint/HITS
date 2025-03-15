import datetime
import csv
from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments

# Set up the folder containing images
folder = Path(r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images")
files = sorted(f.name for f in folder.glob('menu_*.png'))

# Set initial state for the current image index
state = {'index': 0}

# Create a container to hold UI elements
content = ui.column()

def save_user_info(name, sex, age, height, activity, append=False):
    # Get the current date and time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # Create a filename with the name and timestamp
    filename = f"{name.replace(' ', '_')}_{timestamp}.csv"
    
    # Set the mode based on whether you're appending or writing
    mode = 'a' if append else 'w'
    
    with open(filename, mode=mode, newline='') as file:
        writer = csv.writer(file)
        if not append:  # Write headers only once
            writer.writerow(["Name", "Sex", "Age", "Height", "Activity"])
        writer.writerow([name, sex, age, height, activity])
    print(f"User Info Saved to {filename}")

def load_page(page_function):
    content.clear()
    with content:
        page_function()

def opening_screen():
    with ui.column():
        ui.image(f'/images/{files[0]}').classes("max-w-full w-full h-auto").style("width: 60vw; height: auto; max-width: 100%;")
        ui.button("Enter Participant's Information", on_click=lambda: load_page(user_info)).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")

def user_info():
    with ui.column():
        ui.label("Enter the Participant's Information").classes('text-2xl font-bold')
        name = ui.input("Participant's Full Name").classes("w-64")
        sex = ui.radio(["Male", "Female", "Other"], value="Other").classes("w-64")
        age = ui.input("Participant's Age").classes("w-64")
        height = ui.input("Participant's Height [cm]").classes("w-64")
        ui.label("Select the activity:").classes('text-lg')
        activity = ui.select(['Drunk', 'Sober', 'Soccer'], value=None)
        
        def submit():
            save_user_info(name.value, sex.value, age.value, height.value, activity.value)
            ui.notify("User Info Saved!", color="green")
            state['index'] = 1  # Skip menu_0 and go directly to the next image
            load_page(main_menu)

        ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")
        ui.button("Back to Main Menu", on_click=lambda: load_page(opening_screen)).classes("text-lg")

def update_image():
    image.set_source(f'/images/{files[state["index"]]}')
    # Ensure the image takes up 60% of the screen width every time it's updated
    image.style("width: 60vw; height: auto; max-width: 100%;")

def handle_key(event: KeyEventArguments) -> None:
    if event.action.keydown:
        if event.key.arrow_right:
            next_image()
        if event.key.arrow_left:
            previous_image()

def next_image():
    if state['index'] < len(files) - 1:
        state['index'] += 1
        update_image()
        trigger_test()

def previous_image():
    if state['index'] > 0:
        state['index'] -= 1
        update_image()
        trigger_test()

def trigger_test():
    if state['index'] == 1:
        run_test_1()
    elif state['index'] == 2:
        run_test_2()
    elif state['index'] == 3:
        run_test_3()
    elif state['index'] == 4:
        run_test_4()

def run_test_1():
    print("Running Test 1 (COGNITIVE)...")
    ui.label("Running Test 1").classes("text-center")

def run_test_2():
    print("Running Test 2...")
    ui.label("Running Test 2").classes("text-center")

def run_test_3():
    print("Running Test 3...")
    ui.label("Running Test 3").classes("text-center")

def run_test_4():
    print("Running Test 4...")
    ui.label("Running Test 4").classes("text-center")

def main_menu():
    global image
    with ui.column():
        # Create or update the image component and apply the styling
        image = ui.image(f'/images/{files[state["index"]]}').classes("max-w-full w-full h-auto").style("width: 60vw; height: auto; max-width: 100%;")
        ui.button("Back", on_click=previous_image).classes('w-full sm:w-auto')
        ui.button("Next", on_click=next_image).classes('w-full sm:w-auto')
        ui.keyboard(on_key=handle_key)

# Add static file serving
app.add_static_files('/images', folder)

# Start with the opening screen
with content:
    opening_screen()

ui.run()
