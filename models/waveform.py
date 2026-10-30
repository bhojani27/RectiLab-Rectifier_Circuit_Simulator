import numpy as np


class Waveform:
    """Stores the sampled electrical data from a simulation."""

    def __init__(
        self,
        time,
        source_voltage,
        load_voltage,
        load_current,
        source_current,
    ):
        self.time = np.asarray(time, dtype=float)
        self.source_voltage = np.asarray(source_voltage, dtype=float)
        self.load_voltage = np.asarray(load_voltage, dtype=float)
        self.load_current = np.asarray(load_current, dtype=float)
        self.source_current = np.asarray(source_current, dtype=float)

        if self.time.ndim != 1 or self.time.size == 0:
            raise ValueError("Time must contain at least one sample.")

        arrays = [
            self.source_voltage,
            self.load_voltage,
            self.load_current,
            self.source_current,
        ]

        for array in arrays:
            if array.ndim != 1 or array.size != self.time.size:
                raise ValueError(
                    "All waveform arrays must have the same number of samples."
                )