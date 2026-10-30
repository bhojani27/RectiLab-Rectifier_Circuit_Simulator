# RectiLab — Interactive Rectifier Circuit Simulator

RectiLab is a web-based, single-phase rectifier circuit simulator developed as an Object-Oriented Design and Analysis (OOAD) project. It allows users to select a rectifier topology, switching device, load model, and electrical parameters, then view simulated waveforms and related electrical measurements.

The application uses a Python/Flask backend for configuration validation, simulation, and analysis, and an HTML/CSS/JavaScript frontend for user interaction and visualization.

## Technology Stack

- **Backend:** Python, Flask, NumPy
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Plotly
- **Automated testing:** pytest
- **Circuit export:** PSpice-style `.cir` netlist generation

## Features

### 1. Rectifier Simulation

RectiLab provides four single-phase rectifier topology options:

1. Half-wave rectifier
2. Half-wave rectifier with a freewheeling diode
3. Full-wave centre-tapped rectifier
4. Full-wave bridge rectifier

The application provides two switching-device options:

- **Diode (uncontrolled):** Conduction is determined by the input waveform and the implemented diode model.
- **Thyristor (controlled):** The user can specify a firing angle to control the start of conduction in the implemented switching model.

The available load models are:

- **Resistive (R):** Current is calculated using the applied load voltage and resistance.
- **Resistive-inductive (R–L):** Current is calculated using a numerical time-step method that accounts for the inductor's effect on current.

Users can configure source peak voltage, frequency, resistance, inductance, firing angle, and number of cycles, subject to the selected configuration.

### 2. Waveform Visualization and Analysis

- Interactive source-voltage, load-voltage, and load-current waveform charts.
- Peak, average, and RMS measurements.
- Harmonic spectrum analysis.
- Total harmonic distortion (THD) calculation.
- Power-factor calculation.
- Comparison with theoretical values for supported resistive-load cases.
- Graph toolbar options for Download PNG, Zoom In, and Zoom Out.

### 3. Dynamic Circuit Schematic Visualization

RectiLab includes a **Circuit Schematic** section that displays a visual representation of the selected rectifier circuit.

The diagrams are generated dynamically using SVG through `static/js/schematics.js`.

The schematic updates automatically when the user changes the selected configuration.

The feature provides diagrams for:

- **Half-wave rectifier:** Displays the AC source, switching device, and load.
- **Half-wave rectifier with a freewheeling diode:** Displays the main switching device and the additional freewheeling diode.
- **Full-wave centre-tapped rectifier:** Displays the centre-tapped source arrangement and two rectifying branches.
- **Full-wave bridge rectifier:** Displays the four switching branches arranged in a bridge configuration.

The schematic also reflects the selected switching device:

- Diode (uncontrolled)
- Thyristor (controlled)

It also displays the selected load type:

- Resistive (R)
- Resistive-inductive (R–L)

For controlled devices, the selected firing angle is displayed as part of the schematic information.

The schematic is intended as a visual aid for understanding the selected circuit. It is an illustrative representation and should not be treated as an independently validated electrical drawing or a replacement for the numerical simulation model.

### 4. Data and Circuit Export

- **CSV Export:** Downloads waveform samples from the most recent simulation.
- **PSpice-style Netlist Export:** Generates a `.cir` text file describing the selected supported circuit configuration.

The netlist exporter is separate from the Python numerical simulator.

Successfully downloading a `.cir` file does not by itself prove that the circuit will run correctly or produce identical results in PSpice or another SPICE-compatible simulator.

## Current Simulation Scope and Limitations

The current implementation has configuration restrictions.

In particular:

