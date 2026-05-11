const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");

// Colors
const C = {
  darkBg:   "0D1117",
  darkCard: "161B22",
  blue:     "1E6FDB",
  cyan:     "00D4FF",
  green:    "3FB950",
  orange:   "F78166",
  white:    "FFFFFF",
  light:    "C9D1D9",
  muted:    "8B949E",
  border:   "21262D",
};

// Icon helper
const { FaMemory, FaBrain, FaNetworkWired, FaShieldAlt, FaKey, FaSearch, FaCode, FaLayerGroup } = require("react-icons/fa");
const { MdSecurity, MdBugReport, MdDashboard } = require("react-icons/md");

async function iconPng(IconComponent, color = "#FFFFFF", size = 256) {
  const svg = ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
  const buf = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + buf.toString("base64");
}

async function main() {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9";
  pres.title = "MemForensics — Memory Forensics Framework";

  // Pre-render icons
  const icoMemory   = await iconPng(FaMemory,       "#00D4FF");
  const icoShield   = await iconPng(FaShieldAlt,    "#3FB950");
  const icoNetwork  = await iconPng(FaNetworkWired, "#F78166");
  const icoKey      = await iconPng(FaKey,          "#F78166");
  const icoSearch   = await iconPng(FaSearch,       "#00D4FF");
  const icoBug      = await iconPng(MdBugReport,    "#F78166");
  const icoCode     = await iconPng(FaCode,         "#3FB950");
  const icoLayer    = await iconPng(FaLayerGroup,   "#00D4FF");
  const icoDash     = await iconPng(MdDashboard,    "#00D4FF");
  const icoBrain    = await iconPng(FaBrain,        "#F78166");

  // ─────────────────────────────────────────
  // SLIDE 1 — Title
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };

    // Top cyan accent bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    // Left accent block
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0.06, w: 0.55, h: 5.565, fill: { color: C.darkCard }, line: { color: C.darkCard } });

    // Brain icon large
    s.addImage({ data: icoBrain, x: 0.12, y: 1.6, w: 0.3, h: 0.3 });

    // Vertical label
    s.addText("MEMFORENSICS", {
      x: 0.05, y: 1.0, w: 3.5, h: 0.4,
      fontSize: 8, color: C.cyan, bold: true, charSpacing: 4,
      rotate: 270, align: "center", margin: 0
    });

    // Main title
    s.addText("Memory Forensics", {
      x: 0.75, y: 0.8, w: 8.8, h: 1.1,
      fontSize: 52, color: C.white, bold: true, fontFace: "Calibri", margin: 0
    });
    s.addText("& Volatile Data Analysis Framework", {
      x: 0.75, y: 1.8, w: 8.8, h: 0.7,
      fontSize: 24, color: C.cyan, bold: false, fontFace: "Calibri", margin: 0
    });

    // Separator line
    s.addShape(pres.shapes.RECTANGLE, { x: 0.75, y: 2.65, w: 8.0, h: 0.025, fill: { color: C.border }, line: { color: C.border } });

    // Subtitle description
    s.addText("A zero-click automated desktop application for parsing RAM dumps,\nextracting forensic artifacts, and detecting malware signatures.", {
      x: 0.75, y: 2.8, w: 7.5, h: 0.95,
      fontSize: 14, color: C.light, fontFace: "Calibri", margin: 0
    });

    // Tags row
    const tags = ["Python 3.10+", "PyQt5", "Volatility3", "YARA"];
    tags.forEach((t, i) => {
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.75 + i * 2.05, y: 3.95, w: 1.85, h: 0.38, fill: { color: C.darkCard }, line: { color: C.cyan }, rectRadius: 0.08 });
      s.addText(t, { x: 0.75 + i * 2.05, y: 3.95, w: 1.85, h: 0.38, fontSize: 11, color: C.cyan, align: "center", bold: true, margin: 0 });
    });

    // Team
    s.addText("Eslam Ebrahim  ·  Ahmed Emad  ·  Mohamed Wael  |  Supervisor: Dr. Maryam Adel", {
      x: 0.75, y: 4.6, w: 9.0, h: 0.35,
      fontSize: 10, color: C.muted, fontFace: "Calibri", margin: 0
    });
    s.addText("Advanced Digital Forensics Course", {
      x: 0.75, y: 4.95, w: 9.0, h: 0.3,
      fontSize: 10, color: C.muted, italic: true, fontFace: "Calibri", margin: 0
    });

    // Bottom bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 2 — Agenda
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("Agenda", { x: 0.5, y: 0.25, w: 9, h: 0.65, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("What we'll cover today", { x: 0.5, y: 0.9, w: 9, h: 0.35, fontSize: 14, color: C.muted, margin: 0 });

    const items = [
      { n: "01", label: "Problem Statement",    sub: "Why volatile data matters" },
      { n: "02", label: "Our Solution",         sub: "What MemForensics does" },
      { n: "03", label: "Key Features",         sub: "5-step analysis pipeline" },
      { n: "04", label: "Tech Stack",           sub: "Tools & technologies used" },
      { n: "05", label: "Architecture",         sub: "Project structure overview" },
      { n: "06", label: "YARA Intelligence",    sub: "Threat detection rules" },
      { n: "07", label: "Demo & Results",       sub: "Live pipeline walkthrough" },
      { n: "08", label: "Team & Conclusion",    sub: "Takeaways & next steps" },
    ];

    // 2 columns x 4 rows
    items.forEach((item, i) => {
      const col = i % 2;
      const row = Math.floor(i / 2);
      const x = 0.5 + col * 4.85;
      const y = 1.45 + row * 0.95;

      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 4.55, h: 0.78,
        fill: { color: C.darkCard }, line: { color: C.border },
        shadow: { type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.3 }
      });
      // Number
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 0.55, h: 0.78, fill: { color: C.blue }, line: { color: C.blue } });
      s.addText(item.n, { x, y, w: 0.55, h: 0.78, fontSize: 15, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
      s.addText(item.label, { x: x + 0.65, y: y + 0.07, w: 3.8, h: 0.35, fontSize: 13, bold: true, color: C.white, margin: 0 });
      s.addText(item.sub, { x: x + 0.65, y: y + 0.42, w: 3.8, h: 0.28, fontSize: 10, color: C.muted, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 3 — Problem Statement
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.orange }, line: { color: C.orange } });

    s.addText("The Problem", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Why volatile data is a forensic challenge", { x: 0.5, y: 0.8, w: 9, h: 0.35, fontSize: 14, color: C.muted, margin: 0 });

    // Big RAM danger illustration box
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 4.2, h: 3.8,
      fill: { color: C.darkCard }, line: { color: C.orange }
    });
    s.addImage({ data: icoMemory, x: 1.7, y: 1.5, w: 0.7, h: 0.7 });
    s.addText("RAM Contains:", { x: 0.6, y: 2.35, w: 4.0, h: 0.4, fontSize: 14, bold: true, color: C.orange, margin: 0 });

    const ramItems = [
      "Running processes & threads",
      "Active network connections",
      "Encryption keys in plaintext",
      "Injected malware code",
      "Credential hashes (NTLM/LM)",
    ];
    ramItems.forEach((t, i) => {
      s.addText([
        { text: "▸ ", options: { color: C.orange, bold: true } },
        { text: t, options: { color: C.light } }
      ], { x: 0.7, y: 2.82 + i * 0.42, w: 3.9, h: 0.35, fontSize: 12, margin: 0 });
    });

    // Right side
    s.addShape(pres.shapes.RECTANGLE, { x: 5.0, y: 1.3, w: 4.5, h: 1.6,
      fill: { color: "1A0A0A" }, line: { color: C.orange }
    });
    s.addText("⚠ Power Off = Evidence Destroyed", {
      x: 5.1, y: 1.4, w: 4.3, h: 0.5,
      fontSize: 14, bold: true, color: C.orange, margin: 0
    });
    s.addText("The moment a system is shut down, ALL volatile data disappears permanently — processes, keys, and loaded malware are gone forever.", {
      x: 5.1, y: 1.88, w: 4.3, h: 0.85,
      fontSize: 11, color: C.light, margin: 0
    });

    // 2 problem cards on right
    const probs = [
      { title: "Manual & Complex", body: "Traditional tools require extensive CLI expertise and plugin-by-plugin execution." },
      { title: "Too Slow", body: "Incident responders need rapid intelligence — not hours of manual configuration." },
    ];
    probs.forEach((p, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 5.0, y: 3.05 + i * 1.05, w: 4.5, h: 0.9,
        fill: { color: C.darkCard }, line: { color: C.border }
      });
      s.addShape(pres.shapes.RECTANGLE, { x: 5.0, y: 3.05 + i * 1.05, w: 0.07, h: 0.9, fill: { color: C.orange }, line: { color: C.orange } });
      s.addText(p.title, { x: 5.18, y: 3.1 + i * 1.05, w: 4.2, h: 0.3, fontSize: 13, bold: true, color: C.white, margin: 0 });
      s.addText(p.body,  { x: 5.18, y: 3.42 + i * 1.05, w: 4.2, h: 0.45, fontSize: 11, color: C.muted, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 4 — Our Solution
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("Our Solution", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });

    // Hero description
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 0.95, w: 9.0, h: 1.1,
      fill: { color: "0D2438" }, line: { color: C.cyan }
    });
    s.addText("MemForensics", { x: 0.7, y: 1.0, w: 3.0, h: 0.45, fontSize: 22, bold: true, color: C.cyan, margin: 0 });
    s.addText("is a fully automated, zero-click desktop framework that transforms raw memory dumps into structured forensic intelligence. Load a memory image — the rest is automatic.", {
      x: 0.7, y: 1.45, w: 8.6, h: 0.48, fontSize: 12, color: C.light, margin: 0
    });

    // 3 value cards
    const vals = [
      { icon: icoSearch,  title: "Zero Manual Effort",     body: "One click loads the dump. The 5-step pipeline starts automatically with no commands needed." },
      { icon: icoShield,  title: "Full Forensic Coverage", body: "Processes, network sockets, injections, credentials, and YARA scans — all in one run." },
      { icon: icoCode,    title: "Resilient by Design",    body: "If any scan fails, the pipeline continues gracefully. No popups. No interruptions." },
    ];
    vals.forEach((v, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + i * 3.1, y: 2.25, w: 2.85, h: 2.85,
        fill: { color: C.darkCard }, line: { color: C.border },
        shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.25 }
      });
      s.addImage({ data: v.icon, x: 0.85 + i * 3.1, y: 2.45, w: 0.5, h: 0.5 });
      s.addText(v.title, { x: 0.6 + i * 3.1, y: 3.1, w: 2.65, h: 0.45, fontSize: 13, bold: true, color: C.white, margin: 0 });
      s.addText(v.body,  { x: 0.6 + i * 3.1, y: 3.58, w: 2.65, h: 1.35, fontSize: 11, color: C.muted, margin: 0 });
    });

    s.addText('"Zero manual intervention. Zero command-line interaction. Full forensic coverage."', {
      x: 0.5, y: 5.2, w: 9, h: 0.3,
      fontSize: 12, italic: true, color: C.cyan, align: "center", margin: 0
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 5 — Key Features (5-step pipeline)
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green }, line: { color: C.green } });

    s.addText("5-Step Analysis Pipeline", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Automated sequential execution on every memory image loaded", { x: 0.5, y: 0.82, w: 9, h: 0.3, fontSize: 13, color: C.muted, margin: 0 });

    const steps = [
      { n: "1", label: "Process Extraction",  plugin: "windows.pslist",   desc: "Lists all running & terminated processes with PID, PPID, threads, handles, and timestamps.", color: C.cyan,   icon: icoLayer },
      { n: "2", label: "Network Recovery",    plugin: "windows.netscan",  desc: "Recovers active TCP/UDP connections, listening ports, local/remote IPs, and owning processes.", color: C.green,  icon: icoNetwork },
      { n: "3", label: "Injection Detection", plugin: "windows.malfind",  desc: "Identifies memory regions with PAGE_EXECUTE_READWRITE — hallmark of code injection.", color: C.orange, icon: icoBug },
      { n: "4", label: "Credential Recovery", plugin: "windows.hashdump", desc: "Extracts Windows SAM database entries: usernames, RIDs, LM hashes, NTLM hashes.", color: C.orange, icon: icoKey },
      { n: "5", label: "YARA Malware Scan",   plugin: "windows.yarascan", desc: "Auto-fetches Neo23x0/signature-base rules and scans process memory for known malware.", color: C.cyan,   icon: icoSearch },
    ];

    steps.forEach((st, i) => {
      const y = 1.25 + i * 0.845;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 9.0, h: 0.77,
        fill: { color: C.darkCard }, line: { color: C.border }
      });
      // Step number circle (simulated with rectangle)
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y, w: 0.6, h: 0.77, fill: { color: st.color }, line: { color: st.color } });
      s.addText(st.n, { x: 0.5, y, w: 0.6, h: 0.77, fontSize: 18, bold: true, color: C.darkBg, align: "center", valign: "middle", margin: 0 });
      // Icon
      s.addImage({ data: st.icon, x: 1.25, y: y + 0.14, w: 0.42, h: 0.42 });
      // Label
      s.addText(st.label, { x: 1.85, y: y + 0.08, w: 2.8, h: 0.32, fontSize: 13, bold: true, color: C.white, margin: 0 });
      // Plugin tag
      s.addShape(pres.shapes.RECTANGLE, { x: 1.85, y: y + 0.43, w: 2.2, h: 0.22, fill: { color: "1C2A3A" }, line: { color: st.color } });
      s.addText(st.plugin, { x: 1.87, y: y + 0.43, w: 2.16, h: 0.22, fontSize: 8, color: st.color, fontFace: "Consolas", margin: 0 });
      // Description
      s.addText(st.desc, { x: 4.3, y: y + 0.1, w: 5.1, h: 0.55, fontSize: 11, color: C.muted, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 6 — Tech Stack
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.blue }, line: { color: C.blue } });

    s.addText("Tech Stack", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Technologies powering MemForensics", { x: 0.5, y: 0.82, w: 9, h: 0.3, fontSize: 13, color: C.muted, margin: 0 });

    const techs = [
      { name: "Python 3.10+",    role: "Language",         desc: "Core application logic and automation",          color: C.cyan,   icon: icoCode },
      { name: "PyQt5",           role: "GUI Framework",    desc: "Modern dark-themed desktop dashboard",           color: C.blue,   icon: icoDash },
      { name: "Volatility3",     role: "Forensics Engine", desc: "Memory image parsing & plugin execution",        color: C.orange, icon: icoLayer },
      { name: "YARA-Python",     role: "Malware Detection","desc": "Signature-based malware scanning",            color: C.green,  icon: icoShield },
      { name: "PyCryptodome",    role: "Crypto Support",   desc: "Required for credential hash extraction",        color: C.cyan,   icon: icoKey },
    ];

    // 2 col layout: first 3, then 2 centered
    const positions = [
      [0.5, 1.3], [3.65, 1.3], [6.8, 1.3],
      [2.08, 3.35], [5.23, 3.35],
    ];
    techs.forEach((t, i) => {
      const [x, y] = positions[i];
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.85, h: 1.75,
        fill: { color: C.darkCard }, line: { color: C.border },
        shadow: { type: "outer", blur: 5, offset: 2, angle: 135, color: "000000", opacity: 0.25 }
      });
      s.addShape(pres.shapes.RECTANGLE, { x, y, w: 2.85, h: 0.07, fill: { color: t.color }, line: { color: t.color } });
      s.addImage({ data: t.icon, x: x + 0.18, y: y + 0.22, w: 0.38, h: 0.38 });
      s.addText(t.name, { x: x + 0.68, y: y + 0.18, w: 2.1, h: 0.35, fontSize: 13, bold: true, color: C.white, margin: 0 });
      s.addText(t.role, { x: x + 0.68, y: y + 0.52, w: 2.1, h: 0.25, fontSize: 10, color: t.color, margin: 0 });
      s.addText(t.desc, { x: x + 0.15, y: y + 0.93, w: 2.55, h: 0.68, fontSize: 10, color: C.muted, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 7 — Architecture
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("Project Architecture", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Modular structure with separated concerns", { x: 0.5, y: 0.82, w: 9, h: 0.3, fontSize: 13, color: C.muted, margin: 0 });

    // Entry point box
    s.addShape(pres.shapes.RECTANGLE, { x: 3.7, y: 1.22, w: 2.6, h: 0.55,
      fill: { color: C.blue }, line: { color: C.blue }
    });
    s.addText("main.py  (Entry Point)", { x: 3.7, y: 1.22, w: 2.6, h: 0.55, fontSize: 12, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });

    // Arrow down
    s.addShape(pres.shapes.LINE, { x: 5.0, y: 1.77, w: 0, h: 0.38, line: { color: C.muted, width: 2 } });

    // 3 module boxes
    const modules = [
      { x: 0.4,  label: "gui/",          sub: "main_window.py",     desc: "PyQt5 Dashboard\n5-step pipeline UI\nReal-time stat cards\nBackground QThreads", color: C.cyan },
      { x: 3.7,  label: "core/",         sub: "vol_wrapper.py\nyara_scanner.py", desc: "VolatilityManager\nCLI wrapper + JSON parser\nYaraScanner\nAuto-fetch & scan", color: C.green },
      { x: 6.85, label: "yara_rules/",   sub: ".yar rule files",    desc: "Neo23x0 signatures:\nCobaltStrike\nMimikatz\nCustom rules", color: C.orange },
    ];
    modules.forEach(m => {
      s.addShape(pres.shapes.RECTANGLE, { x: m.x, y: 2.15, w: 2.85, h: 2.95,
        fill: { color: C.darkCard }, line: { color: m.color }
      });
      s.addShape(pres.shapes.RECTANGLE, { x: m.x, y: 2.15, w: 2.85, h: 0.07, fill: { color: m.color }, line: { color: m.color } });
      s.addText(m.label, { x: m.x + 0.15, y: 2.25, w: 2.55, h: 0.35, fontSize: 14, bold: true, color: m.color, fontFace: "Consolas", margin: 0 });
      s.addText(m.sub,   { x: m.x + 0.15, y: 2.6, w: 2.55, h: 0.55, fontSize: 10, color: C.cyan, fontFace: "Consolas", margin: 0 });
      s.addShape(pres.shapes.RECTANGLE, { x: m.x + 0.15, y: 3.22, w: 2.55, h: 0.025, fill: { color: C.border }, line: { color: C.border } });
      s.addText(m.desc,  { x: m.x + 0.15, y: 3.3, w: 2.55, h: 1.65, fontSize: 10, color: C.muted, margin: 0 });

      // Arrow from main.py (center)
      if (m.x !== 3.7) {
        s.addShape(pres.shapes.LINE, {
          x: m.x + 1.425, y: 1.77, w: 0, h: 0.38, line: { color: C.muted, width: 2 }
        });
      }
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 8 — YARA Intelligence
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.orange }, line: { color: C.orange } });

    s.addText("YARA Threat Intelligence", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Automated signature-based malware detection", { x: 0.5, y: 0.82, w: 9, h: 0.3, fontSize: 13, color: C.muted, margin: 0 });

    // Left: how it works
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 4.4, h: 3.9,
      fill: { color: C.darkCard }, line: { color: C.border }
    });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 4.4, h: 0.07, fill: { color: C.orange }, line: { color: C.orange } });
    s.addText("How It Works", { x: 0.65, y: 1.35, w: 4.1, h: 0.38, fontSize: 15, bold: true, color: C.white, margin: 0 });

    const steps = [
      { n: "1", text: "Auto-fetches rules from Neo23x0/signature-base on first scan" },
      { n: "2", text: "Merges all .yar files from the yara_rules/ directory" },
      { n: "3", text: "Scans every process in the memory dump against all rules" },
      { n: "4", text: "Appends [YARA] hits to the Malware table in the dashboard" },
      { n: "5", text: "Results cached — no re-download needed on subsequent scans" },
    ];
    steps.forEach((st, i) => {
      const y = 1.85 + i * 0.57;
      s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y, w: 0.38, h: 0.38, fill: { color: C.orange }, line: { color: C.orange } });
      s.addText(st.n, { x: 0.7, y, w: 0.38, h: 0.38, fontSize: 12, bold: true, color: C.darkBg, align: "center", valign: "middle", margin: 0 });
      s.addText(st.text, { x: 1.2, y: y + 0.02, w: 3.55, h: 0.34, fontSize: 11, color: C.light, margin: 0 });
    });

    // Right: rule cards
    const rules = [
      { file: "apt_cobaltstrike.yar",        target: "CobaltStrike beacon implants and shellcode patterns" },
      { file: "gen_mimikatz.yar",            target: "Mimikatz credential harvesting tool signatures" },
      { file: "gen_suspicious_strings.yar",  target: "Obfuscated strings & suspicious encoding patterns" },
      { file: "example.yar (custom)",        target: "User-defined custom rules — drop any .yar file here" },
    ];
    s.addText("Bundled Rule Files", { x: 5.2, y: 1.25, w: 4.5, h: 0.38, fontSize: 15, bold: true, color: C.white, margin: 0 });
    rules.forEach((r, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.75 + i * 0.95, w: 4.5, h: 0.8,
        fill: { color: C.darkCard }, line: { color: C.border }
      });
      s.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.75 + i * 0.95, w: 0.07, h: 0.8, fill: { color: C.orange }, line: { color: C.orange } });
      s.addText(r.file,   { x: 5.37, y: 1.8 + i * 0.95, w: 4.2, h: 0.3, fontSize: 11, bold: true, color: C.orange, fontFace: "Consolas", margin: 0 });
      s.addText(r.target, { x: 5.37, y: 2.12 + i * 0.95, w: 4.2, h: 0.35, fontSize: 10, color: C.muted, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 9 — GUI & Dashboard
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green }, line: { color: C.green } });

    s.addText("Dashboard & GUI", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Modern dark-themed PyQt5 interface", { x: 0.5, y: 0.82, w: 9, h: 0.3, fontSize: 13, color: C.muted, margin: 0 });

    // Simulated dashboard mockup
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 6.0, h: 3.95,
      fill: { color: "0A0E13" }, line: { color: C.border }
    });
    // Mockup title bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 6.0, h: 0.45, fill: { color: C.darkCard }, line: { color: C.darkCard } });
    s.addText("MemForensics — Memory Analysis Dashboard", { x: 0.65, y: 1.3, w: 5.7, h: 0.35, fontSize: 10, color: C.cyan, bold: true, margin: 0 });

    // 4 stat cards in mockup
    const statCards = [
      { label: "Processes", val: "127", color: C.cyan },
      { label: "Network",   val: "34",  color: C.green },
      { label: "Malware",   val: "8",   color: C.orange },
      { label: "Creds",     val: "12",  color: C.blue },
    ];
    statCards.forEach((c, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.65 + i * 1.42, y: 1.82, w: 1.27, h: 0.72, fill: { color: C.darkCard }, line: { color: c.color } });
      s.addText(c.val,   { x: 0.65 + i * 1.42, y: 1.87, w: 1.27, h: 0.35, fontSize: 18, bold: true, color: c.color, align: "center", margin: 0 });
      s.addText(c.label, { x: 0.65 + i * 1.42, y: 2.22, w: 1.27, h: 0.28, fontSize: 8, color: C.muted, align: "center", margin: 0 });
    });

    // Results table mockup
    s.addShape(pres.shapes.RECTANGLE, { x: 0.65, y: 2.65, w: 5.7, h: 0.3, fill: { color: C.darkCard }, line: { color: C.border } });
    s.addText("PID    Process Name         Status", { x: 0.7, y: 2.68, w: 5.5, h: 0.25, fontSize: 9, color: C.cyan, fontFace: "Consolas", bold: true, margin: 0 });
    const fakeRows = ["4      System               Running", "688    lsass.exe            Running", "1234   malware.exe  ⚠      Suspicious", "2048   svchost.exe          Running"];
    fakeRows.forEach((r, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.65, y: 2.97 + i * 0.28, w: 5.7, h: 0.27, fill: { color: i % 2 === 0 ? "0F1419" : C.darkCard }, line: { color: C.border } });
      s.addText(r, { x: 0.7, y: 2.99 + i * 0.28, w: 5.5, h: 0.23, fontSize: 9, color: r.includes("Suspicious") ? C.orange : C.light, fontFace: "Consolas", margin: 0 });
    });

    // Progress bar
    s.addShape(pres.shapes.RECTANGLE, { x: 0.65, y: 4.1, w: 5.7, h: 0.22, fill: { color: C.darkCard }, line: { color: C.border } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.65, y: 4.1, w: 4.56, h: 0.22, fill: { color: C.green }, line: { color: C.green } });
    s.addText("Analysis progress: 80%", { x: 0.7, y: 4.12, w: 5.5, h: 0.18, fontSize: 8, color: C.white, margin: 0 });
    s.addText("Step [4/5] — Credential Recovery (hashdump) running...", { x: 0.65, y: 4.38, w: 5.7, h: 0.22, fontSize: 9, color: C.muted, margin: 0 });

    // Right: feature highlights
    const feats = [
      { icon: icoDash,   title: "Non-Blocking UI",     desc: "All scans run on background QThread workers — GUI stays responsive throughout." },
      { icon: icoShield, title: "Resilient Pipeline",  desc: "Any failed step is skipped gracefully. No error popups, no blocked execution." },
      { icon: icoSearch, title: "Real-Time Counters",  desc: "Stat cards update live as each scan completes — instant visibility into findings." },
    ];
    feats.forEach((f, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 6.75, y: 1.25 + i * 1.3, w: 2.8, h: 1.15,
        fill: { color: C.darkCard }, line: { color: C.border }
      });
      s.addImage({ data: f.icon, x: 6.9, y: 1.35 + i * 1.3, w: 0.35, h: 0.35 });
      s.addText(f.title, { x: 7.35, y: 1.33 + i * 1.3, w: 2.1, h: 0.35, fontSize: 12, bold: true, color: C.white, margin: 0 });
      s.addText(f.desc,  { x: 6.9, y: 1.72 + i * 1.3, w: 2.55, h: 0.6, fontSize: 10, color: C.muted, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 10 — Installation & Usage
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("Installation & Usage", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });
    s.addText("Get up and running in 3 simple steps", { x: 0.5, y: 0.82, w: 9, h: 0.3, fontSize: 13, color: C.muted, margin: 0 });

    // Prerequisites
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.25, w: 9.0, h: 0.7, fill: { color: "0D2438" }, line: { color: C.blue } });
    s.addText("Prerequisites: ", { x: 0.7, y: 1.3, w: 1.8, h: 0.3, fontSize: 12, bold: true, color: C.blue, margin: 0 });
    s.addText("Python 3.10+  ·  A Windows memory dump file (.raw / .mem / .dmp / .vmem)", { x: 2.4, y: 1.3, w: 7.0, h: 0.3, fontSize: 12, color: C.light, margin: 0 });
    s.addText("Supported OS: Windows (memory analysis of Windows RAM images)", { x: 0.7, y: 1.62, w: 8.6, h: 0.25, fontSize: 11, color: C.muted, margin: 0 });

    // 3 step cards
    const instSteps = [
      {
        n: "1", color: C.cyan, title: "Create Virtual Environment",
        code: "python -m venv venv\nvenv\\Scripts\\activate",
        note: "Isolates dependencies from your system Python"
      },
      {
        n: "2", color: C.green, title: "Launch the Framework",
        code: "python main.py",
        note: "Auto-installs all dependencies from requirements.txt on first launch"
      },
      {
        n: "3", color: C.orange, title: "One-Click Launcher (Alternative)",
        code: "run.bat",
        note: "Activates venv and launches the app in one double-click"
      },
    ];
    instSteps.forEach((st, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + i * 3.1, y: 2.12, w: 2.85, h: 2.95,
        fill: { color: C.darkCard }, line: { color: st.color }
      });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + i * 3.1, y: 2.12, w: 2.85, h: 0.07, fill: { color: st.color }, line: { color: st.color } });
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + i * 3.1, y: 2.12, w: 0.55, h: 0.62, fill: { color: st.color }, line: { color: st.color } });
      s.addText(st.n, { x: 0.5 + i * 3.1, y: 2.12, w: 0.55, h: 0.62, fontSize: 20, bold: true, color: C.darkBg, align: "center", valign: "middle", margin: 0 });
      s.addText(st.title, { x: 1.18 + i * 3.1, y: 2.19, w: 2.1, h: 0.48, fontSize: 12, bold: true, color: C.white, margin: 0 });
      // code block
      s.addShape(pres.shapes.RECTANGLE, { x: 0.65 + i * 3.1, y: 2.85, w: 2.55, h: 0.75, fill: { color: "0A0E13" }, line: { color: st.color } });
      s.addText(st.code, { x: 0.75 + i * 3.1, y: 2.9, w: 2.35, h: 0.65, fontSize: 10, color: st.color, fontFace: "Consolas", margin: 0 });
      s.addText(st.note, { x: 0.65 + i * 3.1, y: 3.7, w: 2.55, h: 0.8, fontSize: 10, color: C.muted, margin: 0 });
    });

    // In the GUI
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 5.2, w: 9.0, h: 0.28, fill: { color: "0D2438" }, line: { color: C.cyan } });
    s.addText("In the GUI:  Click 📂 Load Memory Dump → Select your image → The 5-step pipeline starts automatically", {
      x: 0.7, y: 5.21, w: 8.7, h: 0.26,
      fontSize: 11, color: C.cyan, margin: 0
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 11 — Team & Conclusion
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("Team & Conclusion", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 32, bold: true, color: C.white, margin: 0 });

    // Team members
    const members = [
      { name: "Eslam Ebrahim",  role: "Developer & Architect", color: C.cyan },
      { name: "Ahmed Emad",     role: "Developer & Testing",   color: C.green },
      { name: "Mohamed Wael",   role: "Developer & Documentation", color: C.orange },
    ];
    members.forEach((m, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5 + i * 3.1, y: 1.0, w: 2.85, h: 1.3,
        fill: { color: C.darkCard }, line: { color: m.color },
        shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.25 }
      });
      // Avatar placeholder
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5 + i * 3.1 + 1.1, y: 1.1, w: 0.65, h: 0.65, fill: { color: m.color }, line: { color: m.color }, rectRadius: 0.33 });
      s.addText(m.name[0], { x: 0.5 + i * 3.1 + 1.1, y: 1.1, w: 0.65, h: 0.65, fontSize: 20, bold: true, color: C.darkBg, align: "center", valign: "middle", margin: 0 });
      s.addText(m.name, { x: 0.5 + i * 3.1, y: 1.82, w: 2.85, h: 0.28, fontSize: 12, bold: true, color: C.white, align: "center", margin: 0 });
      s.addText(m.role, { x: 0.5 + i * 3.1, y: 2.1, w: 2.85, h: 0.2, fontSize: 10, color: m.color, align: "center", margin: 0 });
    });

    // Supervisor
    s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: 2.5, w: 5.0, h: 0.55,
      fill: { color: C.darkCard }, line: { color: C.blue }
    });
    s.addText("Supervisor: Dr. Maryam Adel  |  Advanced Digital Forensics Course", {
      x: 2.5, y: 2.5, w: 5.0, h: 0.55, fontSize: 12, color: C.light, align: "center", valign: "middle", margin: 0
    });

    // Key takeaways
    s.addText("Key Takeaways", { x: 0.5, y: 3.22, w: 9, h: 0.38, fontSize: 16, bold: true, color: C.white, margin: 0 });
    const takeaways = [
      { icon: "✓", color: C.green,  text: "MemForensics automates the full memory forensics workflow — zero command-line expertise needed." },
      { icon: "✓", color: C.cyan,   text: "The 5-step pipeline covers all critical volatile artifacts: processes, network, injection, credentials, YARA." },
      { icon: "✓", color: C.orange, text: "YARA integration provides real threat intelligence with industry-standard signatures from Neo23x0." },
      { icon: "✓", color: C.blue,   text: "Resilient architecture ensures partial results are always delivered — even if some scans fail." },
    ];
    takeaways.forEach((t, i) => {
      s.addText([
        { text: t.icon + " ", options: { color: t.color, bold: true, fontSize: 13 } },
        { text: t.text,       options: { color: C.light, fontSize: 12 } }
      ], { x: 0.5, y: 3.72 + i * 0.42, w: 9.0, h: 0.36, margin: 0 });
    });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 12 — Thank You
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };

    // Full-bleed accent
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });

    // Big icon
    s.addImage({ data: icoBrain, x: 4.3, y: 0.6, w: 1.4, h: 1.4 });

    s.addText("Thank You", { x: 0, y: 2.1, w: 10, h: 0.9, fontSize: 52, bold: true, color: C.white, align: "center", margin: 0 });
    s.addText("Questions & Discussion", { x: 0, y: 3.0, w: 10, h: 0.55, fontSize: 20, color: C.cyan, align: "center", margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: 2.5, y: 3.72, w: 5.0, h: 0.04, fill: { color: C.border }, line: { color: C.border } });

    s.addText("github.com/Eslamm1928/Memforensics", {
      x: 0, y: 3.9, w: 10, h: 0.4,
      fontSize: 14, color: C.muted, align: "center", fontFace: "Consolas", margin: 0
    });
    s.addText("Advanced Digital Forensics  ·  Dr. Maryam Adel", {
      x: 0, y: 4.4, w: 10, h: 0.35,
      fontSize: 12, color: C.muted, align: "center", margin: 0
    });
  }

  await pres.writeFile({ fileName: "MemForensics_Presentation.pptx" });
  console.log("Done!");
}

main().catch(console.error);