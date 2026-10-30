import math

def generate_netlist(config):
    """Generate a basic PSpice-style netlist for the selected circuit."""

    if (
        config.load_type == "Resistive-inductive (R-L)"
        and not (
            config.topology == "Full-wave bridge"
            and config.device == "Diode (uncontrolled)"
        )
    ):
        raise NotImplementedError(
            "R-L netlist export currently supports only "
            "a full-wave bridge with an uncontrolled diode."
        )

    vm = config.amplitude
    frequency = config.frequency
    resistance = config.resistance
    period = 1.0 / frequency
    half_period = period / 2
    stop_time = config.cycles / frequency
    time_step = period / 600

    controlled = config.device == "Thyristor (controlled)"
    alpha = (
        math.radians(config.firing_angle_deg)
        if controlled else 0.0
    )
    delay = alpha / (2 * math.pi * frequency)
    pulse_width = max(half_period - delay, 1e-12)

    lines = [
        "RectiLab - Rectifier Circuit",
        f"* Topology: {config.topology}",
        f"* Device: {config.device}",
        f"* Load: {config.load_type}",
        f"* Peak source voltage: {vm} V",
        f"* Frequency: {frequency} Hz"
        "",
    ]

    # Build the selected rectifier circuit.
    if config.topology in {
        "Half-wave",
        "Half-wave + freewheeling diode",
    }:
        lines.append(f"V1 IN 0 SIN(0 {vm} {frequency})")

        if controlled:
            lines.extend([
                "D1 IN N1 DIDEAL",
                (
                    f"VGATE1 GATE1 0 PULSE(0 5 "
                    f"{delay:.8e} 1e-9 1e-9 "
                    f"{pulse_width:.8e} {period:.8e})"
                ),
                "S1 N1 OUTP GATE1 0 SWMOD",
            ])
        else:
            lines.append("D1 IN OUTP DIDEAL")

        if config.topology == "Half-wave + freewheeling diode":
            lines.append("DFW 0 OUTP DIDEAL")

        positive_node = "OUTP"
        negative_node = "0"

    elif config.topology == "Full-wave centre-tapped":
        lines.extend([
            f"VTOP SEC1 0 SIN(0 {vm} {frequency})",
            f"VBOT SEC2 0 SIN(0 {vm} {frequency} 0 0 180)",
            ])

        if controlled:
            lines.extend([
                "D1 SEC1 N1 DIDEAL",
                (
                    f"VGATE1 GATE1 0 PULSE(0 5 "
                    f"{delay:.8e} 1e-9 1e-9 "
                    f"{pulse_width:.8e} {period:.8e})"
                ),
                "S1 N1 OUTP GATE1 0 SWMOD",
                "D2 SEC2 N2 DIDEAL",
                (
                    f"VGATE2 GATE2 0 PULSE(0 5 "
                    f"{(half_period + delay):.8e} "
                    f"1e-9 1e-9 {pulse_width:.8e} "
                    f"{period:.8e})"
                ),
                "S2 N2 OUTP GATE2 0 SWMOD",
            ])
        else:
            lines.extend([
                "D1 SEC1 OUTP DIDEAL",
                "D2 SEC2 OUTP DIDEAL",
            ])

        positive_node = "OUTP"
        negative_node = "0"

    else:  # Full-wave bridge
        lines.append(f"V1 AC1 AC2 SIN(0 {vm} {frequency})")
        lines.append("RREF AC2 0 1G")

        if controlled:
            lines.extend([
                (
                    f"VGATE1 GATE1 0 PULSE(0 5 "
                    f"{delay:.8e} 1e-9 1e-9 "
                    f"{pulse_width:.8e} {period:.8e})"
                ),
                (
                    f"VGATE2 GATE2 0 PULSE(0 5 "
                    f"{(half_period + delay):.8e} "
                    f"1e-9 1e-9 {pulse_width:.8e} "
                    f"{period:.8e})"
                ),
                "S1 AC1 OUTP GATE1 0 SWMOD",
                "S2 AC2 OUTP GATE2 0 SWMOD",
                "S3 OUTN AC2 GATE1 0 SWMOD",
                "S4 OUTN AC1 GATE2 0 SWMOD",
            ])

            positive_node = "OUTP"
            negative_node = "OUTN"

            if config.load_type == "Resistive-inductive (R-L)":
                lines.append("DFW RECTN OUTP DIDEAL")

            positive_node = "OUTP"
            negative_node = "OUTN"

        else:
            lines.extend([
                "D1 AC1 OUTP DIDEAL",
                "D2 AC2 OUTP DIDEAL",
                "D3 OUTN AC1 DIDEAL",
                "D4 OUTN AC2 DIDEAL",
            ])

            positive_node = "OUTP"
            negative_node = "OUTN"

    # Add the selected load.
    if config.load_type == "Resistive (R)":
        lines.append(
            f"RLOAD {positive_node} {negative_node} {resistance}"
        )
    else:
        lines.extend([
            f"RLOAD {positive_node} NLOAD {resistance}",
            f"LLOAD NLOAD {negative_node} {config.inductance}",
        ])

    # Declare device models and transient simulation settings.
    lines.extend([
        "",
        ".MODEL DIDEAL D",
    ])

    if controlled:
        lines.append(
            ".MODEL SWMOD VSWITCH "
            "(RON=0.01 ROFF=1E9 VON=2 VOFF=1)"
        )

    lines.extend([
        f".TRAN {time_step:.8e} {stop_time:.8e} "
        f"0 {time_step:.8e}",
        ".PROBE",
        ".END",
        "",
    ])

    return "\n".join(lines)
