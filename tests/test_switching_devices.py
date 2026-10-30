
import math
import pytest
import numpy as np

from models.switching_devices import Diode, Thyristor, SwitchingDevice


def test_diode_implements_switching_device():
    assert isinstance(Diode(), SwitchingDevice)


def test_diode_allows_conduction_in_half_cycle():
    diode = Diode()

    assert diode.allows_conduction(0)
    assert diode.allows_conduction(math.pi / 2)
    assert diode.allows_conduction(math.pi)


def test_thyristor_respects_firing_angle():
    thyristor = Thyristor(30)

    assert not thyristor.allows_conduction(math.radians(20))
    assert thyristor.allows_conduction(math.radians(30))
    assert thyristor.allows_conduction(math.radians(90))


def test_thyristor_rejects_invalid_firing_angle():
    with pytest.raises(ValueError):
        Thyristor(181)


def test_thyristor_implements_switching_device():
    assert isinstance(Thyristor(30), SwitchingDevice)

def test_diode_handles_phase_array():
    diode = Diode()

    phases = np.array([
        0,
        np.pi / 2,
        3 * np.pi / 2,
    ])

    result = diode.allows_conduction(phases)

    assert result.tolist() == [True, True, False]


def test_thyristor_handles_phase_array():
    thyristor = Thyristor(30)

    phases = np.radians([20, 30, 90])

    result = thyristor.allows_conduction(phases)

    assert result.tolist() == [False, True, True]