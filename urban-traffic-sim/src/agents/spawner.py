"""
VehicleSpawner
==============
Injects vehicles into the simulation at configurable intervals using
SUMO flows defined in the route file, with optional runtime top-up.
"""

import random
import logging
import traci
import sumolib
from typing import List

logger = logging.getLogger(__name__)


class VehicleSpawner:
    """Spawns vehicles onto random valid edges in the network."""

    def __init__(self, net_file: str, cfg: dict, seed: int = 42):
        self.cfg = cfg
        self.spawn_interval: int = cfg["traffic"]["spawn_interval"]
        self.batch_size: int = cfg["traffic"]["batch_size"]
        self._counter = 0
        random.seed(seed)

        # Load valid departure edges (not internal, have lanes)
        self._net = sumolib.net.readNet(net_file, withInternal=False)
        self._edges: List[str] = [
            e.getID() for e in self._net.getEdges()
            if e.allows("passenger") and e.getLength() > 20
        ]
        if not self._edges:
            logger.warning("No valid spawn edges found — check the network file.")

        # Build vehicle type list with weights
        vtypes = cfg["traffic"]["vehicle_types"]
        self._vtypes = [v["id"] for v in vtypes]
        self._weights = [1.0] * len(self._vtypes)   # uniform by default

    # ── public API ───────────────────────────────────────────────────

    def step(self, sim_step: int) -> int:
        """Call every simulation step. Returns vehicles spawned this step."""
        if sim_step % self.spawn_interval != 0:
            return 0
        return self._spawn_batch()

    # ── internals ────────────────────────────────────────────────────

    def _spawn_batch(self) -> int:
        if not self._edges:
            return 0

        spawned = 0
        for _ in range(self.batch_size):
            src, dst = random.sample(self._edges, 2)
            vtype = random.choices(self._vtypes, weights=self._weights, k=1)[0]
            vid = f"v_{self._counter}"
            self._counter += 1
            try:
                route_id = f"route_{vid}"
                traci.route.add(route_id, [src, dst])
                traci.vehicle.add(
                    vehID=vid,
                    routeID=route_id,
                    typeID=vtype,
                    depart="now",
                    departLane="best",
                    departSpeed="max",
                )
                spawned += 1
            except traci.exceptions.TraCIException as e:
                logger.debug("Could not spawn %s: %s", vid, e)
        return spawned
