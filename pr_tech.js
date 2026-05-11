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
  codeBg:   "0A0E13",
};

// Icons
const { FaCode, FaMicrochip, FaServer, FaCogs, FaProjectDiagram, FaBug, FaDatabase, FaShieldAlt, FaTerminal } = require("react-icons/fa");

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
  pres.title = "MemForensics — Technical Deep Dive";

  const icoCode   = await iconPng(FaCode,           C.cyan);
  const icoChip   = await iconPng(FaMicrochip,      C.green);
  const icoServer = await iconPng(FaServer,         C.blue);
  const icoCogs   = await iconPng(FaCogs,           C.orange);
  const icoGraph  = await iconPng(FaProjectDiagram, C.cyan);
  const icoBug    = await iconPng(FaBug,            C.orange);
  const icoDb     = await iconPng(FaDatabase,       C.green);
  const icoShield = await iconPng(FaShieldAlt,      C.cyan);
  const icoTerm   = await iconPng(FaTerminal,       C.blue);

  // ─────────────────────────────────────────
  // SLIDE 1 — Title
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    // Grid background
    for(let i=0; i<10; i+=0.5) s.addShape(pres.shapes.LINE, { x: i, y: 0, w: 0, h: 5.625, line: { color: "151A22", width: 1 } });
    for(let i=0; i<6; i+=0.5) s.addShape(pres.shapes.LINE, { x: 0, y: i, w: 10, h: 0, line: { color: "151A22", width: 1 } });

    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 9, h: 3.2, fill: { color: C.darkCard }, line: { color: C.border } });

    s.addImage({ data: icoCode, x: 0.8, y: 1.5, w: 0.5, h: 0.5 });
    s.addText("TECHNICAL DEEP DIVE", { x: 1.4, y: 1.5, w: 5, h: 0.5, fontSize: 16, bold: true, color: C.cyan, charSpacing: 2, margin: 0 });

    s.addText("MemForensics Architecture", { x: 0.8, y: 2.1, w: 8.4, h: 1.0, fontSize: 44, bold: true, color: C.white, margin: 0 });
    s.addText("Under the hood: Volatility3 wrapping, asynchronous GUI pipelines,\nand automated YARA rule ingestion mechanisms.", { x: 0.8, y: 3.2, w: 8.4, h: 0.8, fontSize: 16, color: C.light, margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.525, w: 10, h: 0.1, fill: { color: C.blue }, line: { color: C.blue } });
  }

  // ─────────────────────────────────────────
  // SLIDE 2 — System Architecture
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("System Architecture Overview", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 28, bold: true, color: C.white, margin: 0 });
    s.addText("Decoupled logic for maintainability and non-blocking execution", { x: 0.5, y: 0.8, w: 9, h: 0.3, fontSize: 14, color: C.muted, margin: 0 });

    // UI Layer
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.5, w: 2.5, h: 3.0, fill: { color: C.darkCard }, line: { color: C.cyan } });
    s.addText("Presentation Layer\n(PyQt5 GUI)", { x: 0.5, y: 1.6, w: 2.5, h: 0.6, fontSize: 12, bold: true, color: C.cyan, align: "center", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 2.3, w: 2.1, h: 0.6, fill: { color: C.codeBg }, line: { color: C.border } });
    s.addText("MainWindow\nState Management", { x: 0.7, y: 2.3, w: 2.1, h: 0.6, fontSize: 10, color: C.light, align: "center", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 0.7, y: 3.1, w: 2.1, h: 0.6, fill: { color: C.codeBg }, line: { color: C.border } });
    s.addText("QStackedWidget\nDynamic Views", { x: 0.7, y: 3.1, w: 2.1, h: 0.6, fontSize: 10, color: C.light, align: "center", margin: 0 });

    // Arrows
    s.addText("QThread\nSignals", { x: 3.0, y: 2.5, w: 0.9, h: 0.4, fontSize: 9, color: C.muted, align: "center", margin: 0 });
    s.addShape(pres.shapes.RIGHT_ARROW, { x: 3.1, y: 2.9, w: 0.7, h: 0.2, fill: { color: C.muted }, line: { color: C.muted } });

    // Integration Layer
    s.addShape(pres.shapes.RECTANGLE, { x: 3.9, y: 1.5, w: 2.5, h: 3.0, fill: { color: C.darkCard }, line: { color: C.green } });
    s.addText("Integration Layer\n(Core Wrappers)", { x: 3.9, y: 1.6, w: 2.5, h: 0.6, fontSize: 12, bold: true, color: C.green, align: "center", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.1, y: 2.3, w: 2.1, h: 0.6, fill: { color: C.codeBg }, line: { color: C.border } });
    s.addText("VolatilityManager\nSubprocess Controller", { x: 4.1, y: 2.3, w: 2.1, h: 0.6, fontSize: 10, color: C.light, align: "center", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 4.1, y: 3.1, w: 2.1, h: 0.6, fill: { color: C.codeBg }, line: { color: C.border } });
    s.addText("YaraScanner\nRule Compiler & Merger", { x: 4.1, y: 3.1, w: 2.1, h: 0.6, fontSize: 10, color: C.light, align: "center", margin: 0 });

    // Arrows
    s.addText("Subprocess\nJSON IO", { x: 6.4, y: 2.5, w: 0.9, h: 0.4, fontSize: 9, color: C.muted, align: "center", margin: 0 });
    s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.5, y: 2.9, w: 0.7, h: 0.2, fill: { color: C.muted }, line: { color: C.muted } });

    // Execution Layer
    s.addShape(pres.shapes.RECTANGLE, { x: 7.3, y: 1.5, w: 2.2, h: 3.0, fill: { color: C.darkCard }, line: { color: C.orange } });
    s.addText("Execution Layer\n(External Binaries)", { x: 7.3, y: 1.6, w: 2.2, h: 0.6, fontSize: 12, bold: true, color: C.orange, align: "center", margin: 0 });
    s.addShape(pres.shapes.RECTANGLE, { x: 7.5, y: 2.3, w: 1.8, h: 1.4, fill: { color: C.codeBg }, line: { color: C.border } });
    s.addText("Volatility3 API\n-----------------\n• Memory Parsing\n• VAD Traversing\n• Crypto Extraction", { x: 7.5, y: 2.4, w: 1.8, h: 1.2, fontSize: 9, color: C.light, align: "center", margin: 0 });
  }

  // ─────────────────────────────────────────
  // SLIDE 3 — The Volatility Wrapper
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.green }, line: { color: C.green } });

    s.addText("VolatilityManager: Execution & Parsing", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 28, bold: true, color: C.white, margin: 0 });
    
    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 4.3, h: 3.8, fill: { color: C.codeBg }, line: { color: C.border } });
    const code = `def run_command(self, plugin, extra_args=[]):
    cmd = [
        self.vol_exe,
        "-f", self.dump_path,
        "-r", "json",
        plugin
    ] + extra_args

    try:
        result = subprocess.run(
            cmd, capture_output=True,
            text=True, timeout=300
        )
        return json.loads(result.stdout)
    except Exception as e:
        # Handle Timeout, DecodeErrors
        return []`;
    s.addText(code, { x: 0.6, y: 1.3, w: 4.1, h: 3.6, fontSize: 11, fontFace: "Consolas", color: C.green, margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: 5.0, y: 1.2, w: 4.5, h: 3.8, fill: { color: C.darkCard }, line: { color: C.border } });
    s.addText("Technical Implementation Details", { x: 5.2, y: 1.4, w: 4.1, h: 0.4, fontSize: 14, bold: true, color: C.white, margin: 0 });
    
    const pts = [
      { t: "Dynamic Binary Resolution:", d: "Automatically falls back from embedded virtual environment (venv) binary to system path." },
      { t: "Structured Output Mapping:", d: "Force Volatility to emit '-r json' to bypass unreliable stdout string scraping." },
      { t: "Process Isolation:", d: "Subprocess isolates Volatility crashes from the PyQt main application." },
      { t: "Strict Bounds:", d: "Implements a 5-minute timeout boundary to prevent hanging on corrupted memory dumps." }
    ];
    pts.forEach((p, i) => {
      s.addText([
        { text: p.t + "\n", options: { bold: true, color: C.cyan, fontSize: 12 } },
        { text: p.d, options: { color: C.muted, fontSize: 11 } }
      ], { x: 5.2, y: 1.9 + (i * 0.75), w: 4.1, h: 0.65, margin: 0 });
    });
  }

  // ─────────────────────────────────────────
  // SLIDE 4 — Async GUI with QThread
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.blue }, line: { color: C.blue } });

    s.addText("Asynchronous Pipeline via QThread", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 28, bold: true, color: C.white, margin: 0 });

    s.addText("Problem:", { x: 0.5, y: 1.0, w: 1.2, h: 0.3, fontSize: 14, bold: true, color: C.orange, margin: 0 });
    s.addText("Volatility scans are blocking I/O operations taking 30s+; running them on the main thread triggers OS 'Application Not Responding'.", { x: 1.5, y: 1.0, w: 8.0, h: 0.3, fontSize: 13, color: C.light, margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.5, w: 4.3, h: 3.5, fill: { color: C.codeBg }, line: { color: C.border } });
    const code2 = `class RunVolThread(QThread):
    done = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        try:
            vol = VolatilityManager(self.path)
            func = getattr(vol, self.method)
            result = func()
            self.done.emit(result)
        except Exception as e:
            self.error.emit(str(e))

# In main window:
self.thread1 = RunVolThread(path, "run_pslist")
self.thread1.done.connect(self.on_done)
self.thread1.start()`;
    s.addText(code2, { x: 0.6, y: 1.6, w: 4.1, h: 3.3, fontSize: 11, fontFace: "Consolas", color: C.blue, margin: 0 });

    s.addShape(pres.shapes.RECTANGLE, { x: 5.0, y: 1.5, w: 4.5, h: 3.5, fill: { color: C.darkCard }, line: { color: C.border } });
    
    s.addText("Thread Chaining Implementation", { x: 5.2, y: 1.7, w: 4.1, h: 0.4, fontSize: 14, bold: true, color: C.white, margin: 0 });
    
    s.addText("Instead of deeply nested async calls, the pipeline uses Sequential Signal Emitting:\n\n1. Thread finishes -> Emits `done` signal.\n2. Slot receives data -> Updates GUI table.\n3. Slot initiates Thread 2.\n4. If error -> Emits `error` -> Slot logs it and still launches Thread 2.", {
      x: 5.2, y: 2.3, w: 4.1, h: 2.0, fontSize: 12, color: C.light, margin: 0
    });
  }

  // ─────────────────────────────────────────
  // SLIDE 5 — The YARA Engine
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.orange }, line: { color: C.orange } });

    s.addText("YaraScanner: Dynamic Threat Intelligence", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 28, bold: true, color: C.white, margin: 0 });

    // Workflow diagram
    const boxes = [
      { x: 0.5, t: "urllib.request", d: "Auto-fetches Neo23x0 rules missing from disk" },
      { x: 3.8, t: "yara-python", d: "Pre-compiles .yar files to detect syntax errors" },
      { x: 7.1, t: "Volatility Yarascan", d: "Injects compiled master file into process memory space" }
    ];

    boxes.forEach(b => {
      s.addShape(pres.shapes.RECTANGLE, { x: b.x, y: 1.2, w: 2.4, h: 1.0, fill: { color: C.darkCard }, line: { color: C.orange } });
      s.addText(b.t, { x: b.x, y: 1.3, w: 2.4, h: 0.3, fontSize: 12, bold: true, color: C.orange, align: "center", margin: 0 });
      s.addText(b.d, { x: b.x+0.1, y: 1.6, w: 2.2, h: 0.5, fontSize: 10, color: C.light, align: "center", margin: 0 });
    });

    s.addShape(pres.shapes.RIGHT_ARROW, { x: 3.1, y: 1.6, w: 0.5, h: 0.2, fill: { color: C.muted } });
    s.addShape(pres.shapes.RIGHT_ARROW, { x: 6.4, y: 1.6, w: 0.5, h: 0.2, fill: { color: C.muted } });

    s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.7, w: 9.0, h: 2.3, fill: { color: C.codeBg }, line: { color: C.border } });
    const code3 = `def merge_all_rules(self):
    # Volatility accepts ONLY ONE YARA file. We must dynamically concatenate.
    with open("all_rules.yar", "w") as out_file:
        for filepath in glob.glob("*.yar"):
            try:
                yara.compile(filepath=filepath) # Syntax pre-validation
            except yara.SyntaxError:
                continue # Gracefully skip broken community rules
            out_file.write(open(filepath).read() + "\\n")`;
    s.addText("Rule Aggregation Logic", { x: 0.7, y: 2.8, w: 5.0, h: 0.3, fontSize: 12, bold: true, color: C.white, margin: 0 });
    s.addText(code3, { x: 0.7, y: 3.1, w: 8.6, h: 1.7, fontSize: 12, fontFace: "Consolas", color: C.orange, margin: 0 });
  }

  // ─────────────────────────────────────────
  // SLIDE 6 — Summary
  // ─────────────────────────────────────────
  {
    const s = pres.addSlide();
    s.background = { color: C.darkBg };
    s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.06, fill: { color: C.cyan }, line: { color: C.cyan } });

    s.addText("Technical Achievements Summary", { x: 0.5, y: 0.2, w: 9, h: 0.6, fontSize: 28, bold: true, color: C.white, margin: 0 });

    const achievements = [
      "Zero-dependency drift via automated venv parsing logic.",
      "O(1) GUI thread blocking: completely decoupled logic from UI.",
      "Resilient JSON deserialization handling raw CLI volatility outputs.",
      "Dynamic YARA parsing engine that self-heals syntax errors."
    ];

    achievements.forEach((a, i) => {
      s.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.5 + (i * 0.9), w: 9.0, h: 0.7, fill: { color: C.darkCard }, line: { color: C.cyan } });
      s.addText("✓", { x: 0.7, y: 1.5 + (i * 0.9), w: 0.5, h: 0.7, fontSize: 18, color: C.cyan, bold: true, margin: 0 });
      s.addText(a, { x: 1.2, y: 1.5 + (i * 0.9), w: 8.0, h: 0.7, fontSize: 14, color: C.white, margin: 0 });
    });
  }

  await pres.writeFile({ fileName: "MemForensics_TechPresentation.pptx" });
  console.log("Technical PPTX Generated!");
}

main().catch(console.error);
