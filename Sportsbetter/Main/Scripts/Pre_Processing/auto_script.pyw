import os
import pandas as pd
import importlib.util
import argparse

def run_dataframe_processing(input_data_folder, dataframe_processing_folder, output_data_folder, max_files=None):
    """
    Applies processing scripts from a specified folder to each DataFrame in the input data folder.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_data_folder, exist_ok=True)

    # List all CSV files in the input folder
    files = sorted([f for f in os.listdir(input_data_folder) if f.endswith(".csv")])

    if max_files:
        files = files[:max_files]

    # List all Python processing scripts in the processing folder
    processing_scripts = [
        os.path.join(dataframe_processing_folder, f) for f in os.listdir(dataframe_processing_folder) if f.endswith(".py")
    ]

    for file_name in files:
        input_file_path = os.path.join(input_data_folder, file_name)
        output_file_path = os.path.join(output_data_folder, file_name)

        print(f"Processing file: {input_file_path}")

        # Load the CSV into a DataFrame
        df = pd.read_csv(input_file_path)

        # Apply each processing script to the DataFrame
        for script_path in processing_scripts:
            print(f"Applying script: {script_path}")

            # Dynamically load the processing script
            spec = importlib.util.spec_from_file_location("module.name", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Assume each script has a `process_dataframe` function
            if hasattr(module, "process_dataframe"):
                df = module.process_dataframe(df)

        # Save the processed DataFrame to the output folder
        df.to_csv(output_file_path, index=False)
        print(f"Saved processed file to: {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files with custom Python scripts.")
    parser.add_argument("input_data_folder", type=str, nargs="?", default="../Data/Training/Temp", help="Folder containing input CSV files.")
    parser.add_argument("dataframe_processing_folder", type=str, nargs="?", default="../Scripts/Pre_Processing/Dataframe_Processing/", help="Folder containing Python scripts for processing DataFrames.")
    parser.add_argument("output_data_folder", type=str, nargs="?", default="../Data/Training/Temp_2", help="Folder to save processed CSV files.")
    parser.add_argument("--max_files", type=int, default=None, help="Maximum number of files to process.")

    args = parser.parse_args()

    run_dataframe_processing(args.input_data_folder, args.dataframe_processing_folder, args.output_data_folder, args.max_files)
