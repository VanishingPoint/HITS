from PIL import Image
import os
import random
import time
import csv
import socket
#import pandas
from picamera2 import Picamera2, Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import serial
import cv2
import numpy as np

HOST = "100.120.18.53"  # Server's hostname or IP address
PORT = 65432  # Port used by the cognitive test server
csv_directory = "/home/hits/Documents/GitHub/HITS/csv_files"  # Folder to save CSV files
file_path = None

def handle_data(data):
    if user_data_received == False:
        response = record_user_data(data)
    elif user_data_received == True and cognitive_test_completed == False:
        response = cognitive_test(data)
    elif cognitive_test_completed == True and balance_test_completed == False:
        response = balance_test(data)
    elif cognitive_test_completed == True and balance_test_completed == True and eye_tracking_completed == False:
        response = eye_tracking_test(data) 
    else:
        print("All Tests Complete or Error")
    return response 
    
def append_cognitive_data(cognitive_data):
    """Append cognitive data to the existing user CSV file, starting at column G."""
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Add the cognitive data starting from column G
        writer.writerow(cognitive_data)

# Function to open and display an image
opened_image = None  # Initialize the variable at the global level

def show_image(image_path):
    global opened_image
    if opened_image:
        opened_image.close()  # Close the previous image if it exists
    opened_image = Image.open(image_path)
    opened_image.show()

def record_user_data(data):
    global file_path, user_data_received, sequence
    sequence, age, sex, height, drunk = data.split()

    # Generate the CSV filename based on the sequence number and save it in the csv_directory
    file_name = f"{sequence}.csv"
    file_name = file_name[:255].replace(":", "_").replace(" ", "_")
    file_path = os.path.join(csv_directory, file_name)  # Full path to the CSV file, since this is global it defines it everywhere

    # Ensure the directory exists
    os.makedirs(csv_directory, exist_ok=True)

    # Open file in append mode without checking size first
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if os.path.getsize(file_path) == 0:
            writer.writerow(["Sequence", "Age", "Sex", "Height", "Drunk", "Timestamp", "Image Number", "Color", "Word", "Response", "Time Taken"])
        log_data = [sequence, age, sex, height, drunk, time.time()]
        writer.writerow(log_data)

    user_data_received = True
    print("User Data Recorded")
    return("Data Saved")


# Function to handle client connections for the cognitive test
def cognitive_test(key):
    global cognitive_test_completed, cognitive_test_started, image_numbers, current_index, start_time

    if cognitive_test_started == False:
        image_numbers = list(range(1, 4))  # Assuming 16 images
        random.shuffle(image_numbers)

        #TODO: Show instructions to the participant here

        current_index = 0  # Tracks the current image index
        start_time = 0

    # Defining attributes for each image
    image_colour = {
        1: "blue", 2: "green", 3: "red", 4: "yellow", 5: "blue", 6: "green", 7: "red", 8: "yellow", 9: "blue", 10: "green", 
        11: "red", 12: "yellow", 13: "blue", 14: "green", 15: "red", 16: "yellow"}
    image_word = {
        1: "red", 2: "red", 3: "red", 4: "red", 5: "blue", 6: "blue", 7: "blue", 8: "blue", 9: "yellow", 10: "yellow", 
        11: "yellow", 12: "yellow", 13: "green", 14: "green", 15: "green", 16: "green"}

    # List of image paths based on shuffled numbers
    image_paths = [
        fr"/home/hits/Documents/GitHub/HITS/Cognitive/Cognitive Participant Images/page_{num}.png"
        for num in image_numbers
    ]

    end_time = time.time()
    time_taken = end_time - start_time

    if key == "s" and cognitive_test_started == False: 
        # Show the current image
        response = str(image_numbers[current_index])
        show_image(image_paths[current_index])
        start_time = time.time()  # Reset start time for the next image
        current_index += 1
        cognitive_test_started = True
    elif key in ["y", "n"]:
        if current_index < len(image_numbers):
            # Show next image
            response = str(image_numbers[current_index])
            show_image(image_paths[current_index])
            start_time = time.time()  # Reset start time for the next image
            current_index += 1
        else:
            # End the test when all images are shown
            cognitive_test_completed = True
            print("Test completed.")
            response = "end"
    elif key == "Exit":
        cognitive_test_completed = True
        return("Exited")
    else:
        print(f"Invalid key pressed: {key}")
        return "Invalid"
    
    if current_index != 1:
        print("Logging data")
        # Log the data after each keystroke and image
        image_num = image_numbers[current_index - 1]
        colour = image_colour[image_num]
        word = image_word[image_num]
        # Additional data logging here (cognitive data)
        cognitive_data = [0, 0, 0, 0, 0, 0, image_num, colour, word, key, time_taken]
        append_cognitive_data(cognitive_data)

        print("Finished logging")

    return(response)

