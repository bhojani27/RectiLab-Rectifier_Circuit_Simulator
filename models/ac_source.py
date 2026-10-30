import numpy as np


class ACSource:
    """Ideal sinusoidal source with peak amplitude in volts and frequency in Hz."""

    def __init__(self, amplitude: float, frequency: float):
        if amplitude <= 0:
            raise ValueError("Peak source voltage must be greater than zero.")
        if frequency <= 0:
            raise ValueError("Frequency must be greater than zero.")
        self.amplitude = float(amplitude)
        self.frequency = float(frequency)

    def voltage_at(self, time):
        """Accept either a scalar time or a NumPy array of time samples."""
        return self.amplitude * np.sin(2 * np.pi * self.frequency * time)

    @property
    def period(self):
        return 1.0 / self.frequency
