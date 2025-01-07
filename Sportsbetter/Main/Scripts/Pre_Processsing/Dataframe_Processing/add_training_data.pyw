import pandas as pd

def process_dataframe(dataframe):
    """
    Removes duplicate rows from a DataFrame.

    Parameters:
    dataframe (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with duplicates removed.
    """
    # Step 1: Add the 'punt_next_drive' and 'punt_in_exactly_two_drives' columns with default value 0
    dataframe['punt_next_drive'] = 0
    dataframe['punt_in_exactly_two_drives'] = 0

    # Step 2: Iterate through rows and set 'punt_next_drive' and 'punt_in_exactly_two_drives'
    for i in range(len(dataframe) - 2):
        if dataframe.iloc[i + 1]['play_type'] == 'punt':
            dataframe.at[i, 'punt_next_drive'] = 1
        if dataframe.iloc[i + 2]['play_type'] == 'punt':
            dataframe.at[i, 'punt_in_exactly_two_drives'] = 1

    return dataframe
