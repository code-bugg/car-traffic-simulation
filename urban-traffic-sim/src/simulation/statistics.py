"""
StatisticsCollector
===================
Collects per-step aggregate metrics from the running SUMO simulation
and stores them in a pandas DataFrame for later analysis/plotting.
"""

import logging
import traci
import pandas as pd
from typing import List, Dict

logger = logging.getLogger(__name__)


class StatisticsCollector:
    def __init__(self, cfg: dict):
        self.interval: int = cfg["output"]["statistics_interval"]
        self._records: List[Dict] = []

    # ── public ───────────────────────────────────────────────────────

    def step(self, sim_step: int) -> None:
        if sim_step % self.interval != 0:
            return
        record = self._snapshot(sim_step)
        self._records.append(record)
        logger.debug(
            "Step %d | vehicles=%d | mean_speed=%.2f m/s | mean_wait=%.2f s",
            sim_step,
            record["vehicle_count"],
            record["mean_speed"],
            record["mean_waiting_time"],
        )

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self._records)

    def save_csv(self, path: str) -> None:
        df = self.to_dataframe()
        df.to_csv(path, index=False)
        logger.info("Statistics saved → %s", path)

    # ── internals ────────────────────────────────────────────────────

    def _snapshot(self, step: int) -> Dict:
        vehicle_ids = traci.vehicle.getIDList()
        n = len(vehicle_ids)

        if n == 0:
            return {
                "step": step,
                "vehicle_count": 0,
                "mean_speed": 0.0,
                "mean_waiting_time": 0.0,
                "mean_co2": 0.0,
                "mean_fuel": 0.0,
                "halting_vehicles": 0,
                "teleport_count": traci.simulation.getStartingTeleportNumber(),
            }

        speeds        = [traci.vehicle.getSpeed(v) for v in vehicle_ids]
        waiting_times = [traci.vehicle.getWaitingTime(v) for v in vehicle_ids]
        co2           = [traci.vehicle.getCO2Emission(v) for v in vehicle_ids]
        fuel          = [traci.vehicle.getFuelConsumption(v) for v in vehicle_ids]
        halting       = sum(1 for s in speeds if s < 0.1)

        return {
            "step":             step,
            "vehicle_count":    n,
            "mean_speed":       sum(speeds) / n,
            "mean_waiting_time": sum(waiting_times) / n,
            "mean_co2":         sum(co2) / n,
            "mean_fuel":        sum(fuel) / n,
            "halting_vehicles": halting,
            "teleport_count":   traci.simulation.getStartingTeleportNumber(),
        }