def eye_tracking_recording(): #TODO: Set proper cropping, change encoding to increase frame rate

    cam1 = Picamera2(0)
    cam1.start_preview(Preview.QTGL, x=100,y=300,width=400,height=300)

    video_config1= cam1.create_video_configuration()
    cam1.configure(video_config1)

    encoder1 = H264Encoder(10000000)

    if eye_tracking_horizontal_completed == True:
        output1 = FfmpegOutput(video_path + f'{sequence}verticalcam1.mp4')
    else:
        output1 = FfmpegOutput(video_path + f'{sequence}horizontalcam1.mp4')

    cam2 = Picamera2(1)
    cam2.start_preview(Preview.QTGL, x=500,y=300,width=400,height=300)

    video_config2 = cam2.create_video_configuration()
    cam2.configure(video_config2)

    encoder2= H264Encoder(10000000)

    if eye_tracking_horizontal_completed == True:
        output2 = FfmpegOutput(video_path + f'{sequence}verticalcam2.mp4')
    else:
        output2 = FfmpegOutput(video_path + f'{sequence}horizontalcam2.mp4')

    cam1.start_recording(encoder1, output1)
    cam2.start_recording(encoder2, output2)

    time.sleep(10) #Set recording duration here, 10 seconds set for now

    cam2.stop_recording()
    cam1.stop_recording()

    cam1.stop_preview()
    cam2.stop_preview()

    cam2.stop()
    cam1.stop()

    #added this because it said the resource was busy the second time...
    cam2.close()
    cam1.close()

'''
EYE TRACKING VIDEO PROCESSING FUNCTIONS BELOW
'''

# Crop the image to maintain a specific aspect ratio (width:height) before resizing. 
def crop_to_aspect_ratio(image, width=640, height=480):
    
    # Calculate current aspect ratio
    current_height, current_width = image.shape[:2]
    desired_ratio = width / height
    current_ratio = current_width / current_height

    if current_ratio > desired_ratio:
        # Current image is too wide
        new_width = int(desired_ratio * current_height)
        offset = (current_width - new_width) // 2
        cropped_img = image[:, offset:offset+new_width]
    else:
        # Current image is too tall
        new_height = int(current_width / desired_ratio)
        offset = (current_height - new_height) // 2
        cropped_img = image[offset:offset+new_height, :]

    return cv2.resize(cropped_img, (width, height))

#apply thresholding to an image
def apply_binary_threshold(image, darkestPixelValue, addedThreshold):
    # Calculate the threshold as the sum of the two input values
    threshold = darkestPixelValue + addedThreshold
    # Apply the binary threshold
    _, thresholded_image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)
    
    return thresholded_image

