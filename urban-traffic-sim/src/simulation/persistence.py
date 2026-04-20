"""
VehiclePersistenceController
============================
Keeps vehicles on the map:
  - On arrival: re-inject with a new random destination (loop).
  - When stuck (speed below threshold for `patience_steps`): rerouteTraveltime().

Only acts on vehicles spawned by our VehicleSpawner (prefix `v_`).
XML-defined vehicles from the static route file are left to SUMO.
"""

import logging
import traci

logger = logging.getLogger(__name__)

RUNTIME_VID_PREFIX = "v_"


class VehiclePersistenceController:
    def __init__(self, config: dict, spawner):
        self.spawner = spawner
        persistence = config.get("traffic", {}).get("persistence", {}) or {}
        self.never_despawn: bool = bool(persistence.get("never_despawn", False))
        br = persistence.get("blocked_reroute", {}) or {}
        self.reroute_enabled: bool = bool(br.get("enabled", False))
        self.speed_threshold: float = float(br.get("speed_threshold", 0.3))
        self.patience_steps: int = int(br.get("patience_steps", 15))
        self._stuck_counters: dict[str, int] = {}

    def step(self, sim_step: int) -> None:
        if self.never_despawn:
            self._loop_arrivals()
        if self.reroute_enabled:
            self._reroute_stuck()

    # ── internals ────────────────────────────────────────────────────

    def _loop_arrivals(self) -> None:
        arrived = traci.simulation.getArrivedIDList()
        for old_vid in arrived:
            if not old_vid.startswith(RUNTIME_VID_PREFIX):
                continue
            self._stuck_counters.pop(old_vid, None)
            new_vid = self.spawner.respawn_like(old_vid)
            if new_vid:
                logger.debug("Looped %s -> %s", old_vid, new_vid)

    def _reroute_stuck(self) -> None:
        active = set(traci.vehicle.getIDList())
        # Drop counters for vehicles no longer present
        for vid in list(self._stuck_counters):
            if vid not in active:
                del self._stuck_counters[vid]

        for vid in active:
            if not vid.startswith(RUNTIME_VID_PREFIX):
                continue
            try:
                speed = traci.vehicle.getSpeed(vid)
            except traci.exceptions.TraCIException:
                continue
            if speed < self.speed_threshold:
                count = self._stuck_counters.get(vid, 0) + 1
                if count >= self.patience_steps:
                    try:
                        traci.vehicle.rerouteTraveltime(vid)
                        logger.info("Rerouted stuck vehicle %s after %d steps",
                                    vid, count)
                    except traci.exceptions.TraCIException as e:
                        logger.debug("Reroute failed for %s: %s", vid, e)
                    self._stuck_counters[vid] = 0
                else:
                    self._stuck_counters[vid] = count
            else:
                self._stuck_counters.pop(vid, None)
