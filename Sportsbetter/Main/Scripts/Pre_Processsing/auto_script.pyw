import os
import pandas as pd
import importlib.util
import argparse

def load_script(script_path):
    """Dynamically load a Python script."""
    spec = importlib.util.spec_from_file_location("script_module", script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def process_csvs_with_scripts(csv_folder, scripts_folder, output_folder):
    """
    Process CSV files in a folder using Python scripts designed to process DataFrames.

    Args:
        csv_folder (str): Path to the folder containing input CSV files.
        scripts_folder (str): Path to the folder containing Python scripts.
        output_folder (str): Path to the folder where processed CSVs will be saved.
    """
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Get list of CSV files and scripts
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
    scripts = [f for f in os.listdir(scripts_folder) if f.endswith('.py')]

    if not csv_files:
        print("No CSV files found in the input folder.")
        return

    if not scripts:
        print("No Python scripts found in the scripts folder.")
        return

    for script_name in scripts:
        script_path = os.path.join(scripts_folder, script_name)
        script_module = load_script(script_path)

        for csv_file in csv_files:
            csv_path = os.path.join(csv_folder, csv_file)
            output_path = os.path.join(output_folder, f"processed_{script_name[:-3]}_{csv_file}")

            try:
                # Load CSV into a DataFrame
                df = pd.read_csv(csv_path)

                # Ensure the script has a `process_dataframe` function
                if hasattr(script_module, 'process_dataframe'):
                    df_processed = script_module.process_dataframe(df)
                    
                    # Save processed DataFrame to the output folder
                    df_processed.to_csv(output_path, index=False)
                    print(f"Processed {csv_file} with {script_name} -> {output_path}")
                else:
                    print(f"Script {script_name} does not have a 'process_dataframe' function.")
            except Exception as e:
                print(f"Error processing {csv_file} with {script_name}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process CSV files with Python scripts.")
    parser.add_argument("csv_folder", type=str, help="Path to the folder containing CSV files.")
    parser.add_argument("scripts_folder", type=str, help="Path to the folder containing Python scripts.")
    parser.add_argument("output_folder", type=str, help="Path to the folder where processed files should be saved.")

    args = parser.parse_args()

    process_csvs_with_scripts(args.csv_folder, args.scripts_folder, args.output_folder)
