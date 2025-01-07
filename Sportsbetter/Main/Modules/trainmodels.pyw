import os
import sys
import argparse
import shutil
import joblib
from sklearn.metrics import confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, accuracy_score, recall_score
import pandas as pd

# Common preprocessing function for both training and evaluation
def common_preprocessing(df, target_column):
    """
    Common preprocessing for both training and evaluation.
    - Handles missing values in numeric and categorical columns.
    - Drops unnecessary target columns.
    
    Parameters:
        df (DataFrame): The input dataframe to preprocess.
        target_column (str): The target column to extract.
    
    Returns:
        X (DataFrame): The feature matrix after preprocessing.
        y (Series): The target vector after preprocessing.
    """
    # Extract the target variable (y)
    if target_column in df.columns:
        y = df[target_column]
    else:
        y = None
        print(f"Warning: {target_column} not found in the data.")
    
    # Drop target columns from the feature set (X)
    X = df.drop(columns=["punt_next_drive", "punt_in_exactly_two_drives", "is_latest_play"], errors="ignore")
    
    # Handle missing values:
    # Replace NaN values in numeric columns with the column's mean
    numeric_cols = X.select_dtypes(include=["float64", "int64"]).columns
    X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].mean())

    # Replace NaN in categorical columns with a placeholder string
    categorical_cols = X.select_dtypes(include=["object"]).columns
    for col in categorical_cols:
        X[col] = X[col].fillna("unknown").astype(str)
        X[col] = pd.factorize(X[col])[0]

    # Ensure that X is not empty and has the correct shape
    if X.isnull().sum().sum() > 0:
        print(f"Warning: Data still contains missing values after preprocessing.")
    
    # Check if X is a valid 2D array (in case of a single feature)
    if X.ndim == 1:
        X = X.reshape(-1, 1)

    return X, y


def preprocess_data_train(input_directory, target_column):
    """
    Prepares data for training by processing a directory of files.
    """
    data_frames = []
    target_values = []  # Store target variable (y) values

    # Loop over files in the directory
    for file_name in os.listdir(input_directory):
        if file_name.endswith(".csv"):  # Ensure we're processing CSV files
            file_path = os.path.join(input_directory, file_name)
            print(f"Processing training file: {file_path}")
            try:
                df = pd.read_csv(file_path)
                X, y = common_preprocessing(df, target_column)  # Use common preprocessing
                data_frames.append(X)  # Append processed features
                target_values.append(y)  # Append target variable (y)
            except Exception as e:
                print(f"Error processing {file_name}: {e}")

    if not data_frames:
        print(f"Warning: No valid CSV files found in {input_directory}.")
        return None, None

    # Concatenate the data frames into one for training
    X_combined = pd.concat(data_frames, ignore_index=True)

    # Ensure that `y` values are properly concatenated
    y_combined = pd.concat(target_values, ignore_index=True)

    return X_combined, y_combined


def preprocess_data_evaluate(input_file, target_column):
    """
    Prepares data for evaluation by processing a single file.
    """
    try:
        df = pd.read_csv(input_file)
        X, y = common_preprocessing(df, target_column)  # Use common preprocessing
    except Exception as e:
        print(f"Error processing {input_file}: {e}")
        return None, None, None

    return X, y, input_file

