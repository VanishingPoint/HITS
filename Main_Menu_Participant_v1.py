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

import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk
import threading

import numpy as np
import pandas as pd  
import matplotlib.pyplot as plt  
import seaborn as sb

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
        # Load CSV files
        dataset = pd.read_csv(f'/home/hits/Documents/GitHub/HITS/csv_files/{sequence}.csv')

        metrics_data = metrics_data(dataset)  # Assuming metrics_data is a list at this point
    
        # Convert the combined_metrics list into a 2D numpy array
        metrics_data = np.array([metrics_data])  # This will make it a 2D array with 1 row

        print(metrics_data)

        # Load the trained logistic regression model and scaler
        model_filename = '/home/hits/Documents/GitHub/HITS/pkl files/logistic_regression_model.pkl'  # Ensure you saved it during training
        scaler_filename = '/home/hits/Documents/GitHub/HITS/pkl files/scaler.pkl'  # Ensure you saved it during training
        csv_path = '/home/hits/Documents/GitHub/HITS/csv files/metric_data.csv'

        # Load the scaler
        scaler = pickle.load(open(scaler_filename, 'rb'))

        # Load the logistic regression model
        model = pickle.load(open(model_filename, 'rb'))

        # Get prediction
        prediction = predict_concussion_probability(model, scaler, csv_path, metrics_data)

        print(prediction)
        
        image_a_path = "/home/hits/Documents/GitHub/HITS/Results images/concussed_result.png"  # Replace with your path to PNG A
        image_b_path = "/home/hits/Documents/GitHub/HITS/Results images/nonconcussed_result.png"  # Replace with your path to PNG B
        output_path = "/home/hits/Documents/GitHub/HITS/Results images/hits_result_probability.png"  # Path where you want to save the new image

        probability_hits_result(prediction, image_a_path, image_b_path, output_path)

        show_image("/home/hits/Documents/GitHub/HITS/Results images/hits_result_probability.png")

        print("All Tests Complete or Error")
    return response 
    
def append_cognitive_data(cognitive_data):
    """Append cognitive data to the existing user CSV file, starting at column G."""
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        # Add the cognitive data starting from column G
        writer.writerow(cognitive_data)

# ------------------------- Tkinter Setup -------------------------
root = tk.Tk()
root.title("Cognitive Test")
root.attributes('-fullscreen', True)  # Start full-screen

image_label = Label(root)
image_label.pack()

def show_image(image_path):
    """
    Open an image from the given path, resize it, and display it in the tkinter label.
    """
    image = Image.open(image_path)
    max_width, max_height = 800, 900  # Adjust as needed
    image.thumbnail((max_width, max_height))
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.image = photo  # Keep a reference to prevent garbage collection

# Bind Escape key to exit full-screen mode.
root.bind('<Escape>', lambda e: root.attributes('-fullscreen', False))

# ------------------------- Tkinter Setup -------------------------

def record_user_data(data):
    global file_path, user_data_received, sequence
    sequence, age, sex  = data.split()

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
            writer.writerow(["Sequence", "Age", "Sex", "Cognitive Response", "Cognitive Time Taken", "Balance Path Length EC above EO", "Eye Tracking Timestamp", "Pupil_X", "Pupil_Y"])
        log_data = [sequence, age, sex]
        writer.writerow(log_data)

    user_data_received = True
    print("User Data Recorded")
    return("Data Saved")

## ------- Functions for calculate results start --------- ##

# Load CSV files
dataset = pd.read_csv(f'/home/hits/Documents/GitHub/HITS/csv_files/{sequence}.csv')

## Metric Calculation functions ##

# Compute cognitive metric
def compute_cognitive_metrics(dataset):
    # Ensure the dataset contains the required columns
    if 'Cognitive Response' not in dataset or 'Cognitive Time Taken' not in dataset:
        raise ValueError("Dataset must contain 'Cognitive Response' and 'Cognitive Time Taken' columns")
    
    accuracy_values = []  # Create an empty list to store accuracy values

    for value in dataset['Cognitive Response']:  # Loop through each value in the column
        if value == 'y':  
            accuracy_values.append(100)  # If 'y', add 100 to the list
        elif value == 'n':  
            accuracy_values.append(0)  # If not 'y', add 0 to the list
    
    # Select only rows 1 to 3 
    filtered_data = dataset.iloc[1:4]
    
    # Compute mean response time for selected rows
    mean_response_time = filtered_data['Cognitive Time Taken'].mean() if not filtered_data.empty else 0
    
    # Compute accuracy, avoiding division by zero
    accuracy = sum(accuracy_values) / len(accuracy_values) if accuracy_values else 0
    
    return accuracy, mean_response_time

