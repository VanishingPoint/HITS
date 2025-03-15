import datetime
import csv
from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments

# Set up the folder containing images
folder = Path(r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images")
files = sorted(f.name for f in folder.glob('menu_*.png'))
csv_file_path = None # Global variable

# Set initial state for the current image index
state = {'index': 0}

# Create a container to hold UI elements
content = ui.column()

def save_user_info(name, sex, age, height, activity, append=False):
    # Set the folder where the CSV file should be saved
    global csv_file_path # Declare so that you can treat it as a global variable
    folder_path = Path(r"C:\Users\chane\Desktop\HITS\HITS\csv_files")
    
    # Ensure the folder exists
    folder_path.mkdir(parents=True, exist_ok=True)
    
    # Get the current date and time
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Create a filename with the name and timestamp
    csv_file_path = folder_path / f"{name.replace(' ', '_')}_{timestamp}.csv"
    
    # Set the mode based on whether you're appending or writing
    mode = 'a' if append else 'w'
    
    with open(csv_file_path, mode=mode, newline='') as file:
        writer = csv.writer(file)
        if not append:  # Write headers only once
            writer.writerow(["Name", "Sex", "Age", "Height", "Activity"])
        writer.writerow([name, sex, age, height, activity])
    print(f"User Info Saved to {csv_file_path}")


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
    cognitive_proctor(csv_file_path)
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

def cognitive_proctor(csv_file_path: Path):
    # Image path setup
    image_numbers = list(range(0, 17))  # image 0 is explanation, others are answers
    image_folder = Path(r"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images")
    image_paths = [
        image_folder / f"cognitive_page_{num}.png"
        for num in image_numbers
    ]

    # Shuffle images excluding the first one
    shuffled_images = random.sample(image_paths[1:], len(image_paths) - 1)
    shuffled_images = [image_paths[0]] + shuffled_images  # Keep the first image fixed

    # State to track progress
    state = {'index': 0}
    responses = []
    response_count = 0  # Track the number of responses

    # Function to save responses to CSV (save in columns F and G)
    def save_responses():
        with open(csv_file_path, mode='a', newline='') as file:  # Open in append mode to avoid overwriting
            writer = csv.writer(file)
            # If file is empty, write header in columns F and G
            if file.tell() == 0:
                writer.writerow(['response', 'image_number'])  # Header: 'response' in column F, 'image_number' in column G
            for response in responses:
                writer.writerow(response)  # Append each response and image number

    # Function to update the image in the UI
    def update_image():
        image_path = f"/slides/{shuffled_images[state['index']].name}"  # Serve from static files
        slide.set_source(image_path)

    # Create the UI with a scaling factor for the image
    slide = ui.image(f"/slides/{shuffled_images[state['index']].name}").style('width: 70%; height: 70%')

    # Serve static files
    app.add_static_files('/slides', image_folder)  # Serve all files in this folder

    # Function to handle responses and move to the next image
    def handle_response(response):
        nonlocal state, response_count
        image_number = state['index']
        responses.append((response, image_number))  # Log the response
        response_count += 1  # Increment the response counter
        print(f"Button {response} pressed for image {image_number}")
        
        # Save response to CSV
        save_responses()

        # Move to next image
        state['index'] += 1
        if state['index'] < len(shuffled_images):
            update_image()
        else:
            print("End of images.")
            ui.notify('End of images.')
            state['index'] = 0  # Reset index for the next round

        # If 15 responses have been made, stop the app
        if response_count >= 15:
            print("15 responses reached. Exiting.")
            ui.notify('15 responses reached. Exiting.')
            app.stop()  # Stop the app

    # Function to handle the "Next" button for the first image
    def handle_next():
        state['index'] += 1
        update_image()
        button_next.visible = False  # Hide the "Next" button after it's clicked
        button_yes.visible = True    # Show "Yes" and "No" buttons
        button_no.visible = True

    # Show the "Next" button only for the first image
    button_next = ui.button('Next', on_click=handle_next).style('position: absolute; top: 80%; left: 70%')

    # Show the "Yes" and "No" buttons only after the first image
    button_yes = ui.button('Yes', on_click=lambda: handle_response('y')).style('position: absolute; top: 40%; left: 20%')
    button_yes.visible = False
    button_no = ui.button('No', on_click=lambda: handle_response('n')).style('position: absolute; top: 50%; left: 20%')
    button_no.visible = False

    # Run the app
    ui.run()





# Add static file serving
app.add_static_files('/images', folder)

# Start with the opening screen
with content:
    opening_screen()

ui.run()