- R–L numerical simulation is enabled for the **full-wave bridge with an uncontrolled diode** and the **full-wave centre-tapped rectifier with an uncontrolled diode**.
- Other R–L combinations are currently unsupported and are rejected by the simulation service.
- Theoretical validation is provided for supported resistive-load cases. The same theoretical validation table is not currently provided for R–L cases.
- Diode and thyristor behaviour is represented using simplified numerical switching models. The application is an educational simulator and does not model every non-ideal electrical effect of physical components.
- Controlled-device netlist export uses ideal switch approximations. These switches do not reproduce all physical thyristor characteristics, such as full latching and recovery behaviour.
- R–L netlist export is currently limited to the full-wave bridge with an uncontrolled diode.
- Generated netlists have not yet been independently validated for every supported circuit by running them in PSpice or another SPICE-compatible simulator.
- The numerical simulator and netlist exporter are separate implementations. A configuration working in the web simulator does not automatically establish that its exported netlist is electrically equivalent.
- The circuit schematic visualization is illustrative and has not been independently validated as a complete electrical design.
- Plotly is loaded from a public CDN, so an internet connection is required for interactive charts to load.

Only configurations explicitly supported by the application should be presented as implemented. Additional combinations should be enabled only after their simulation behaviour has been checked.

## Requirements

- Python 3.10 or a compatible newer version.
- A modern web browser.
- Internet access for loading Plotly from its public CDN.
- Python packages listed in `requirements.txt`.

## Setup and Run on Windows

Open the project folder in VS Code and select **Terminal → New Terminal**.

Make sure the terminal is in the project root, which contains `app.py` and `requirements.txt`.

### 1. Create a Virtual Environment

```powershell
py -m venv .venv
```

### 2. Install Dependencies

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

If pytest is not included in `requirements.txt`, install it separately:

```powershell
.\.venv\Scripts\python.exe -m pip install pytest
```

### 3. Start the Application

```powershell
.\.venv\Scripts\python.exe app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

Keep the terminal open while using RectiLab.

To stop the Flask development server, press `Ctrl + C` in the terminal.

### Optional: Activate the Virtual Environment

In PowerShell, run:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, the terminal prompt should display `(.venv)`.

You can then use:

```powershell
python app.py
```

To deactivate the environment, run:

```powershell
deactivate
```

## Using RectiLab

1. Start the Flask application and open `http://127.0.0.1:5000`.
2. Select a rectifier topology.
3. Select a diode or thyristor switching device.
4. Select a resistive (R) or resistive-inductive (R–L) load.
5. Enter the source and load parameters required for the selected configuration.
6. Inspect the **Circuit Schematic** section. Its diagram updates when the selected topology, switching device, or load changes.
7. Click **Run Simulation** to calculate the circuit response.
8. Inspect the waveform charts and electrical measurements.
9. Open the Harmonics and Validation tabs to view the available analysis.
10. Use **Export CSV** to download waveform samples or **Export PSpice netlist** to download a circuit description for a supported configuration.

If a selected combination is unsupported, the application should display an error rather than silently running an unsupported model.

## Application Workflow

A typical simulation request follows this sequence:

1. `templates/index.html` displays the user interface and input controls.
2. `static/js/app.js` reads the selected values and sends a JSON request to the Flask API.
3. `routes/simulation_routes.py` receives the request at `POST /api/simulate`.
4. `models/simulation_config.py` validates the input and creates a configuration object.
5. `simulation/simulation_service.py` creates the AC source and load, checks supported combinations, and coordinates the simulation.
6. `simulation/rectifier_factory.py` selects and creates the appropriate rectifier and switching-device objects.
7. `simulation/rectifiers.py` generates time samples and calculates source voltage, load voltage, load current, and source current using the selected models.
8. `simulation/analysis_service.py` calculates measurements, harmonic information, THD, power factor, and theoretical comparisons where supported.
9. The simulation service prepares a JSON-compatible response. Flask returns it to the browser.
10. `static/js/app.js` updates the measurement cards and uses Plotly to draw the waveforms and analysis charts.

The schematic display follows a separate frontend path:

- `static/js/schematics.js` reads the selected topology, switching device, and load values.
- It selects the corresponding schematic-generation function.
- The function generates an SVG representation of the circuit.
- The generated SVG is inserted into the schematic container in `templates/index.html`.

CSV export is assembled in the browser from the most recent simulation result.

Netlist export follows a separate API path:

1. JavaScript sends a request to `POST /api/export/netlist`.
2. Flask receives the selected configuration.
3. `export/netlist_exporter.py` generates the `.cir` content.
4. Flask returns the generated file for download.

## Project Structure