# Compute balance metric
def compute_balance_metrics(dataset):
    # Ensure the dataset contains the required columns
    if 'Balance Path Length EC above EO' not in dataset:
        raise ValueError("Dataset must contain 'Balance Path Length EC above EO' columns")

    # Select balance EC and EO path length
    EC_path_length = dataset['Balance Path Length EC above EO'].iloc[17]
    EO_path_length = dataset['Balance Path Length EC above EO'].iloc[18]

    return EC_path_length, EO_path_length

# Compute all metric
def metrics_data(dataset):
    accuracy, mean_response_time = compute_cognitive_metrics(dataset)
    EC_path_length, EO_path_length = compute_balance_metrics(dataset)

    calibration()


    average_gaze_points(f'/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}1.csv', f'/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}2.csv', f'/home/hits/Documents/Git/HITS/csv_files/averaged_gaze{sequence}1.csv')
    average_gaze_points(f'/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}3.csv', f'/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}4.csv', rf'/home/hits/Documents/Git/HITS/csv_files/averaged_gaze{sequence}2.csv')
    
    average_gaze1 = pd.read_csv(f'/home/hits/Documents/Git/HITS/csv_files/averaged_gaze{sequence}1.csv')
    average_gaze2 = pd.read_csv(f'/home/hits/Documents/Git/HITS/csv_files/averaged_gaze{sequence}2.csv') 
    new_time1, x_resampled1, y_resampled1 = resample_data(average_gaze1['Timestamp'], average_gaze1['Predicted_Screen_X'], average_gaze1['Predicted_Screen_Y'])
    new_time2, x_resampled2, y_resampled2 = resample_data(average_gaze2['Timestamp'], average_gaze2['Predicted_Screen_X'], average_gaze2['Predicted_Screen_Y'])

    # Assume x_resampled, y_resampled, and new_time are properly resampled
    segments1, classes1 = classify_velocity(x_resampled1, y_resampled1, new_time1, threshold=0.05, return_discrete=False)
    # Count fixations and saccades
    fixation_indices1 = np.where(classes1 == "Fixation")[0]
    # Print results
    num_fixation1 = len(fixation_indices1)
    # Assume x_resampled, y_resampled, and new_time are properly resampled
    segments2, classes2 = classify_velocity(x_resampled2, y_resampled2, new_time2, threshold=0.05, return_discrete=False)
    # Count fixations and saccades
    fixation_indices2 = np.where(classes2 == "Fixation")[0]
    # Print results
    num_fixation2 = len(fixation_indices2)

    left_avg_distance1 = calculate_left_fixation_distance(x_resampled1, y_resampled1, fixation_indices1)
    right_avg_distance1 = calculate_right_fixation_distance(x_resampled1, y_resampled1, fixation_indices1)
    target_average_distance1 = (right_avg_distance1 + left_avg_distance1) / 2

    left_avg_distance2 = calculate_left_fixation_distance(x_resampled2, y_resampled2, fixation_indices2)
    right_avg_distance2 = calculate_right_fixation_distance(x_resampled2, y_resampled2, fixation_indices2)
    target_average_distance2 = (right_avg_distance2 + left_avg_distance2) / 2

    sa_ratio1 = compute_saratio(classes1, x_resampled1, y_resampled1, new_time1, target_average_distance1)

    efficiency2 = compute_distance_to_vertical_line(x_resampled2, y_resampled2)

    combined_metrics = [EC_path_length, EO_path_length, accuracy, mean_response_time, num_fixation1, target_average_distance1, sa_ratio1, num_fixation2, target_average_distance2, efficiency2]
    return combined_metrics

## Calibration functions ##

import pickle

def load_model(filename="gaze_model.pkl"):
    """Load trained gaze model from pickle file."""
    with open(filename, "rb") as file:
        model_x, model_y = pickle.load(file)
    print(f"Model loaded from {filename}")
    return model_x, model_y

def predict_gaze(model_x, model_y, pupil_x, pupil_y):
    """Predict gaze point on screen from pupil coordinates."""
    screen_x = model_x.predict([[pupil_x, pupil_y]])[0]
    screen_y = model_y.predict([[pupil_x, pupil_y]])[0]
    return int(screen_x), int(screen_y)

