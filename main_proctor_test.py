import datetime
import csv
import random
from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments

# Set up the folder containing images
folder = Path(r"C:\Users\chane\Desktop\HITS\HITS\Main Menu Proctor Images")
files = sorted(f.name for f in folder.glob('menu_*.png'))
csv_file_path = None  # Global variable

# Set initial state for the current image index
state = {'index': 0}
responses = []  # Store responses
response_count = 0  # Track the number of responses

# Create a container to hold UI elements
content = ui.column()

def save_user_info(name, sex, age, height, activity, append=False):
    global csv_file_path  # Declare so that you can treat it as a global variable
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
        # Display the first image from the menu
        ui.image(f'/images/{files[0]}').classes("max-w-full w-full h-auto").style("width: 60vw; height: auto; max-width: 100%;")
        
        # Button to proceed to user information page
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
            state['index'] = 1  # Set index to 1 to show the next menu image (menu_1)
            load_page(main_menu)

        ui.button("Save and Continue", on_click=submit).classes("text-lg bg-blue-500 text-white p-2 rounded-lg")
        ui.button("Back to Main Menu", on_click=lambda: load_page(opening_screen)).classes("text-lg")


def update_image():
    image.set_source(f'/images/{files[state["index"]]}')
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


def previous_image():
    if state['index'] > 0:
        state['index'] -= 1
        update_image()


def main_menu():
    global image
    with ui.column():
        # Create or update the image component and apply the styling
        image = ui.image(f'/images/{files[state["index"]]}').classes("max-w-full w-full h-auto").style("width: 60vw; height: auto; max-width: 100%;")
        ui.button("Back", on_click=previous_image).classes('w-full sm:w-auto')
        ui.button("Next", on_click=next_image).classes('w-full sm:w-auto')

        # Button to start the cognitive test
        ui.button("Start Test", on_click=start_test).classes("text-lg bg-green-500 text-white p-2 rounded-lg")


def start_test():
    # Hide the Start Test button and show the cognitive test buttons
    ui.button("Start Test").visible = False
    ui.notify("Test Started!")

    # Start the cognitive test
    cognitive_proctor(csv_file_path)


def cognitive_proctor(csv_file_path: Path):
    # Define two state variables: one for the main menu, and one for the test.
    test_state = {'cognitive_index': 0, 'response_count': 0, 'responses': []}

    # Image path setup
    image_numbers = list(range(0, 17))  # Image 0 is explanation, others are answers
    image_folder = Path(r"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images")
    image_paths = [
        image_folder / f"cognitive_page_{num}.png"
        for num in image_numbers
    ]

    # Shuffle images excluding the first one
    shuffled_images = random.sample(image_paths[1:], len(image_paths) - 1)
    shuffled_images = [image_paths[0]] + shuffled_images  # Keep the first image fixed

    # Function to update the image in the test UI
    def update_test_image():
        image_path = f"/slides/{shuffled_images[test_state['cognitive_index']].name}"  # Serve from static files
        slide.set_source(image_path)

    # Create the UI with a scaling factor for the image
    slide = ui.image(f"/slides/{shuffled_images[test_state['cognitive_index']].name}").style('width: 70%; height: 70%')

    # Serve static files
    app.add_static_files('/slides', image_folder)  # Serve all files in this folder

    # Function to handle responses and move to the next image
    def handle_response(response):
        nonlocal test_state  # Access the test state
        image_number = test_state['cognitive_index']
        test_state['responses'].append((response, image_number))  # Log the response
        test_state['response_count'] += 1  # Increment the response counter
        print(f"Button {response} pressed for image {image_number}")
        
        # Save response to CSV
        save_responses(test_state)

        # Move to next image
        test_state['cognitive_index'] += 1
        if test_state['cogntive_index'] < len(shuffled_images):
            update_test_image()
        else:
            print("End of images.")
            ui.notify('End of images.')
            test_state['cognitive_index'] = 0  # Reset index for the next round

        # If 15 responses have been made, stop the app
        if test_state['response_count'] >= 15:
            print("15 responses reached. Exiting.")
            ui.notify('15 responses reached. Exiting.')
            app.stop()  # Stop the app

    # Show the "Yes" and "No" buttons for test responses
    button_yes = ui.button('Yes', on_click=lambda: handle_response('y')).style('position: absolute; top: 40%; left: 20%')
    button_yes.visible = True
    button_no = ui.button('No', on_click=lambda: handle_response('n')).style('position: absolute; top: 50%; left: 20%')
    button_no.visible = True

    # Show the "Next" button only for the first image, then handle it for the rest of the test
    button_next = ui.button('Next', on_click=handle_response).style('position: absolute; top: 80%; left: 70%')


def save_responses(test_state):
    # Save responses to CSV
    with open(csv_file_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        for response, image_num in test_state['responses']:
            writer.writerow([response, image_num])
    print("Responses saved to CSV.")


# Add static file serving
app.add_static_files('/images', folder)

# Start with the opening screen
with content:
    opening_screen()

ui.run()
