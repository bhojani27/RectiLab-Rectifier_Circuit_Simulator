const form = document.getElementById("config-form");
const runButton = form.querySelector(".run-button");
const toast = document.getElementById("toast");
let latestResult = null;
let toastTimer = null;

const tabMeta = {
  simulation: [
    "SIMULATOR",
    "Rectifier simulator",
    "Configure a circuit, run the model, and inspect its electrical response.",
  ],
  harmonics: [
    "HARMONICS",
    "Harmonic analysis",
    "Inspect the source-current spectrum, total harmonic distortion, and input power factor.",
  ],
  validation: [
    "VALIDATION",
    "Analytical validation",
    "Compare sampled results with ideal formulas for supported circuits.",
  ],
  guide: [
    "QUICK GUIDE",
    "Quick guide",
    "A short guide to using the RectiLab workspace.",
  ],
};

function showToast(message, isSuccess = false) {
  toast.textContent = message;
  toast.classList.remove("hidden", "success");
  if (isSuccess) toast.classList.add("success");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("hidden"), 5000);
}

function setStatus(text, mode = "ready") {
  const badge = document.getElementById("run-status");
  badge.innerHTML = `<span class="status-dot"></span> ${text}`;
  const dot = badge.querySelector(".status-dot");
  dot.style.background =
    mode === "success"
      ? "var(--green)"
      : mode === "error"
        ? "var(--red)"
        : mode === "busy"
          ? "var(--cyan)"
          : "var(--amber)";
}

function openTab(tabName) {
  document.querySelectorAll(".nav-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tabName);
  });
  document.querySelectorAll(".tab-panel").forEach((panel) => {
    panel.classList.toggle("active", panel.id === `panel-${tabName}`);
  });
  const meta = tabMeta[tabName];
  document.getElementById("breadcrumb-current").textContent = meta[0];
  document.getElementById("page-title").textContent = meta[1];
  document.getElementById("page-subtitle").textContent = meta[2];
  if (tabName === "harmonics" && latestResult) drawHarmonics(latestResult);
  setTimeout(() => {
    if (window.Plotly) {
      ["waveform-chart", "harmonics-chart"].forEach((id) => {
        const el = document.getElementById(id);
        if (el && el.data) Plotly.Plots.resize(el);
      });
    }
  }, 50);
}

document.querySelectorAll(".nav-item").forEach((button) => {
  button.addEventListener("click", () => openTab(button.dataset.tab));
});

function updateConditionalFields() {
  const controlled =
    document.getElementById("device").value === "Thyristor (controlled)";
  const rl =
    document.getElementById("load_type").value === "Resistive-inductive (R-L)";
  document
    .getElementById("firing-wrap")
    .classList.toggle("hidden", !controlled);
  document.getElementById("inductance-wrap").classList.toggle("hidden", !rl);
}
document
  .getElementById("device")
  .addEventListener("change", updateConditionalFields);
document
  .getElementById("load_type")
  .addEventListener("change", updateConditionalFields);
updateConditionalFields();

function getConfig() {
  const data = new FormData(form);
  return {
    topology: data.get("topology"),
    device: data.get("device"),
    load_type: data.get("load_type"),
    amplitude: data.get("amplitude"),
    frequency: data.get("frequency"),
    resistance: data.get("resistance"),
    inductance: data.get("inductance") || "0",
    firing_angle_deg: data.get("firing_angle_deg") || "0",
    cycles: data.get("cycles"),
  };
}

function updateSummary(result) {
  const c = result.config;
  document.getElementById("summary-topology").textContent = c.topology
    .replace("Full-wave ", "")
    .replace("Half-wave + ", "");
  document.getElementById("summary-device").textContent = c.device.startsWith(
    "Thyristor",
  )
    ? "Thyristor"
    : "Diode";
  document.getElementById("summary-load").textContent = c.load_type.startsWith(
    "Resistive-inductive",
  )
    ? "R-L load"
    : "R load";
  document.getElementById("summary-resistance").textContent =
    `${formatNumber(c.resistance, 2)} Ω`;
  document.getElementById("summary-amplitude").textContent =
    `${formatNumber(c.amplitude, 2)} V`;
  document.getElementById("summary-frequency").textContent =
    `${formatNumber(c.frequency, 2)} Hz`;
  document.getElementById("summary-firing").textContent = c.device.startsWith(
    "Thyristor",
  )
    ? `${formatNumber(c.firing_angle_deg, 1)}°`
    : "Not applicable";
  document.getElementById("summary-pf").textContent = formatNumber(
    result.metrics.power_factor,
    3,
  );
  document.getElementById("summary-thd").textContent =
    `${formatNumber(result.metrics.thd_percent, 2)}%`;
}

