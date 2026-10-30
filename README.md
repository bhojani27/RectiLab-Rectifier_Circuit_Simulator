# RectiLab — Interactive Rectifier Circuit Simulator

RectiLab is a web-based single-phase rectifier circuit simulator developed as an Object-Oriented Design and Analysis (OOAD) project. It lets users select a rectifier topology, switching device, load model, and electrical parameters, then view simulated voltage and current waveforms and related electrical measurements.

**Frontend:** HTML, CSS, JavaScript, Plotly  
**Backend:** Python, Flask, NumPy  
**Testing:** pytest

## Features

- Four single-phase rectifier topologies:
  - Half-wave rectifier
  - Half-wave rectifier with a freewheeling diode
  - Full-wave centre-tapped rectifier
  - Full-wave bridge rectifier
- Uncontrolled diode and controlled thyristor options with firing-angle input.
- Resistive (R) and resistive-inductive (R–L) load models.
- Configurable source peak voltage, frequency, resistance, inductance, firing angle, and number of cycles, subject to the selected configuration.
- Interactive voltage and current waveform charts.
- Peak, average, and RMS measurements.
- Harmonic spectrum, total harmonic distortion (THD), and power-factor analysis.
- Theoretical comparison for supported resistive-load configurations.
- CSV export of waveform samples.
- PSpice-style `.cir` netlist generation for supported configurations.
- Automated tests for models, simulation behaviour, rectifier selection, and netlist structure.

## Current simulation scope and limitations

The current implementation supports resistive-load simulations across the four listed topologies. Thyristor firing-angle control is implemented using a simplified switching model; it does not represent every physical characteristic of a real thyristor.

R–L numerical simulation is currently enabled for these configurations:

- Full-wave bridge with an uncontrolled diode.
- Full-wave centre-tapped with an uncontrolled diode.

Other R–L combinations are rejected with a message indicating that the configuration is not currently supported.

Analytical validation is provided for supported resistive-load cases. R–L cases do not currently use the same theoretical validation table.

The `.cir` exporter generates a **PSpice-style netlist**. It has not yet been independently validated by running every generated circuit in PSpice or another SPICE-compatible simulator. Controlled-device exports use ideal switch approximations rather than a full physical thyristor model. R–L netlist export is currently limited to a full-wave bridge with an uncontrolled diode.

The numerical simulator and netlist exporter are separate implementations. A simulation working in the RectiLab web app does not, by itself, prove that the exported netlist will run or produce identical results in a SPICE simulator.

Plotly is loaded from a public CDN, so the browser needs internet access to render the interactive charts.

## Requirements

- Python 3.10 or a compatible newer Python version.
- A modern web browser.
- Internet access for loading Plotly from its CDN.

The Python packages used by the project are listed in `requirements.txt`.

## Setup and run on Windows

Open the project folder in VS Code, then open **Terminal → New Terminal**.

Create a virtual environment:

```powershell
py -m venv .venv
```

Install the dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Start the application:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open this address in your browser:

```text
http://127.0.0.1:5000
```

Keep the terminal open while using the application. Stop the Flask server with `Ctrl+C` in that terminal.

If you prefer to activate the virtual environment first, use:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks virtual-environment activation, use the direct `.venv\Scripts\python.exe` commands shown above.

## Using RectiLab

1. Start the application and open `http://127.0.0.1:5000`.
2. Select the rectifier topology, switching device, and load type.
3. Enter the required electrical parameters. Use values allowed for the selected configuration.
4. Click **Run Simulation**.
5. Inspect the waveform charts and electrical measurements.
6. Open the Harmonics or Validation tabs to view the available analysis.
7. Use **Export CSV** to download waveform samples or **Export PSpice netlist** to download the circuit description for a supported configuration.

The graph toolbar is configured to show Download PNG, Zoom In, and Zoom Out. Some fields are only applicable to particular device or load selections.

## Application workflow

A typical simulation request follows this path:

1. `templates/index.html` presents the user interface.
2. `static/js/app.js` collects the inputs and sends a JSON request to the Flask API.
3. `routes/simulation_routes.py` receives the request at `POST /api/simulate`.
4. `models/simulation_config.py` validates the configuration.
5. `simulation/simulation_service.py` creates the source and load, asks the rectifier factory for the selected topology, and runs the simulation.
6. `simulation/rectifiers.py` generates the sampled voltage and current waveforms using the selected circuit model.
7. `simulation/analysis_service.py` calculates measurements, harmonics, THD, power factor, and theoretical comparisons where supported.
8. Flask returns the results as JSON.
9. `static/js/app.js` updates the page and uses Plotly to render the charts.

CSV export is assembled in the browser from the most recent simulation data. Netlist export follows a separate request path to `POST /api/export/netlist`, where `export/netlist_exporter.py` generates the `.cir` text.

## Project organization

```text
RectiLab/
├── app.py
├── requirements.txt
├── pytest.ini
├── README.md
│
├── models/
│   ├── ac_source.py
│   ├── loads.py
│   ├── simulation_config.py
│   ├── switching_devices.py
│   └── waveform.py
│
├── simulation/
│   ├── rectifiers.py
│   ├── rectifier_factory.py
│   ├── simulation_service.py
│   └── analysis_service.py
│
├── routes/
│   └── simulation_routes.py
│
├── export/
│   └── netlist_exporter.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
└── tests/
    ├── test_loads.py
    ├── test_netlist_exporter.py
    ├── test_rectifier_factory.py
    ├── test_simulation.py
    ├── test_switching_devices.py
    └── test_waveform.py
```
