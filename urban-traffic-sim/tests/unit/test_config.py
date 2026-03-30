import pytest
import yaml
from src.utils.config import load_config


def test_load_config_returns_dict(tmp_path):
    cfg = {"simulation": {"total_steps": 100}}
    p = tmp_path / "test.yaml"
    p.write_text(yaml.dump(cfg))
    result = load_config(str(p))
    assert result["simulation"]["total_steps"] == 100


def test_load_config_missing_file():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent.yaml")
