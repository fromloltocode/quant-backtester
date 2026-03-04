import pandas as pd


def generate_signal(df: pd.DataFrame, window: int = 5):
    """
    Simple momentum signal.
    Returns +1 for long, -1 for short, 0 for neutral.
    """

    df = df.copy()

    # compute rolling returns
    df["return"] = df["price"].pct_change()

    # rolling momentum
    df["momentum"] = df["return"].rolling(window=window, min_periods=window).mean()

    # signal
    df["signal"] = 0
    df.loc[df["momentum"] > 0, "signal"] = 1
    df.loc[df["momentum"] < 0, "signal"] = -1

    return df

