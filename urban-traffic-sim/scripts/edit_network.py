"""
edit_network.py
===============
Launch SUMO's NETEDIT on the active network file.

Usage:
    python scripts/edit_network.py
    python scripts/edit_network.py --config config/simulation.yaml

After editing, save with Ctrl+S in NETEDIT, then run:
    python scripts/regenerate_routes.py
to rebuild routes against the modified network.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def resolve_netedit() -> str:
    """Find the netedit binary via SUMO_HOME or PATH."""
    sumo_home = os.environ.get("SUMO_HOME")
    if sumo_home:
        for name in ("netedit.exe", "netedit"):
            candidate = Path(sumo_home) / "bin" / name
            if candidate.exists():
                return str(candidate)
    found = shutil.which("netedit")
    if found:
        return found
    logger.error("Could not locate 'netedit'. Set SUMO_HOME or add it to PATH.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Open NETEDIT on the active network.")
    parser.add_argument("--config", default="config/simulation.yaml")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)
    net_path = Path(cfg["sumo"]["network_file"])

    if not net_path.exists():
        logger.error("Network file not found: %s", net_path)
        logger.error("Run `python scripts/prepare_map.py` first.")
        sys.exit(1)

    netedit = resolve_netedit()
    logger.info("Opening %s in NETEDIT ...", net_path)
    logger.info("Save with Ctrl+S, then run: python scripts/regenerate_routes.py")
    subprocess.run([netedit, "--sumo-net-file", str(net_path)])


if __name__ == "__main__":
    main()