def load_test_data(csv_path):
    """Load test dataset (pupil positions over time)."""
    df = pd.read_csv(csv_path)
    return df  # Returns full DataFrame (includes Time, Pupil_X, Pupil_Y)

def save_predictions(df, predictions, output_csv):
    """Save predicted gaze points to a new CSV file."""
    df[['Predicted_Screen_X', 'Predicted_Screen_Y']] = predictions
    df.to_csv(output_csv, index=False)
    print(f"Predictions saved to {output_csv}")

def calibration():
    model_path = "/home/hits/Documents/Git/HITS/csv_files/pkl files/gaze_model.pkl"
    test_data_paths = [f"/home/hits/Documents/Git/HITS/csv_files/{sequence}ha.csv", f"/home/hits/Documents/Git/HITS/csv_files/{sequence}hb.csv", f"/home/hits/Documents/Git/HITS/csv_files/{sequence}va.csv", f"/home/hits/Documents/Git/HITS/csv_files/{sequence}vb.csv"]
    output_csvs = [f"/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}1.csv", f"/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}2.csv", f"/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}3.csv", f"/home/hits/Documents/Git/HITS/csv_files/final_gazepoint_data{sequence}4.csv"]

    # Load trained model
    model_x, model_y = load_model(model_path)

    # Process each test dataset
    for test_data_path, output_csv in zip(test_data_paths, output_csvs):
        test_df = load_test_data(test_data_path)
        predictions = [predict_gaze(model_x, model_y, row['Pupil_X'], row['Pupil_Y']) for _, row in test_df.iterrows()]
        save_predictions(test_df, predictions, output_csv)

## Eye tracking functions ##

def average_gaze_points(file1, file2, output_file):
    # Read both CSV files
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    # Ensure both have the same length
    if len(df1) != len(df2):
        raise ValueError("CSV files must have the same number of rows.")
    
    # Compute the average of X and Y columns
    averaged_df = pd.DataFrame()
    averaged_df['Timestamp'] = (df1['Timestamp'] + df2['Timestamp']) / 2
    averaged_df['Predicted_Screen_X'] = (df1['Predicted_Screen_X'] + df2['Predicted_Screen_X']) / 2
    averaged_df['Predicted_Screen_Y'] = (df1['Predicted_Screen_Y'] + df2['Predicted_Screen_Y']) / 2
    
    # Save to a new CSV file
    averaged_df.to_csv(output_file, index=False)
    print(f"Averaged data saved to {output_file}")

from scipy.interpolate import interp1d

def resample_data(time, x, y):
    time_diffs = np.diff(time)
    print("Min interval:", np.min(time_diffs))
    print("Max interval:", np.max(time_diffs))
    print("Average interval:", np.mean(time_diffs))

    target_rate = 1 / np.mean(time_diffs)  # Calculate average sampling rate (Hz)

    # Create a new uniform time array
    new_time = np.arange(time.iloc[0], time.iloc[-1], 1 / target_rate)

    # Interpolate x and y values to match the new time array
    interp_x = interp1d(time, x, kind='linear', fill_value="extrapolate")
    interp_y = interp1d(time, y, kind='linear', fill_value="extrapolate")
    
    x_resampled = interp_x(new_time)
    y_resampled = interp_y(new_time)

    return new_time, x_resampled, y_resampled

# import libraries
import warnings

WARN_SFREQ = "\n\nIrregular sampling rate detected. This can lead to impaired "\
"performance with this classifier. Consider resampling your data to" \
"a fixed sampling rate. Setting sampling rate to average sampledifference."

WARN_CONT = "\n\nThe discrete_times array passed to continuous_to_discrete " \
"has the same length as the times array. Are you sure that your " \
"discrete_times and discrete_values are not already continuous? " \
"If they are, applying this function can lead to miscalculations."

def sfreq_to_times(gaze_array, sfreq, start_time=0):
    """Creates a times array from the sampling frequency (in Hertz).
    
    Parameters
    ----------
    gaze_array : array
        The gaze array (is required to infer the number of samples).
    sfreq : float
        The sampling frequency in Hz.
    start_time : float
        The time (in seconds) at which the first sample will start.
        Default = 0.
   
    Returns
    -------
    times : array of float
        A 1D-array representing the sampling times of the recording.
        """
    return np.arange(0, len(gaze_array) / sfreq, 1. / sfreq) + start_time