def train_model(input_directory, model_output_path, target_column, output_file, cv_folds=5):
    """
    Trains a machine learning model using K-fold cross-validation for a folder of input files.
    """
    # Preprocess the data (input directory) for training
    X, y = preprocess_data_train(input_directory, target_column)

    if X is None or y is None:
        print(f"Error: Unable to preprocess data from {input_directory}. Skipping.")
        return

    # Initialize the RandomForest model
    model = RandomForestClassifier()

    # K-fold cross-validation
    kfold = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42)
    
    cv_scores = cross_val_score(model, X, y, cv=kfold, scoring='accuracy')

    avg_accuracy = cv_scores.mean()
    print(f"Average Cross-Validation Accuracy: {avg_accuracy * 100:.2f}%")

    # Train the model on the full dataset
    model.fit(X, y)

    # Save the trained model
    joblib.dump(model, model_output_path)
    print(f"Model saved to {model_output_path}")

    # Evaluate the model on the same dataset
    y_pred = model.predict(X)

    # Generate the classification report
    report = classification_report(y, y_pred, output_dict=True)
    accuracy = accuracy_score(y, y_pred)
    recall = recall_score(y, y_pred, average="weighted")

    # Prepare the results
    results = {
        "Accuracy": [f"{accuracy * 100:.2f}%"],
        "Recall": [f"{recall * 100:.2f}%"],
    }
    results.update({f"Class_{key}": [f"{value['f1-score'] * 100:.2f}%"] for key, value in report.items() if key.isdigit()})

    # Save the results to a CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, index=False)
    print(f"Training statistics saved to {output_file}")

    # Extract feature importance from the trained model
    feature_importance = model.feature_importances_

    # Create a DataFrame with the features and their importance
    feature_names = X.columns
    importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': [f"{imp * 100:.2f}%" for imp in feature_importance]  # Convert to percentage with 2 decimal places
    })

    # Get model name from the model output path (e.g., remove '.pkl' extension)
    model_name = os.path.basename(model_output_path).replace('.pkl', '')

    # Save the feature importance DataFrame to a CSV file with model name
    feature_importance_file = os.path.join(os.path.dirname(output_file), f'{model_name}_feature_importance.csv')
    importance_df.to_csv(feature_importance_file, index=False)
    print(f"Feature importances saved to {feature_importance_file}")


def evaluate_model(input_file, model_path, target_column, evaluation_output_file, mapped_output_file, confusion_matrix_output_file, cleaned_features_directory):
    """
    Evaluates a pre-trained model using the specified dataset and maps predictions to the original cleaned features.

    Parameters:
        input_file (str): The file to evaluate the model on.
        model_path (str): Path to the pre-trained model.
        target_column (str): The target column for evaluation.
        evaluation_output_file (str): File path to save evaluation results.
        mapped_output_file (str): File path to save predictions mapped to cleaned features.
        confusion_matrix_output_file (str): File path to save confusion matrix.
        cleaned_features_directory (str): Directory containing cleaned feature files.

    Returns:
        None
    """
    print(f"Evaluating model on file: {input_file}")

    X, y, filename = preprocess_data_evaluate(input_file, target_column)

    if not os.path.exists(model_path):
        print(f"Model file {model_path} does not exist. Evaluation cannot proceed.")
        return

    model = joblib.load(model_path)
    y_pred = model.predict(X)

    # Generate confusion matrix
    conf_matrix = confusion_matrix(y, y_pred, labels=[0, 1])

    # Extract True Positives (TP) and True Negatives (TN) from confusion matrix
    tp = conf_matrix[1][1]  # True Positives
    tn = conf_matrix[0][0]  # True Negatives
    fp = conf_matrix[0][1]  # False Positives
    fn = conf_matrix[1][0]  # False Negatives

    # Accuracy calculation
    accuracy = (tp + tn) / (tp + tn + fp + fn)

    # Save accuracy results
    results = {
        "Accuracy": [f"{accuracy * 100:.2f}%"],
    }
    results_df = pd.DataFrame(results)
    game_id = os.path.basename(filename).split('_')[0]  # Extract game-id from filename

    # Extract model name from the path to append to filenames
    model_name = os.path.basename(model_path).replace('.pkl', '')  # Strip file extension for clarity

    # Create a folder named after the game_id and model name
    game_folder = os.path.join(os.path.dirname(evaluation_output_file), f"{game_id}_{model_name}")
    os.makedirs(game_folder, exist_ok=True)

    # Save evaluation results
    evaluation_output_file = os.path.join(game_folder, f"{game_id}_{model_name}_evaluation.csv")
    results_df.to_csv(evaluation_output_file, index=False)
    print(f"Evaluation results saved to {evaluation_output_file}")

    # Save confusion matrix to CSV
    conf_matrix_df = pd.DataFrame(conf_matrix, 
                                  columns=["Predicted Negative", "Predicted Positive"], 
                                  index=["Actual Negative", "Actual Positive"])

    confusion_matrix_output_file = os.path.join(game_folder, f"{game_id}_{model_name}_confusion_matrix.csv")
    conf_matrix_df.to_csv(confusion_matrix_output_file)
    print(f"Confusion matrix saved to {confusion_matrix_output_file}")

    # Map predictions to cleaned features
    cleaned_file = os.path.join(cleaned_features_directory, f"{game_id}_features.csv")
    if os.path.exists(cleaned_file):
        df_cleaned = pd.read_csv(cleaned_file)
        df_cleaned['Prediction'] = y_pred.astype(int)  # Add predictions to the dataframe
        mapped_file_path = os.path.join(game_folder, f"{game_id}_{model_name}_mapped_predictions.csv")
        df_cleaned.to_csv(mapped_file_path, index=False)
        print(f"Predictions mapped to cleaned features saved to {mapped_file_path}")
    else:
        print(f"Cleaned features file {cleaned_file} does not exist. Skipping mapping.")


