from __future__ import annotations
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def save_equity_plot(df: pd.DataFrame, out_path: Path, equity_col: str = "equity") -> None:
    _ensure_dir(out_path.parent)
    plt.figure()
    plt.plot(df[equity_col].astype(float).values)
    plt.title("Equity Curve")
    plt.xlabel("Bar")
    plt.ylabel("Equity")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


def save_drawdown_plot(df: pd.DataFrame, out_path: Path, equity_col: str = "equity") -> None:
    _ensure_dir(out_path.parent)
    equity = df[equity_col].astype(float)
    peak = equity.cummax()
    dd = equity / peak - 1.0

    plt.figure()
    plt.plot(dd.values)
    plt.title("Drawdown")
    plt.xlabel("Bar")
    plt.ylabel("Drawdown")
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()
