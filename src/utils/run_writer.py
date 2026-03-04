from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Tuple

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def make_run_id() -> str:
    # ISO-ish timestamp, filesystem friendly
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_run_outputs(
    *,
    df: pd.DataFrame,
    report: Dict[str, Any],
    cfg: Dict[str, Any],
    out_dir_rel: str = "logs",
    run_id: str | None = None,
) -> Tuple[str, Path]:
    """
    Writes:
      - logs/<run_id>_results.csv
      - logs/<run_id>_report.json
      - logs/<run_id>_config.json  (resolved config snapshot)

    Returns: (run_id, output_dir_path)
    """
    output_dir = PROJECT_ROOT / out_dir_rel
    ensure_dir(output_dir)

    rid = run_id or make_run_id()

    results_path = output_dir / f"{rid}_results.csv"
    report_path = output_dir / f"{rid}_report.json"
    config_path = output_dir / f"{rid}_config.json"

    df.to_csv(results_path, index=False)

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, sort_keys=True)

    with config_path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, sort_keys=True)

    return rid, output_dir