def continuous_to_discrete(times, indices, values):
    """Matches an array of discrete events to a continuous time series.
    Reverse function of `discrete_to_continuous`.
    
    Parameters
    ----------
    times : array of (float, int)
        A 1D-array representing the sampling times of the continuous 
        eyetracking recording.
    indices : array of int
        Array of length len(times) corresponding to the event index 
        of the discrete events mapped onto the sampling times.
    values : array
        Array of length len(times) corresponding to the event values
        or descriptions of the discrete events.
   
    Returns
    -------
    discrete_times : array of (float, int)
        A 1D-array representing discrete timepoints at which a specific
        event occurs.
    discrete_values : array
        A 1D-array containing the event description or values 
        corresponding to `discrete_times`. Is the same length as 
        `discrete_times`.
    """
    # check to prevent passing discrete array
    if any([len(times) != i for i in (len(indices), len(values))]):
        raise ValueError("Indices and values must have the " \
                         "same length as the times array.")
    
    # fill the discrete lists with events
    discrete_times = []
    discrete_values = []
    cur_idx = np.min(indices) - 1
    for time, idx, val in zip(times, indices, values):
        if idx > cur_idx:
            discrete_times.append(time)
            discrete_values.append(val)
        cur_idx = idx
    
    return discrete_times, discrete_values

def _get_time(x, time, warn_sfreq=False):
    """Process times argument to sfreq/times array"""
    # process time argument
    if hasattr(time, '__iter__'):
        # create sfreq from times array
        times = np.array(time)
        if warn_sfreq and (np.std(times[1:] - times[:-1]) > 1e-5):
            warnings.warn(WARN_SFREQ)
        sfreq = 1. / np.mean(times[1:] - times[:-1]) 
    else:
        # create times array from sfreq
        sfreq = time
        times = sfreq_to_times(x, sfreq)
    return times, sfreq

def classify_velocity(x, y, time, threshold=None, return_discrete=False):
    """I-VT velocity algorithm from Salvucci & Goldberg (2000).
    
    One of several algorithms proposed in Salvucci & Goldberg (2000),
    the I-VT algorithm classifies samples as saccades if their rate of
    change from a previous sample exceeds a certain threshold. I-VT 
    can separate between the following classes:
    ```
    Fixation, Saccade
    ```
    
    For reference see:
    
    ---
    Salvucci, D. D., & Goldberg, J. H. (2000). Identifying fixations 
    and saccades in eye-tracking protocols. In Proceedings of the 
    2000 symposium on Eye tracking research & applications (pp. 71-78).
    ---
    
    Parameters
    ----------
    x : array of float
        A 1D-array representing the x-axis of your gaze data.
    y : array of float
        A 1D-array representing the y-axis of your gaze data.
    time : float or array of float
        Either a 1D-array representing the sampling times of the gaze 
        arrays or a float/int that represents the sampling rate.
    threshold : float
        The maximally allowed velocity after which a sample should be 
        classified as "Saccade". Threshold can be interpreted as
        `gaze_units/s`, with `gaze_units` being the spatial unit of 
        your eyetracking data (e.g. pixels, cm, degrees). If `None`,
        `mad_velocity_thresh` is used to determine a threshold.
        Default=`None`.
    return_discrete : bool
        If True, returns the output in discrete format, if False, in
        continuous format (matching the gaze array). Default=False.
        
    Returns
    -------
    segments : array of (int, float)
        Either the event indices (continuous format) or the event 
        times (discrete format), indicating the start of a new segment.
    classes : array of str
        The predicted class corresponding to each element in `segments`.
        """
    # process time argument and calculate sample threshold
    times, sfreq = _get_time(x, time, warn_sfreq=True)
    
    # find threshold if threshold is None
    if threshold == None:
        threshold = mad_velocity_thresh(x, y, times)
    # express thresh in terms of freq
    sample_thresh = threshold / sfreq
    
    # calculate movement velocities
    gaze = np.stack([x, y])
    vels = np.linalg.norm(gaze[:, 1:] - gaze[:, :-1], axis=0)
    vels = np.concatenate([vels, [0.]])
    
    # define classes by threshold
    classes = np.empty(len(x), dtype=object)
    classes[:] = "Fixation"
    classes[vels > sample_thresh] = "Saccade"
    
    # group consecutive classes to one segment
    segments = np.zeros(len(x), dtype=int)
    for idx in range(1, len(classes)):
        if classes[idx] == classes[idx - 1]:
            segments[idx] = segments[idx - 1]
        else:
            segments[idx] = segments[idx - 1] + 1
    
    # return output
    if return_discrete:
        segments, classes = continuous_to_discrete(times, segments, classes)     
    return segments, classes

