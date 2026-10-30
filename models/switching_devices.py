
from abc import ABC, abstractmethod
import math
import numpy as np


class SwitchingDevice(ABC):
    """Common interface for rectifier switching devices."""

    @abstractmethod
    def allows_conduction(self, phase_angle_rad):
        """Check whether conduction is allowed at this phase angle."""
        raise NotImplementedError


class Diode(SwitchingDevice):
    """Ideal uncontrolled diode."""

    def allows_conduction(self, phase_angle_rad):
        phase = np.asarray(phase_angle_rad, dtype=float)

        return (phase >= 0) & (phase <= np.pi)


class Thyristor(SwitchingDevice):
    """Ideal controlled thyristor with a firing angle."""

    def __init__(self, firing_angle_deg):
        if not 0 <= firing_angle_deg <= 180:
            raise ValueError(
                "Firing angle must be between 0 and 180 degrees."
            )

        self.firing_angle_deg = float(firing_angle_deg)
        self.firing_angle_rad = math.radians(firing_angle_deg)

    def allows_conduction(self, phase_angle_rad):
        phase = np.asarray(phase_angle_rad, dtype=float)

        return (
            (phase >= self.firing_angle_rad)
            & (phase <= np.pi)
        )
