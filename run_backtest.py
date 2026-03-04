import argparse
from src.utils.run_writer import write_run_outputs
from src.utils.config import load_config
from src.utils.data_loader import load_data
from src.signals.momentum import generate_signal
from src.portfolio.backtest import run_backtest
from src.analytics.performance import summarize_performance


def main(config_path: str):
    cfg = load_config(config_path)

    df = load_data(cfg["data"]["path"])

    # signal
    if cfg["signal"]["name"] == "momentum":
        df = generate_signal(df, window=int(cfg["signal"]["window"]))
    else:
        raise ValueError(f"Unknown signal: {cfg['signal']['name']}")

    # backtest with execution realism
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

    cols = [
        "date", "price", "signal", "position", "ret", "turnover",
        "spread_cost", "slippage_cost", "fee_cost", "impact_cost", "total_cost",
        "strat_net_ret", "equity"
    ]
    print(df[cols].tail(10))

    periods = int(cfg.get("analytics", {}).get("periods_per_year", 252))
    report = summarize_performance(df, periods_per_year=periods)

    print("\n=== Performance summary")
    for k, v in report.items():
        if isinstance(v, float):
            print(f"{k:>15}: {v: .6f}")
        else:
            print(f"{k:>15}: {v}")

    rid, out_dir = write_run_outputs(df=df, report=report, cfg=cfg, out_dir_rel="logs")
    print(f"\nSaved run artifacts: {out_dir}/{rid}_results.csv, {rid}_report.json, {rid}_config.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml", help="Path relative to project root")
    args = parser.parse_args()
    main(args.config)