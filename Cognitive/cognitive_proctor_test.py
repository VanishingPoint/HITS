#!/usr/bin/env python3
import csv
import random
from pathlib import Path
from nicegui import app, ui
from PIL import Image

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

# Example usage
cognitive_proctor(Path("responses.csv"))
