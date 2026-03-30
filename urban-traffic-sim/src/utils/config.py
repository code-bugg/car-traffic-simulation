"""Loads YAML configuration files."""

import yaml
from pathlib import Path


def load_config(path: str) -> dict:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")
    with config_path.open() as f:
        return yaml.safe_load(f)
