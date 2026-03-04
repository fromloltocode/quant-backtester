import pandas as pd
from src.portfolio.backtest import run_backtest


def test_position_is_shifted_by_latency():
    df = pd.DataFrame(
        {
            "price": [100, 101, 102, 103],
            "signal": [0, 1, 1, 1],
        }
    )

    out = run_backtest(
        df,
        signal_col="signal",
        price_col="price",
        latency_bars=1,
        spread_bps=0.0,
        slippage_bps=0.0,
        fee_bps=0.0,
        initial_capital=1.0,
    )

    # position should be signal shifted by 1:
    # signal:  [0,1,1,1]
    # position:[0,0,1,1]
    assert out["position"].tolist() == [0.0, 0.0, 1.0, 1.0]