def mad_velocity_thresh(x, y, time, th_0=200, return_past_threshs=False):
    """Robust Saccade threshold estimation using median absolute deviation.
    
    Can be used to estimate a robust velocity threshold to use as threshold
    parameter in the `classify_velocity` algorithm.
    
    Implementation taken from [this gist] by Ashima Keshava.
    [this gist]: https://gist.github.com/ashimakeshava/ecec1dffd63e49149619d3a8f2c0031f
    
    For reference, see the paper:
    
    ---
    Voloh, B., Watson, M. R., König, S., & Womelsdorf, T. (2019). MAD 
    saccade: statistically robust saccade threshold estimation via the 
    median absolute deviation. Journal of Eye Movement Research, 12(8).
    ---
    
    Parameters
    ----------
    x : array of float
        A 1D-array representing the x-axis of your gaze data.
    y : array of float
        A 1D-array representing the y-axis of your gaze data.
    time : float or array of float
        Either a 1D-array representing the sampling times of the gaze 
        arrays or a float/int that represents the sampling rate.
    th_0 : float
        The initial threshold used at start. Threshold can be interpreted 
        as `gaze_units/s`, with `gaze_units` being the spatial unit of 
        your eyetracking data (e.g. pixels, cm, degrees). Defaults to 200.
    return_past_thresholds : bool
        Whether to additionally return a list of all thresholds used 
        during iteration. Defaults do False.
        
    Returns
    -------
    threshold : float
        The maximally allowed velocity after which a sample should be 
        classified as "Saccade". Threshold can be interpreted as
        `gaze_units/ms`, with `gaze_units` being the spatial unit of 
        your eyetracking data (e.g. pixels, cm, degrees).
    past_thresholds : list of float
        A list of all thresholds used during iteration. Only returned
        if `return_past_thresholds` is True.
        
    Example
    --------
    >>> threshold = mad_velocity_thresh(x, y, time)
    >>> segments, classes = classify_velocity(x, y, time, threshold)
    """
    # process time argument and calculate sample threshold
    times, sfreq = _get_time(x, time, warn_sfreq=True)
    # get init thresh per sample
    th_0 = th_0 / sfreq
    
    # calculate movement velocities
    gaze = np.stack([x, y])
    vels = np.linalg.norm(gaze[:, 1:] - gaze[:, :-1], axis=0)
    vels = np.concatenate([[0.], vels])
    
    # define saccade threshold by MAD
    threshs = []
    angular_vel = vels
    while True:
        threshs.append(th_0)
        angular_vel = angular_vel[angular_vel < th_0]
        median = np.median(angular_vel)
        diff = (angular_vel - median) ** 2
        diff = np.sqrt(diff)
        med_abs_deviation = np.median(diff)
        th_1 = median + 3 * 1.48 * med_abs_deviation
        # print(th_0, th_1)
        if (th_0 - th_1) > 1:
            th_0 = th_1
        else:
            saccade_thresh = th_1
            threshs.append(saccade_thresh)
            break
    
    # revert units
    saccade_thresh = saccade_thresh * sfreq
    threshs = [i * sfreq for i in threshs]
    
    if return_past_threshs:
        return saccade_thresh, threshs
    else:
        return saccade_thresh
    
def calculate_left_fixation_distance(x_resampled, y_resampled, fixation_indices, target_x=280, target_y=250):
    # Extract fixation points
    fixation_x = x_resampled[fixation_indices]
    fixation_y = y_resampled[fixation_indices]

    # Filter fixation points where x <= 500
    left_fixation_indices = fixation_x <= 500
    left_fixation_x = fixation_x[left_fixation_indices]
    left_fixation_y = fixation_y[left_fixation_indices]

    # Compute distances to the target point
    left_distances_to_target = np.sqrt((left_fixation_x - target_x) ** 2 + (left_fixation_y - target_y) ** 2)

    # Compute and return the average distance
    left_average_distance = np.mean(left_distances_to_target)
    return left_average_distance

