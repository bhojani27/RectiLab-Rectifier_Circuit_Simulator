from dataclasses import dataclass


TOPOLOGIES = {
    "Half-wave",
    "Half-wave + freewheeling diode",
    "Full-wave centre-tapped",
    "Full-wave bridge",
}
DEVICES = {"Diode (uncontrolled)", "Thyristor (controlled)"}
LOAD_TYPES = {"Resistive (R)", "Resistive-inductive (R-L)"}


@dataclass(frozen=True)
class SimulationConfig:
    topology: str
    device: str
    load_type: str
    amplitude: float
    frequency: float
    resistance: float
    inductance: float
    firing_angle_deg: float
    cycles: int

    @classmethod
    def from_payload(cls, payload):
        try:
            config = cls(
                topology=str(payload["topology"]),
                device=str(payload["device"]),
                load_type=str(payload["load_type"]),
                amplitude=float(payload["amplitude"]),
                frequency=float(payload["frequency"]),
                resistance=float(payload["resistance"]),
                inductance=float(payload.get("inductance", 0.0)),
                firing_angle_deg=float(payload.get("firing_angle_deg", 0.0)),
                cycles=int(payload.get("cycles", 3)),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Please provide valid values for all visible fields.") from exc

        if config.topology not in TOPOLOGIES:
            raise ValueError("Select a supported rectifier topology.")
        if config.device not in DEVICES:
            raise ValueError("Select a supported switching device.")
        if config.load_type not in LOAD_TYPES:
            raise ValueError("Select a supported load type.")
        if config.amplitude <= 0:
            raise ValueError("Peak source voltage must be greater than zero.")
        if config.frequency <= 0:
            raise ValueError("Frequency must be greater than zero.")
        if config.resistance <= 0:
            raise ValueError("Resistance must be greater than zero.")
        if config.load_type == "Resistive-inductive (R-L)" and config.inductance <= 0:
            raise ValueError("Inductance must be greater than zero for an R-L load.")
        if config.device == "Thyristor (controlled)" and not 0 <= config.firing_angle_deg <= 180:
            raise ValueError("Firing angle must be between 0 and 180 degrees.")
        if not 1 <= config.cycles <= 5:
            raise ValueError("Choose between 1 and 5 source cycles.")

        return config
