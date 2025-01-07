import os
import subprocess
import sys
import shutil

def clear_folder(folder_path):
    """
    Clears the contents of the specified folder.

    Parameters:
        folder_path (str): Path to the folder to be cleared.

    Returns:
        None
    """
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
        print(f"{script_name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running {script_name}: {e.stderr}")
        sys.exit(1)
    except PermissionError as pe:
        print(f"PermissionError: Unable to access a file required by {script_name}. "
              f"Ensure no other program is using the files.\nError Details: {pe}")
        sys.exit(1)
    except OSError as oe:
        print(f"OSError: File may be open or locked, causing {script_name} to fail.\nError Details: {oe}")
        sys.exit(1)
    except Exception as ex:
        print(f"An unexpected error occurred while running {script_name}: {ex}")
        sys.exit(1)


import os

def run_preprocessing(data_folder, script_folder, max_files):
    # Define folder paths
    RAW_input = os.path.join(data_folder, "Training/Raw")
    Temp = os.path.join(data_folder, "Training/Temp")
    Temp2 = os.path.join(data_folder, "Training/Temp_2")
    Features = os.path.join(data_folder, "Training/Features")
    Normalized = os.path.join(data_folder, "Training/Normalized")

    # Clear the folders before running the scripts
    folders_to_clear = [
        Temp,
        Temp2,
        Features,
        Normalized
    ]

    for folder in folders_to_clear:
        print(f"Clearing folder: {folder}")
        clear_folder(folder)

    # Define preprocessing scripts and their parameters
    scripts_with_params = [
        {
            "script": os.path.join(script_folder, "Pre_Processing", "feature_extraction.pyw"),
            "positional_args": [RAW_input, Temp],
            "params": {"max_files": max_files, "include_drive_data": True},
        },
        {
            "script": os.path.join(script_folder, "Pre_Processing", "auto_script.py"),
            "positional_args": [
                Temp,  # input_data_folder
                "../Scripts/Pre_Processing/Dataframe_Processing/",  # dataframe_processing_folder
                Temp2  # output_data_folder
            ],
            "params": {"max_files": max_files},
        },
        {
            "script": os.path.join(script_folder, "Pre_Processing", "clean_features.pyw"),
            "positional_args": [Temp2, Features],
            "params": {"max_files": max_files},
        },
        {
            "script": os.path.join(script_folder, "Pre_Processing", "normalize_features.pyw"),
            "positional_args": [Features, Normalized],
            "params": {"max_files": max_files},
        },
    ]

    # Run each preprocessing script
    for script_entry in scripts_with_params:
        script = script_entry["script"]
        positional_args = script_entry.get("positional_args", [])
        params = script_entry.get("params", {})
        run_script(script, *positional_args, **params)

    print("Preprocessing completed successfully!")

def run_training(data_folder, script_folder):
    # Define paths for training
    normalized_features_folder = os.path.join(data_folder, "/Training/Normalized/")
    model_output_folder = os.path.join(data_folder, "/Models/")
    training_statistics_folder = os.path.join(data_folder, "/Training/Statistics/")

    # Define training script and parameters
    training_script = os.path.join(script_folder, "trainmodels.pyw")
    params = {
        "train": True,
        "punt_next_drive_model_path": os.path.join(model_output_folder, "punt_next_drive_model.pkl"),
        "punt_in_two_drives_model_path": os.path.join(model_output_folder, "punt_in_two_drives_model.pkl"),
        "output_directory": training_statistics_folder
    }

    run_script(training_script, normalized_features_folder, **params)

    print("Model training completed successfully!")

if __name__ == "__main__":
    # Define folder paths
    data_folder = "../Data/"
    script_folder = "../Scripts/"

    # Maximum number of files to process
    max_files = None

    # Run preprocessing
    run_preprocessing(data_folder, script_folder, max_files)

    # Run model training
    run_training(data_folder, script_folder)




    """
    This script will assume Data/Training/Raw is populated.
    It will then perform feature extraction into the Data/Training/Temp.
    Then the Auto-script will run which automatically performs pandas operations and adds columns to the dataset.
    Then we will clean the dataset and store that data into Features
    Then we will Normalize the data into Normalized
    Then we will run all the modules in the modules folder
    output data into the Data/Training/Statistics
    """