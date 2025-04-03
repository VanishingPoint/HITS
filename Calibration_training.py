import pandas as pd
import pickle
from sklearn.linear_model import LinearRegression

def train_gaze_model(pupil_data, screen_data):
    """Train regression models using pupil center coordinates."""
    model_x = LinearRegression()
    model_y = LinearRegression()

    model_x.fit(pupil_data, screen_data[:, 0])
    model_y.fit(pupil_data, screen_data[:, 1])

    return model_x, model_y

def save_model(model_x, model_y, filename="gaze_model.pkl"):
    """Save trained models to a pickle file."""
    with open(filename, "wb") as file:
        pickle.dump((model_x, model_y), file)
    print(f"Model saved as {filename}")

def load_pupil_data(csv_path):
    """Load pupil center dataset from CSV."""
    df = pd.read_csv(csv_path)
    pupil_data = df[['Pupil_X', 'Pupil_Y']].values
    screen_data = df[['Screen_X', 'Screen_Y']].values
    return pupil_data, screen_data

def main():
    calibration_data_path = r"C:\Users\richy\Documents\Git\HITS\csv files\initial_gazepoint_data.csv"
    model_output_path = r"C:\Users\richy\Documents\Git\HITS\pkl files\gaze_model.pkl"

    # Load and train model
    pupil_data, screen_data = load_pupil_data(calibration_data_path)
    model_x, model_y = train_gaze_model(pupil_data, screen_data)

    # Save trained model
    save_model(model_x, model_y, model_output_path)

if __name__ == "__main__":
    main()