```text
RectiLab/
│
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
│   │
│   └── js/
│       ├── app.js
│       └── schematics.js
│
└── tests/
    ├── test_loads.py
    ├── test_netlist_exporter.py
    ├── test_rectifier_factory.py
    ├── test_simulation.py
    ├── test_switching_devices.py
    └── test_waveform.py
```

## Main Modules

- **`app.py`** — Creates and starts the Flask application.
- **`models/ac_source.py`** — Represents the AC source and calculates its voltage at sampled time points.
- **`models/loads.py`** — Defines the common load interface and the R and R–L load calculations.
- **`models/simulation_config.py`** — Stores and validates the user's simulation settings.
- **`models/switching_devices.py`** — Defines the diode and thyristor switching behaviour.
- **`models/waveform.py`** — Provides a waveform data structure for sampled values.
- **`simulation/rectifiers.py`** — Defines the common rectifier simulation workflow and topology-specific rectifier classes.
- **`simulation/rectifier_factory.py`** — Centralizes the creation of the selected rectifier and switching-device objects.
- **`simulation/simulation_service.py`** — Coordinates configuration validation, object creation, simulation, analysis, and response preparation.
- **`simulation/analysis_service.py`** — Calculates electrical measurements, harmonic information, THD, power factor, and theoretical comparisons for supported cases.
- **`routes/simulation_routes.py`** — Defines the API endpoints used by the frontend.
- **`export/netlist_exporter.py`** — Generates PSpice-style `.cir` netlist text for supported configurations.
- **`templates/index.html`** — Contains the web page structure and interface elements, including the schematic container.
- **`static/css/style.css`** — Styles the web interface and schematic display.
- **`static/js/app.js`** — Handles user interaction, API requests, results, charts, tabs, and browser-side CSV export.
- **`static/js/schematics.js`** — Creates and updates SVG circuit diagrams based on the selected configuration.
- **`tests/`** — Contains automated tests for selected model, factory, simulation, waveform, and netlist behaviours.
- **`pytest.ini`** — Configures pytest to discover tests in `tests/` and include the project root on the Python import path.

## API Endpoints

### `POST /api/simulate`

Accepts the selected simulation configuration as JSON.

On success, it returns:

- Selected configuration.
- Calculated electrical measurements.
- Available theoretical validation results.
- Sampled waveform data.

Invalid input and unsupported configurations are returned as errors.

### `POST /api/export/netlist`

Accepts the selected configuration as JSON and returns a downloadable `rectilab_netlist.cir` file for supported configurations.

## Running Automated Tests

Run the automated test suite from the project root:

```powershell
pytest -q
```

The `pytest.ini` file contains:

```ini
[pytest]
pythonpath = .
testpaths = tests
```

If the pytest launcher has an environment-path problem, run pytest directly through the project's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The project has most recently been reported to have **42 passing tests**.

Test results can change when the code is modified, so run the suite again after making changes.

Automated tests verify only the behaviours they cover. They do not replace electrical validation of every circuit or independent SPICE validation of exported netlists.

## Object-Oriented Design

RectiLab separates electrical concepts into classes and modules.

Its design demonstrates the following OOAD concepts:

### Abstraction

Abstract base classes such as `Load`, `SwitchingDevice`, and `Rectifier` define common interfaces for their specialized implementations.

### Encapsulation

Classes keep related data and behaviour together. For example, `ACSource` stores source parameters and provides a method to calculate the corresponding voltage.

### Inheritance

Specialized load, switching-device, and rectifier classes reuse common base-class behaviour and interfaces.

### Polymorphism

The simulation can call a common operation such as `calculate_current()` while the selected load provides its own implementation.

### Factory Design Pattern

`RectifierFactory` centralizes the selection and creation of the required rectifier and switching-device objects.

### Template Method-Style Workflow

The base rectifier simulation method defines the common sequence of simulation steps, while topology-specific classes provide the varying calculations.

## Version Control Notes

The `.gitignore` file should exclude local and generated files such as:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.pytest_cache/
.env
.vscode/
```

Do not commit the virtual environment.

It can be recreated by installing the dependencies from `requirements.txt`.
