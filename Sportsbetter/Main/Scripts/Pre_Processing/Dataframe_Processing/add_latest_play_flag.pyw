import os
import pandas as pd
import argparse


import pandas as pd
import pandas as pd

def process_dataframe(df):
    print("Adding the 'is_latest_play' column.")
    if "sequence" in df.columns:
        # Initialize the 'is_latest_play' column with default value of 0
        df["is_latest_play"] = 0

        # Find the highest sequence number
        max_sequence = df["sequence"].max()

        # Mark only the rows with the highest sequence number as the latest play
        df.loc[df["sequence"] == max_sequence, "is_latest_play"] = 1
    return df
