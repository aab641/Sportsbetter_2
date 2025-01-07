import os
import sys
import argparse
import pandas as pd
from sklearn.metrics import classification_report
import subprocess
import shutil

def clear_folders(folders_to_clear):
    """
    Clears the contents of specified folders, excluding the 'pbp-live' folder.
    
    Parameters:
        folders_to_clear (list): List of folder paths to be cleared, excluding 'pbp-live'.
    
    Returns:
        None
    """
    for folder_path in folders_to_clear:
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except PermissionError as pe:
                    print(f"PermissionError: Failed to delete {file_path}. The file may be open or locked. Details: {pe}")
                except OSError as oe:
                    print(f"OSError: Failed to delete {file_path}. The file may be open or locked. Details: {oe}")
                except Exception as e:
                    print(f"Unexpected error while deleting {file_path}. Reason: {e}")

def run_script(script_name, *args, **kwargs):
    """
    Executes a Python script and ensures it completes before proceeding.
    Captures and prints the script's output.
    
    Parameters:
        script_name (str): The filename of the script to execute.
        args (tuple): Positional arguments to pass to the script.
        kwargs (dict): Additional optional arguments to pass to the script.
    
    Returns:
        None
    """
    try:
        print(f"Running {script_name}...")
        # Build the argument list
        cmd = [sys.executable, script_name]
        cmd.extend(args)  # Add positional arguments
        for key, value in kwargs.items():
            if isinstance(value, bool):
                if value:  # Add the flag only if it's True
                    cmd.append(f"--{key}")
            elif value is not None:
                cmd.append(f"--{key}")
                cmd.append(str(value))  # Add the key-value pair as arguments

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )

        print(f"Output from {script_name}:\n{result.stdout}")
        print(f"Error from {script_name}:\n{result.stderr}")  # Print the error details
        print(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e.stderr}")
        sys.exit(1)


def ensure_predictions_file(predictions_file):
    """
    Ensures the predictions file exists. Creates a placeholder file if it doesn't.
    
    Parameters:
        predictions_file (str): Path to the predictions file.
    
    Returns:
        None
    """
    if not os.path.exists(predictions_file):
        print(f"{predictions_file} does not exist. Creating a placeholder file.")
        os.makedirs(os.path.dirname(predictions_file), exist_ok=True)
        placeholder_data = {
            "sequence": [],
            "punt_next_drive_prediction": [],
            "punt_in_exactly_two_drives_prediction": [],
        }
        placeholder_df = pd.DataFrame(placeholder_data)
        placeholder_df.to_csv(predictions_file, index=False)
        print(f"Placeholder predictions file created at {predictions_file}")


