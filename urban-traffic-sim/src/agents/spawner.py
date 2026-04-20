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
from typing import List, Optional

logger = logging.getLogger(__name__)

MAX_REACHABILITY_RETRIES = 5


class VehicleSpawner:
    """Spawns vehicles onto random valid edges in the network."""

    def __init__(self, net_file: str, cfg: dict, seed: int = 42):
        self.cfg = cfg
        self.spawn_interval: int = cfg["traffic"]["spawn_interval"]
        self.batch_size: int = cfg["traffic"]["batch_size"]
        self._counter = 0
        self._rng = random.Random(seed)

        # Load valid departure edges (not internal, have lanes)
        self._net = sumolib.net.readNet(net_file, withInternal=False)
        self._edge_objs = [
            e for e in self._net.getEdges()
            if e.allows("passenger") and e.getLength() > 20
        ]
        self._edges: List[str] = [e.getID() for e in self._edge_objs]
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

    def respawn_like(self, old_vid: str) -> Optional[str]:
        """Inject one new vehicle with a fresh random src/dst. Returns new vid or None."""
        if not self._edges:
            return None
        vtype = self._rng.choices(self._vtypes, weights=self._weights, k=1)[0]
        return self._spawn_one(vtype)

    # ── internals ────────────────────────────────────────────────────

    def _pick_reachable_pair(self):
        """Random (src_edge, dst_edge) pair with a valid path, or (None, None)."""
        for _ in range(MAX_REACHABILITY_RETRIES):
            src, dst = self._rng.sample(self._edge_objs, 2)
            path, _cost = self._net.getShortestPath(src, dst)
            if path:
                return src.getID(), dst.getID()
        return None, None

    def _spawn_one(self, vtype: str) -> Optional[str]:
        src, dst = self._pick_reachable_pair()
        if src is None:
            logger.debug("No reachable src/dst after %d tries", MAX_REACHABILITY_RETRIES)
            return None
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
            return vid
        except traci.exceptions.TraCIException as e:
            logger.debug("Could not spawn %s: %s", vid, e)
            return None

    def _spawn_batch(self) -> int:
        if not self._edges:
            return 0

        spawned = 0
        for _ in range(self.batch_size):
            vtype = self._rng.choices(self._vtypes, weights=self._weights, k=1)[0]
            if self._spawn_one(vtype) is not None:
                spawned += 1
        return spawned
