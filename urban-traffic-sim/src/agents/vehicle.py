"""
VehicleAgent
============
Wraps a single SUMO vehicle. All traci.vehicle.* calls are centralised here.
"""

import traci
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class VehicleState:
    vehicle_id: str
    speed: float = 0.0
    position: Tuple[float, float] = (0.0, 0.0)
    lane_id: str = ""
    edge_id: str = ""
    waiting_time: float = 0.0
    co2_emission: float = 0.0   # mg/s
    fuel_consumption: float = 0.0  # ml/s


class VehicleAgent:
    """Represents and controls a single vehicle in the simulation."""

    def __init__(self, vehicle_id: str):
        self.vehicle_id = vehicle_id

    # ── state ────────────────────────────────────────────────────────

    def get_state(self) -> VehicleState:
        vid = self.vehicle_id
        return VehicleState(
            vehicle_id=vid,
            speed=traci.vehicle.getSpeed(vid),
            position=traci.vehicle.getPosition(vid),
            lane_id=traci.vehicle.getLaneID(vid),
            edge_id=traci.vehicle.getRoadID(vid),
            waiting_time=traci.vehicle.getWaitingTime(vid),
            co2_emission=traci.vehicle.getCO2Emission(vid),
            fuel_consumption=traci.vehicle.getFuelConsumption(vid),
        )

    # ── control ──────────────────────────────────────────────────────

    def set_speed(self, speed: float) -> None:
        traci.vehicle.setSpeed(self.vehicle_id, speed)

    def reroute(self) -> None:
        traci.vehicle.rerouteTraveltime(self.vehicle_id)

    def set_color(self, r: int, g: int, b: int, a: int = 255) -> None:
        traci.vehicle.setColor(self.vehicle_id, (r, g, b, a))

    def __repr__(self) -> str:
        return f"VehicleAgent(id={self.vehicle_id!r})"
