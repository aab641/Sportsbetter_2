import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import argparse

def normalize_columns(input_directory, output_directory, max_files=None):
    """
    Normalizes numeric columns in multiple files and ensures consistent data types.

    Parameters:
        input_directory (str): Directory containing input files.
        output_directory (str): Directory to save normalized files.
        max_files (int, optional): Maximum number of files to process. Default is None (no limit).

    Returns:
        None
    """
    os.makedirs(output_directory, exist_ok=True)
    files = sorted(os.listdir(input_directory))

    # Limit the number of files to process if max_files is specified
    if max_files:
        files = files[:max_files]

    # Columns to standardize and their target data types
    target_data_types = {
        "line_of_scrimmage": "int",
        "start_yardline": "int",
        "end_yardline": "int",
        "start_reason":"str",
        "end_reason":"str",
        "first_downs":"int",
        "id": "str",  # Convert to string for consistency
        "duration": "int",
        "start_reason": "str",  # Convert to string for consistency
        "run_pass_option": "int64",
        "play_count": "int",
        "first_downs": "int",
        "net_yards": "int",
        "drive_sequence": "int",
        "clock": "str",  # Treat clock as a string initially
    }

    for file_name in files:
        if file_name.endswith(".csv"):
            input_file = os.path.join(input_directory, file_name)
            output_file = os.path.join(output_directory, file_name)
            print(f"Normalizing {input_file} -> {output_file}")

            # Load the data
            df = pd.read_csv(input_file)

            # Convert clock column to total seconds
            if "clock" in df.columns:
                def clock_to_seconds(clock_str):
                    try:
                        minutes, seconds = map(int, clock_str.split(":"))
                        return minutes * 60 + seconds
                    except ValueError:
                        return None  # Handle invalid formats
                df["clock"] = df["clock"].apply(clock_to_seconds)

            # Standardize data types for specified columns
            for col, dtype in target_data_types.items():
                if col in df.columns:
                    try:
                        if dtype == "float64":
                            df[col] = pd.to_numeric(df[col], errors="coerce")
                        elif dtype == "int64":
                            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")
                        elif dtype == "str":
                            df[col] = df[col].astype(str)
                    except Exception as e:
                        print(f"Error converting column '{col}' to {dtype}: {e}")

            # Identify numeric columns for normalization
            exclude_from_normalization = [
                "id", "start_reason", "end_reason", "play_count",
                "first_downs", "net_yards", "duration", "drive_sequence",
                "weather_condition", "temperature", "wind_speed",
                "home_points", "away_points", "home_wins", "home_losses",
                "away_wins", "away_losses",
            ]
            numeric_cols = [
                col for col in df.select_dtypes(include=["float64", "int64"]).columns
                if col not in exclude_from_normalization
            ]

            # Fill missing values for numeric columns to be normalized
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

            # Normalize numeric data using Min-Max scaling
            scaler = MinMaxScaler()
            df[numeric_cols] = scaler.fit_transform(df[numeric_cols])

            # Save the processed file
            df.to_csv(output_file, index=False)
            print(f"Normalized file saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize features and ensure consistent data types.")
    parser.add_argument("input_directory", type=str, help="Directory containing input CSV files.")
    parser.add_argument("output_directory", type=str, help="Directory to save normalized CSV files.")
    parser.add_argument("--max_files", type=int, default=None, help="Maximum number of files to process.")
    args = parser.parse_args()

    normalize_columns(args.input_directory, args.output_directory, args.max_files)
