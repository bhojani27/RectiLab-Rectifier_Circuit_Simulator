
from simulation.rectifiers import (
    HalfWaveRectifier,
    HalfWaveFreewheelingRectifier,
    FullWaveCentreTappedRectifier,
    FullWaveBridgeRectifier,
)
from models.switching_devices import Diode, Thyristor


class RectifierFactory:
    """Creates the selected rectifier and switching device."""

    @staticmethod
    def create(config):
        if config.device == "Thyristor (controlled)":
            device = Thyristor(config.firing_angle_deg)
        else:
            device = Diode()

        if config.topology == "Half-wave":
            return HalfWaveRectifier(config, device)

        if config.topology == "Half-wave + freewheeling diode":
            return HalfWaveFreewheelingRectifier(config, device)

        if config.topology == "Full-wave centre-tapped":
            return FullWaveCentreTappedRectifier(config, device)

        if config.topology == "Full-wave bridge":
            return FullWaveBridgeRectifier(config, device)

        raise ValueError(
            f"Unsupported rectifier topology: {config.topology}"
        )
