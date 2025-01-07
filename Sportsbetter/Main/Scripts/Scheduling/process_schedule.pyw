import json
import pandas as pd
import os

def process_schedule(json_file, output_file):
    """
    Reads the NFL schedule JSON file, extracts relevant details, and saves them into a CSV file.

    Parameters:
        json_file (str): Path to the input JSON file.
        output_file (str): Path to save the output CSV file.

    Returns:
        None
    """
    with open(json_file, 'r') as f:
        data = json.load(f)

    all_games = []

    # Process each week's games
    for week in data.get("weeks", []):
        week_number = week.get("sequence")
        for game in week.get("games", []):
            game_info = {
                "week_number": week_number,
                "game_id": game.get("id"),
                "status": game.get("status"),
                "scheduled": game.get("scheduled"),
                "home_team": game.get("home", {}).get("name"),
                "home_alias": game.get("home", {}).get("alias"),
                "away_team": game.get("away", {}).get("name"),
                "away_alias": game.get("away", {}).get("alias"),
                "venue_name": game.get("venue", {}).get("name"),
                "venue_city": game.get("venue", {}).get("city"),
                "venue_state": game.get("venue", {}).get("state"),
                "venue_country": game.get("venue", {}).get("country"),
                "attendance": game.get("attendance", 0),
                "home_points": game.get("scoring", {}).get("home_points", 0),
                "away_points": game.get("scoring", {}).get("away_points", 0),
            }
            all_games.append(game_info)

    # Convert to DataFrame
    df = pd.DataFrame(all_games)

    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Data successfully saved to {output_file}")

def main():
    """
    Main function to process the NFL schedule JSON file and save it as a CSV.
    """
    input_file = "schedule_data/current_schedule.json"
    output_file = "schedule_data/organized_schedule.csv"

    # Ensure the input file exists
    if not os.path.exists(input_file):
        print(f"Input file does not exist: {input_file}")
        return

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Process the schedule
    process_schedule(input_file, output_file)

if __name__ == "__main__":
    main()
