import numpy as np


def summarize(results):
    v = results["load_voltage"]
    i = results["load_current"]
    source_v = results["source_voltage"]
    source_i = results["source_current"]
    v_rms_source = float(np.sqrt(np.mean(source_v ** 2)))
    i_rms_source = float(np.sqrt(np.mean(source_i ** 2)))
    denominator = v_rms_source * i_rms_source
    pf = float(np.mean(source_v * source_i) / denominator) if denominator else 0.0

    n = len(source_i)
    spectrum = np.fft.rfft(source_i)
    amplitudes = 2.0 * np.abs(spectrum) / n
    harmonics = []
    fundamental = 0.0
    cycle_count = n // 600
    for order in range(1, 26):
        index = order * cycle_count
        if index >= len(amplitudes):
            break
        magnitude = float(amplitudes[index])
        harmonics.append({"order": order, "magnitude": magnitude})
        if order == 1:
            fundamental = magnitude
    harmonic_rms_sq = sum(h["magnitude"] ** 2 for h in harmonics if h["order"] >= 2)
    thd = float(np.sqrt(harmonic_rms_sq) / fundamental * 100) if fundamental > 1e-12 else 0.0

    return {
        "vpeak": float(np.max(np.abs(v))),
        "vavg": float(np.mean(v)),
        "vrms": float(np.sqrt(np.mean(v ** 2))),
        "ipeak": float(np.max(np.abs(i))),
        "iavg": float(np.mean(i)),
        "irms": float(np.sqrt(np.mean(i ** 2))),
        "source_vrms": v_rms_source,
        "source_irms": i_rms_source,
        "power_factor": max(-1.0, min(1.0, pf)),
        "thd_percent": thd,
        "harmonics": harmonics,
    }


def analytical_values(config):
    """Ideal analytical load voltage values for an R load only."""
    vm = config.amplitude
    controlled = config.device == "Thyristor (controlled)"
    alpha = np.deg2rad(config.firing_angle_deg) if controlled else 0.0
    if config.topology in {"Half-wave", "Half-wave + freewheeling diode"}:
        average = vm * (1 + np.cos(alpha)) / (2 * np.pi) if controlled else vm / np.pi
        rms = (vm / 2) * np.sqrt(max(0.0, 1 - alpha / np.pi + np.sin(2 * alpha) / (2 * np.pi))) if controlled else vm / 2
    else:
        factor = np.sqrt(max(0.0, 1 - alpha / np.pi + np.sin(2 * alpha) / (2 * np.pi)))
        average = vm * (1 + np.cos(alpha)) / np.pi if controlled else 2 * vm / np.pi
        rms = (vm / np.sqrt(2)) * factor if controlled else vm / np.sqrt(2)
    return {"vavg": float(average), "vrms": float(rms)}


def build_validation(metrics, theory):
    rows = []
    for key, title in [("vavg", "Average load voltage"), ("vrms", "RMS load voltage")]:
        numerical = metrics[key]
        analytical = theory[key]
        error = abs(numerical - analytical) / abs(analytical) * 100 if analytical else 0.0
        rows.append({
            "quantity": title,
            "numerical": numerical,
            "analytical": analytical,
            "error_percent": error,
        })
    return rows
