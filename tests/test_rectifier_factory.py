
import pytest

from models.simulation_config import SimulationConfig
from simulation.rectifier_factory import RectifierFactory
from simulation.rectifiers import (
    HalfWaveRectifier,
    HalfWaveFreewheelingRectifier,
    FullWaveCentreTappedRectifier,
    FullWaveBridgeRectifier,
)


@pytest.mark.parametrize(
    ("topology", "expected_class"),
    [
        ("Half-wave", HalfWaveRectifier),
        ("Half-wave + freewheeling diode", HalfWaveFreewheelingRectifier),
        ("Full-wave centre-tapped", FullWaveCentreTappedRectifier),
        ("Full-wave bridge", FullWaveBridgeRectifier),
    ],
)
def test_factory_creates_selected_topology(topology, expected_class):
    config = SimulationConfig.from_payload({
        "topology": topology,
        "device": "Diode (uncontrolled)",
        "load_type": "Resistive (R)",
        "amplitude": 100,
        "frequency": 50,
        "resistance": 10,
        "inductance": 0.05,
        "firing_angle_deg": 30,
        "cycles": 3,
    })

    rectifier = RectifierFactory.create(config)

    assert type(rectifier) is expected_class
