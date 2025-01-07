import pandas as pd

def process_dataframe(df):
    """
    Processes the input DataFrame by removing duplicate rows.

    Parameters:
        df (pd.DataFrame): The input DataFrame to process.

    Returns:
        pd.DataFrame: The processed DataFrame with duplicates removed.
    """
    print("Removing duplicate rows...")
    df.drop_duplicates(inplace=True)
    return df
