function schematicLine(x1, y1, x2, y2) {
  return `<line class="schematic-wire"
        x1="${x1}" y1="${y1}"
        x2="${x2}" y2="${y2}" />`;
}

function schematicText(
  x,
  y,
  value,
  className = "schematic-label",
  anchor = "middle",
) {
  return `<text class="${className}"
        x="${x}" y="${y}"
        text-anchor="${anchor}">${value}</text>`;
}

function schematicSource(x, y, label = "AC source") {
  return `
        <circle class="schematic-component" cx="${x}" cy="${y}" r="25"/>
        <path class="schematic-ac-wave"
            d="M ${x - 15} ${y}
            C ${x - 8} ${y - 16}, ${x - 1} ${y - 16}, ${x + 6} ${y}
            S ${x + 20} ${y + 16}, ${x + 15} ${y + 5}"/>
        ${schematicText(x, y + 43, label, "schematic-small-label")}
    `;
}

function schematicDevice(x, y, angle, label, controlled) {
  const gate = controlled
    ? `<path class="schematic-gate" d="M -5 25 L 5 10"/>
           <text class="schematic-gate-label" x="-9" y="32">G</text>`
    : "";

  return `
        <g transform="translate(${x} ${y}) rotate(${angle})">
            <line class="schematic-wire" x1="-36" y1="0" x2="-12" y2="0"/>
            <polygon class="schematic-diode"
                points="-12,-12 10,0 -12,12"/>
            <line class="schematic-component"
                x1="10" y1="-14" x2="10" y2="14"/>
            <line class="schematic-wire"
                x1="10" y1="0" x2="36" y2="0"/>
            ${gate}
        </g>
        ${schematicText(x, y + 35, label, "schematic-small-label")}
    `;
}

function schematicDeviceBranch(x1, y1, x2, y2, label, controlled) {
  const dx = x2 - x1;
  const dy = y2 - y1;
  const length = Math.hypot(dx, dy);

  const ux = dx / length;
  const uy = dy / length;

  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;
  const cx = (x1 + x2) / 2;
  const cy = (y1 + y2) / 2;

  const lead = 36;

  return `
        ${schematicLine(x1, y1, cx - ux * lead, cy - uy * lead)}
        ${schematicDevice(cx, cy, angle, label, controlled)}
        ${schematicLine(cx + ux * lead, cy + uy * lead, x2, y2)}
    `;
}

function schematicLoad(x, top, bottom, isRL) {
  const resistorTop = top + 24;
  const resistorHeight = isRL ? 32 : 44;
  const resistorBottom = resistorTop + resistorHeight;

  let parts = [];

  parts.push(schematicLine(x, top, x, resistorTop));

  parts.push(`
        <rect class="schematic-resistor"
            x="${x - 13}" y="${resistorTop}"
            width="26" height="${resistorHeight}" rx="3"/>
    `);

  parts.push(
    schematicText(
      x + 25,
      resistorTop + resistorHeight / 2 + 4,
      "R",
      "schematic-small-label",
      "start",
    ),
  );

  if (isRL) {
    const coilTop = resistorBottom + 13;
    const coilBottom = coilTop + 42;

    parts.push(schematicLine(x, resistorBottom, x, coilTop));

    parts.push(`
            <path class="schematic-inductor"
                d="M ${x} ${coilTop}
                L ${x - 9} ${coilTop + 7}
                L ${x + 9} ${coilTop + 14}
                L ${x - 9} ${coilTop + 21}
                L ${x + 9} ${coilTop + 28}
                L ${x - 9} ${coilTop + 35}
                L ${x} ${coilBottom}"/>
        `);

    parts.push(
      schematicText(
        x + 25,
        coilTop + 27,
        "L",
        "schematic-small-label",
        "start",
      ),
    );

    parts.push(schematicLine(x, coilBottom, x, bottom));
  } else {
    parts.push(schematicLine(x, resistorBottom, x, bottom));
  }

  return parts.join("");
}