def calculate_right_fixation_distance(x_resampled, y_resampled, fixation_indices, target_x=330, target_y=250):
    # Extract fixation points
    fixation_x = x_resampled[fixation_indices]
    fixation_y = y_resampled[fixation_indices]

    # Filter fixation points where x >= 500
    right_fixation_indices = fixation_x >= 500
    right_fixation_x = fixation_x[right_fixation_indices]
    right_fixation_y = fixation_y[right_fixation_indices]

    # Compute distances to the target point
    right_distances_to_target = np.sqrt((right_fixation_x - target_x) ** 2 + (right_fixation_y - target_y) ** 2)

    # Compute and return the average distance
    right_average_distance = np.mean(right_distances_to_target)
    return right_average_distance

def compute_saratio(classes, x_resampled, y_resampled, new_time, target_average_distance):
    # Extract saccadic indices
    saccade_indices = np.where(classes == "Saccade")[0]
    
    # List to store saccadic velocities
    saccadic_velocities = []

    # Loop through the saccades
    for i in range(len(saccade_indices) - 1):
        idx1, idx2 = saccade_indices[i], saccade_indices[i + 1]

        # Calculate displacement (distance between two points in gaze coordinates)
        delta_x = x_resampled[idx2] - x_resampled[idx1]
        delta_y = y_resampled[idx2] - y_resampled[idx1]
        delta_theta = np.sqrt(delta_x**2 + delta_y**2)

        # Calculate the time difference
        delta_t = new_time[idx2] - new_time[idx1]

        # Avoid division by zero
        if delta_t > 0:
            velocity = delta_theta / delta_t
            saccadic_velocities.append(velocity)

    # Compute mean saccadic velocity
    mean_saccadic_velocity = np.mean(saccadic_velocities) if saccadic_velocities else 0

    # Compute S/A Ratio
    sa_ratio = mean_saccadic_velocity / target_average_distance if target_average_distance > 0 else 0

    return sa_ratio

def compute_distance_to_vertical_line(x_resampled, y_resampled, target_x=250):
    # Calculate perpendicular distances to the vertical line (absolute x-difference)
    distances_to_line = np.abs(x_resampled - target_x)

    # Create a DataFrame with gaze points and their distances
    df_distances = pd.DataFrame({
        'Gaze X': x_resampled,
        'Gaze Y': y_resampled,
        'Distance to Line': distances_to_line
    })

    # Compute mean distance to the vertical line
    mean_distance_to_line = df_distances['Distance to Line'].mean()

    return mean_distance_to_line

## Model Functions ##

import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

def predict_concussion_probability(model, scaler, csv_path, input_data):
    # Scale input data
    input_scaled = scaler.transform(input_data)
    
    # Predict probability
    probabilities = model.predict_proba(input_scaled)[0]
    prediction_value = round(probabilities[1] * 100)
    
    return prediction_value

## ------- Functions for calculate results end --------- ##

## -------- Display Plot ----- ##

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from math import pi
import os

