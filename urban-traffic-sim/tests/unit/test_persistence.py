from unittest.mock import MagicMock, patch
from src.simulation.persistence import VehiclePersistenceController


def _cfg(**overrides):
    base = {
        "traffic": {
            "persistence": {
                "never_despawn": True,
                "disable_teleport": True,
                "blocked_reroute": {
                    "enabled": True,
                    "speed_threshold": 0.3,
                    "patience_steps": 3,
                },
            }
        }
    }
    base["traffic"]["persistence"].update(overrides)
    return base


@patch("src.simulation.persistence.traci")
def test_arrival_triggers_respawn(mock_traci):
    mock_traci.simulation.getArrivedIDList.return_value = ["v_7", "static_42"]
    mock_traci.vehicle.getIDList.return_value = []

    spawner = MagicMock()
    spawner.respawn_like.return_value = "v_99"

    ctrl = VehiclePersistenceController(_cfg(), spawner)
    ctrl.step(sim_step=5)

    spawner.respawn_like.assert_called_once_with("v_7")


@patch("src.simulation.persistence.traci")
def test_stuck_vehicle_reroutes_after_patience(mock_traci):
    mock_traci.simulation.getArrivedIDList.return_value = []
    mock_traci.vehicle.getIDList.return_value = ["v_1"]
    mock_traci.vehicle.getSpeed.return_value = 0.0

    spawner = MagicMock()
    ctrl = VehiclePersistenceController(_cfg(), spawner)

    for step in range(3):
        ctrl.step(sim_step=step)

    mock_traci.vehicle.rerouteTraveltime.assert_called_once_with("v_1")


@patch("src.simulation.persistence.traci")
def test_moving_vehicle_not_rerouted(mock_traci):
    mock_traci.simulation.getArrivedIDList.return_value = []
    mock_traci.vehicle.getIDList.return_value = ["v_1"]
    mock_traci.vehicle.getSpeed.return_value = 8.0

    ctrl = VehiclePersistenceController(_cfg(), MagicMock())
    for step in range(5):
        ctrl.step(sim_step=step)

    mock_traci.vehicle.rerouteTraveltime.assert_not_called()


@patch("src.simulation.persistence.traci")
def test_static_vehicle_not_looped(mock_traci):
    """XML-defined vehicles (no v_ prefix) must not be respawned."""
    mock_traci.simulation.getArrivedIDList.return_value = ["car_0", "999"]
    mock_traci.vehicle.getIDList.return_value = []

    spawner = MagicMock()
    ctrl = VehiclePersistenceController(_cfg(), spawner)
    ctrl.step(sim_step=1)

    spawner.respawn_like.assert_not_called()