#Finds a square area of dark pixels in the image
#@param I input image (converted to grayscale during search process)
#@return a point within the pupil region
def get_darkest_area(image):

    ignoreBounds = 20 #don't search the boundaries of the image for ignoreBounds pixels
    imageSkipSize = 10 #only check the darkness of a block for every Nth x and y pixel (sparse sampling)
    searchArea = 20 #the size of the block to search
    internalSkipSize = 5 #skip every Nth x and y pixel in the local search area (sparse sampling)
    
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    min_sum = float('inf')
    darkest_point = None

    # Loop over the image with spacing defined by imageSkipSize, ignoring the boundaries
    for y in range(ignoreBounds, gray.shape[0] - ignoreBounds, imageSkipSize):
        for x in range(ignoreBounds, gray.shape[1] - ignoreBounds, imageSkipSize):
            # Calculate sum of pixel values in the search area, skipping pixels based on internalSkipSize
            current_sum = np.int64(0)
            num_pixels = 0
            for dy in range(0, searchArea, internalSkipSize):
                if y + dy >= gray.shape[0]:
                    break
                for dx in range(0, searchArea, internalSkipSize):
                    if x + dx >= gray.shape[1]:
                        break
                    current_sum += gray[y + dy][x + dx]
                    num_pixels += 1

            # Update the darkest point if the current block is darker
            if current_sum < min_sum and num_pixels > 0:
                min_sum = current_sum
                darkest_point = (x + searchArea // 2, y + searchArea // 2)  # Center of the block

    return darkest_point

#mask all pixels outside a square defined by center and size
def mask_outside_square(image, center, size):
    x, y = center
    half_size = size // 2

    # Create a mask initialized to black
    mask = np.zeros_like(image)

    # Calculate the top-left corner of the square
    top_left_x = max(0, x - half_size)
    top_left_y = max(0, y - half_size)

    # Calculate the bottom-right corner of the square
    bottom_right_x = min(image.shape[1], x + half_size)
    bottom_right_y = min(image.shape[0], y + half_size)

    # Set the square area in the mask to white
    mask[top_left_y:bottom_right_y, top_left_x:bottom_right_x] = 255

    # Apply the mask to the image
    masked_image = cv2.bitwise_and(image, mask)

    return masked_image
   
def optimize_contours_by_angle(contours, image):
    if len(contours) < 1:
        return contours

    # Holds the candidate points
    all_contours = np.concatenate(contours[0], axis=0)

    # Set spacing based on size of contours
    spacing = int(len(all_contours)/25)  # Spacing between sampled points

    # Temporary array for result
    filtered_points = []
    
    # Calculate centroid of the original contours
    centroid = np.mean(all_contours, axis=0)
    
    # Create an image of the same size as the original image
    point_image = image.copy()
    
    skip = 0
    
    # Loop through each point in the all_contours array
    for i in range(0, len(all_contours), 1):
    
        # Get three points: current point, previous point, and next point
        current_point = all_contours[i]
        prev_point = all_contours[i - spacing] if i - spacing >= 0 else all_contours[-spacing]
        next_point = all_contours[i + spacing] if i + spacing < len(all_contours) else all_contours[spacing]
        
        # Calculate vectors between points
        vec1 = prev_point - current_point
        vec2 = next_point - current_point
        
        with np.errstate(invalid='ignore'):
            # Calculate angles between vectors
            angle = np.arccos(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

        
        # Calculate vector from current point to centroid
        vec_to_centroid = centroid - current_point
        
        # Check if angle is oriented towards centroid
        # Calculate the cosine of the desired angle threshold (e.g., 80 degrees)
        cos_threshold = np.cos(np.radians(60))  # Convert angle to radians
        
        if np.dot(vec_to_centroid, (vec1+vec2)/2) >= cos_threshold:
            filtered_points.append(current_point)
    
    return np.array(filtered_points, dtype=np.int32).reshape((-1, 1, 2))

#returns the largest contour that is not extremely long or tall
#contours is the list of contours, pixel_thresh is the max pixels to filter, and ratio_thresh is the max ratio
def filter_contours_by_area_and_return_largest(contours, pixel_thresh, ratio_thresh):
    max_area = 0
    largest_contour = None
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= pixel_thresh:
            x, y, w, h = cv2.boundingRect(contour)
            length = max(w, h)
            width = min(w, h)

            # Calculate the length-to-width ratio and width-to-length ratio
            length_to_width_ratio = length / width
            width_to_length_ratio = width / length

            # Pick the higher of the two ratios
            current_ratio = max(length_to_width_ratio, width_to_length_ratio)

            # Check if highest ratio is within the acceptable threshold
            if current_ratio <= ratio_thresh:
                # Update the largest contour if the current one is bigger
                if area > max_area:
                    max_area = area
                    largest_contour = contour

    # Return a list with only the largest contour, or an empty list if no contour was found
    if largest_contour is not None:
        return [largest_contour]
    else:
        return []

#Fits an ellipse to the optimized contours and draws it on the image.
def fit_and_draw_ellipses(image, optimized_contours, color):
    if len(optimized_contours) >= 5:
        # Ensure the data is in the correct shape (n, 1, 2) for cv2.fitEllipse
        contour = np.array(optimized_contours, dtype=np.int32).reshape((-1, 1, 2))

        # Fit ellipse
        ellipse = cv2.fitEllipse(contour)

        # Draw the ellipse
        cv2.ellipse(image, ellipse, color, 2)  # Draw with green color and thickness of 2

        return image
    else:
        print("Not enough points to fit an ellipse.")
        return image

#checks how many pixels in the contour fall under a slightly thickened ellipse
#also returns that number of pixels divided by the total pixels on the contour border
#assists with checking ellipse goodness    
def check_contour_pixels(contour, image_shape, debug_mode_on):
    # Check if the contour can be used to fit an ellipse (requires at least 5 points)
    if len(contour) < 5:
        return [0, 0]  # Not enough points to fit an ellipse
    
    # Create an empty mask for the contour
    contour_mask = np.zeros(image_shape, dtype=np.uint8)
    # Draw the contour on the mask, filling it
    cv2.drawContours(contour_mask, [contour], -1, (255), 1)
   
    # Fit an ellipse to the contour and create a mask for the ellipse
    ellipse_mask_thick = np.zeros(image_shape, dtype=np.uint8)
    ellipse_mask_thin = np.zeros(image_shape, dtype=np.uint8)
    ellipse = cv2.fitEllipse(contour)
    
    # Draw the ellipse with a specific thickness
    cv2.ellipse(ellipse_mask_thick, ellipse, (255), 10) #capture more for absolute
    cv2.ellipse(ellipse_mask_thin, ellipse, (255), 4) #capture fewer for ratio

    # Calculate the overlap of the contour mask and the thickened ellipse mask
    overlap_thick = cv2.bitwise_and(contour_mask, ellipse_mask_thick)
    overlap_thin = cv2.bitwise_and(contour_mask, ellipse_mask_thin)
    
    # Count the number of non-zero (white) pixels in the overlap
    absolute_pixel_total_thick = np.sum(overlap_thick > 0)#compute with thicker border
    absolute_pixel_total_thin = np.sum(overlap_thin > 0)#compute with thicker border
    
    # Compute the ratio of pixels under the ellipse to the total pixels on the contour border
    total_border_pixels = np.sum(contour_mask > 0)
    
    ratio_under_ellipse = absolute_pixel_total_thin / total_border_pixels if total_border_pixels > 0 else 0
    
    return [absolute_pixel_total_thick, ratio_under_ellipse, overlap_thin]

#outside of this method, select the ellipse with the highest percentage of pixels under the ellipse 
#TODO for efficiency, work with downscaled or cropped images
def check_ellipse_goodness(binary_image, contour, debug_mode_on):
    ellipse_goodness = [0,0,0] #covered pixels, edge straightness stdev, skewedness   
    # Check if the contour can be used to fit an ellipse (requires at least 5 points)
    if len(contour) < 5:
        print("length of contour was 0")
        return 0  # Not enough points to fit an ellipse
    
    # Fit an ellipse to the contour
    ellipse = cv2.fitEllipse(contour)
    
    # Create a mask with the same dimensions as the binary image, initialized to zero (black)
    mask = np.zeros_like(binary_image)
    
    # Draw the ellipse on the mask with white color (255)
    cv2.ellipse(mask, ellipse, (255), -1)
    
    # Calculate the number of pixels within the ellipse
    ellipse_area = np.sum(mask == 255)
    
    # Calculate the number of white pixels within the ellipse
    covered_pixels = np.sum((binary_image == 255) & (mask == 255))
    
    # Calculate the percentage of covered white pixels within the ellipse
    if ellipse_area == 0:
        print("area was 0")
        return ellipse_goodness  # Avoid division by zero if the ellipse area is somehow zero
    
    #percentage of covered pixels to number of pixels under area
    ellipse_goodness[0] = covered_pixels / ellipse_area
    
    #skew of the ellipse (less skewed is better?) - may not need this
    axes_lengths = ellipse[1]  # This is a tuple (minor_axis_length, major_axis_length)
    major_axis_length = axes_lengths[1]
    minor_axis_length = axes_lengths[0]
    ellipse_goodness[2] = min(ellipse[1][1]/ellipse[1][0], ellipse[1][0]/ellipse[1][1])
    
    return ellipse_goodness

def process_frames(thresholded_image_strict, thresholded_image_medium, thresholded_image_relaxed, frame, gray_frame, darkest_point, debug_mode_on, render_cv_window):
  
    final_rotated_rect = ((0,0),(0,0),0)

    image_array = [thresholded_image_relaxed, thresholded_image_medium, thresholded_image_strict] #holds images
    name_array = ["relaxed", "medium", "strict"] #for naming windows
    final_image = image_array[0] #holds return array
    final_contours = [] #holds final contours
    ellipse_reduced_contours = [] #holds an array of the best contour points from the fitting process
    goodness = 0 #goodness value for best ellipse
    best_array = 0 
    kernel_size = 5  # Size of the kernel (5x5)
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    gray_copy1 = gray_frame.copy()
    gray_copy2 = gray_frame.copy()
    gray_copy3 = gray_frame.copy()
    gray_copies = [gray_copy1, gray_copy2, gray_copy3]
    final_goodness = 0
    
    #iterate through binary images and see which fits the ellipse best
    for i in range(1,4):
        # Dilate the binary image
        dilated_image = cv2.dilate(image_array[i-1], kernel, iterations=2)#medium
        
        # Find contours
        contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Create an empty image to draw contours
        contour_img2 = np.zeros_like(dilated_image)
        reduced_contours = filter_contours_by_area_and_return_largest(contours, 1000, 3)

        if len(reduced_contours) > 0 and len(reduced_contours[0]) > 5:
            current_goodness = check_ellipse_goodness(dilated_image, reduced_contours[0], debug_mode_on)
            #gray_copy = gray_frame.copy()
            #cv2.drawContours(gray_copies[i-1], reduced_contours, -1, (255), 1)
            ellipse = cv2.fitEllipse(reduced_contours[0])
            if debug_mode_on: #show contours 
                cv2.imshow(name_array[i-1] + " threshold", gray_copies[i-1])
                
            #in total pixels, first element is pixel total, next is ratio
            total_pixels = check_contour_pixels(reduced_contours[0], dilated_image.shape, debug_mode_on)                 
            
            cv2.ellipse(gray_copies[i-1], ellipse, (255, 0, 0), 2)  # Draw with specified color and thickness of 2
            font = cv2.FONT_HERSHEY_SIMPLEX  # Font type
            
            final_goodness = current_goodness[0]*total_pixels[0]*total_pixels[0]*total_pixels[1]
            
            #show intermediary images with text output
            if debug_mode_on:
                cv2.putText(gray_copies[i-1], "%filled:     " + str(current_goodness[0])[:5] + " (percentage of filled contour pixels inside ellipse)", (10,30), font, .55, (255,255,255), 1) #%filled
                cv2.putText(gray_copies[i-1], "abs. pix:   " + str(total_pixels[0]) + " (total pixels under fit ellipse)", (10,50), font, .55, (255,255,255), 1    ) #abs pix
                cv2.putText(gray_copies[i-1], "pix ratio:  " + str(total_pixels[1]) + " (total pix under fit ellipse / contour border pix)", (10,70), font, .55, (255,255,255), 1    ) #abs pix
                cv2.putText(gray_copies[i-1], "final:     " + str(final_goodness) + " (filled*ratio)", (10,90), font, .55, (255,255,255), 1) #skewedness
                cv2.imshow(name_array[i-1] + " threshold", image_array[i-1])
                cv2.imshow(name_array[i-1], gray_copies[i-1])

        if final_goodness > 0 and final_goodness > goodness: 
            goodness = final_goodness
            ellipse_reduced_contours = total_pixels[2]
            best_image = image_array[i-1]
            final_contours = reduced_contours
            final_image = dilated_image
    
    #if debug_mode_on:
        #cv2.imshow("Reduced contours of best thresholded image", ellipse_reduced_contours)

    test_frame = frame.copy()
    
    final_contours = [optimize_contours_by_angle(final_contours, gray_frame)]
    
    if final_contours and not isinstance(final_contours[0], list) and len(final_contours[0] > 5):
        #cv2.drawContours(test_frame, final_contours, -1, (255, 255, 255), 1)
        ellipse = cv2.fitEllipse(final_contours[0])
        final_rotated_rect = ellipse
        cv2.ellipse(test_frame, ellipse, (55, 255, 0), 2)
        #cv2.circle(test_frame, darkest_point, 3, (255, 125, 125), -1)
        center_x, center_y = map(int, ellipse[0])
        cv2.circle(test_frame, (center_x, center_y), 3, (255, 255, 0), -1)

        # Display the center coordinates on the frame
        coord_text = f"Center: ({center_x}, {center_y})"
        cv2.putText(test_frame, coord_text, (10,390), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,90,30), 2)
        
        cv2.putText(test_frame, "SPACE = play/pause", (10,410), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,90,30), 2) #space
        cv2.putText(test_frame, "Q      = quit", (10,430), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,90,30), 2) #quit
        cv2.putText(test_frame, "D      = show debug", (10,450), cv2.FONT_HERSHEY_SIMPLEX, .55, (255,90,30), 2) #debug

    #if render_cv_window:
        #cv2.imshow('best_thresholded_image_contours_on_frame', test_frame)
    
    # Create an empty image to draw contours
    contour_img3 = np.zeros_like(image_array[i-1])
    
    if len(final_contours[0]) >= 5:
        contour = np.array(final_contours[0], dtype=np.int32).reshape((-1, 1, 2)) #format for cv2.fitEllipse
        ellipse = cv2.fitEllipse(contour) # Fit ellipse
        cv2.ellipse(gray_frame, ellipse, (255,255,255), 2)  # Draw with white color and thickness of 2

    #process_frames now returns a rotated rectangle for the ellipse for easy access
    return final_rotated_rect


