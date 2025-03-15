#!/usr/bin/env python3
import csv
import random
from pathlib import Path
from nicegui import app, ui
from nicegui.events import KeyEventArguments
from PIL import Image

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

# Display the image and update the UI
def update_image():
    image_path = f"slides/{shuffled_images[state['index']].name}"
    slide.set_source(image_path)

# Create the UI with a scaling factor for the image (using style attribute)
slide = ui.image(f"slides/{shuffled_images[state['index']].name}").style('width: 70%; height: 70%')  # Scale to 70%

# Serve static files using ui.static_files
app.add_static_files('/slides', image_folder)  # Serve all files in this folder

# Positioning the buttons
button_y = ui.button('Yes', on_click=lambda: handle_response('y')).style('position: absolute; top: 40%; left: 20%')
button_n = ui.button('No', on_click=lambda: handle_response('n')).style('position: absolute; top: 50%; left: 20%')

# Different buttons for the first image
def handle_first_image_response(response):
    global state, response_count
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

# Function to handle responses and move to the next image
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

# Handle keyboard events
def handle_key(event: KeyEventArguments) -> None:
    if event.action.keydown:
        if event.key == 'y':
            handle_response('y')
        elif event.key == 'n':
            handle_response('n')
        elif event.key == 'escape':
            print("Exiting program.")
            app.stop()  # Stop the app

# Keyboard event handling
ui.keyboard(on_key=handle_key)

# Run the app
ui.run()
