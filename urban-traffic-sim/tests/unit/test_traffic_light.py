from unittest.mock import patch, MagicMock
from src.traffic_control.traffic_light import TrafficLightController, PhaseInfo


@patch("src.traffic_control.traffic_light.traci")
def test_get_phase_info(mock_traci):
    mock_traci.trafficlight.getPhase.return_value = 1
    mock_traci.trafficlight.getPhaseDuration.return_value = 30.0
    mock_traci.trafficlight.getRedYellowGreenState.return_value = "GGrrGGrr"
    mock_traci.trafficlight.getNextSwitch.return_value = 100.0
    mock_traci.simulation.getTime.return_value = 80.0

    ctrl = TrafficLightController("J1")
    info = ctrl.get_phase_info()

    assert isinstance(info, PhaseInfo)
    assert info.current_phase == 1
    assert info.state == "GGrrGGrr"


@patch("src.traffic_control.traffic_light.traci")
def test_set_phase(mock_traci):
    ctrl = TrafficLightController("J1")
    ctrl.set_phase(2)
    mock_traci.trafficlight.setPhase.assert_called_once_with("J1", 2)
