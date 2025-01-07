import os
import requests
import json
import argparse

# API key and base URL
API_KEY = "cpdruG6xV2Ywo8cSt2ZcnpTLIoPw9MDvKQnOcyXr"
BASE_URL = "https://api.sportradar.com/nfl/official/trial/v7/en/games"

def download_pbp(game_id, output_file):
    """
    Downloads the play-by-play data for a given game ID and saves it to the specified file.

    Parameters:
        game_id (str): The ID of the game.
        output_file (str): The file path to save the play-by-play data.

    Returns:
        None
    """
    url = f"{BASE_URL}/{game_id}/pbp.json"
    params = {"api_key": API_KEY}

    try:
        print(f"Downloading play-by-play data for game ID: {game_id}...")
        response = requests.get(url, params=params)
        response.raise_for_status()

        # Save the response data
        with open(output_file, "w") as file:
            json.dump(response.json(), file)

        print(f"Play-by-play data saved to: {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download play-by-play data for game ID: {game_id}. Error: {e}")

def main():
    """
    Main function to parse arguments and download play-by-play data.
    """
    parser = argparse.ArgumentParser(description="Download play-by-play data for an NFL game.")
    parser.add_argument("game_id", help="The ID of the game to download play-by-play data for.")
    parser.add_argument("output_directory", help="The directory to save the play-by-play data.")
    args = parser.parse_args()

    # Ensure the output directory exists
    os.makedirs(args.output_directory, exist_ok=True)

    # Output file path
    output_file = os.path.join(args.output_directory, f"{args.game_id}_pbp.json")

    # Download the play-by-play data
    download_pbp(args.game_id, output_file)

if __name__ == "__main__":
    main()
