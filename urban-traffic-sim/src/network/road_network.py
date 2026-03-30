"""
RoadNetwork
===========
Loads and queries the SUMO .net.xml file via sumolib.
"""

import sumolib
from typing import List, Optional, Tuple


class RoadNetwork:
    def __init__(self, net_file: str):
        self.net_file = net_file
        self._net: Optional[sumolib.net.Net] = None

    def load(self) -> None:
        self._net = sumolib.net.readNet(self.net_file, withInternal=False)

    @property
    def net(self) -> sumolib.net.Net:
        if self._net is None:
            raise RuntimeError("Call load() before accessing the network.")
        return self._net

    def get_edge_ids(self) -> List[str]:
        return [e.getID() for e in self.net.getEdges()]

    def get_junction_ids(self) -> List[str]:
        return [n.getID() for n in self.net.getNodes()]

    def edge_length(self, edge_id: str) -> float:
        return self.net.getEdge(edge_id).getLength()

    def get_tl_junction_ids(self) -> List[str]:
        return [n.getID() for n in self.net.getNodes()
                if n.getType() == "traffic_light"]

    def total_road_length_km(self) -> float:
        return sum(e.getLength() for e in self.net.getEdges()) / 1000.0

    def summary(self) -> str:
        edges = len(self.get_edge_ids())
        junctions = len(self.get_junction_ids())
        tls = len(self.get_tl_junction_ids())
        km = self.total_road_length_km()
        return (f"Network: {edges} edges | {junctions} junctions | "
                f"{tls} traffic lights | {km:.1f} km total")
