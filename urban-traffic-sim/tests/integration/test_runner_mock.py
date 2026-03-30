"""
Integration test: runs the SimulationRunner with all TraCI calls mocked,
verifying that the orchestration wiring works without a real SUMO install.
"""

from unittest.mock import patch, MagicMock, call
import pytest


@patch("src.simulation.runner.traci")
@patch("src.agents.spawner.traci")
@patch("src.agents.spawner.sumolib")
@patch("src.traffic_control.adaptive_controller.traci")
@patch("src.simulation.statistics.traci")
@patch("src.simulation.vehicle_type_loader.traci")
def test_runner_completes(
    mock_vt_traci, mock_stats_traci, mock_tl_traci,
    mock_sumolib, mock_spawn_traci, mock_runner_traci,
    tmp_path
):
    import yaml, os
    # Minimal config
    cfg = {
        "simulation": {"name": "test", "step_length": 1.0,
                       "total_steps": 3, "seed": 42, "warmup_steps": 0},
        "sumo": {"binary": "sumo",
                 "network_file": str(tmp_path / "test.net.xml"),
                 "route_file":   str(tmp_path / "test.rou.xml"),
                 "additional_files": []},
        "traffic": {
            "spawn_interval": 10, "batch_size": 2,
            "vehicle_types": [
                {"id": "car", "accel": 2.6, "decel": 4.5,
                 "max_speed": 13.89, "length": 4.5, "color": "255,255,0"}
            ]
        },
        "traffic_lights": {"adaptive": False,
                           "min_green_time": 10, "max_green_time": 90,
                           "congestion_threshold": 8},
        "output": {"statistics_interval": 1,
                   "output_dir": str(tmp_path / "output"),
                   "log_dir":    str(tmp_path / "logs")},
    }
    cfg_path = tmp_path / "sim.yaml"
    cfg_path.write_text(yaml.dump(cfg))

    # Mock sumolib net
    mock_net = MagicMock()
    mock_net.getEdges.return_value = []
    mock_sumolib.net.readNet.return_value = mock_net

    # Mock traci calls
    mock_runner_traci.vehicle.getIDList.return_value = []
    mock_stats_traci.vehicle.getIDList.return_value = []
    mock_stats_traci.simulation.getStartingTeleportNumber.return_value = 0
    mock_vt_traci.vehicletype.getIDList.return_value = ["DEFAULT_VEHTYPE"]
    mock_vt_traci.vehicletype.copy.return_value = None

    from src.simulation.runner import SimulationRunner
    runner = SimulationRunner(config_path=str(cfg_path))
    runner.run()

    assert runner.step_num == 3
    assert mock_runner_traci.simulationStep.call_count == 3
