import pandas as pd

def process_dataframe(dataframe):
    """
    Removes duplicate rows from a DataFrame.

    Parameters:
    dataframe (pd.DataFrame): The input DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with duplicates removed.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame.")
    
    dataframe = dataframe.drop_duplicates()
    return dataframe
