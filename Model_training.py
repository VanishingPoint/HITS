import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import shap
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score

def load_dataset(file_path):
    """Loads dataset from a CSV file."""
    dataset = pd.read_csv(file_path)
    X = dataset.iloc[:, :-1].values
    y = dataset.iloc[:, -1].values
    return X, y

def preprocess_data(X, y, test_size=0.2, random_state=0):
    """Splits and scales the dataset."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler

def train_model(X_train, y_train):
    """Trains a logistic regression model."""
    model = LogisticRegression()
    model.fit(X_train, y_train)
    return model

def evaluate_model(model, X_test, y_test):
    """Evaluates the trained model."""
    y_pred = model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred) * 100
    print("Confusion Matrix:\n", cm)
    print(f"Model Accuracy: {accuracy:.2f}%")
    return accuracy

def predict_manual_input(model, scaler, input_values):
    """Predicts health status using manual input values."""
    manual_input = np.array([input_values])
    manual_input_scaled = scaler.transform(manual_input)
    probabilities = model.predict_proba(manual_input_scaled)[0]
    print(f"Healthy: {probabilities[1] * 100:.2f}%, Concussed: {probabilities[0] * 100:.2f}%")
    return probabilities

def explain_shap(model, X_train, input_values, scaler):
    """Generates SHAP values for feature importance explanation."""
    explainer = shap.Explainer(model, X_train)
    input_scaled = scaler.transform(np.array([input_values]))
    shap_values_input = explainer(input_scaled)
    shap_values = shap_values_input[0].values
    for i, value in enumerate(shap_values):
        print(f"Feature {i}: SHAP value = {value:.4f}")
    return shap_values

def shap_to_percentage(shap_values, baseline=50, max_shap_value=5):
    """Converts SHAP values into percentage scores."""
    percentages = [(baseline + (shap_value / max_shap_value) * 50) for shap_value in shap_values]
    return [max(0, min(100, round(p))) for p in percentages]

def save_model(model, scaler, model_filename=r'C:\Users\richy\Documents\Git\HITS\pkl files\logistic_regression_model.pkl', scaler_filename=r'C:\Users\richy\Documents\Git\HITS\pkl files\scaler.pkl'):
    """Saves the trained model and scaler."""
    pickle.dump(model, open(model_filename, 'wb'))
    pickle.dump(scaler, open(scaler_filename, 'wb'))
    print("Model and scaler saved successfully.")

# Main execution
if __name__ == "__main__":
    X, y = load_dataset(r'C:\Users\richy\Documents\Git\HITS\csv files\metric_data.csv')
    X_train, X_test, y_train, y_test, scaler = preprocess_data(X, y)
    model = train_model(X_train, y_train)
    evaluate_model(model, X_test, y_test)
    
    # Manual input prediction
    manual_input_values = [4, 15, 23, 35, 42, 58, 69, 71, 91, 101]
    predict_manual_input(model, scaler, manual_input_values)
    
    # SHAP explanation
    shap_values = explain_shap(model, X_train, manual_input_values, scaler)
    percentages = shap_to_percentage(shap_values)
    print("SHAP Percentages:", percentages)
    
    # Save model
    save_model(model, scaler)