def plot_hits_result(values, save_path=None):
    """
    Generates a radar chart of the results for HITS.
    
    Args:
        values (list): A list of exactly 10 numerical values.
    
    Raises:
        ValueError: If the length of values is not 10.
    """
    if len(values) != 10:
        raise ValueError("Values list must contain exactly 10 elements.")
        
    categories = [
            'EC Path Length', 'EO Path Length', 'H. Fixation', 
            'H. Targeting', 'H. S/A Ratio', 'V. Targeting', 
            'V. S/A Ratio', 'V. Efficiency', 'Time', 'Accuracy'
    ]
    num_vars = len(categories)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # Completing the loop for a circular plot.
    values += values[:1]
    
    # Create the radar chart.
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    # Set transparent background
    fig.patch.set_alpha(0)  # Figure background.
    ax.set_facecolor('none')  # Axis background.
        
    # Define circular regions with different background colors.
    radii = [0, 50, 100]
    colors = ["red", "blue"]

    # Fill each circular layer.
    for i in range(len(radii) - 1):
        theta = np.linspace(0, 2 * np.pi, 100)
        ax.fill_between(theta, radii[i], radii[i+1], color=colors[i], alpha=0.25)
        
    # Plot radar chart values.
    ax.plot(angles, values, color='green', linewidth=2, label="Patient", zorder=3)
    ax.fill(angles, values, color='green', alpha=0.25, zorder=3)
        
    # Configure axis and labels.
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)

    # Change category label font size.
    ax.set_thetagrids(np.degrees(angles[:-1]), categories, fontsize=20)

    # Set all category label colors to white.
    for label in ax.get_xticklabels():
        label.set_color("white")  # Change text color to white.

    # Go through labels and adjust alignment based on where it is in the circle.
    for label, angle in zip(ax.get_xticklabels(), angles):
        if angle in (0, np.pi):
            label.set_horizontalalignment('center')
        elif 0 < angle < np.pi:
            label.set_horizontalalignment('left')
        else:
            label.set_horizontalalignment('right')

    # Set the radial limit (0-100).
    ax.set_ylim(0, 100)
    # Set position of y-labels to be in the middle.
    ax.set_rlabel_position(0 / num_vars)
    # Change the color of the tick labels.
    ax.tick_params(colors='black', axis='y', labelsize=8)
    # Change the color of the circular gridlines.
    ax.grid(color='grey')
    # Change the color of the outermost gridline (the spine).
    ax.spines['polar'].set_color('black')
    # Change the width of the outermost gridline (the spine).
    ax.spines['polar'].set_linewidth(2)
    # Change the background color inside the circle itself.
    ax.set_facecolor('white')
        
    # Add overlay pie chart to indicate different test types.
    sizes = [20, 60, 20]
    labels = ['Cognitive Function', 'Eye Tracking', 'Balance Test']
    ax2 = fig.add_subplot(111, label="pie axes", zorder=-1)
    ax2.pie(sizes, radius=1.305, autopct='%1.1f%%', startangle=108.5, labeldistance=1.05,
            wedgeprops={'edgecolor': 'black', 'linewidth': 2}, colors=['blue', 'red', 'yellow'])
    ax2.set(aspect="equal")
        
    # Draw section dividers.
    for angle in [np.pi / 4 + 0.15, np.pi * 3 / 2 - 0.01, -0.32]:
        ax.plot([angle, angle], [0, 100], color='black', linewidth=2)
        
    # Create and display legend.
    radar_line = mlines.Line2D([0], [0], color='green', label='Patient', linewidth=2)
    red_patch = mpatches.Patch(color='red', label='Concussed Zone', alpha=0.25)
    blue_patch = mpatches.Patch(color='blue', label='Non-Concussed Zone', alpha=0.25)
    handles = [radar_line, red_patch, blue_patch]
    # Add legend for radar plot.
    ax.legend(handles=handles, loc='upper left', bbox_to_anchor=(1.38, 0.83), fontsize=16)
    # Add legend for pie plot.
    plt.legend(labels=labels, loc='upper right', bbox_to_anchor=(2.05, 1.10), fontsize=16)

    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")

    # Show the plot.
    plt.show()

## -------- Display Plot ----- ##

## ----- Display Result Value ----- ##

import os
from PIL import Image, ImageDraw, ImageFont

def probability_hits_result(input_number, image_a_path, image_b_path, output_path):
    # Choose the image based on the input number
    if input_number >= 50:
        chosen_image_path = image_a_path
    else:
        chosen_image_path = image_b_path

    # Open the chosen image
    img = Image.open(chosen_image_path)
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Define the text to display
    text = f"{input_number}%"
    
    # Try to load a scalable font
    try:
        # Using the system font available on macOS (Helvetica)
        font = ImageFont.truetype("/Library/Fonts/Helvetica.ttc", 90)
    except IOError:
        print("Font file not found, using default font.")
        font = ImageFont.load_default(90)  # Fallback to default if the font is not found

    # Get text size using textbbox() (for calculating the size of the text)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Set a custom position (x, y) in pixels
    text_position = (270, 250)
    
    # Add text to image (white color)
    draw.text(text_position, text, fill="white", font=font)

    # Save the image to the specified output path
    img.save(output_path)
    print(f"Image saved to {output_path}")

## ----- Display Result Value ----- ##

## ----- Combine Results ---- ##

from PIL import Image