function schematicSvg(content) {
  return `
        <svg class="circuit-schematic-svg"
            viewBox="0 0 820 340"
            role="presentation"
            xmlns="http://www.w3.org/2000/svg">

            <style>
                .schematic-wire {
                    stroke: #91a4bd;
                    stroke-width: 3;
                    fill: none;
                    stroke-linecap: round;
                    stroke-linejoin: round;
                }

                .schematic-component {
                    stroke: #35d4e8;
                    stroke-width: 2.8;
                    fill: none;
                }

                .schematic-ac-wave {
                    stroke: #35d4e8;
                    stroke-width: 2.5;
                    fill: none;
                }

                .schematic-diode {
                    stroke: #35d4e8;
                    stroke-width: 2.6;
                    fill: rgba(53,212,232,0.12);
                }

                .schematic-resistor {
                    stroke: #5b8cff;
                    stroke-width: 2.8;
                    fill: rgba(91,140,255,0.10);
                }

                .schematic-inductor {
                    stroke: #5b8cff;
                    stroke-width: 2.8;
                    fill: none;
                }

                .schematic-gate {
                    stroke: #f5b942;
                    stroke-width: 2.5;
                    fill: none;
                }

                .schematic-label {
                    fill: #e5edf7;
                    font: 600 13px Inter, sans-serif;
                }

                .schematic-small-label {
                    fill: #9aacc5;
                    font: 11px Inter, sans-serif;
                }

                .schematic-gate-label {
                    fill: #f5b942;
                    font: 10px Inter, sans-serif;
                }
            </style>

            ${content}
        </svg>
    `;
}

function buildHalfWaveSchematic(isRL, controlled, withFreewheel) {
  const deviceName = controlled ? "T1" : "D1";

  const content = [
    schematicSource(105, 150),

    schematicLine(105, 125, 105, 120),
    schematicLine(105, 120, 245, 120),

    schematicDeviceBranch(245, 120, 365, 120, deviceName, controlled),

    schematicLine(365, 120, 650, 120),

    schematicLoad(650, 120, 230, isRL),

    schematicLine(650, 230, 105, 230),
    schematicLine(105, 230, 105, 175),

    schematicText(425, 95, "Rectified output", "schematic-small-label"),

    schematicText(
      420,
      285,
      withFreewheel
        ? "Freewheeling diode connected across the load"
        : "Single device conducts during the allowed half-cycle",
      "schematic-small-label",
    ),
  ];

  if (withFreewheel) {
    content.push(schematicDeviceBranch(520, 230, 520, 120, "DFW", false));
  }

  return schematicSvg(content.join(""));
}

function buildCentreTappedSchematic(isRL, controlled) {
  const firstDevice = controlled ? "T1" : "D1";
  const secondDevice = controlled ? "T2" : "D2";

  const content = [
    schematicSource(120, 105, "Secondary half 1"),
    schematicSource(120, 215, "Secondary half 2"),

    schematicLine(120, 80, 120, 75),
    schematicLine(120, 75, 150, 75),

    schematicLine(120, 130, 120, 160),
    schematicLine(120, 190, 120, 160),

    schematicLine(120, 240, 150, 240),

    schematicText(82, 164, "CT", "schematic-small-label", "end"),

    schematicDeviceBranch(150, 75, 560, 75, firstDevice, controlled),

    schematicDeviceBranch(150, 240, 560, 75, secondDevice, controlled),

    schematicLine(560, 75, 650, 75),

    schematicLoad(650, 75, 245, isRL),

    schematicLine(650, 245, 650, 270),
    schematicLine(650, 270, 75, 270),
    schematicLine(75, 270, 75, 160),
    schematicLine(75, 160, 120, 160),

    schematicText(
      420,
      315,
      "Two secondary halves feed a common positive output",
      "schematic-small-label",
    ),
  ];

  return schematicSvg(content.join(""));
}

