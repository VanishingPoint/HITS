import random
import csv
from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments

# Image path setup for main menu
menu_image_numbers = list(range(0, 6))  # Image 0 to 5 for main menu images
menu_image_folder = Path(r"C:/Users/chane/Desktop/HITS/HITS/Main Menu Proctor Images")  # Main menu images
menu_image_paths = [
    menu_image_folder / f"menu_{num}.png" for num in menu_image_numbers
]

# Image path setup for cognitive test
cognitive_image_numbers = list(range(0, 17))  # Image 0 is explanation, others are answers
cognitive_image_folder = Path(r"C:/Users/chane/Desktop/HITS/HITS/Cognitive/Cognitive Proctor Images")
cognitive_image_paths = [
    cognitive_image_folder / f"cognitive_page_{num}.png" for num in cognitive_image_numbers
]

# Shuffle cognitive test images
shuffled_cognitive_images = random.sample(cognitive_image_paths[1:], len(cognitive_image_paths) - 1)
shuffled_cognitive_images = [cognitive_image_paths[0]] + shuffled_cognitive_images  # Keep the first image fixed

# Global state
state = {'index': 0}
responses = []
response_count = 0  # Track the number of responses

# Function to save responses to CSV
def save_responses():
    with open('responses.csv', mode='w', newline='') as file:  # Open in write mode to overwrite the file
        writer = csv.writer(file)
        writer.writerow(['response', 'image_number'])  # Write header
        writer.writerows(responses)

# Function to update cognitive test image
def update_cognitive_image():
    image_path = f"slides/{shuffled_cognitive_images[state['index']].name}"
    cognitive_slide.set_source(image_path)

# Main menu function
def show_main_menu():
    # Display the first image from the menu
    menu_slide.set_source(f"menu/{menu_image_paths[0].name}")
    ui.button('Start Cognitive Test', on_click=start_cognitive_test).style('position: absolute; top: 70%; left: 40%')
    ui.button('Exit', on_click=exit_program).style('position: absolute; top: 80%; left: 40%')

# Start cognitive test function
def start_cognitive_test():
    global state
    state['index'] = 0  # Reset to first cognitive image
    update_cognitive_image()

    # Remove main menu and start cognitive test UI
    menu_slide.delete()
    ui.button('Yes', on_click=lambda: handle_response('y')).style('position: absolute; top: 40%; left: 20%')
    ui.button('No', on_click=lambda: handle_response('n')).style('position: absolute; top: 50%; left: 20%')

# Handle responses in cognitive test
def handle_response(response):
    global state, response_count
    image_number = state['index']
    responses.append((response, image_number))  # Log the response
    response_count += 1  # Increment the response counter
    print(f"Button {response} pressed for image {image_number}")
    
    # Save response to CSV
    save_responses()

    # Move to next image
    state['index'] += 1
    if state['index'] < len(shuffled_cognitive_images):
        update_cognitive_image()
    else:
        print("End of images.")
        ui.notify('End of images.')
        state['index'] = 0  # Reset index for the next round

    # If 15 responses have been made, stop the app
    if response_count >= 15:
        print("15 responses reached. Exiting.")
        ui.notify('15 responses reached. Exiting.')
        ui.app.stop()  # Stop the app

# Function to exit the program
def exit_program():
    print("Exiting program.")
    ui.app.stop()

# Function to handle keyboard events
def handle_key(event: KeyEventArguments) -> None:
    if event.action.keydown:
        if event.key == 'y':
            handle_response('y')
        elif event.key == 'n':
            handle_response('n')
        elif event.key == 'escape':
            exit_program()

# Keyboard event handling
ui.keyboard(on_key=handle_key)

# UI setup
menu_slide = ui.image(f"menu/{menu_image_paths[0].name}").style('width: 70%; height: 70%')  # Initial menu image
app.add_static_files('/menu', menu_image_folder)  # Serve menu images
app.add_static_files('/slides', cognitive_image_folder)  # Serve cognitive images

# Main UI flow
def run_test():
    show_main_menu()

# Run the test
run_test()