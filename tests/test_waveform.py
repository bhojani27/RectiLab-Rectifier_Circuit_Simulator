import pytest
import numpy as np

from models.waveform import Waveform


def test_waveform_stores_samples():
    waveform = Waveform(
        time=[0, 0.005],
        source_voltage=[0, 100],
        load_voltage=[0, 100],
        load_current=[0, 10],
        source_current=[0, 10],
    )

    assert np.array_equal(waveform.time, [0, 0.005])
    assert np.array_equal(waveform.load_voltage, [0, 100])
    assert np.array_equal(waveform.load_current, [0, 10])


def test_waveform_rejects_mismatched_lengths():
    with pytest.raises(ValueError):
        Waveform(
            time=[0, 0.005],
            source_voltage=[0, 100],
            load_voltage=[0],
            load_current=[0, 10],
            source_current=[0, 10],
        )