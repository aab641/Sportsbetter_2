import pandas as pd

def process_dataframe(df):
    print("Adding punt next drive and punt in exactly two drives.")
    # Step 1: Add the 'punt_next_drive' and 'punt_in_exactly_two_drives' columns with default value 0
    df['punt_next_drive'] = 0
    df['punt_in_exactly_two_drives'] = 0

    # Step 2: Iterate through rows and set 'punt_next_drive' and 'punt_in_exactly_two_drives'
    for i in range(len(df) - 2):
        if df.iloc[i + 1]['play_type'] == 'punt':
            df.at[i, 'punt_next_drive'] = 1
        if df.iloc[i + 2]['play_type'] == 'punt':
            df.at[i, 'punt_in_exactly_two_drives'] = 1
    return df