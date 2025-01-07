import pandas as pd

def process_dataframe(dataframe):
    """
    Removes duplicate rows from a DataFrame.

    Parameters:
    dataframe (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with duplicates removed.
    """
    if "sequence" in dataframe.columns:
        # Initialize the 'is_latest_play' column with default value of 0
        dataframe["is_latest_play"] = 0

        # Find the highest sequence number
        max_sequence = dataframe["sequence"].max()

        # Mark only the rows with the highest sequence number as the latest play
        dataframe.loc[dataframe["sequence"] == max_sequence, "is_latest_play"] = 1

    return dataframe

