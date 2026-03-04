from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[2]  # src/utils -> src -> project root


def load_config(rel_path: str) -> Dict[str, Any]:
    """
    Load YAML config located relative to project root.
    Example: load_config("configs/default.yaml")
    """
    path = PROJECT_ROOT / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if not isinstance(cfg, dict):
        raise ValueError(f"Config must parse to a dict, got: {type(cfg)}")

    return cfg