# Finds the pupil in an individual frame and returns the center point
def process_frame(frame, timestamp, csv_writer):

    # Crop and resize frame
    frame = crop_to_aspect_ratio(frame)

    #find the darkest point
    darkest_point = get_darkest_area(frame)

    # Convert to grayscale to handle pixel value operations
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    darkest_pixel_value = gray_frame[darkest_point[1], darkest_point[0]]
    
    # apply thresholding operations at different levels
    # at least one should give us a good ellipse segment
    thresholded_image_strict = apply_binary_threshold(gray_frame, darkest_pixel_value, 5)#lite
    thresholded_image_strict = mask_outside_square(thresholded_image_strict, darkest_point, 250)

    thresholded_image_medium = apply_binary_threshold(gray_frame, darkest_pixel_value, 15)#medium
    thresholded_image_medium = mask_outside_square(thresholded_image_medium, darkest_point, 250)
    
    thresholded_image_relaxed = apply_binary_threshold(gray_frame, darkest_pixel_value, 25)#heavy
    thresholded_image_relaxed = mask_outside_square(thresholded_image_relaxed, darkest_point, 250)
    
    #take the three images thresholded at different levels and process them
    final_rotated_rect = process_frames(thresholded_image_strict, thresholded_image_medium, thresholded_image_relaxed, frame, gray_frame, darkest_point, False, False)

    if final_rotated_rect is not None and final_rotated_rect[1] != (0, 0):
        center_x, center_y = final_rotated_rect[0][0], final_rotated_rect[0][1]  # Keep as is without rounding
        csv_writer.writerow([timestamp, center_x, center_y])  # Writing the float values without rounding #TODO: Pad with zeros
    
    return final_rotated_rect


    # Finds the pupil in an individual frame and returns the center point
