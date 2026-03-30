"""
SimulationRunner
================
Top-level orchestrator.  Wires together:
  - SUMO / TraCI lifecycle
  - VehicleTypeLoader   – registers car / bus / truck
  - VehicleSpawner      – injects vehicles at runtime
  - AdaptiveTrafficLightController – extends green phases under load
  - StatisticsCollector – records per-step KPIs
"""

import logging
import os
import traci

from src.utils.config import load_config
from src.agents.spawner import VehicleSpawner
from src.simulation.statistics import StatisticsCollector
from src.simulation.vehicle_type_loader import VehicleTypeLoader
from src.traffic_control.adaptive_controller import AdaptiveTrafficLightController

logger = logging.getLogger(__name__)


class SimulationRunner:

    def __init__(self, config_path: str = "config/simulation.yaml"):
        self.config = load_config(config_path)
        self.step_num = 0
        self.total_steps: int = self.config["simulation"]["total_steps"]
        self.warmup_steps: int = self.config["simulation"].get("warmup_steps", 0)
        self._running = False

        # Sub-systems (initialised after TraCI connects)
        self.stats: StatisticsCollector | None = None
        self.spawner: VehicleSpawner | None = None
        self.tl_ctrl: AdaptiveTrafficLightController | None = None

    # ── lifecycle ────────────────────────────────────────────────────

    def start(self) -> None:
        sumo_cfg = self.config["sumo"]

        # Build sumo command
        # Build sumo command
        cmd = [
            sumo_cfg["binary"],
            "--net-file",    sumo_cfg["network_file"],
            "--route-files", sumo_cfg["route_file"],
            "--step-length", str(self.config["simulation"]["step_length"]),
            "--seed",        str(self.config["simulation"]["seed"]),
            "--no-step-log", "true",
            "--collision.action", "warn",
            "--time-to-teleport", "300",
            "--ignore-route-errors", "true",  # <--- LINIA NOU ADĂUGATĂ
        ]
        
        additional = sumo_cfg.get("additional_files", [])
        if additional:
            cmd += ["--additional-files", ",".join(additional)]

        traci.start(cmd)
        self._running = True
        logger.info("SUMO started — network: %s", sumo_cfg["network_file"])

        # Register vehicle types
        VehicleTypeLoader(self.config).register()

        # Initialise sub-systems
        self.stats   = StatisticsCollector(self.config)
        self.spawner = VehicleSpawner(
            net_file=sumo_cfg["network_file"],
            cfg=self.config,
            seed=self.config["simulation"]["seed"],
        )

        if self.config["traffic_lights"].get("adaptive", False):
            self.tl_ctrl = AdaptiveTrafficLightController(self.config)
            self.tl_ctrl.initialise()

    def run(self) -> None:
        if not self._running:
            self.start()

        logger.info("Running %d steps (warmup=%d) ...",
                    self.total_steps, self.warmup_steps)
        try:
            while self.step_num < self.total_steps:
                traci.simulationStep()
                self._on_step()
                self.step_num += 1
        except KeyboardInterrupt:
            logger.warning("Simulation interrupted by user.")
        finally:
            self._finalise()
            self.stop()

    def stop(self) -> None:
        if self._running:
            traci.close()
            self._running = False
            logger.info("SUMO closed at step %d.", self.step_num)

    # ── per-step logic ───────────────────────────────────────────────

    def _on_step(self) -> None:
        # 1. Spawn new vehicles
        self.spawner.step(self.step_num)

        # 2. Adaptive traffic lights
        if self.tl_ctrl:
            self.tl_ctrl.step()

        # 3. Collect stats (skip warmup)
        if self.step_num >= self.warmup_steps:
            self.stats.step(self.step_num)

    # ── finalise ─────────────────────────────────────────────────────

    def _finalise(self) -> None:
        import os
        out_dir = self.config["output"]["output_dir"]
        os.makedirs(out_dir, exist_ok=True)

        csv_path = os.path.join(out_dir, "statistics.csv")
        self.stats.save_csv(csv_path)

        from src.visualization.stats_plotter import StatsPlotter
        plotter = StatsPlotter(out_dir)
        df = self.stats.to_dataframe()
        if not df.empty:
            plotter.plot_all(df)
            logger.info("Charts saved to %s/", out_dir)