function buildBridgeSchematic(isRL, controlled) {
  const names = controlled
    ? ["T1", "T2", "T3", "T4"]
    : ["D1", "D2", "D3", "D4"];

  const left = { x: 245, y: 150 };
  const right = { x: 500, y: 150 };
  const positive = { x: 372, y: 58 };
  const negative = { x: 372, y: 245 };

  const content = [
    schematicSource(80, 150),

    schematicLine(80, 125, 80, 122),
    schematicLine(80, 122, 160, 122),
    schematicLine(160, 122, left.x, left.y),

    schematicLine(80, 175, 120, 175),
    schematicLine(120, 175, 120, 285),
    schematicLine(120, 285, right.x, 285),
    schematicLine(right.x, 285, right.x, right.y),

    schematicDeviceBranch(
      left.x,
      left.y,
      positive.x,
      positive.y,
      names[0],
      controlled,
    ),

    schematicDeviceBranch(
      right.x,
      right.y,
      positive.x,
      positive.y,
      names[1],
      controlled,
    ),

    schematicDeviceBranch(
      negative.x,
      negative.y,
      left.x,
      left.y,
      names[2],
      controlled,
    ),

    schematicDeviceBranch(
      negative.x,
      negative.y,
      right.x,
      right.y,
      names[3],
      controlled,
    ),

    schematicLine(positive.x, positive.y, 650, positive.y),

    schematicLoad(650, positive.y, negative.y, isRL),

    schematicLine(negative.x, negative.y, 650, negative.y),

    schematicText(372, 35, "+ DC", "schematic-label"),
    schematicText(372, 270, "− DC", "schematic-label"),

    schematicText(
      372,
      315,
      "Four switching branches form the bridge",
      "schematic-small-label",
    ),
  ];

  return schematicSvg(content.join(""));
}

function updateSchematic() {
  const topologyField = document.getElementById("topology");
  const deviceField = document.getElementById("device");
  const loadField = document.getElementById("load_type");
  const stage = document.getElementById("circuit-schematic");

  if (!topologyField || !deviceField || !loadField || !stage) {
    return;
  }

  const topology = topologyField.value;
  const device = deviceField.value;
  const loadType = loadField.value;

  const isRL = loadType === "Resistive-inductive (R-L)";
  const controlled = device === "Thyristor (controlled)";

  const title = document.getElementById("schematic-type");
  const description = document.getElementById("schematic-description");
  const caption = document.getElementById("schematic-caption");

  let diagram = "";
  let explanation = "";

  if (topology === "Half-wave") {
    diagram = buildHalfWaveSchematic(isRL, controlled, false);
    explanation = "One diode or thyristor controls the positive half-cycle.";
  } else if (topology === "Half-wave + freewheeling diode") {
    diagram = buildHalfWaveSchematic(isRL, controlled, true);
    explanation =
      "The freewheeling diode provides an alternate path for inductive load current.";
  } else if (topology === "Full-wave centre-tapped") {
    diagram = buildCentreTappedSchematic(isRL, controlled);
    explanation =
      "Two secondary halves and two switching devices produce full-wave rectification.";
  } else {
    diagram = buildBridgeSchematic(isRL, controlled);
    explanation =
      "Four switching branches form a bridge that rectifies both half-cycles.";
  }

  const resistance = document.getElementById("resistance")?.value || "";
  const inductance = document.getElementById("inductance")?.value || "";
  const firingAngle = document.getElementById("firing_angle_deg")?.value || "";

  if (title) title.textContent = topology;
  if (description) description.textContent = explanation;

  if (caption) {
    caption.textContent =
      `${device} · ${
        isRL
          ? `R–L load (${resistance} Ω, ${inductance} H)`
          : `R load (${resistance} Ω)`
      }` + `${controlled ? ` · Firing angle: ${firingAngle}°` : ""}`;
  }

  stage.innerHTML = diagram;

  stage.setAttribute(
    "aria-label",
    `${topology} circuit using ${device} and ${isRL ? "R-L" : "resistive"} load`,
  );
}

document.addEventListener("DOMContentLoaded", () => {
  const fieldIds = [
    "topology",
    "device",
    "load_type",
    "firing_angle_deg",
    "resistance",
    "inductance",
  ];

  fieldIds.forEach((id) => {
    const field = document.getElementById(id);

    if (field) {
      field.addEventListener("change", updateSchematic);
      field.addEventListener("input", updateSchematic);
    }
  });

  const resetButton = document.getElementById("reset-button");

  if (resetButton) {
    resetButton.addEventListener("click", () => {
      setTimeout(updateSchematic, 0);
    });
  }

  updateSchematic();
});
