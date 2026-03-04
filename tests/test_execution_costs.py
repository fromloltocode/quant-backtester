import pandas as pd
from src.execution.costs import apply_execution_costs


def test_cost_attribution_on_entry():
    # position goes 0 -> 1 (turnover 1)
    df = pd.DataFrame({"position": [0.0, 1.0]})

    out = apply_execution_costs(
        df,
        position_col="position",
        spread_bps=2.0,     # half spread = 1 bp
        slippage_bps=1.0,   # 1 bp
        fee_bps=0.0,
        impact_bps=0.0,
    )

    # turnover at t=1 is 1
    assert out["turnover"].tolist() == [0.0, 1.0]

    # costs in decimal returns
    # spread_cost = 1 * 0.0001
    # slippage_cost = 1 * 0.0001
    assert abs(out["spread_cost"].iloc[1] - 0.0001) < 1e-12
    assert abs(out["slippage_cost"].iloc[1] - 0.0001) < 1e-12
    assert abs(out["total_cost"].iloc[1] - 0.0002) < 1e-12


def test_turnover_on_flip_long_to_short():
    # position goes 1 -> -1 (turnover 2)
    df = pd.DataFrame({"position": [1.0, -1.0]})

    out = apply_execution_costs(
        df,
        position_col="position",
        spread_bps=2.0,
        slippage_bps=1.0,
        fee_bps=0.0,
        impact_bps=0.0,
    )

    assert out["turnover"].tolist() == [0.0, 2.0]
    # total cost should double vs entry case: 2 * 0.0002 = 0.0004
    assert abs(out["total_cost"].iloc[1] - 0.0004) < 1e-12
