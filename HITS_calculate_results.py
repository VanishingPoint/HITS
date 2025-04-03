import numpy as np
import pandas as pd  
import matplotlib.pyplot as plt  
import seaborn as sb

# Load CSV files
dataset = pd.read_csv(r'/home/hits/Documents/GitHub/HITS/csv_files/1.csv')

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

    average_gaze_points(r'C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data1.csv', r'C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data2.csv', r'C:\Users\richy\Documents\Git\HITS\csv files\averaged_gaze1.csv')
    average_gaze_points(r'C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data3.csv', r'C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data4.csv', r'C:\Users\richy\Documents\Git\HITS\csv files\averaged_gaze2.csv')
    
    average_gaze1 = pd.read_csv(r'C:\Users\richy\Documents\Git\HITS\csv files\averaged_gaze1.csv')
    average_gaze2 = pd.read_csv(r'C:\Users\richy\Documents\Git\HITS\csv files\averaged_gaze2.csv') 
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
    model_path = r"C:\Users\richy\Documents\Git\HITS\pkl files\gaze_model.pkl"
    test_data_paths = [r"C:\Users\richy\Documents\Git\HITS\csv files\healthy_data1.csv", r"C:\Users\richy\Documents\Git\HITS\csv files\healthy_data2.csv", r"C:\Users\richy\Documents\Git\HITS\csv files\healthy_data3.csv", r"C:\Users\richy\Documents\Git\HITS\csv files\healthy_data4.csv"]
    output_csvs = [r"C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data1.csv", r"C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data2.csv", r"C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data3.csv", r"C:\Users\richy\Documents\Git\HITS\csv files\final_gazepoint_data4.csv"]

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
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()

def predict_concussion_probability(model, scaler, csv_path, input_data):
    # Scale input data
    input_scaled = scaler.transform(input_data)
    
    # Predict probability
    probabilities = model.predict_proba(input_scaled)[0]
    prediction_value = round(probabilities[1] * 100)
    
    # Load dataset
    dataset = pd.read_csv(csv_path)
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)
    
    # Scale dataset
    sc = StandardScaler()
    X_train = sc.fit_transform(X_train)
    
    # SHAP Analysis
    explainer = shap.Explainer(model, X_train)
    shap_values_input = explainer(input_scaled)
    shap_values = shap_values_input[0].values
    
    # Convert SHAP values to percentages
    def shap_to_percentage(shap_values, baseline=50, max_shap_value=5):
        percentages = [(baseline + (shap_value / max_shap_value) * 50) for shap_value in shap_values]
        return [max(0, min(100, round(percentage))) for percentage in percentages]
    
    percentages = shap_to_percentage(shap_values)
    
    return prediction_value, percentages

if __name__ == "__main__":
    metrics_data = metrics_data(dataset)  # Assuming metrics_data is a list at this point
    
    # Convert the combined_metrics list into a 2D numpy array
    metrics_data = np.array([metrics_data])  # This will make it a 2D array with 1 row

    print(metrics_data)

    # Load the trained logistic regression model and scaler
    model_filename = r'C:\Users\richy\Documents\Git\HITS\pkl files\logistic_regression_model.pkl'  # Ensure you saved it during training
    scaler_filename = r'C:\Users\richy\Documents\Git\HITS\pkl files\scaler.pkl'  # Ensure you saved it during training
    csv_path = r'C:\Users\richy\Documents\Git\HITS\csv files\metric_data.csv'

    # Load the scaler
    scaler = pickle.load(open(scaler_filename, 'rb'))

    # Load the logistic regression model
    model = pickle.load(open(model_filename, 'rb'))

    # Get prediction
    prediction, percentages = predict_concussion_probability(model, scaler, csv_path, metrics_data)

    print(prediction)
    print(percentages)
