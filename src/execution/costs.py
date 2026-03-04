import pandas as pd


def apply_execution_costs(
    df: pd.DataFrame,
    *,
    position_col: str = "position",
    spread_bps: float = 0.0,
    slippage_bps: float = 0.0,
    fee_bps: float = 0.0,
    impact_bps: float = 0.0,
    impact_col: str | None = None,
) -> pd.DataFrame:
    """
    Execution cost attribution using turnover.

    Costs are applied in returns-space per bar:

      turnover_t = abs(position_t - position_{t-1})

    Components:
      - spread_cost: turnover * (half spread)
      - slippage_cost: turnover * slippage
      - fee_cost: turnover * fee
      - impact_cost:
          A) if impact_col is None: turnover * impact_bps (simple flat impact)
          B) else: turnover * impact_bps * (turnover / df[impact_col])  (volume-aware proxy)

    Notes:
      - spread_bps is TOTAL spread; we charge half per side.
      - slippage_bps is per-side cost.
      - fee_bps is commission-like cost on turnover.
      - impact is optional; you can wire volume later (minute_volume, dollar_volume, etc.)
    """
    out = df.copy()

    # turnover in "position units"
    out["turnover"] = out[position_col].diff().abs().fillna(0.0)

    # bps -> decimal returns
    half_spread = (spread_bps / 10000.0) / 2.0
    slip = slippage_bps / 10000.0
    fee = fee_bps / 10000.0
    impact = impact_bps / 10000.0

    out["spread_cost"] = out["turnover"] * half_spread
    out["slippage_cost"] = out["turnover"] * slip
    out["fee_cost"] = out["turnover"] * fee

    if impact_bps and impact_bps != 0.0:
        if impact_col is None:
            # flat proxy impact
            out["impact_cost"] = out["turnover"] * impact
        else:
            # volume-aware proxy (very rough but useful):
            # higher turnover relative to liquidity => higher impact
            liq = out[impact_col].replace(0, pd.NA).astype(float)
            ratio = (out["turnover"] / liq).fillna(0.0)
            out["impact_cost"] = out["turnover"] * impact * ratio
    else:
        out["impact_cost"] = 0.0

    out["total_cost"] = (
        out["spread_cost"]
        + out["slippage_cost"]
        + out["fee_cost"]
        + out["impact_cost"]
    )

    return out