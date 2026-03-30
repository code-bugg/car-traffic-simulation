"""
TrafficLightController
======================
Manages a single SUMO traffic light junction.
Supports reading phase info and optionally overriding phase durations.
"""

import traci
from dataclasses import dataclass
from typing import List


@dataclass
class PhaseInfo:
    tl_id: str
    current_phase: int
    phase_duration: float
    state: str          # e.g. "GGrrGGrr"
    elapsed: float      # seconds spent in current phase


class TrafficLightController:
    def __init__(self, tl_id: str):
        self.tl_id = tl_id

    def get_phase_info(self) -> PhaseInfo:
        return PhaseInfo(
            tl_id=self.tl_id,
            current_phase=traci.trafficlight.getPhase(self.tl_id),
            phase_duration=traci.trafficlight.getPhaseDuration(self.tl_id),
            state=traci.trafficlight.getRedYellowGreenState(self.tl_id),
            elapsed=traci.trafficlight.getPhaseDuration(self.tl_id)
                    - traci.trafficlight.getNextSwitch(self.tl_id)
                    + traci.simulation.getTime(),
        )

    def set_phase(self, phase_index: int) -> None:
        traci.trafficlight.setPhase(self.tl_id, phase_index)

    def set_duration(self, duration: float) -> None:
        traci.trafficlight.setPhaseDuration(self.tl_id, duration)

    def get_controlled_lanes(self) -> List[str]:
        return list(traci.trafficlight.getControlledLanes(self.tl_id))

    @staticmethod
    def get_all_tl_ids() -> List[str]:
        return list(traci.trafficlight.getIDList())
