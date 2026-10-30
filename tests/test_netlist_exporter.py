
from models.simulation_config import SimulationConfig
from export.netlist_exporter import generate_netlist


def test_bridge_netlist_contains_circuit_components():
    config = SimulationConfig.from_payload({
        "topology": "Full-wave bridge",
        "device": "Diode (uncontrolled)",
        "load_type": "Resistive (R)",
        "amplitude": 100,
        "frequency": 50,
        "resistance": 10,
        "inductance": 0.05,
        "firing_angle_deg": 30,
        "cycles": 3,
    })

    netlist = generate_netlist(config)

    assert "SIN(0 100.0 50.0)" in netlist
    assert "RLOAD OUTP OUTN 10.0" in netlist
    assert "D1 AC1 OUTP DIDEAL" in netlist
    assert ".TRAN" in netlist
    assert netlist.strip().endswith(".END")

def test_controlled_bridge_netlist_has_four_switches():
    config = SimulationConfig.from_payload({
        "topology": "Full-wave bridge",
        "device": "Thyristor (controlled)",
        "load_type": "Resistive (R)",
        "amplitude": 100,
        "frequency": 50,
        "resistance": 10,
        "inductance": 0.05,
        "firing_angle_deg": 30,
        "cycles": 3,
    })

    netlist = generate_netlist(config)

    assert "S1 AC1 OUTP GATE1 0 SWMOD" in netlist
    assert "S2 AC2 OUTP GATE2 0 SWMOD" in netlist
    assert "S3 OUTN AC2 GATE1 0 SWMOD" in netlist
    assert "S4 OUTN AC1 GATE2 0 SWMOD" in netlist
    assert ".MODEL SWMOD VSWITCH" in netlist

def test_centre_tapped_netlist_connections():
    config = SimulationConfig.from_payload({
        "topology": "Full-wave centre-tapped",
        "device": "Diode (uncontrolled)",
        "load_type": "Resistive (R)",
        "amplitude": 100,
        "frequency": 50,
        "resistance": 10,
        "inductance": 0.05,
        "firing_angle_deg": 30,
        "cycles": 3,
    })

    netlist = generate_netlist(config)

    assert "VTOP SEC1 0 SIN(0 100.0 50.0)" in netlist
    assert "D1 SEC1 OUTP DIDEAL" in netlist
    assert "D2 SEC2 OUTP DIDEAL" in netlist
    assert "RLOAD OUTP 0 10.0" in netlist
    assert ".MODEL DIDEAL D" in netlist
    assert ".TRAN" in netlist
    assert netlist.strip().endswith(".END")