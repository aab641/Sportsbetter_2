import os
import pandas as pd


from play_by_play.download_play_by_play_data import download_pbp

# Directory for storing play-by-play data for in-progress games
live_dir = "pbp-live"
os.makedirs(live_dir, exist_ok=True)

def process_in_progress_games(schedule_file):
    """
    Reads the organized schedule and downloads play-by-play data only for in-progress games.

    Parameters:
        schedule_file (str): Path to the organized schedule CSV file.

    Returns:
        None
    """
    if not os.path.exists(schedule_file):
        print(f"Schedule file not found: {schedule_file}")
        return

    # Load the schedule CSV
    schedule = pd.read_csv(schedule_file)

    for _, row in schedule.iterrows():
        game_id = row["game_id"]
        status = row["status"]

        # Only process in-progress games
        if status != "inprogress":
            print(f"Skipping game ID {game_id} with status: {status}")
            continue

        # Determine output file path
        output_file = os.path.join(live_dir, f"{game_id}_pbp.json")

        # Download play-by-play data
        print(f"Downloading play-by-play data for in-progress game ID: {game_id}...")
        download_pbp(game_id, output_file)

if __name__ == "__main__":
    # Path to the organized schedule
    schedule_file = "schedule_data/organized_schedule.csv"

    # Process only in-progress games and download play-by-play data
    process_in_progress_games(schedule_file)
