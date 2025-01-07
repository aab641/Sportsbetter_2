import os
import json
import pandas as pd
import argparse


def calculate_scrimmage_line(location, home_alias, away_alias):
    """
    Calculate the absolute scrimmage line from the yardline and alias, dynamically mapping aliases to teams.

    Parameters:
        location (dict): A dictionary containing 'yardline' and 'alias'.
        home_alias (str): Alias for the home team.
        away_alias (str): Alias for the away team.

    Returns:
        int: The absolute scrimmage line (0-100 scale).
    """
    if not location or "yardline" not in location or "alias" not in location:
        return None  # Return None for missing data

    yardline = location.get("yardline", 0)
    alias = location.get("alias", "").lower()

    # Determine scrimmage line based on the alias
    if alias == home_alias:
        return 100 - yardline  # Flip for the home team
    elif alias == away_alias:
        return yardline  # Away team's yardline remains as is
    else:
        return None  # Return None for unknown alias


def calculate_net_yards(start_location, end_location, home_alias, away_alias):
    """
    Calculate the net yards gained or lost during a play based on the start and end locations.

    Parameters:
        start_location (dict): A dictionary containing 'yardline' and 'alias' for the start situation.
        end_location (dict): A dictionary containing 'yardline' and 'alias' for the end situation.
        home_alias (str): Alias for the home team.
        away_alias (str): Alias for the away team.

    Returns:
        int: The net yards gained or lost (negative for loss).
    """
    if not start_location or not end_location:
        return None  # Return None if either location is missing

    start_yardline = calculate_scrimmage_line(start_location, home_alias, away_alias)
    end_yardline = calculate_scrimmage_line(end_location, home_alias, away_alias)

    if start_yardline is None or end_yardline is None:
        return None  # Return None if scrimmage line could not be calculated

    return end_yardline - start_yardline


def extract_features_from_json(file_path, output_folder="features_extraction", include_drive_data=True):
    """
    Extract detailed features from a single JSON file in chronological order and save to the specified output folder.

    Parameters:
        file_path (str): Path to the JSON file.
        output_folder (str): Directory to save the extracted features.
        include_drive_data (bool): Whether to include drive-level data.

    Returns:
        None: Saves the extracted features to a CSV file.
    """
    with open(file_path, 'r') as file:
        data = json.load(file)

    features = []

    # Extract game-level details
    game_details = {
        "weather_condition": data.get("weather", {}).get("condition", "unknown"),
        "temperature": data.get("weather", {}).get("temp", 0),
        "wind_speed": data.get("weather", {}).get("wind", {}).get("speed", 0),
        "home_team": data.get("summary", {}).get("home", {}).get("name", "unknown"),
        "away_team": data.get("summary", {}).get("away", {}).get("name", "unknown"),
        "home_alias": data.get("summary", {}).get("home", {}).get("alias", "").lower(),
        "away_alias": data.get("summary", {}).get("away", {}).get("alias", "").lower(),
    }

    # Get home and away aliases
    home_alias = game_details["home_alias"]
    away_alias = game_details["away_alias"]

    # Iterate through periods (no sorting applied)
    for period in data.get("periods", []):
        period_details = {"period_number": period.get("number")}

        # Process drives and plays
        for drive in period.get("pbp", []):
            if include_drive_data and drive.get("sequence", 0) > 0:
                # Extract drive details
                drive_details = {
                    "id": drive.get("id", "unknown"),
                    "start_reason": drive.get("start_reason", "unknown"),
                    "end_reason": drive.get("end_reason", "unknown"),
                    "first_downs": drive.get("first_downs", 0),
                    "duration": drive.get("duration", "unknown"),
                }

                # Add drive entry
                drive_details["entry_type"] = "drive"
                features.append({**game_details, **period_details, **drive_details})

            # Process plays within each drive
            for play in drive.get("events", []):
                if play.get("type") == "play":
                    start_location = play.get("start_situation", {}).get("location", {})
                    end_location = play.get("end_situation", {}).get("location", {})

                    play_details = {
                        "id": play.get("id", "unknown"),
                        "play_type": play.get("play_type", "unknown"),
                        "description": play.get("description", ""),
                        "clock": play.get("clock", "00:00"),
                        "sequence": drive.get("sequence", "unknown"),
                        "start_down": play.get("start_situation", {}).get("down", 0),
                        "start_yfd": play.get("start_situation", {}).get("yfd", 0),
                        "end_down": play.get("end_situation", {}).get("down", 0),
                        "end_yfd": play.get("end_situation", {}).get("yfd", 0),
                        "possession_team": play.get("start_situation", {}).get("possession", {}).get("name", "unknown"),
                        "play_hash_mark": play.get("hash_mark", "unknown"),
                        "play_action": play.get("play_action", "unknown"),
                        "run_pass_option": play.get("run_pass_option", "unknown"),
                        "home_points": play.get("home_points", 0),
                        "away_points": play.get("away_points", 0),
                        # Add scrimmage line calculation
                        "scrimmage_line_start": calculate_scrimmage_line(start_location, home_alias, away_alias),
                        "scrimmage_line_end": calculate_scrimmage_line(end_location, home_alias, away_alias),
                        # Calculate net yards dynamically
                        "net_yards": calculate_net_yards(start_location, end_location, home_alias, away_alias),
                    }

                    # Add play entry
                    play_details["entry_type"] = "play"
                    features.append({**game_details, **period_details, **play_details})

    # Convert features to DataFrame
    features_df = pd.DataFrame(features)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Save to CSV
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(output_folder, f"{base_name}_features.csv")
    features_df.to_csv(output_file, index=False)
    print(f"Features extracted and saved to {output_file} (Include drives: {include_drive_data}).")




def process_files(input_directory, output_directory, max_files=None, include_drive_data=False):
    """
    Processes play-by-play data files to extract features.

    Parameters:
        input_directory (str): Directory containing input files.
        output_directory (str): Directory to save processed features.
        max_files (int, optional): Maximum number of files to process.
        include_drive_data (bool): Whether to include drive-level data in extraction.

    Returns:
        None
    """
    os.makedirs(output_directory, exist_ok=True)
    files = sorted(os.listdir(input_directory))

    if max_files:
        files = files[:max_files]

    for file_name in files:
        if file_name.endswith(".json"):
            file_path = os.path.join(input_directory, file_name)
            print(f"Processing file: {file_path}")
            extract_features_from_json(file_path, output_folder=output_directory, include_drive_data=include_drive_data)


if __name__ == "__main__":
    # Use argparse for argument parsing
    parser = argparse.ArgumentParser(description="Extract features from JSON play-by-play data.")
    parser.add_argument("input_directory", type=str, help="Directory containing JSON files.")
    parser.add_argument("output_directory", type=str, help="Directory to save extracted features.")
    parser.add_argument("--max_files", type=int, default=None, help="Maximum number of files to process.")
    parser.add_argument("--include_drive_data", action="store_true", help="Include drive-level data in extraction.")

    args = parser.parse_args()

    process_files(
        input_directory=args.input_directory,
        output_directory=args.output_directory,
        max_files=args.max_files,
        include_drive_data=args.include_drive_data
    )
