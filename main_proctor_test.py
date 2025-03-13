from pathlib import Path
import csv
from nicegui import app, ui
from nicegui.events import KeyEventArguments

# Set up the folder containing images
folder = Path(r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images")
files = sorted(f.name for f in folder.glob('menu_*.png'))

# Set initial state for the current image index
state = {'index': 0}

def save_user_info(name, sex, age, height, activity):
    filename = f"{name.replace(' ', '_')}.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Sex", "Age", "Height", "Activity"])
        writer.writerow([name, sex, age, height, activity])
    print(f"User Info Saved to {filename}")

def load_page(page_function):
    ui.remove_all()
    page_function()

def user_info():
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
        load_page(main_menu)  # Continue to main menu after saving

    ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")
    ui.button("Back to Main Menu", on_click=lambda: load_page(main_menu)).classes("text-lg")

def update_image():
    image.set_source(f'/images/{files[state["index"]]}')

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
    ui.remove_all()
    global image
    image = ui.image(f'/images/{files[state["index"]]}').classes("max-w-full").style("max-width: 500px; max-height: 500px;")
    ui.button("Back", on_click=previous_image).classes('w-full sm:w-auto')
    ui.button("Next", on_click=next_image).classes('w-full sm:w-auto')
    ui.keyboard(on_key=handle_key)

app.add_static_files('/images', folder)

# Start with user info page
user_info()

ui.run()
