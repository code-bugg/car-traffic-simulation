"""
regenerate_routes.py
====================
Rebuild the route file against the current network (useful after editing the
network in NETEDIT — old routes may reference deleted edges).

Skips OSM download and netconvert; only re-runs randomTrips.py.

Usage:
    python scripts/regenerate_routes.py
    python scripts/regenerate_routes.py --config config/simulation.yaml
"""

import argparse
import logging
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
from prepare_map import generate_routes  # noqa: E402

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Regenerate routes against the current network.")
    parser.add_argument("--config", default="config/simulation.yaml")
    args = parser.parse_args()

    with open(args.config) as f:
        cfg = yaml.safe_load(f)

    net_path = Path(cfg["sumo"]["network_file"])
    rou_path = Path(cfg["sumo"]["route_file"])

    if not net_path.exists():
        logger.error("Network file not found: %s", net_path)
        sys.exit(1)

    generate_routes(net_path, rou_path, cfg, force=True)
    logger.info("Done. You can now run: python main.py --gui")


if __name__ == "__main__":
    main()
