import requests
import os
import time
import json
import subprocess
import pandas as pd
import argparse

# API keys and base URLs
SPORTRADAR_API_KEY_NFL = "cpdruG6xV2Ywo8cSt2ZcnpTLIoPw9MDvKQnOcyXr"  # NFL API key
SPORTRADAR_API_KEY_NCAA = "cpdruG6xV2Ywo8cSt2ZcnpTLIoPw9MDvKQnOcyXr"  # NCAA API key
SPORTRADAR_BASE_URL_NFL = "https://api.sportradar.com/nfl/official/trial/v7/en"
SPORTRADAR_BASE_URL_NCAA = "https://api.sportradar.com/ncaafb/trial/v7/en"

# Paths and directories
output_dir = "pbp-live"
testing_script = "main driver for testing.pyw"
predictions_csv = "predictions/pbp_live_predictions.csv"

# Fetch NFL live games
def fetch_live_games_nfl():
    url = f"{SPORTRADAR_BASE_URL_NFL}/games/current_season/schedule.json"
    params = {"api_key": SPORTRADAR_API_KEY_NFL}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Ensure the request was successful
        data = response.json()

        # Extract in-progress games
        in_progress_games = []

        # Check for 'weeks' in the JSON
        if "weeks" in data:
            weeks = data["weeks"]
            for week in weeks:
                for game in week.get("games", []):
                    if game.get("status") == "inprogress":  # Look for in-progress games
                        in_progress_games.append(game)
        return in_progress_games
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch NFL live games. Error: {e}")
        return []


# Fetch NCAA live games
def fetch_live_games_ncaafb():
    url = f"{SPORTRADAR_BASE_URL_NCAA}/games/current_week/schedule.json"
    params = {"api_key": SPORTRADAR_API_KEY_NCAA}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Ensure the request was successful
        data = response.json()

        games = data.get("week", {}).get("games", [])
        live_games = [game for game in games if game.get("status") == "inprogress"]
        return live_games
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch NCAA live games. Error: {e}")
        return []


# Fetch play-by-play data for NFL
def fetch_play_by_play_nfl(game_id):
    url = f"{SPORTRADAR_BASE_URL_NFL}/games/{game_id}/pbp.json"
    params = {"api_key": SPORTRADAR_API_KEY_NFL}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch PBP data for NFL game ID {game_id}. Error: {e}")
        return {}


# Fetch play-by-play data for NCAA
def fetch_pbp_ncaafb(game_id):
    url = f"{SPORTRADAR_BASE_URL_NCAA}/games/{game_id}/pbp.json"
    params = {"api_key": SPORTRADAR_API_KEY_NCAA}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch PBP data for NCAA game ID {game_id}. Error: {e}")
        return {}


# Function to clear a folder before starting
def clear_folder(folder_path):
    """
    Clears the contents of the specified folder.
    """
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    os.rmdir(file_path)
            except Exception as e:
                print(f"Error while clearing folder {folder_path}: {e}")


# Run testing script
def run_testing_script():
    try:
        subprocess.run(["python", testing_script], check=True)
        print(f"Successfully ran {testing_script}.")
    except subprocess.CalledProcessError as e:
        print(f"Error running {testing_script}: {e}")


# Function to place a bet, called when a positive prediction and 'is_latest_play' is True are found
def place_bet(row):
    """
    This function prints the row details to the console.
    It represents the action of placing a bet based on the prediction.
    """
    print("\nPlacing bet on the following row:")
    print(row.to_string(index=False))