def main():
    parser = argparse.ArgumentParser(description="Train or evaluate machine learning models.")
    parser.add_argument("input_directory", type=str, help="Directory containing feature files for training or evaluation.")
    parser.add_argument("--cleaned_features_directory", type=str, help="Directory containing original cleaned features for mapping predictions.", nargs='?')
    parser.add_argument("--train", action="store_true", help="Train the models.")
    parser.add_argument("--evaluate_only", action="store_true", help="Evaluate the models.")
    parser.add_argument("--punt_next_drive_model_path", type=str, default="models/punt_next_drive_model.pkl", help="Path to save/load the model for 'punt_next_drive'.")
    parser.add_argument("--punt_in_two_drives_model_path", type=str, default="models/punt_in_two_drives_model.pkl", help="Path to save/load the model for 'punt_in_exactly_two_drives'.")
    parser.add_argument("--output_directory", type=str, default="predictions", help="Directory to save outputs during evaluation.")
    args = parser.parse_args()

    os.makedirs(args.output_directory, exist_ok=True)

    if args.train:
        # Loop over files in input directory and call train_model for the entire directory
        print(f"Training models for all files in: {args.input_directory}")
        train_model(
            input_directory=args.input_directory,
            model_output_path=args.punt_next_drive_model_path,
            target_column="punt_next_drive",
            output_file=os.path.join(args.output_directory, "punt_next_drive_training_stats.csv")
        )
        train_model(
            input_directory=args.input_directory,
            model_output_path=args.punt_in_two_drives_model_path,
            target_column="punt_in_exactly_two_drives",
            output_file=os.path.join(args.output_directory, "punt_in_two_drives_training_stats.csv")
        )
    elif args.evaluate_only:
        if args.cleaned_features_directory is None:
            print("The --evaluate_only flag requires the --cleaned_features_directory argument.")
            sys.exit(1)

        files = os.listdir(args.input_directory)  # Get all files in the input directory
        for file_name in files:
            if file_name.endswith(".csv"):  # Ensure we're processing CSV files
                input_file = os.path.join(args.input_directory, file_name)
                evaluate_model(
                    input_file=input_file,
                    model_path=args.punt_next_drive_model_path,
                    target_column="punt_next_drive",
                    evaluation_output_file=os.path.join(args.output_directory, f"{file_name.replace('.csv', '_punt_next_drive_evaluation.csv')}"),
                    mapped_output_file=os.path.join(args.output_directory, f"{file_name.replace('.csv', '_punt_next_drive_mapped.csv')}"),
                    confusion_matrix_output_file=os.path.join(args.output_directory, f"{file_name.replace('.csv', '_punt_next_drive_confusion_matrix.csv')}"),
                    cleaned_features_directory=args.cleaned_features_directory
                )
                evaluate_model(
                    input_file=input_file,
                    model_path=args.punt_in_two_drives_model_path,
                    target_column="punt_in_exactly_two_drives",
                    evaluation_output_file=os.path.join(args.output_directory, f"{file_name.replace('.csv', '_punt_in_two_drives_evaluation.csv')}"),
                    mapped_output_file=os.path.join(args.output_directory, f"{file_name.replace('.csv', '_punt_in_two_drives_mapped.csv')}"),
                    confusion_matrix_output_file=os.path.join(args.output_directory, f"{file_name.replace('.csv', '_punt_in_two_drives_confusion_matrix.csv')}"),
                    cleaned_features_directory=args.cleaned_features_directory
                )
    else:
        print("Please specify --train or --evaluate_only.")


if __name__ == "__main__":
    main()
