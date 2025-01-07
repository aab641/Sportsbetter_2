import requests
import json
import os

# API key and base URL
API_KEY = "cpdruG6xV2Ywo8cSt2ZcnpTLIoPw9MDvKQnOcyXr"
BASE_URL = "https://api.sportradar.com/nfl/official/trial/v7/en"

# Directory to save the play-by-play JSON files
output_dir = "pbp-live"
os.makedirs(output_dir, exist_ok=True)

# Function to fetch current live games
def fetch_live_games():
    url = f"{BASE_URL}/games.json"
    params = {"api_key": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        games = response.json().get("games", [])
        live_games = [game for game in games if game.get("status", "") == "inprogress"]
        return live_games
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch live games. Error: {e}")
        return []

# Function to display live games and get user selection
def select_game(live_games):
    if not live_games:
        print("No live games available at the moment.")
        return None

    print("\nCurrent Live Games:")
    for i, game in enumerate(live_games):
        home_team = game.get("home", {}).get("name", "Unknown")
        away_team = game.get("away", {}).get("name", "Unknown")
        print(f"{i + 1}. {away_team} vs {home_team}")

    while True:
        try:
            choice = int(input("\nEnter the number of the game you want to download PBP data for: "))
            if 1 <= choice <= len(live_games):
                return live_games[choice - 1]
            else:
                print("Invalid selection. Please choose a valid game number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

# Function to download PBP data for a selected game
def download_pbp(game):
    game_id = game.get("id")
    if not game_id:
        print("Invalid game data. Skipping download.")
        return
    
    url = f"{BASE_URL}/games/{game_id}/pbp.json"
    params = {"api_key": API_KEY}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Save the response to a file
        output_file = os.path.join(output_dir, f"{game_id}_pbp.json")
        with open(output_file, "w") as file:
            json.dump(response.json(), file)
        
        print(f"Downloaded PBP data for game: {game_id}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download PBP data for game ID: {game_id}. Error: {e}")

# Main script
def main():
    live_games = fetch_live_games()
    selected_game = select_game(live_games)
    
    if selected_game:
        download_pbp(selected_game)
    else:
        print("No game selected. Exiting.")

if __name__ == "__main__":
    main()
