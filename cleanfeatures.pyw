import os
import pandas as pd
import numpy as np

def clean_and_extract_features(input_directory, output_directory):
    # Ensure the output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Loop through all CSV files in the input directory
    for filename in os.listdir(input_directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(input_directory, filename)
            df = pd.read_csv(filepath)

            # Step 1: Handle missing values
            df.fillna({
                'weather_condition': 'Unknown',
                'temperature': df['temperature'].mean(),
                'wind_speed': df['wind_speed'].mean(),
                'play_type': 'unknown',
                'result': 'unknown',
            }, inplace=True)

            # Step 2: Encode categorical variables
            df = pd.get_dummies(df, columns=['weather_condition', 'play_type', 'result'], drop_first=True)

            # Step 3: Convert clock to seconds remaining in period
            def clock_to_seconds(clock):
                try:
                    minutes, seconds = map(int, clock.split(':'))
                    return minutes * 60 + seconds
                except:
                    return np.nan

            df['clock_seconds_remaining'] = df['clock'].apply(clock_to_seconds)
            df.drop(columns=['clock'], inplace=True)

            # Step 4: Generate game-time feature
            df['time_remaining_in_game'] = df['period_number'] * 900 - df['clock_seconds_remaining']
            df.drop(columns=['period_number'], inplace=True)

            # Step 5: Create feature subsets for different modules
            # Module 1: Game State Features
            game_state_features = ['home_score', 'away_score', 'time_remaining_in_game']

            # Module 2: Drive Performance Features
            drive_performance_features = ['play_count', 'first_downs', 'net_yards', 'duration']

            # Module 3: Environmental and Play Context Features
            context_features = [
                'temperature', 'wind_speed', 'weather_condition_Unknown',
                'play_type_rush', 'play_type_pass', 'result_touchback',
            ]

            # Combine relevant features for output
            relevant_features = game_state_features + drive_performance_features + context_features
            cleaned_df = df[relevant_features].copy()

            # Step 6: Save the cleaned dataset
            output_filename = f"cleaned_features_{filename}"
            cleaned_filepath = os.path.join(output_directory, output_filename)
            cleaned_df.to_csv(cleaned_filepath, index=False)
            print(f"Processed and saved: {cleaned_filepath}")

# Directory paths
input_directory = "feature_extraction"
output_directory = "cleaned_features"

# Run the cleaning and feature extraction process
clean_and_extract_features(input_directory, output_directory)