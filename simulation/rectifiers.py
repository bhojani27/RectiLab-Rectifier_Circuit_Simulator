from abc import ABC, abstractmethod
import numpy as np


class Rectifier(ABC):
    """Template Method: shared sampling and load-current steps for all topologies."""

    def __init__(self, config, switching_device):
        self.config = config
        self.switching_device = switching_device

    
    def simulate(self, source, load):
        """Generate voltage and current waveforms for the rectifier."""

        samples_per_cycle = 600
        count = self.config.cycles * samples_per_cycle
        duration = self.config.cycles / self.config.frequency

        time = np.linspace(
            0.0,
            duration,
            count,
            endpoint=False,
        )

        source_voltage = source.voltage_at(time)

        load_voltage = self.output_voltage(
            time,
            source_voltage,
        )

        time_step = time[1] - time[0]

        load_current = load.calculate_current(
            load_voltage,
            time_step,
            samples_per_cycle=samples_per_cycle,
        )

        source_current = self.input_current(
            source_voltage,
            load_voltage,
            load_current,
        )

        return {
            "time": time,
            "source_voltage": source_voltage,
            "load_voltage": load_voltage,
            "load_current": load_current,
            "source_current": source_current,
        }

    @abstractmethod
    def output_voltage(self, time, source_voltage):
        """Return the voltage applied to the load for this topology."""
        raise NotImplementedError

    @abstractmethod
    def input_current(self, source_voltage, load_voltage, load_current):
        """Return source current with the correct sign convention."""
        raise NotImplementedError


class HalfWaveRectifier(Rectifier):
    def output_voltage(self, time, source_voltage):
        phase = (
            2 * np.pi * self.config.frequency * time
        ) % (2 * np.pi)

        conducting = self.switching_device.allows_conduction(
            phase
        )

        return np.where(
            conducting,
            np.maximum(source_voltage, 0.0),
            0.0,
        )

    def input_current(self, source_voltage, load_voltage, load_current):
        return np.where(load_voltage > 0, load_current, 0.0)


class FullWaveRectifier(Rectifier):
    def output_voltage(self, time, source_voltage):
        phase = (
            2 * np.pi * self.config.frequency * time
        ) % np.pi

        conducting = self.switching_device.allows_conduction(
            phase
        )

        return np.where(
            conducting,
            np.abs(source_voltage),
            0.0,
        )

    def input_current(self, source_voltage, load_voltage, load_current):
        return np.where(load_voltage > 0, np.sign(source_voltage) * load_current, 0.0)


class HalfWaveFreewheelingRectifier(HalfWaveRectifier):
    """Half-wave rectifier with a freewheeling diode."""

    topology_name = "Half-wave + freewheeling diode"


class FullWaveCentreTappedRectifier(FullWaveRectifier):
    """Full-wave rectifier using a centre-tapped transformer."""

    topology_name = "Full-wave centre-tapped"


class FullWaveBridgeRectifier(FullWaveRectifier):
    """Full-wave rectifier using a diode bridge."""

    topology_name = "Full-wave bridge"
