import os
import pandas as pd
import argparse

import pandas as pd

def add_latest_play_flag(input_directory, output_directory, max_files=None):
    """
    Adds an 'is_latest_play' column and calculates 'line_of_scrimmage' and 
    'first_down_marker' for each file in the input directory, modifying cells in place.
    """
    os.makedirs(output_directory, exist_ok=True)
    files = sorted(os.listdir(input_directory))

    if max_files:
        files = files[:max_files]

    for file_name in files:
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_directory, file_name)
            print(f"Processing file: {file_path}")
            
            df = pd.read_csv(file_path)

            if "sequence" in df.columns:
                # Initialize the 'is_latest_play' column with default value of 0
                df["is_latest_play"] = 0

                # Find the highest sequence number
                max_sequence = df["sequence"].max()

                # Mark only the rows with the highest sequence number as the latest play
                df.loc[df["sequence"] == max_sequence, "is_latest_play"] = 1

            df.drop_duplicates(inplace=True)

            # Save the updated file without altering the row order
            output_file = os.path.join(output_directory, file_name)
            df.to_csv(output_file, index=False)
            print(f"Saved updated file to: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add 'is_latest_play' column to feature files.")
    parser.add_argument("input_directory", type=str, help="Directory containing input CSV files.")
    parser.add_argument("output_directory", type=str, help="Directory to save updated CSV files.")
    parser.add_argument("--max_files", type=int, default=None, help="Maximum number of files to process.")
    args = parser.parse_args()

    add_latest_play_flag(args.input_directory, args.output_directory, args.max_files)