def process_frame(frame, timestamp, csv_writer):

    # Crop and resize frame
    frame = crop_to_aspect_ratio(frame)

    #find the darkest point
    darkest_point = get_darkest_area(frame)

    # Convert to grayscale to handle pixel value operations
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    darkest_pixel_value = gray_frame[darkest_point[1], darkest_point[0]]
    
    # apply thresholding operations at different levels
    # at least one should give us a good ellipse segment
    thresholded_image_strict = apply_binary_threshold(gray_frame, darkest_pixel_value, 5)#lite
    thresholded_image_strict = mask_outside_square(thresholded_image_strict, darkest_point, 250)

    thresholded_image_medium = apply_binary_threshold(gray_frame, darkest_pixel_value, 15)#medium
    thresholded_image_medium = mask_outside_square(thresholded_image_medium, darkest_point, 250)
    
    thresholded_image_relaxed = apply_binary_threshold(gray_frame, darkest_pixel_value, 25)#heavy
    thresholded_image_relaxed = mask_outside_square(thresholded_image_relaxed, darkest_point, 250)
    
    #take the three images thresholded at different levels and process them
    final_rotated_rect = process_frames(thresholded_image_strict, thresholded_image_medium, thresholded_image_relaxed, frame, gray_frame, darkest_point, False, False)

    if final_rotated_rect is not None and final_rotated_rect[1] != (0, 0):
        center_x, center_y = final_rotated_rect[0][0], final_rotated_rect[0][1]  # Keep as is without rounding
        csv_writer.writerow([timestamp, center_x, center_y])  # Writing the float values without rounding
    
    return final_rotated_rect

