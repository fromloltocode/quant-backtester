import pandas as pd


def load_data(path: str):
    """
    Load market data from CSV.
    """
    df = pd.read_csv(path)
    return df
