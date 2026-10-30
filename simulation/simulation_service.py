
from models.ac_source import ACSource
from models.loads import (
    ResistiveLoad,
    ResistiveInductiveLoad,
)
from models.simulation_config import SimulationConfig
from simulation.rectifier_factory import RectifierFactory
from simulation.analysis_service import (
    summarize,
    analytical_values,
    build_validation,
)


def create_load(config):
    """Create the load selected by the user."""

    if config.load_type == "Resistive (R)":
        return ResistiveLoad(config.resistance)

    if config.load_type == "Resistive-inductive (R-L)":
        return ResistiveInductiveLoad(
            config.resistance,
            config.inductance,
        )

    raise ValueError("Unsupported load type.")


def run_simulation(payload):
    """Run the selected rectifier simulation and prepare its results."""

    # Step 1: Validate the user's configuration.
    config = SimulationConfig.from_payload(payload)

    # Step 2: Limit R-L simulations to verified model configurations.
    if config.load_type == "Resistive-inductive (R-L)":
        supported_rl_case = (
            config.device == "Diode (uncontrolled)"
            and config.topology in {
                "Full-wave bridge",
                "Full-wave centre-tapped",
            }
        )

        if not supported_rl_case:
            raise NotImplementedError(
                "R-L simulation is currently supported only for "
                "full-wave bridge and full-wave centre-tapped "
                "rectifiers with an uncontrolled diode."
            )

    # Step 3: Create the source and load.
    source = ACSource(
        config.amplitude,
        config.frequency,
    )
    load = create_load(config)

    # Step 4: Create the selected rectifier.
    rectifier = RectifierFactory.create(config)

    # Step 5: Calculate electrical waveforms.
    results = rectifier.simulate(source, load)

    # Step 6: Calculate measurements.
    metrics = summarize(results)

    # Step 7: Validate against theory for resistive loads.
    if config.load_type == "Resistive (R)":
        theory = analytical_values(config)
        validation = build_validation(metrics, theory)
    else:
        validation = []

    # Step 8: Reduce the number of returned samples if necessary.
    stride = max(1, len(results["time"]) // 1800)

    # Step 9: Prepare the response for the frontend.
    response = {
        "config": {
            "topology": config.topology,
            "device": config.device,
            "load_type": config.load_type,
            "amplitude": config.amplitude,
            "frequency": config.frequency,
            "resistance": config.resistance,
            "inductance": config.inductance,
            "firing_angle_deg": config.firing_angle_deg,
            "cycles": config.cycles,
        },
        "metrics": metrics,
        "validation": validation,
        "waveform": {
            "time": results["time"][::stride].tolist(),
            "source_voltage": (
                results["source_voltage"][::stride].tolist()
            ),
            "load_voltage": (
                results["load_voltage"][::stride].tolist()
            ),
            "load_current": (
                results["load_current"][::stride].tolist()
            ),
            "source_current": (
                results["source_current"][::stride].tolist()
            ),
        },
    }

    return response