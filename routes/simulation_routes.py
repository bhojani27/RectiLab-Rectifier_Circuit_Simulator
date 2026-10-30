
from flask import Blueprint, jsonify, request, Response

from models.simulation_config import SimulationConfig
from simulation.simulation_service import run_simulation
from export.netlist_exporter import generate_netlist


simulation_blueprint = Blueprint("simulation_api", __name__)


@simulation_blueprint.post("/api/simulate")
def simulate():
    """Run the circuit simulation and return its results."""

    payload = request.get_json(silent=True) or {}

    try:
        result = run_simulation(payload)
        return jsonify({"ok": True, "result": result})

    except NotImplementedError as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
            "kind": "not_implemented",
        }), 422

    except ValueError as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
            "kind": "validation",
        }), 400

    except Exception:
        return jsonify({
            "ok": False,
            "error": (
                "The simulation could not be completed. "
                "Check the terminal for details."
            ),
            "kind": "server_error",
        }), 500


@simulation_blueprint.post("/api/export/netlist")
def export_netlist():
    """Generate and download a PSpice-style netlist."""

    payload = request.get_json(silent=True) or {}

    try:
        config = SimulationConfig.from_payload(payload)
        netlist = generate_netlist(config)

        return Response(
            netlist,
            mimetype="text/plain",
            headers={
                "Content-Disposition": (
                    'attachment; filename="rectilab_netlist.cir"'
                )
            },
        )

    except NotImplementedError as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
            "kind": "not_implemented",
        }), 422

    except ValueError as exc:
        return jsonify({
            "ok": False,
            "error": str(exc),
            "kind": "validation",
        }), 400