def save_statistics(predictions_folder, output_file):
    """
    Saves aggregated statistics about AI predictions for all files in a folder to a CSV file.
    
    Parameters:
        predictions_folder (str): Path to the folder containing model predictions.
        output_file (str): Path to save the aggregated statistics CSV.
    
    Returns:
        None
    """
    all_stats = []
    # Ensure the predictions folder exists
    if not os.path.exists(predictions_folder):
        print(f"{predictions_folder} does not exist. Creating it.")
        os.makedirs(predictions_folder, exist_ok=True)

    # Iterate over all CSV files in the folder
    for file_name in os.listdir(predictions_folder):
        if file_name.endswith(".csv"):
            predictions_file = os.path.join(predictions_folder, file_name)
            print(f"Processing {predictions_file}...")

            # Load predictions
            predictions_df = pd.read_csv(predictions_file)

            # Check for the required columns
            required_columns = [
                "punt_next_drive", "punt_next_drive_prediction",
                "punt_in_exactly_two_drives", "punt_in_exactly_two_drives_prediction"
            ]
            if not all(col in predictions_df.columns for col in required_columns):
                print(f"Skipping {predictions_file}: Missing required columns.")
                continue

            # Calculate statistics for punt_next_drive
            if not predictions_df.empty:
                next_drive_stats = predictions_df.groupby(
                    ["punt_next_drive", "punt_next_drive_prediction"]
                ).size().reset_index(name="count")
                next_drive_stats["type"] = "punt_next_drive"
                next_drive_stats["file_name"] = file_name
                all_stats.append(next_drive_stats)

                # Calculate percentages
                total_next_drive = next_drive_stats["count"].sum()
                next_drive_stats["percentage"] = (next_drive_stats["count"] / total_next_drive) * 100

                # Calculate statistics for punt_in_exactly_two_drives
                in_two_drives_stats = predictions_df.groupby(
                    ["punt_in_exactly_two_drives", "punt_in_exactly_two_drives_prediction"]
                ).size().reset_index(name="count")
                in_two_drives_stats["type"] = "punt_in_exactly_two_drives"
                in_two_drives_stats["file_name"] = file_name
                all_stats.append(in_two_drives_stats)

                # Calculate percentages
                total_in_two_drives = in_two_drives_stats["count"].sum()
                in_two_drives_stats["percentage"] = (in_two_drives_stats["count"] / total_in_two_drives) * 100
            else:
                print(f"No data in {predictions_file}. Skipping.")

    # Combine statistics from all files
    if all_stats:
        aggregated_stats = pd.concat(all_stats, ignore_index=True)
    else:
        # Create an empty statistics DataFrame if no predictions are available
        aggregated_stats = pd.DataFrame(
            columns=["punt_next_drive", "punt_next_drive_prediction", 
                     "punt_in_exactly_two_drives", "punt_in_exactly_two_drives_prediction"]
        )

    # Save aggregated statistics to a CSV file
    aggregated_stats.to_csv(output_file, index=False)
    print(f"Aggregated prediction statistics saved to {output_file}")


if __name__ == "__main__":
    # Define folder paths
    pbp_live_data_folder = "pbp-live"
    pbp_live_features_extraction = "pbp-live_features_extraction"
    latest_play_features_folder = "pbp-live_latest_play_features"  # New folder for updated files
    predictions_output_file = "predictions-mapped/pbp-live_prediction_stats.csv"

    # Clear the relevant folders (excluding pbp-live)
    clear_folders([pbp_live_features_extraction, latest_play_features_folder, "pbp-live_cleaned_features", "pbp-live_normalized_features", "pbp-live_training_features", "predictions"])

    max_files = 249

    # Define the order of scripts and their parameters
    scripts_with_params = [
        {
            "script": "feature-extraction/featureextraction.pyw",
            "positional_args": [pbp_live_data_folder, pbp_live_features_extraction],
            "params": {"max_files": max_files, "include_drive_data": True},
        },
        {
            "script": "feature-extraction/addtrainingdata.pyw",
            "positional_args": [pbp_live_features_extraction, "pbp-live_training_features"],
            "params": {"max_files": max_files},
        },
        {
            "script": "feature-extraction/add_latest_play_flag.pyw",  # Add latest play flag step
            "positional_args": ["pbp-live_training_features", latest_play_features_folder],
            "params": {"max_files": max_files},
        },
        {
            "script": "feature-extraction/cleanfeatures.pyw",
            "positional_args": [latest_play_features_folder, "pbp-live_cleaned_features"],
            "params": {"max_files": max_files},
        },
        {
            "script": "feature-extraction/normalize_features.pyw",
            "positional_args": ["pbp-live_cleaned_features", "pbp-live_normalized_features"],
            "params": {"max_files": max_files},
        },
        {
            "script": "trainmodels.pyw",
            "positional_args": ["pbp-live_normalized_features"],  # This will pass the normalized features folder
            "params": {
                "evaluate_only": True,  # Evaluation mode for testing
                "punt_next_drive_model_path": "models/punt_next_drive_model.pkl",
                "punt_in_two_drives_model_path": "models/punt_in_two_drives_model.pkl",
                "output_directory": "predictions",
                "cleaned_features_directory": "pbp-live_cleaned_features"  # Use cleaned features folder here
            },
        },
    ]

    # Run each script with its parameters
    for script_entry in scripts_with_params:
        script = script_entry["script"]
        positional_args = script_entry.get("positional_args", [])
        params = script_entry.get("params", {})
        run_script(script, *positional_args, **params)

    print("All scripts executed successfully, including saving prediction statistics!")
