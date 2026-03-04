from __future__ import annotations

import argparse
import copy
from itertools import product
from typing import Any, Dict, List, Tuple

import pandas as pd

from src.utils.config import load_config
from src.utils.data_loader import load_data
from src.signals.momentum import generate_signal
from src.portfolio.backtest import run_backtest
from src.analytics.performance import summarize_performance
from src.utils.run_writer import write_run_outputs, make_run_id


def _set_cfg(cfg: Dict[str, Any], dotted_key: str, value: Any) -> None:
    """
    Set nested dict value using dotted keys, e.g. "signal.window" or "execution.spread_bps"
    """
    keys = dotted_key.split(".")
    cur = cfg
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value


def _run_once(cfg: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    df = load_data(cfg["data"]["path"])

    # signals
    if cfg["signal"]["name"] == "momentum":
        df = generate_signal(df, window=int(cfg["signal"]["window"]))
    else:
        raise ValueError(f"Unknown signal: {cfg['signal']['name']}")

    # backtest
    df = run_backtest(
        df,
        signal_col="signal",
        price_col=cfg["data"]["price_col"],
        latency_bars=int(cfg["execution"]["latency_bars"]),
        spread_bps=float(cfg["execution"]["spread_bps"]),
        slippage_bps=float(cfg["execution"]["slippage_bps"]),
        fee_bps=float(cfg["execution"]["fee_bps"]),
        impact_bps=float(cfg["execution"].get("impact_bps", 0.0)),
        impact_col=cfg["execution"].get("impact_col", None),
        initial_capital=float(cfg["portfolio"]["initial_capital"]),
    )

    periods = int(cfg.get("analytics", {}).get("periods_per_year", 252))
    report = summarize_performance(df, periods_per_year=periods)
    return df, report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml", help="Base config (relative to project root)")
    # Sweeps are specified like: --sweep signal.window=5,10,20 execution.spread_bps=1,2,5
    parser.add_argument("--sweep", nargs="+", required=True, help="DottedKey=v1,v2,...")
    args = parser.parse_args()

    base_cfg = load_config(args.config)

    # parse sweep specs
    sweep_keys: List[str] = []
    sweep_values: List[List[Any]] = []

    for item in args.sweep:
        if "=" not in item:
            raise ValueError(f"Bad sweep arg: {item} (expected dotted.key=v1,v2,...)")
        k, v = item.split("=", 1)
        vals = v.split(",")
        # try numeric parsing
        parsed: List[Any] = []
        for x in vals:
            x = x.strip()
            if x.lower() == "null":
                parsed.append(None)
            else:
                try:
                    if "." in x:
                        parsed.append(float(x))
                    else:
                        parsed.append(int(x))
                except ValueError:
                    parsed.append(x)
        sweep_keys.append(k.strip())
        sweep_values.append(parsed)

    sweep_id = make_run_id()
    rows = []

    for combo in product(*sweep_values):
        cfg = copy.deepcopy(base_cfg)
        for k, val in zip(sweep_keys, combo):
            _set_cfg(cfg, k, val)

        df, report = _run_once(cfg)

        # use readable run_id for sweep: include keyvals
        tag = "__".join([f"{k.split('.')[-1]}={v}" for k, v in zip(sweep_keys, combo)])
        run_id = f"{sweep_id}__{tag}"

        write_run_outputs(df=df, report=report, cfg=cfg, out_dir_rel="logs", run_id=run_id)

        row = {**{k: v for k, v in zip(sweep_keys, combo)}, **report, "run_id": run_id}
        rows.append(row)

        print(f"done: {run_id} | sharpe={report['sharpe']:.4f} total_return={report['total_return']:.4f}")

    out = pd.DataFrame(rows).sort_values(by="sharpe", ascending=False)
    out_path = f"logs/{sweep_id}_sweep.csv"
    out.to_csv(out_path, index=False)
    print(f"\nSaved sweep summary: {out_path}")
    print(out.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
