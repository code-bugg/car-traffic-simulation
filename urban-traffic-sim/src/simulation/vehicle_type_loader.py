"""
VehicleTypeLoader
=================
Registers custom vehicle types (car, bus, truck) into SUMO at startup
using values from config/simulation.yaml.
"""

import logging
import traci

logger = logging.getLogger(__name__)


class VehicleTypeLoader:
    def __init__(self, cfg: dict):
        self._types = cfg["traffic"]["vehicle_types"]

    def register(self) -> None:
        """Call once after TraCI is connected."""
        existing = traci.vehicletype.getIDList()
        for vt in self._types:
            if vt["id"] in existing:
                logger.debug("Vehicle type '%s' already defined in route file.", vt["id"])
                continue
            traci.vehicletype.copy("DEFAULT_VEHTYPE", vt["id"])
            traci.vehicletype.setAccel(vt["id"], vt["accel"])
            traci.vehicletype.setDecel(vt["id"], vt["decel"])
            traci.vehicletype.setMaxSpeed(vt["id"], vt["max_speed"])
            traci.vehicletype.setLength(vt["id"], vt["length"])
            r, g, b = (int(x) for x in vt["color"].split(","))
            traci.vehicletype.setColor(vt["id"], (r, g, b, 255))
            logger.info("Registered vehicle type: %s", vt["id"])