function formatNumber(value, digits = 2) {
  if (!Number.isFinite(Number(value))) return "—";
  return Number(value).toLocaleString(undefined, {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  });
}

const plotLayoutBase = {
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: { family: "Inter, Segoe UI, sans-serif", color: "#9aacc5", size: 12 },
  margin: { l: 56, r: 20, t: 14, b: 48 },
  hovermode: "x unified",
  legend: { orientation: "h", y: 1.08, x: 0, font: { size: 11 } },
  xaxis: {
    title: "Time (s)",
    gridcolor: "#253650",
    zerolinecolor: "#30445e",
    linecolor: "#30445e",
  },
  yaxis: {
    gridcolor: "#253650",
    zerolinecolor: "#30445e",
    linecolor: "#30445e",
  },
};
const plotConfig = {
  responsive: true,
  displaylogo: false,
  modeBarButtonsToRemove: [
    "lasso2d",
    "select2d",
    "zoom2d",
    "pan2d",
    "autoScale2d",
    "resetScale2d",
  ],
};

function drawEmptyPlots() {
  if (!window.Plotly) return;
  const layout = structuredClone(plotLayoutBase);
  layout.annotations = [
    {
      text: "Configure the circuit and click Run simulation",
      x: 0.5,
      y: 0.5,
      xref: "paper",
      yref: "paper",
      showarrow: false,
      font: { size: 14, color: "#71839d" },
    },
  ];
  Plotly.newPlot("waveform-chart", [], layout, plotConfig);
  const hLayout = structuredClone(plotLayoutBase);
  hLayout.annotations = layout.annotations;
  hLayout.xaxis.title = "Harmonic order";
  hLayout.yaxis.title = "Magnitude (A)";
  Plotly.newPlot("harmonics-chart", [], hLayout, plotConfig);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  runButton.disabled = true;
  runButton.innerHTML = "<span>◌</span> Calculating…";
  setStatus("Calculating", "busy");
  try {
    const response = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(getConfig()),
    });
    const payload = await response.json();
    if (!response.ok || !payload.ok) {
      setStatus(
        payload.kind === "validation" ? "Check inputs" : "Not completed",
        "error",
      );
      showToast(payload.error || "The simulation could not be completed.");
      return;
    }
    latestResult = payload.result;
    renderResult(latestResult);
    setStatus("Simulation complete", "success");
    showToast("Simulation completed. Results and analysis are updated.", true);
  } catch (error) {
    console.error(error);
    setStatus("Backend unavailable", "error");
    showToast(
      "Unable to reach the Python backend. Check that `python app.py` is still running.",
    );
  } finally {
    runButton.disabled = false;
    runButton.innerHTML = "<span>▶</span> Run simulation";
  }
});

function renderResult(result) {
  const m = result.metrics;
  document.getElementById("metric-vpeak").innerHTML =
    `${formatNumber(m.vpeak)} <small>V</small>`;
  document.getElementById("metric-vavg").innerHTML =
    `${formatNumber(m.vavg)} <small>V</small>`;
  document.getElementById("metric-vrms").innerHTML =
    `${formatNumber(m.vrms)} <small>V</small>`;
  document.getElementById("metric-irms").innerHTML =
    `${formatNumber(m.irms)} <small>A</small>`;
  updateSummary(result);
  drawWaveforms(result);
  drawHarmonics(result);
  drawValidation(result);
}

function drawWaveforms(result) {
  const w = result.waveform;
  const traces = [
    {
      x: w.time,
      y: w.load_voltage,
      name: "Load voltage (V)",
      type: "scatter",
      mode: "lines",
      line: { color: "#35d4e8", width: 2.2 },
      yaxis: "y",
    },
    {
      x: w.time,
      y: w.load_current,
      name: "Load current (A)",
      type: "scatter",
      mode: "lines",
      line: { color: "#5b8cff", width: 2.0, dash: "dot" },
      yaxis: "y2",
    },
  ];
  const layout = structuredClone(plotLayoutBase);
  layout.margin = { l: 55, r: 55, t: 15, b: 48 };
  layout.yaxis = {
    title: "Voltage (V)",
    gridcolor: "#253650",
    zerolinecolor: "#30445e",
    linecolor: "#30445e",
    titlefont: { color: "#35d4e8" },
  };
  layout.yaxis2 = {
    title: "Current (A)",
    overlaying: "y",
    side: "right",
    showgrid: false,
    zeroline: false,
    titlefont: { color: "#5b8cff" },
    tickfont: { color: "#9aacc5" },
  };
  layout.legend = { orientation: "h", y: 1.12, x: 0, font: { size: 11 } };
  layout.annotations = [];
  Plotly.react("waveform-chart", traces, layout, plotConfig);
}