# Print positive predictions
def print_positive_predictions(game_id=None):
    """
    This function checks the predictions folder for the specified game-id, finds the relevant file, 
    and filters the rows with positive predictions and 'is_latest_play' as true. 
    It then calls the place_bet function for each matching row. Also, it prints rows where 'is_latest_drive' is True.
    
    Parameters:
        game_id (str): The game ID used to locate the relevant prediction file.
    """
    predictions_folder = "predictions"  # Path to the predictions folder

    if game_id:  # If game_id is provided, use it to search for the folder
        game_folder = os.path.join(predictions_folder, f"{game_id}_*")

        # Iterate over the subfolders in the predictions folder to find the correct one
        for folder in os.listdir(predictions_folder):
            folder_path = os.path.join(predictions_folder, folder)
            if os.path.isdir(folder_path) and game_id in folder:
                # Find the mapped predictions CSV file with the game-id pattern
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(f"{game_id}_*__mapped_predictions.csv"):
                        file_path = os.path.join(folder_path, file_name)
                        print(f"Found file: {file_path}")
                        
                        # Read the CSV file
                        predictions = pd.read_csv(file_path)

                        # Filter rows where prediction > 0.5 and 'is_latest_play' is True
                        positive_predictions = predictions[(predictions["punt_next_drive_prediction"] > 0.5) &
                                                           (predictions["is_latest_play"] == 1)]
                        
                        if not positive_predictions.empty:
                            print("\nPositive Predictions with 'is_latest_play' True:")
                            print(positive_predictions.to_string(index=False))

                            # Call place_bet for each matching row
                            for _, row in positive_predictions.iterrows():
                                place_bet(row)
                        else:
                            print("No positive predictions with 'is_latest_play' as True.")

                        # Print all rows where 'is_latest_drive' is True
                        latest_drive_plays = predictions[predictions["is_latest_play"] == 1]
                        if not latest_drive_plays.empty:
                            print("\nPlays with 'is_latest_play' True:")
                            print(latest_drive_plays.to_string(index=False))
                        return
        print(f"Game ID folder not found in {predictions_folder}.")
    else:
        # For testing mode, just call the function without needing a game_id
        for folder in os.listdir(predictions_folder):
            folder_path = os.path.join(predictions_folder, folder)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    if file_name.endswith(f"_mapped_predictions.csv"):
                        file_path = os.path.join(folder_path, file_name)
                        print(f"Found file: {file_path}")
                        
                        # Read the CSV file
                        predictions = pd.read_csv(file_path)

                        # Find the column that ends with '_prediction'
                        prediction_column = [col for col in predictions.columns if col.endswith('Prediction')]

                        # Check if we found a column that ends with '_prediction'
                        if prediction_column:
                            prediction_column = prediction_column[0]  # Use the first matching column
                            # Filter rows where prediction > 0.5 and 'is_latest_play' is True
                            positive_predictions = predictions[(predictions[prediction_column] > 0.5) &
                                                               (predictions["is_latest_play"] == 1.0)]
                            if not positive_predictions.empty:
                                print("\nPositive Predictions with 'is_latest_play' True:")
                                print(positive_predictions.to_string(index=False))

                                # Call place_bet for each matching row
                                for _, row in positive_predictions.iterrows():
                                    place_bet(row)

                            else:
                                print("No positive predictions with 'is_latest_play' as True.")
                        else:
                            print("No '_prediction' column found in the dataset.")

                        # Print all rows where 'is_latest_play' is True
                        latest_drive_plays = predictions[predictions["is_latest_play"] == 1]
                        if not latest_drive_plays.empty:
                            print("\nPlays with 'is_latest_play' True:")
                            print(latest_drive_plays.to_string(index=False))


# Main polling loop
def main():
    parser = argparse.ArgumentParser(description="Train or evaluate machine learning models.")
    parser.add_argument("--testing", action="store_true", help="Run in testing mode without fetching live games.")
    args = parser.parse_args()
    testing_mode = args.testing

    # Ask user for sport selection if not in testing mode
    if not testing_mode:
        sport_choice = input("Choose sport (NFL/NCAA): ").strip().lower()

        if sport_choice == "nfl":
            live_games = fetch_live_games_nfl()
            sport_name = "NFL"
        elif sport_choice == "ncaa":
            live_games = fetch_live_games_ncaafb()
            sport_name = "NCAA"
        else:
            print("Invalid choice. Exiting.")
            return

        if not live_games:
            print(f"No live games available for {sport_name}.")
            return

        print(f"\nAvailable Live {sport_name} Games:")
        for idx, game in enumerate(live_games):
            print(f"{idx + 1}: {game['away']['name']} vs {game['home']['name']}")
        selected_game_index = int(input(f"\nSelect a game by entering its number: ")) - 1
        selected_game = live_games[selected_game_index]
        print(f"Monitoring game: {selected_game['away']['name']} vs {selected_game['home']['name']}")

        clear_folder("pbp-live")

        while True:
            try:
                if sport_choice == "nfl":
                    pbp_data = fetch_play_by_play_nfl(selected_game["id"])
                else:
                    pbp_data = fetch_pbp_ncaafb(selected_game["id"])

                if pbp_data:
                    # Save PBP data
                    file_path = os.path.join(output_dir, f"{selected_game['id']}.json")
                    with open(file_path, "w") as file:
                        json.dump(pbp_data, file, indent=4)
                    print(f"Saved play-by-play data to {file_path}")

                    # Run testing script and print positive predictions
                    run_testing_script()
                    print_positive_predictions()

                time.sleep(10)  # Poll every 10 seconds
            except KeyboardInterrupt:
                print("Stopping monitoring.")
                break
            except Exception as e:
                print(f"Error: {e}")
                break
    else:
        # If testing mode is enabled, skip live game fetching and just run the testing script and print positive predictions
        print("Running in testing mode...")
        run_testing_script()
        print_positive_predictions()


if __name__ == "__main__":
    main()
