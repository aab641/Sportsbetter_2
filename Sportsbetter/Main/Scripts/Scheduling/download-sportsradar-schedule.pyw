import requests
import os
import json

# API key and base URL
API_KEY = "cpdruG6xV2Ywo8cSt2ZcnpTLIoPw9MDvKQnOcyXr"
BASE_URL = "https://api.sportradar.com/nfl/official/trial/v7/en"

# Endpoint for the current schedule
CURRENT_SCHEDULE_URL = f"{BASE_URL}/games/current_season/schedule.json"

# Directory to save the schedule JSON file
output_dir = "schedule_data"
os.makedirs(output_dir, exist_ok=True)

# Filepath to save the schedule data
output_file = os.path.join(output_dir, "current_schedule.json")

def download_current_schedule():
    """
    Fetches the current NFL schedule and saves it as a JSON file.
    """
    headers = {"accept": "application/json"}
    params = {"api_key": API_KEY}
    
    try:
        print(f"Fetching current schedule from: {CURRENT_SCHEDULE_URL}")
        response = requests.get(CURRENT_SCHEDULE_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the JSON response to a file
        schedule_data = response.json()
        with open(output_file, "w") as file:
            json.dump(schedule_data, file, indent=4)
        
        print(f"Schedule data saved to: {output_file}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch the current schedule. Error: {e}")

if __name__ == "__main__":
    download_current_schedule()