def hits_combined_result(base_image_path, overlay_image_path, output_path, position=(2550, 770)):
    # Open the base and overlay images
    base_image = Image.open(base_image_path).convert("RGBA")
    overlay_image = Image.open(overlay_image_path).convert("RGBA")
    
    # Create a new image for the result
    combined = Image.new("RGBA", base_image.size)
    
    scale_factor = 1.2

    # Resize overlay while maintaining aspect ratio
    overlay_width = int(overlay_image.width * scale_factor)
    overlay_height = int(overlay_image.height * scale_factor)
    overlay_image = overlay_image.resize((overlay_width, overlay_height), Image.LANCZOS)

    # Create a new image for the result
    combined = Image.new("RGBA", base_image.size)

    # Paste the base image first
    combined.paste(base_image, (0, 0))
    
    # Paste the overlay image on top, preserving transparency
    combined.paste(overlay_image, position, overlay_image)
    
    # Save the final image
    combined.save(output_path, format="PNG")
    print(f"Overlayed image saved as {output_path}")

## ----- Combine Results ---- ##

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
        fr"/home/hits/Documents/GitHub/HITS/Cognitive/Cognitive Participant Images/cognitive_participant_page_{num}.png"
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
        cognitive_data = [0, 0, 0, key, time_taken]
        append_cognitive_data(cognitive_data)

        print("Finished logging")

    return(response)

def eye_tracking_recording(): #TODO: Set proper cropping, change encoding to increase frame rate #NOTE: Commented out preview and stop preview for each camera. Uncomment for troubleshooting

    cam1 = Picamera2(0)
    #cam1.start_preview(Preview.QTGL, x=100,y=300,width=400,height=300)

    video_config1= cam1.create_video_configuration()
    cam1.configure(video_config1)

    encoder1 = H264Encoder(10000000)

    if eye_tracking_horizontal_completed == True:
        output1 = FfmpegOutput(video_path + f'{sequence}verticalcam1.mp4')
    else:
        output1 = FfmpegOutput(video_path + f'{sequence}horizontalcam1.mp4')

    cam2 = Picamera2(1)
    #cam2.start_preview(Preview.QTGL, x=500,y=300,width=400,height=300)

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

    #cam1.stop_preview()
    #cam2.stop_preview()

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
        #csv_writer.writerow([0, 0, 0, 0, 0, 0, timestamp, center_x, center_y])  # Writing the float values without rounding #TODO: Pad with zeros
        #NOTE: For single CSV operation uncomment above and remove below
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
        #csv_writer.writerow([0, 0, 0, 0, 0, 0, timestamp, center_x, center_y])  # Writing the float values without rounding
        #NOTE: For single CSV operation uncomment above and remove belo
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
        #csv_writer.writerow([0, 0, 0, 0, 0, 0, "Eye Tracking Timestamp", "Pupil_X", "Pupil_Y"]) #Will probably need to pad with zeros
        #NOTE: For single CSV operation uncomment above and remove below
        csv_writer.writerow(["Eye Tracking Timestamp", "Pupil_X", "Pupil_Y"])
    
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
        #NOTE: These will no longer write to the same CSV - modified by Triss at Richard's request. Can simply remove va/vb/ha/hb to return to prior behaviour
        process_video((video_path + (f"{sequence}verticalcam1.mp4")), 1, (csv_directory + f"/{sequence}va.csv")) #Right now the video path and output dir are defined globally
        process_video((video_path + (f"{sequence}verticalcam2.mp4")), 1, (csv_directory + f"/{sequence}vb.csv")) #Right now the video path and output dir are defined globally
        process_video((video_path + (f"{sequence}horizontalcam1.mp4")), 1, (csv_directory + f"/{sequence}ha.csv")) #Right now the video path and output dir are defined globally
        process_video((video_path + (f"{sequence}horizontalcam2.mp4")), 1, (csv_directory + f"/{sequence}hb.csv")) #Right now the video path and output dir are defined globally
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
    
    balance_data = [0,0,0,0,0,value]
    #Value is the path length
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(balance_data)
    
    if balance_first_test_complete == True and balance_test_completed == False:
        return "Balance Trial 1 Completed"
    elif balance_test_completed == True:
        return eye_tracking_test('x') #Starts eye tracking which will then return "waiting to start eye tracking" which will end up being the response
    else:
        print("Error in cases for balance")

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

# ------------------------- Socket Server Setup -------------------------
def client_thread(conn, addr):
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            data_str = data.decode('utf-8')
            print("Received:", data_str)
            response = handle_data(data_str)
            print("Sending:", response)
            conn.sendall(response.encode('utf-8'))

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=client_thread, args=(conn, addr), daemon=True).start()

# Start the socket server in a separate thread.
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# ------------------------- Mainloop -------------------------
root.mainloop()