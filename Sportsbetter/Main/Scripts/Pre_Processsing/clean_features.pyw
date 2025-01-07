import argparse
import os
import pandas as pd


def propagate_drive_info(df):
    # Initialize placeholders for drive data
    current_start_reason = None
    current_end_reason = None
    current_first_downs = None
    current_duration = None

    # Iterate over the DataFrame
    for index, row in df.iterrows():
        if row['entry_type'] == 'drive':
            # Update drive-related information
            current_start_reason = row['start_reason']
            current_end_reason = row['end_reason']
            current_first_downs = row['first_downs']
            current_duration = row['duration']
        elif row['entry_type'] == 'play':
            # Propagate drive-related information to play rows
            df.at[index, 'start_reason'] = current_start_reason
            df.at[index, 'end_reason'] = current_end_reason
            df.at[index, 'first_downs'] = current_first_downs
            df.at[index, 'duration'] = current_duration

    return df

def clean_features(input_directory, output_directory, max_files=None):
    """
    Cleans features in the input directory by propagating drive-level data row by row
    and removing unnecessary rows.

    Parameters:
        input_directory (str): Directory containing input files.
        output_directory (str): Directory to save cleaned features.
        max_files (int, optional): Maximum number of files to process.

    Returns:
        None
    """
    os.makedirs(output_directory, exist_ok=True)
    files = sorted(os.listdir(input_directory))

    if max_files:
        files = files[:max_files]

    for file_name in files:
        if file_name.endswith(".csv"):
            file_path = os.path.join(input_directory, file_name)
            print(f"Processing file: {file_path}")

            # Load the CSV file
            df = pd.read_csv(file_path)

            # Convert 'duration' from mm:ss to seconds, handle "unknown"
            if 'duration' in df.columns:
                df['duration'] = df['duration'].apply(lambda x: convert_duration_to_seconds(x))

            # Handle 'play_hash_mark' as a categorical column
            if 'play_hash_mark' in df.columns:
                df['play_hash_mark'] = df['play_hash_mark'].fillna('unknown')
                df['play_hash_mark'] = pd.factorize(df['play_hash_mark'])[0]  # Convert to numeric category

            propagate_drive_info(df)

            # Remove rows where 'entry_type' is 'drive'
            df = df[df["entry_type"] != "drive"]

            # Drop unnecessary columns if they exist
            drop_columns = ["id", "end_reason"]  # Explicitly drop these columns
            df = df.drop(columns=[col for col in drop_columns if col in df.columns], errors="ignore")

            # Save the cleaned file
            output_file = os.path.join(output_directory, file_name)
            df.to_csv(output_file, index=False)

            # Log the columns in the cleaned file for debugging
            print(f"Cleaned file saved to: {output_file}. Columns: {list(df.columns)}")

def convert_duration_to_seconds(duration):
    """
    Converts a duration string in 'mm:ss' format to total seconds.
    Handles "unknown" values by returning 0 seconds.
    
    Parameters:
        duration (str): Duration in 'mm:ss' format or 'unknown'.
    
    Returns:
        int: Duration in total seconds or 0 for "unknown".
    """
    if pd.isna(duration) or duration == "unknown":
        return 0
    try:
        minutes, seconds = map(int, duration.split(":"))
        return minutes * 60 + seconds
    except ValueError:
        # Handle any invalid format gracefully, return 0
        return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean extracted features and propagate drive-level data.")
    parser.add_argument("input_directory", type=str, help="Directory containing input CSV files.")
    parser.add_argument("output_directory", type=str, help="Directory to save cleaned CSV files.")
    parser.add_argument("--max_files", type=int, default=None, help="Maximum number of files to process.")
    args = parser.parse_args()

    clean_features(args.input_directory, args.output_directory, args.max_files)
