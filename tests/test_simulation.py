from simulation.simulation_service import run_simulation
import math
import pytest

def base_payload(**overrides):
    payload = {
        "topology": "Full-wave bridge",
        "device": "Diode (uncontrolled)",
        "load_type": "Resistive (R)",
        "amplitude": 100,
        "frequency": 50,
        "resistance": 10,
        "inductance": 0.05,
        "firing_angle_deg": 30,
        "cycles": 3,
    }
    payload.update(overrides)
    return payload


def test_full_wave_bridge_default_metrics_near_ideal_values():
    result = run_simulation(base_payload())
    metrics = result["metrics"]
    assert abs(metrics["vpeak"] - 100) < 0.1
    assert abs(metrics["vavg"] - (200 / 3.141592653589793)) < 0.2
    assert abs(metrics["vrms"] - (100 / (2 ** 0.5))) < 0.2


def test_rejects_zero_frequency():
    try:
        run_simulation(base_payload(frequency=0))
    except ValueError as exc:
        assert "Frequency" in str(exc)
    else:
        raise AssertionError("Expected invalid frequency to be rejected")

def test_unsupported_rl_configuration_is_rejected():
    with pytest.raises(NotImplementedError):
        run_simulation(
            base_payload(
                topology="Half-wave",
                device="Diode (uncontrolled)",
                load_type="Resistive-inductive (R-L)",
            )
        )

def test_thyristor_firing_angle_reduces_average_voltage():
    diode_result = run_simulation(
        base_payload(
            topology="Half-wave",
            device="Diode (uncontrolled)",
        )
    )

    thyristor_result = run_simulation(
        base_payload(
            topology="Half-wave",
            device="Thyristor (controlled)",
            firing_angle_deg=60,
        )
    )

    diode_average = diode_result["metrics"]["vavg"]
    thyristor_average = thyristor_result["metrics"]["vavg"]

    assert diode_average > 0
    assert thyristor_average > 0
    assert thyristor_average < diode_average

def test_half_wave_thyristor_matches_analytical_average():
    result = run_simulation(
        base_payload(
            topology="Half-wave",
            device="Thyristor (controlled)",
            firing_angle_deg=60,
        )
    )

    calculated_average = result["metrics"]["vavg"]

    amplitude = 100
    firing_angle = math.radians(60)

    expected_average = (
        amplitude * (1 + math.cos(firing_angle))
        / (2 * math.pi)
    )

    assert abs(calculated_average - expected_average) < 0.2

@pytest.mark.parametrize(
    ("topology", "expected_average", "expected_rms"),
    [
        ("Half-wave", 100 / math.pi, 50.0),
        ("Half-wave + freewheeling diode", 100 / math.pi, 50.0),
        ("Full-wave centre-tapped", 200 / math.pi, 100 / math.sqrt(2)),
        ("Full-wave bridge", 200 / math.pi, 100 / math.sqrt(2)),
    ],
)
def test_rectifier_topology_voltage_values(
    topology, expected_average, expected_rms
):
    result = run_simulation(
        base_payload(
            topology=topology,
            device="Diode (uncontrolled)",
            load_type="Resistive (R)",
        )
    )

    metrics = result["metrics"]

    assert abs(metrics["vavg"] - expected_average) < 0.2
    assert abs(metrics["vrms"] - expected_rms) < 0.2


@pytest.mark.parametrize(
    ("topology", "expected_average", "expected_rms"),
    [
        (
            "Half-wave",
            100 * (1 + math.cos(math.pi / 6)) / (2 * math.pi),
            50 * math.sqrt(
                1 - 1 / 6 + math.sin(math.pi / 3) / (2 * math.pi)
            ),
        ),
        (
            "Full-wave bridge",
            100 * (1 + math.cos(math.pi / 6)) / math.pi,
            (100 / math.sqrt(2)) * math.sqrt(
                1 - 1 / 6 + math.sin(math.pi / 3) / (2 * math.pi)
            ),
        ),
    ],
)

def test_controlled_rectifier_matches_analytical_values(
    topology, expected_average, expected_rms
):
    result = run_simulation(
        base_payload(
            topology=topology,
            device="Thyristor (controlled)",
            load_type="Resistive (R)",
            firing_angle_deg=30,
        )
    )

    metrics = result["metrics"]

    assert abs(metrics["vavg"] - expected_average) < 0.2
    assert abs(metrics["vrms"] - expected_rms) < 0.2


def test_rl_full_wave_bridge_returns_valid_current_waveform():
    result = run_simulation(
        base_payload(
            topology="Full-wave bridge",
            device="Diode (uncontrolled)",
            load_type="Resistive-inductive (R-L)",
            resistance=10,
            inductance=0.05,
        )
    )

    waveform = result["waveform"]
    current = waveform["load_current"]

    assert len(waveform["time"]) > 0
    assert len(current) == len(waveform["time"])
    assert all(math.isfinite(value) for value in current)
    assert all(value >= -1e-9 for value in current)
    assert result["metrics"]["irms"] > 0
    assert result["validation"] == []


def test_rl_current_repeats_across_simulation_cycles():
    result = run_simulation(
        base_payload(
            topology="Full-wave bridge",
            device="Diode (uncontrolled)",
            load_type="Resistive-inductive (R-L)",
            resistance=10,
            inductance=0.05,
            cycles=3,
        )
    )

    current = result["waveform"]["load_current"]
    samples_per_cycle = 600

    first_cycle = current[:samples_per_cycle]
    second_cycle = current[samples_per_cycle:2 * samples_per_cycle]
    third_cycle = current[2 * samples_per_cycle:3 * samples_per_cycle]

    assert len(current) == 3 * samples_per_cycle

    assert all(
        abs(a - b) < 1e-8
        for a, b in zip(first_cycle, second_cycle)
    )

    assert all(
        abs(a - b) < 1e-8
        for a, b in zip(second_cycle, third_cycle)
    )


def test_full_wave_bridge_analysis():
    result = run_simulation(
        base_payload(
            topology="Full-wave bridge",
            device="Diode (uncontrolled)",
            load_type="Resistive (R)",
        )
    )

    metrics = result["metrics"]

    # A bridge rectifier with an ideal resistor draws
    # a sinusoidal source current in phase with source voltage.
    assert abs(metrics["vrms"] - 100 / math.sqrt(2)) < 0.2
    assert abs(metrics["irms"] - (100 / math.sqrt(2)) / 10) < 0.02
    assert abs(metrics["power_factor"] - 1.0) < 0.01
    assert metrics["thd_percent"] < 0.1


def test_half_wave_power_factor():
    result = run_simulation(
        base_payload(
            topology="Half-wave",
            device="Diode (uncontrolled)",
            load_type="Resistive (R)",
        )
    )

    # Ideal half-wave rectification with a resistive load
    # has a true input power factor of approximately 1/sqrt(2).
    expected_power_factor = 1 / math.sqrt(2)

    assert abs(
        result["metrics"]["power_factor"] - expected_power_factor
    ) < 0.02
