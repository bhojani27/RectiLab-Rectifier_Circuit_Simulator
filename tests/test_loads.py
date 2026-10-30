import pytest
from models.loads import ResistiveLoad
import numpy as np
from models.loads import Load, ResistiveLoad, ResistiveInductiveLoad
from models.simulation_config import SimulationConfig
from simulation.simulation_service import create_load
from models.loads import ResistiveInductiveLoad

def test_calculate_current():
    load = ResistiveLoad(10)

    assert load.current(100) == 10


def test_reject_zero_resistance():
    with pytest.raises(ValueError):
        ResistiveLoad(0)

def test_rl_current_derivative():
    load = ResistiveInductiveLoad(10, 0.5)
    derivative = load.current_derivative(100, 0)

    assert derivative == 200

def test_rl_current_update():
    load = ResistiveInductiveLoad(10, 0.5)

    next_current = load.update_current(100, 0, 0.001)
    expected = 10 * (1 - np.exp(-0.02))
    assert abs(next_current - expected) < 1e-9

def test_rl_load_rejects_zero_inductance():
    import pytest

    with pytest.raises(ValueError):
        ResistiveInductiveLoad(10, 0)

def test_both_loads_implement_common_interface():
    resistive = ResistiveLoad(10)
    inductive = ResistiveInductiveLoad(10, 0.5)

    assert isinstance(resistive, Load)
    assert isinstance(inductive, Load)


def test_resistive_load_calculates_voltage_samples():
    load = ResistiveLoad(10)

    result = load.calculate_current(
        np.array([0, 50, 100]),
        0.001,
    )

    assert np.allclose(result, [0, 5, 10])

def test_rl_load_calculates_current_sequentially():
    load = ResistiveInductiveLoad(10, 0.5)

    result = load.calculate_current(
        np.array([100, 100, 100]),
        0.001,
    )

    expected = [
        0,
        10 * (1 - np.exp(-0.02)),
        10 * (1 - np.exp(-0.04)),
    ]

    assert np.allclose(result, expected)

def make_config(load_type):
    return SimulationConfig.from_payload({
        "topology": "Full-wave bridge",
        "device": "Diode (uncontrolled)",
        "load_type": load_type,
        "amplitude": 100,
        "frequency": 50,
        "resistance": 10,
        "inductance": 0.05,
        "firing_angle_deg": 30,
        "cycles": 3,
    })


def test_create_resistive_load():
    load = create_load(make_config("Resistive (R)"))

    assert isinstance(load, ResistiveLoad)
    assert load.resistance == 10


def test_create_resistive_inductive_load():
    load = create_load(
        make_config("Resistive-inductive (R-L)")
    )

    assert isinstance(load, ResistiveInductiveLoad)
    assert load.resistance == 10
    assert load.inductance == 0.05


def test_rl_current_repeats_for_periodic_voltage():
    load = ResistiveInductiveLoad(10, 0.5)

    one_cycle = np.array([0, 50, 100, 50], dtype=float)
    voltage = np.tile(one_cycle, 3)

    current = load.calculate_current(
        voltage,
        0.001,
        samples_per_cycle=4,
    )

    assert np.allclose(
        current[:4],
        current[4:8],
        atol=1e-9,
    )

    assert np.allclose(
        current[4:8],
        current[8:12],
        atol=1e-9,
    )
