from unittest.mock import patch, MagicMock
from src.simulation.statistics import StatisticsCollector

CFG = {
    "output": {"statistics_interval": 10, "output_dir": "/tmp"}
}


@patch("src.simulation.statistics.traci")
def test_snapshot_no_vehicles(mock_traci):
    mock_traci.vehicle.getIDList.return_value = []
    mock_traci.simulation.getStartingTeleportNumber.return_value = 0

    collector = StatisticsCollector(CFG)
    collector.step(10)
    df = collector.to_dataframe()

    assert len(df) == 1
    assert df.iloc[0]["vehicle_count"] == 0


@patch("src.simulation.statistics.traci")
def test_snapshot_with_vehicles(mock_traci):
    mock_traci.vehicle.getIDList.return_value = ["v0", "v1"]
    mock_traci.vehicle.getSpeed.side_effect = [10.0, 0.0]
    mock_traci.vehicle.getWaitingTime.side_effect = [0.0, 5.0]
    mock_traci.vehicle.getCO2Emission.side_effect = [100.0, 200.0]
    mock_traci.vehicle.getFuelConsumption.side_effect = [0.4, 0.6]
    mock_traci.simulation.getStartingTeleportNumber.return_value = 0

    collector = StatisticsCollector(CFG)
    collector.step(10)
    df = collector.to_dataframe()

    assert df.iloc[0]["vehicle_count"] == 2
    assert df.iloc[0]["mean_speed"] == 5.0
    assert df.iloc[0]["halting_vehicles"] == 1
