from unittest.mock import patch, MagicMock
from src.agents.vehicle import VehicleAgent, VehicleState


@patch("src.agents.vehicle.traci")
def test_get_state_fields(mock_traci):
    mock_traci.vehicle.getSpeed.return_value = 13.5
    mock_traci.vehicle.getPosition.return_value = (100.0, 200.0)
    mock_traci.vehicle.getLaneID.return_value = "E0_0"
    mock_traci.vehicle.getRoadID.return_value = "E0"
    mock_traci.vehicle.getWaitingTime.return_value = 2.0
    mock_traci.vehicle.getCO2Emission.return_value = 110.5
    mock_traci.vehicle.getFuelConsumption.return_value = 0.5

    agent = VehicleAgent("v_001")
    state = agent.get_state()

    assert isinstance(state, VehicleState)
    assert state.speed == 13.5
    assert state.waiting_time == 2.0
    assert state.co2_emission == 110.5


@patch("src.agents.vehicle.traci")
def test_set_speed_calls_traci(mock_traci):
    agent = VehicleAgent("v_002")
    agent.set_speed(5.0)
    mock_traci.vehicle.setSpeed.assert_called_once_with("v_002", 5.0)
