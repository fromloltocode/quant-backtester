import pandas as pd
from src.execution.costs import apply_execution_costs


def run_backtest(
    df: pd.DataFrame,
    *,
    signal_col: str = "signal",
    price_col: str = "price",
    latency_bars: int = 1,
    spread_bps: float = 0.0,
    slippage_bps: float = 0.0,
    fee_bps: float = 0.0,
    impact_bps: float = 0.0,
    impact_col: str | None = None,
    initial_capital: float = 1.0,
) -> pd.DataFrame:
    out = df.copy()

    # position with latency
    out["position"] = out[signal_col].shift(latency_bars).fillna(0.0)

    # asset returns
    out["ret"] = out[price_col].pct_change().fillna(0.0)

    # gross strategy return
    out["strat_gross_ret"] = out["position"] * out["ret"]

    # execution cost attribution
    out = apply_execution_costs(
        out,
        position_col="position",
        spread_bps=spread_bps,
        slippage_bps=slippage_bps,
        fee_bps=fee_bps,
        impact_bps=impact_bps,
        impact_col=impact_col,
    )

    # net return & equity
    out["strat_net_ret"] = out["strat_gross_ret"] - out["total_cost"]
    out["equity"] = initial_capital * (1.0 + out["strat_net_ret"]).cumprod()

    return out