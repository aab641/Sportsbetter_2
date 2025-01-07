import os
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import (
    classification_report,
    accuracy_score,
    ConfusionMatrixDisplay,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)

# Paths to preprocessed data and saved models
preprocessed_directory = "preprocessed_PBP_data"
models_directory = "models"

def load_model(file_name):
    """Load a saved model."""
    import pickle
    file_path = os.path.join(models_directory, file_name)
    with open(file_path, "rb") as f:
        return pickle.load(f)

def evaluate_game_outcome_model():
    """Evaluate the Game Outcome Prediction model."""
    print("\nEvaluating Game Outcome Prediction Model...")
    model = load_model("game_outcome_model.pkl")
    data = pd.read_csv(os.path.join(preprocessed_directory, "game_outcome_data.csv"))

    # Prepare features and target
    data["outcome"] = data.apply(
        lambda row: 1 if row["home_points"] > row["away_points"] else (-1 if row["home_points"] < row["away_points"] else 0),
        axis=1,
    )
    X = data[["home_points", "away_points", "quarter"]]
    y = data["outcome"]

    # Predict and evaluate
    y_pred = model.predict(X)
    print(f"Accuracy: {accuracy_score(y, y_pred):.2f}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred))

    # Confusion Matrix
    ConfusionMatrixDisplay.from_predictions(y, y_pred)
    plt.title("Confusion Matrix: Game Outcome Prediction")
    plt.show()

def evaluate_next_play_model():
    """Evaluate the Next Play Prediction model."""
    print("\nEvaluating Next Play Type Prediction Model...")
    model = load_model("next_play_model.pkl")
    data = pd.read_csv(os.path.join(preprocessed_directory, "next_play_data.csv"))

    # Encode categorical columns
    from sklearn.preprocessing import LabelEncoder
    encoder = LabelEncoder()
    data["offense_encoded"] = encoder.fit_transform(data["offense"])
    data["defense_encoded"] = encoder.fit_transform(data["defense"])
    data["play_type_encoded"] = encoder.fit_transform(data["play_type"])

    # Prepare features and target
    X = data[["quarter", "yards_gained", "offense_encoded", "defense_encoded"]]
    y = data["play_type_encoded"]

    # Predict and evaluate
    y_pred = model.predict(X)
    print(f"Accuracy: {accuracy_score(y, y_pred):.2f}")
    print("\nClassification Report:")
    print(classification_report(y, y_pred))

    # Confusion Matrix
    ConfusionMatrixDisplay.from_predictions(y, y_pred)
    plt.title("Confusion Matrix: Next Play Type Prediction")
    plt.show()

def evaluate_drive_analysis_model():
    """Evaluate the Drive Analysis models."""
    print("\nEvaluating Drive Analysis Models...")
    model_class = load_model("drive_outcome_model.pkl")
    model_reg = load_model("drive_efficiency_model.pkl")
    data = pd.read_csv(os.path.join(preprocessed_directory, "drive_analysis_data.csv"))

    # Classification: Predict drive result
    classification_data = data.dropna(subset=["result", "quarter", "start_yardline", "end_yardline", "yards_gained"])
    classification_data["result_encoded"] = classification_data["result"].factorize()[0]
    X_class = classification_data[["quarter", "start_yardline", "end_yardline", "yards_gained"]]
    y_class = classification_data["result_encoded"]

    # Predict and evaluate classification
    y_pred_class = model_class.predict(X_class)
    print(f"Accuracy (Classification): {accuracy_score(y_class, y_pred_class):.2f}")
    print("\nClassification Report:")
    print(classification_report(y_class, y_pred_class))

    # Confusion Matrix
    ConfusionMatrixDisplay.from_predictions(y_class, y_pred_class)
    plt.title("Confusion Matrix: Drive Outcome Prediction")
    plt.show()

    # Regression: Predict yards gained
    regression_data = data.dropna(subset=["yards_gained", "quarter", "start_yardline", "end_yardline"])
    X_reg = regression_data[["quarter", "start_yardline", "end_yardline"]]
    y_reg = regression_data["yards_gained"]

    # Predict and evaluate regression
    y_pred_reg = model_reg.predict(X_reg)
    print(f"Mean Absolute Error (Regression): {mean_absolute_error(y_reg, y_pred_reg):.2f}")
    print(f"Root Mean Squared Error (Regression): {mean_squared_error(y_reg, y_pred_reg, squared=False):.2f}")
    print(f"R-square: {r2_score(y_reg, y_pred_reg):.2f}")

    # Residual Plot
    residuals = y_reg - y_pred_reg
    plt.scatter(y_reg, residuals)
    plt.axhline(0, color="red", linestyle="--")
    plt.xlabel("Observed Values")
    plt.ylabel("Residuals")
    plt.title("Residual Plot: Drive Efficiency Analysis")
    plt.show()

if __name__ == "__main__":
    # Ensure directories exist
    if not os.path.exists(preprocessed_directory):
        print(f"Error: Preprocessed directory '{preprocessed_directory}' not found.")
        exit(1)

    if not os.path.exists(models_directory):
        print(f"Error: Models directory '{models_directory}' not found.")
        exit(1)

    # Evaluate all models
    evaluate_game_outcome_model()
    evaluate_next_play_model()
    evaluate_drive_analysis_model()
    print("\nResults presented successfully.")
