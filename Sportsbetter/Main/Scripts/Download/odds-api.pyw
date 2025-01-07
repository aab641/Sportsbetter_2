import json
import time
import requests

# An API key is emailed to you when you sign up to a plan
api_key = '840b27e81d8e513215eb5e411d9c7de9'

# Parse active NFL games
def parse_active_nfl_games(sports_data, events_data):
    nfl_sport_key = None
    for sport in sports_data:
        if sport['key'] == 'americanfootball_nfl' and sport['active']:
            nfl_sport_key = sport['key']
            break

    if not nfl_sport_key:
        print("No active NFL sports found.")
        return []

    nfl_games = []
    for event in events_data:
        if event['sport_key'] == nfl_sport_key:
            game = {
                'id': event['id'],
                'teams': event['teams'],
                'home_team': event['home_team'],
                'commence_time': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(event['commence_time'])),
                'odds': {site['site_nice']: site['odds'] for site in event['sites']}
            }
            nfl_games.append(game)

    return nfl_games

# Format and calculate implied probabilities
def format_odds_with_probabilities(odds):
    formatted_output = ""
    for i, (site, odds_data) in enumerate(odds.items(), start=1):
        punt_odds = odds_data['h2h'][0]
        no_punt_odds = odds_data['h2h'][1]

        punt_prob = round((1 / punt_odds) * 100, 2)
        no_punt_prob = round((1 / no_punt_odds) * 100, 2)

        formatted_output += (
            f"{i}. {site}:\n"
            f"   - Punt: {punt_odds} (Implied Probability: {punt_prob}%)\n"
            f"   - No Punt: {no_punt_odds} (Implied Probability: {no_punt_prob}%)\n\n"
        )
    return formatted_output

# Function to poll odds continuously
def poll_odds(selected_game_id, poll_interval=30):
    while True:
        try:
            odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
                'api_key': api_key,
                'sport': 'americanfootball_nfl',
                'region': 'uk',
                'mkt': 'h2h'
            })

            odds_json = json.loads(odds_response.text)
            if not odds_json['success']:
                print('There was a problem with the odds request:', odds_json['msg'])
                break

            game = next((event for event in odds_json['data'] if event['id'] == selected_game_id), None)
            if game:
                formatted_odds = format_odds_with_probabilities(
                    {site['site_nice']: site['odds'] for site in game['sites']}
                )
                print(f"\nUpdated Odds for {game['teams'][0]} vs {game['teams'][1]}:\n{formatted_odds}")
            else:
                print("Selected game is no longer available.")

            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\nPolling stopped.")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break

# Fetch odds and sports data
sports_response = requests.get('https://api.the-odds-api.com/v3/sports', params={'api_key': api_key})
sports_json = json.loads(sports_response.text)

odds_response = requests.get('https://api.the-odds-api.com/v3/odds', params={
    'api_key': api_key,
    'sport': 'upcoming',
    'region': 'uk',
    'mkt': 'h2h'
})
odds_json = json.loads(odds_response.text)

if not sports_json['success'] or not odds_json['success']:
    print("Failed to fetch sports or odds data.")
else:
    active_nfl_games = parse_active_nfl_games(sports_json['data'], odds_json['data'])

    if active_nfl_games:
        print("\nActive NFL Games:")
        for i, game in enumerate(active_nfl_games):
            print(f"{i + 1}: {game['teams'][0]} vs {game['teams'][1]} (Start Time: {game['commence_time']})")

        game_choice = int(input("\nEnter the number of the game to start polling odds: ")) - 1
        if 0 <= game_choice < len(active_nfl_games):
            selected_game = active_nfl_games[game_choice]
            print(f"\nPolling odds for {selected_game['teams'][0]} vs {selected_game['teams'][1]}...")
            poll_odds(selected_game['id'], poll_interval=30)
        else:
            print("\nInvalid selection.")
    else:
        print("\nNo active NFL games found.")