function drawHarmonics(result) {
  const harmonics = result.metrics.harmonics || [];
  const fundamental = harmonics.find((h) => h.order === 1)?.magnitude || 0;
  const labels = harmonics.map((h) => h.order);
  const values = harmonics.map((h) => h.magnitude);
  const traces = [
    {
      x: labels,
      y: values,
      type: "bar",
      marker: {
        color: labels.map((order) => (order === 1 ? "#35d4e8" : "#5b8cff")),
        line: { width: 0 },
      },
      hovertemplate: "Harmonic %{x}<br>Magnitude %{y:.4f} A<extra></extra>",
    },
  ];
  const layout = structuredClone(plotLayoutBase);
  layout.xaxis = {
    title: "Harmonic order",
    gridcolor: "#253650",
    dtick: 1,
    linecolor: "#30445e",
  };
  layout.yaxis = {
    title: "Magnitude (A)",
    gridcolor: "#253650",
    linecolor: "#30445e",
  };
  layout.showlegend = false;
  layout.annotations = [];
  Plotly.react("harmonics-chart", traces, layout, plotConfig);
  document.getElementById("harmonics-thd").innerHTML =
    `${formatNumber(result.metrics.thd_percent)} <small>%</small>`;
  document.getElementById("harmonics-pf").textContent = formatNumber(
    result.metrics.power_factor,
    3,
  );

  const tbody = document.getElementById("harmonics-table");
  if (!harmonics.length) {
    tbody.innerHTML =
      '<tr><td colspan="3" class="empty-cell">No harmonic components were calculated.</td></tr>';
    return;
  }
  tbody.innerHTML = harmonics
    .map((h) => {
      const relative = fundamental > 0 ? (h.magnitude / fundamental) * 100 : 0;
      return `<tr><td>${h.order}</td><td>${formatNumber(h.magnitude, 5)}</td><td>${formatNumber(relative, 2)}%</td></tr>`;
    })
    .join("");
}

function drawValidation(result) {
  const tbody = document.getElementById("validation-table");
  tbody.innerHTML = result.validation
    .map((row) => {
      const error = row.error_percent;
      const status = error < 1 ? "Good" : "Review";
      const className = error < 1 ? "good-value" : "warn-value";
      return `<tr>
      <td>${row.quantity}</td>
      <td>${formatNumber(row.numerical, 5)} V</td>
      <td>${formatNumber(row.analytical, 5)} V</td>
      <td><span class="${className}">${formatNumber(error, 3)}%</span> <span class="tiny-status">${status}</span></td>
    </tr>`;
    })
    .join("");
}

document.getElementById("reset-button").addEventListener("click", () => {
  form.reset();
  updateConditionalFields();
  setStatus("Ready to simulate", "ready");
  showToast("Inputs reset to the default configuration.", true);
});

document.getElementById("dismiss-notice").addEventListener("click", () => {
  document.getElementById("notice").classList.add("hidden");
});

document.getElementById("export-csv").addEventListener("click", () => {
  if (!latestResult) {
    showToast("Run a simulation before exporting samples.");
    return;
  }
  const w = latestResult.waveform;
  const lines = ["time_s,source_voltage_V,load_voltage_V,load_current_A"];
  for (let i = 0; i < w.time.length; i++) {
    lines.push(
      [
        w.time[i],
        w.source_voltage[i],
        w.load_voltage[i],
        w.load_current[i],
      ].join(","),
    );
  }
  const blob = new Blob([lines.join("\n")], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "rectilab_waveforms.csv";
  a.click();
  URL.revokeObjectURL(url);
  showToast("CSV waveform data exported.", true);
});

window.addEventListener("resize", () => {
  if (!window.Plotly) return;
  ["waveform-chart", "harmonics-chart"].forEach((id) => {
    const el = document.getElementById(id);
    if (el && el.data) Plotly.Plots.resize(el);
  });
});

drawEmptyPlots();

document
  .getElementById("export-netlist")
  .addEventListener("click", async () => {
    try {
      const response = await fetch("/api/export/netlist", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(getConfig()),
      });

      if (!response.ok) {
        const error = await response.json();

        showToast(error.error || "Unable to export the netlist.");
        return;
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);

      const link = document.createElement("a");
      link.href = url;
      link.download = "rectilab_netlist.cir";

      document.body.appendChild(link);
      link.click();
      link.remove();

      URL.revokeObjectURL(url);

      showToast("PSpice-style netlist downloaded.", true);
    } catch (error) {
      console.error(error);
      showToast("Export failed. Check that the Python server is running.");
    }
  });
