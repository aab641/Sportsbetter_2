import os
import pandas as pd
import argparse

def add_training_data(input_directory, output_directory, max_files=None):
    """
    Adds training data columns to existing features.

    Parameters:
        input_directory (str): Directory containing input files.
        output_directory (str): Directory to save updated features.
        max_files (int, optional): Maximum number of files to process.

    Returns:
        None
    """
    os.makedirs(output_directory, exist_ok=True)
    files = sorted(os.listdir(input_directory))

    if max_files:
        files = files[:max_files]

    for file_name in files:
        print(f"Adding training data to file: {file_name}")
        if file_name.endswith('.csv'):
            filepath = os.path.join(input_directory, file_name)
            df = pd.read_csv(filepath)

            # Step 1: Add the 'punt_next_drive' and 'punt_in_exactly_two_drives' columns with default value 0
            df['punt_next_drive'] = 0
            df['punt_in_exactly_two_drives'] = 0

            # Step 2: Iterate through rows and set 'punt_next_drive' and 'punt_in_exactly_two_drives'
            for i in range(len(df) - 2):
                if df.iloc[i + 1]['play_type'] == 'punt':
                    df.at[i, 'punt_next_drive'] = 1
                if df.iloc[i + 2]['play_type'] == 'punt':
                    df.at[i, 'punt_in_exactly_two_drives'] = 1

            # Step 3: Save the processed DataFrame to the output directory
            output_filepath = os.path.join(output_directory, file_name)
            df.to_csv(output_filepath, index=False)
            print(f"Processed and saved: {output_filepath}")

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Add training data to features.")
    parser.add_argument("input_directory", type=str, help="Directory containing input CSV files.")
    parser.add_argument("output_directory", type=str, help="Directory to save updated CSV files.")
    parser.add_argument("--max_files", type=int, default=None, help="Maximum number of files to process.")

    args = parser.parse_args()

    # Call the function with parsed arguments
    add_training_data(args.input_directory, args.output_directory, args.max_files)
