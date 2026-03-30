"""
AdaptiveTrafficLightController
================================
Extends green phases when the number of waiting vehicles on
controlled lanes exceeds a configurable threshold.
"""

import logging
import traci
from typing import Dict, List

from src.traffic_control.traffic_light import TrafficLightController

logger = logging.getLogger(__name__)


class AdaptiveTrafficLightController:
    """
    Wraps every TL junction in the network and extends green time
    when congestion is detected on the active green lanes.
    """

    def __init__(self, cfg: dict):
        tl_cfg = cfg["traffic_lights"]
        self.min_green: float = tl_cfg["min_green_time"]
        self.max_green: float = tl_cfg["max_green_time"]
        self.threshold: int   = tl_cfg["congestion_threshold"]
        self._controllers: Dict[str, TrafficLightController] = {}
        self._extended: Dict[str, bool] = {}   # guard: extend only once per phase

    # ── lifecycle ────────────────────────────────────────────────────

    def initialise(self) -> None:
        """Call after TraCI is connected."""
        for tl_id in TrafficLightController.get_all_tl_ids():
            self._controllers[tl_id] = TrafficLightController(tl_id)
            self._extended[tl_id] = False
        logger.info("AdaptiveController managing %d TL junctions.",
                    len(self._controllers))

    def step(self) -> None:
        """Call every simulation step to apply adaptive logic."""
        for tl_id, ctrl in self._controllers.items():
            self._adapt(tl_id, ctrl)

    # ── internals ────────────────────────────────────────────────────

    def _adapt(self, tl_id: str, ctrl: TrafficLightController) -> None:
        info = ctrl.get_phase_info()
        state = info.state

        # Identify lanes currently seeing green
        green_lanes = self._green_lanes(tl_id, state)
        if not green_lanes:
            self._extended[tl_id] = False
            return

        waiting = sum(
            traci.lane.getLastStepHaltingNumber(lane)
            for lane in green_lanes
        )

        if waiting >= self.threshold and not self._extended[tl_id]:
            extension = min(info.phase_duration + 15.0, self.max_green)
            ctrl.set_duration(extension)
            self._extended[tl_id] = True
            logger.debug("TL %s extended green to %.0f s (%d waiting)",
                         tl_id, extension, waiting)
        elif waiting < self.threshold:
            self._extended[tl_id] = False

    def _green_lanes(self, tl_id: str, state: str) -> List[str]:
        lanes = traci.trafficlight.getControlledLanes(tl_id)
        return [
            lane for lane, sig in zip(lanes, state)
            if sig in ("G", "g")
        ]
