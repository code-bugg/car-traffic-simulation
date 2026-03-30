import pytest
from src.network.road_network import RoadNetwork


def test_raises_before_load():
    rn = RoadNetwork("maps/chisinau.net.xml")
    with pytest.raises(RuntimeError, match="Call load()"):
        _ = rn.net
