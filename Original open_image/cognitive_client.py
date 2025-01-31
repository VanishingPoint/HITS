from PIL import Image
import keyboard
import os
import random
import time
import csv

# List of image numbers (shuffled for randomness)
image_numbers = list(range(1, 31))  # Assuming 30 images
random.shuffle(image_numbers)

# Defining attributes for each image
image_colour = {
    1: "blue", 2: "green", 3: "red", 4: "blue", 5: "green",  6: "green",  7: "blue", 8: "yellow", 9: "red", 10: "green", 
    11: "red", 12: "yellow", 13: "green", 14: "blue", 15: "blue", 16: "yellow", 17: "blue", 18: "green", 19: "red", 20: "yellow", 
    21: "yellow", 22: "red", 23: "red", 24: "yellow", 25: "blue", 26: "blue", 27: "green", 28: "blue", 29: "red", 30: "yellow"}
image_word = {
    1: "red", 2: "green", 3: "blue", 4: "yellow", 5: "blue", 6: "red", 7: "blue", 8: "red", 9: "yellow", 10: "red", 
    11: "green", 12: "yellow", 13: "yellow", 14: "green", 15: "red", 16: "blue", 17: "yellow", 18: "green", 19: "blue", 20: "yellow", 
    21: "green", 22: "green", 23: "red", 24: "blue", 25: "green", 26: "blue", 27: "blue", 28: "yellow", 29: "blue", 30: "red"}

current_index = 0  # Tracks the current image index
opened_image = None  # Keeps reference to the currently open PIL Image object
data = []  # To store keypress data
start_time = time.time()  # Start timing

print("Press 's' to start the randomized image sequence.")
print("Press 'y' or 'n' to open the next image after starting.")
print("Press 'esc' to exit the program.")

# Wait for the user to press 's' to start the program
while not keyboard.is_pressed("s"):
    pass
keyboard.wait("s")  # Wait for the key release

#TODO: Send keypress to server then wait for response

print("Starting the randomized image sequence...")

# Function to handle key presses
def process_keypress(key):
    global current_index, start_time
    elapsed_time = time.time() - start_time
    page_number = image_numbers[current_index]  # Get the current page number
    attribute1 = image_colour.get(page_number, "unknown")  # Get attributes or default to 'unknown'
    attribute2 = image_word.get(page_number, "unknown")  # Get attributes or default to 'unknown'
    data.append([current_index + 1, f"page_{page_number}", attribute1, attribute2, key, elapsed_time])
    print(f"'{key}' pressed for image {current_index + 1}. Time: {elapsed_time:.2f} seconds. Attributes: {attribute1}.")

#TODO: Modify the above to send the keypress to the server and get a response

    current_index += 1
    if current_index < len(image_paths):
        show_image(image_paths[current_index])
    else:
        print("No more images to display. Exiting program.")
        return False

    start_time = time.time()  # Reset the start time for the next image
    return True

# Start showing images
try:
    show_image(image_paths[current_index])
    while current_index < len(image_paths):
        if keyboard.is_pressed("y"):  # If 'y' is pressed
            keyboard.wait("y")  # Wait for the key release
            if not process_keypress("y"):
                break

        elif keyboard.is_pressed("n"):  # If 'n' is pressed
            keyboard.wait("n")  # Wait for the key release
            if not process_keypress("n"):
                break

        elif keyboard.is_pressed("esc"):  # Exit the program if 'esc' is pressed
            print("Exiting program.")
            break

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # Clean up
    if opened_image:
        opened_image.close()
    # Save data to a CSV file
    output_file = "keypress_data_with_attributes.csv"
    with open(output_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Image Index", "Image Opened", "Colour", "Word", "Key Pressed", "Elapsed Time (seconds)"])
        writer.writerows(data)
    print(f"Key press data saved to {output_file}.")
    print("Program finished.")
