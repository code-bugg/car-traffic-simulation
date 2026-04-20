"""
main.py
=======
Entry point for the Chișinău Urban Traffic Simulation.

Usage:
    python main.py                          # run with default config
    python main.py --config path/to/cfg.yaml
    python main.py --gui                    # open SUMO visual interface
    python main.py --steps 1000             # override total steps
"""

import argparse
import logging
import runpy
import sys
from pathlib import Path

from src.utils.config import load_config
from src.utils.logger import setup_logger
from src.simulation.runner import SimulationRunner


def parse_args():
    p = argparse.ArgumentParser(
        description="Chișinău Urban Traffic Simulation (SUMO)"
    )
    p.add_argument("--config", default="config/simulation.yaml",
                   help="Path to YAML config file")
    p.add_argument("--gui", action="store_true",
                   help="Open SUMO-GUI instead of headless mode")
    p.add_argument("--steps", type=int, default=None,
                   help="Override total simulation steps")
    p.add_argument("--debug", action="store_true",
                   help="Set log level to DEBUG")
    p.add_argument("--edit", action="store_true",
                   help="Open NETEDIT on the active network and exit")
    return p.parse_args()


def main():
    args = parse_args()

    if args.edit:
        editor = Path(__file__).parent / "scripts" / "edit_network.py"
        sys.argv = [str(editor), "--config", args.config]
        runpy.run_path(str(editor), run_name="__main__")
        return

    cfg = load_config(args.config)

    setup_logger(
        log_dir=cfg["output"]["log_dir"],
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    logger = logging.getLogger(__name__)

    # CLI overrides
    if args.gui:
        cfg["sumo"]["binary"] = "sumo-gui"
    if args.steps:
        cfg["simulation"]["total_steps"] = args.steps

    logger.info("=" * 60)
    logger.info("Chișinău Urban Traffic Simulation")
    logger.info("Config : %s", args.config)
    logger.info("Steps  : %d", cfg["simulation"]["total_steps"])
    logger.info("Mode   : %s", cfg["sumo"]["binary"])
    logger.info("=" * 60)

    runner = SimulationRunner(config_path=args.config)
    # Apply any in-memory overrides
    runner.config = cfg
    runner.total_steps = cfg["simulation"]["total_steps"]

    try:
        runner.run()
    except Exception as e:
        logger.error("Simulation failed: %s", e, exc_info=True)
        sys.exit(1)

    logger.info("Simulation complete. Results in: %s/", cfg["output"]["output_dir"])


if __name__ == "__main__":
    main()
