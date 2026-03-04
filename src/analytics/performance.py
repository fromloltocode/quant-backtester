from __future__ import annotations
import numpy as np
import pandas as pd


def max_drawdown(equity: pd.Series) -> float:
    equity = equity.astype(float)
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return float(dd.min())


def sharpe(returns: pd.Series, periods_per_year: int) -> float:
    r = returns.astype(float)
    mu = r.mean()
    sig = r.std(ddof=1)
    if sig == 0 or np.isnan(sig):
        return 0.0
    return float((mu / sig) * np.sqrt(periods_per_year))


def summarize_performance(
    df: pd.DataFrame,
    *,
    net_ret_col: str = "strat_net_ret",
    equity_col: str = "equity",
    turnover_col: str = "turnover",
    cost_col: str = "total_cost",
    periods_per_year: int = 252,  # for daily; for minute data you’ll change this
) -> dict:
    net_ret = df[net_ret_col].fillna(0.0)
    equity = df[equity_col].ffill()

    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    mdd = max_drawdown(equity)
    sh = sharpe(net_ret, periods_per_year=periods_per_year)

    avg_turnover = float(df[turnover_col].fillna(0.0).mean())
    total_cost = float(df[cost_col].fillna(0.0).sum())

    # simple hit rate
    hit_rate = float((net_ret > 0).mean())

    return {
        "total_return": total_return,
        "sharpe": sh,
        "max_drawdown": mdd,
        "avg_turnover": avg_turnover,
        "total_cost": total_cost,
        "hit_rate": hit_rate,
        "bars": int(len(df)),
    }