# Loads a video and finds the pupil in each frame
def process_video(video_path, input_method, csv_path):
    print("Starting video processing...")  # Indicate start

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
    out = cv2.VideoWriter('C:/Storage/Source Videos/output_video.mp4', fourcc, 60.0, (640, 480))  # Output video filename, codec, frame rate, and frame size #TODO: Change this path

    if input_method == 1:
        cap = cv2.VideoCapture(video_path)
    elif input_method == 2:
        cap = cv2.VideoCapture(00, cv2.CAP_DSHOW)  # Camera input
        cap.set(cv2.CAP_PROP_EXPOSURE, -5)
    else:
        print("Invalid video source.")
        return

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # Ensure the directory exists
    #os.makedirs(csv_path, exist_ok=True)
    
    # Define CSV filename in the specified directory
    #csv_filename = os.path.join(csv_dir, "pupil_tracking_data.csv") #TODO: Change this to write to the partipant file
    with open(csv_path, mode='a', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(["Timestamp", "Pupil_X", "Pupil_Y"]) #Will probably need to pad with zeros
    
        debug_mode_on = False
    
        temp_center = (0,0)

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            timestamp = cap.get(cv2.CAP_PROP_POS_MSEC)
            process_frame(frame, timestamp, csv_writer)

            # Crop and resize frame
            frame = crop_to_aspect_ratio(frame)

            #find the darkest point
            darkest_point = get_darkest_area(frame)

            #if debug_mode_on:
            #    darkest_image = frame.copy()
            #    cv2.circle(darkest_image, darkest_point, 10, (0, 0, 255), -1)
            #    cv2.imshow('Darkest image patch', darkest_image)

            # Convert to grayscale to handle pixel value operations
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            darkest_pixel_value = gray_frame[darkest_point[1], darkest_point[0]]
        
            # apply thresholding operations at different levels
            # at least one should give us a good ellipse segment
            thresholded_image_strict = apply_binary_threshold(gray_frame, darkest_pixel_value, 5)#lite
            thresholded_image_strict = mask_outside_square(thresholded_image_strict, darkest_point, 250)

            thresholded_image_medium = apply_binary_threshold(gray_frame, darkest_pixel_value, 15)#medium
            thresholded_image_medium = mask_outside_square(thresholded_image_medium, darkest_point, 250)
        
            thresholded_image_relaxed = apply_binary_threshold(gray_frame, darkest_pixel_value, 25)#heavy
            thresholded_image_relaxed = mask_outside_square(thresholded_image_relaxed, darkest_point, 250)
        
            #take the three images thresholded at different levels and process them
            pupil_rotated_rect = process_frames(thresholded_image_strict, thresholded_image_medium, thresholded_image_relaxed, frame, gray_frame, darkest_point, debug_mode_on, True)
        
            #key = cv2.waitKey(1) & 0xFF
        
            #if key == ord('d') and debug_mode_on == False:  # Press 'q' to start debug mode
                #debug_mode_on = True
            #elif key == ord('d') and debug_mode_on == True:
                #debug_mode_on = False
                #cv2.destroyAllWindows()
            #if key == ord('q'):  # Press 'q' to quit
                #out.release()
                #break   
            #elif key == ord(' '):  # Press spacebar to start/stop
                #while True:
                    #key = cv2.waitKey(1) & 0xFF
                    #if key == ord(' '):  # Press spacebar again to resume
                        #break
                    #elif key == ord('q'):  # Press 'q' to quit
                        #break

    cap.release()
    out.release()
    #cv2.destroyAllWindows()

    print("Video processing complete!")  # Indicate end

def eye_tracking_test(key):
    global eye_tracking_started, eye_tracking_completed, eye_tracking_horizontal_completed, eye_tracking_ready_to_process

    if eye_tracking_started == False:
        #1st show instructions, wait for key to proceed (have to go to main loop to detect)
        show_image('/home/hits/Documents/GitHub/HITS/Eye Tracking/Eye Tracking Participant Images/eyetracking_0.png')
        eye_tracking_started = True
        print("Eye Tracking Started, Waiting For S")
        print(eye_tracking_started, eye_tracking_horizontal_completed, eye_tracking_completed)
        return "Waiting to Start Eye Tracking"
    
    elif eye_tracking_started == True and key == 's' and eye_tracking_horizontal_completed == False:
        #Show Horizontal Image
        show_image('/home/hits/Documents/GitHub/HITS/Eye Tracking/Eye Tracking Participant Images/eyetracking_4.png')
        #Then show 1st image here
        eye_tracking_recording() #Record the first test (Figure out if we need to pass anything...)
        #TODO: Show the proctor something during this
        #Go back to instruction image
        show_image('/home/hits/Documents/GitHub/HITS/Eye Tracking/Eye Tracking Participant Images/eyetracking_0.png')
        #Now we should wait for the second test
        eye_tracking_horizontal_completed = True
        return "Waiting to start vertical test"
    
    elif eye_tracking_horizontal_completed == True and key == 's' and eye_tracking_ready_to_process == False:
        #Show Vertical Image
        show_image('/home/hits/Documents/GitHub/HITS/Eye Tracking/Eye Tracking Participant Images/eyetracking_5.png')
        #Then show 1st image here
        eye_tracking_recording() #Record the second test (Figure out if we need to pass anything...)
        #TODO: Show the proctor something during this
        #Show "You are done image"
        show_image('/home/hits/Documents/GitHub/HITS/Eye Tracking/Eye Tracking Participant Images/eyetracking_6.png')
        eye_tracking_ready_to_process = True
        return "Finished Vertical Test Videos, ready to process"
    
    elif eye_tracking_ready_to_process == True:
        #Process the videos
        #second parameter is 1 for video 2 for webcam
        process_video((video_path + (f"{sequence}verticalcam1.mp4")), 1, (csv_directory + f"/{sequence}.csv")) #Right now the video path and output dir are defined globally
        process_video((video_path + (f"{sequence}verticalcam2.mp4")), 1, (csv_directory + f"/{sequence}.csv")) #Right now the video path and output dir are defined globally
        process_video((video_path + (f"{sequence}horizontalcam1.mp4")), 1, (csv_directory + f"/{sequence}.csv")) #Right now the video path and output dir are defined globally
        process_video((video_path + (f"{sequence}horizontalcam2.mp4")), 1, (csv_directory + f"/{sequence}.csv")) #Right now the video path and output dir are defined globally
        eye_tracking_completed = True
        return "Eye Tracking Complete"
    
    else:
        print("Error in Eye Tracking")



def balance_test(data):
    global balance_test_started, balance_test_completed, balance_first_test_complete, ser
    
    if balance_test_started == False: 
        # Intial set up to establish connection with Arduino? 
        balance_test_started = True
        ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Adjust as necessary
        ser.reset_input_buffer()
        return "Waiting to start balance test"
    
    elif balance_test_started == True and data == 's' and balance_first_test_complete == False:
        ser.write(b's\n')
        print("Sent 'start' to Arduino for Trial 1")
        balance_first_test_complete = True
        # waits 2 minutes

    elif balance_test_started == True and data == 's' and balance_first_test_complete == True:
        ser.write(b's\n')
        print("Sent 'start' to Arduino for Trial 2")
        # waits 2 minutes
        balance_test_completed = True

    while True: # Should this be in each elif statement? 
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8').rstrip()
            print(f"Received from Arduino: {line}")
            try:
                # Try to convert the line to a float
                value = float(line)
                break
            except ValueError:
                # If conversion fails, continue waiting for a valid float
                continue
    
    balance_data = [0,0,0,0,0,0,0,0,0,0,0, value]
    #Value is the path length
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(balance_data)
    
    if balance_first_test_complete:
        return "Balance Trial 1 Completed"
    elif balance_test_completed:
        return eye_tracking_test('x') #Starts eye tracking which will then return "waiting to start eye tracking" which will end up being the response

response = None
user_data_received = False
cognitive_test_completed = False
cognitive_test_started = False
balance_test_completed = False
balance_test_started = False
balance_trial = 1
eye_tracking_started = False
eye_tracking_completed = False
eye_tracking_horizontal_completed = False
eye_tracking_ready_to_process = False
balance_first_test_complete = False
ser = None

#Defines where the eye tracking videos to be processed are, and where the results file should be made
video_path='/home/hits/Documents/GitHub/HITS/Eye_Tracking_Participant_Videos/'

#TODO: Choose a location for these, delete the videos once they have been processed, and instead of making a new CSV, append the data to the existing

# This cannot be in a function!!
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server listening on {HOST}:{PORT}")
    conn, addr = s.accept()
    with conn:
        while True:
            data = conn.recv(1024)
            print("received:", data.decode('utf-8'))
            response = handle_data(data.decode('utf-8'))
            print("sending", response)
            if not data:
                print("Disconnected from Pi")

            conn.sendall(response.encode('utf-8'))

