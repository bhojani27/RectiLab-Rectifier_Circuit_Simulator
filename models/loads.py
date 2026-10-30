
from abc import ABC, abstractmethod
import numpy as np


class Load(ABC):
    """Common interface for electrical loads."""

    @abstractmethod
    def calculate_current(
        self, voltage, time_step, samples_per_cycle=None
    ):
        """Calculate current samples for the applied voltage."""
        raise NotImplementedError


class ResistiveLoad(Load):
    """Ideal resistor that follows Ohm's law."""

    def __init__(self, resistance: float):
        if resistance <= 0:
            raise ValueError(
                "Resistance must be greater than zero."
            )

        self.resistance = float(resistance)

    def current(self, voltage):
        """Calculate current directly using Ohm's law."""
        return voltage / self.resistance

    def calculate_current(
        self, voltage, time_step, samples_per_cycle=None
    ):
        """Calculate current for all voltage samples."""
        return (
            np.asarray(voltage, dtype=float)
            / self.resistance
        )


class ResistiveInductiveLoad(Load):
    """Load containing resistance and inductance."""

    def __init__(self, resistance: float, inductance: float):
        if resistance <= 0:
            raise ValueError(
                "Resistance must be greater than zero."
            )

        if inductance <= 0:
            raise ValueError(
                "Inductance must be greater than zero."
            )

        self.resistance = float(resistance)
        self.inductance = float(inductance)

    def current_derivative(self, voltage, current):
        """Calculate the rate of change of current."""
        return (
            voltage - self.resistance * current
        ) / self.inductance

    def update_current(self, voltage, current, time_step):
        """Update current assuming constant voltage over one time step."""
        if time_step <= 0:
            raise ValueError(
                "Time step must be greater than zero."
            )

        decay = np.exp(
            -self.resistance * time_step / self.inductance
        )

        return (
            current * decay
            + (voltage / self.resistance) * (1 - decay)
        )

    def calculate_current(
        self, voltage, time_step, samples_per_cycle=None
    ):
        """Calculate current samples sequentially."""

        if time_step <= 0:
            raise ValueError(
                "Time step must be greater than zero."
            )

        voltage_samples = np.asarray(voltage, dtype=float)

        if (
            voltage_samples.ndim != 1
            or voltage_samples.size == 0
        ):
            raise ValueError(
                "Voltage must be a non-empty one-dimensional array."
            )

        initial_current = 0.0

        if samples_per_cycle is not None:
            if (
                not isinstance(samples_per_cycle, (int, np.integer))
                or samples_per_cycle <= 0
                or samples_per_cycle > len(voltage_samples)
                or len(voltage_samples) % samples_per_cycle != 0
            ):
                raise ValueError(
                    "Samples per cycle must be a positive integer "
                    "that divides the total number of samples."
                )

            decay = np.exp(
                -self.resistance * time_step / self.inductance
            )

            # Simulate one cycle starting from zero current.
            cycle_end_current = 0.0

            for sample_voltage in voltage_samples[:samples_per_cycle]:
                cycle_end_current = self.update_current(
                    sample_voltage,
                    cycle_end_current,
                    time_step,
                )

            # Find the initial current that repeats after one cycle.
            decay_per_cycle = decay ** samples_per_cycle
            denominator = 1.0 - decay_per_cycle

            if denominator <= 0:
                raise ValueError(
                    "Unable to calculate periodic steady-state current."
                )

            initial_current = cycle_end_current / denominator

        current_samples = np.zeros_like(voltage_samples)
        current_samples[0] = initial_current

        for index in range(1, len(voltage_samples)):
            current_samples[index] = self.update_current(
                voltage_samples[index - 1],
                current_samples[index - 1],
                time_step,
            )

        return current_samples
