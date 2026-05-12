# 🧠 MemForensics Framework — Comprehensive Documentation

---

## 📌 Project Overview

**MemForensics** is a Python + PyQt5 desktop application designed to analyze **Memory Dump** files (RAM images) in a **fully automated, zero-click** manner — no command-line interaction required.

The user does one thing: **loads a Memory Dump file** → the application automatically runs a **7-step analysis pipeline** in the background and displays all results in a professional dashboard.

---

## 🎯 Project Goal & Problem Statement

In Digital Forensics, **Volatile Data** includes:
- Running processes and loaded DLLs
- Active network connections
- Passwords, credential hashes, and encryption keys
- Injected malicious code (Malware)

All of this exists **only in RAM**. When the system powers off → this data is **permanently destroyed**.

### The Problem:
Traditional tools like Volatility require extensive CLI knowledge and manual plugin-by-plugin execution — creating a barrier for incident responders who need fast results.

### The Solution:
MemForensics provides **full automation** — it runs all required Volatility plugins automatically and displays structured results in a modern GUI dashboard. Users can also add **custom YARA rules** via URL or local file before each scan.

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Language | **Python 3.10+** | Core application logic |
| GUI Framework | **PyQt5** | Desktop dashboard with dark theme |
| Forensics Engine | **Volatility3** | Memory image parsing & plugin execution |
| Malware Detection | **YARA-Python** | Signature-based malware scanning |
| Crypto Support | **PyCryptodome + Cryptography** | Required by Volatility for credential extraction |

### `requirements.txt`:
```
PyQt5>=5.15
volatility3>=2.0
yara-python>=4.0
pycryptodome>=3.0
cryptography>=3.0
```

---

## 📁 Project Structure

```
MemForensics_Framework/
│
├── main.py                          # Entry point — installs deps & launches GUI
├── requirements.txt                 # Python dependencies
├── run.bat                          # One-click launcher (activates venv)
├── .gitignore                       # Git ignored files
│
├── core/                            # Backend logic
│   ├── __init__.py                  # Package initializer
│   ├── vol_wrapper.py               # Volatility3 CLI wrapper (7 scan methods)
│   └── yara_scanner.py              # YARA rule management (URL + file + scanning)
│
├── gui/                             # Frontend UI
│   ├── __init__.py                  # Package initializer
│   └── main_window.py               # Full dashboard UI + 7-step pipeline
│
├── yara_rules/                      # YARA rules for malware detection
│   ├── example.yar                  # Sample placeholder rule
│   ├── gen_suspicious_strings.yar   # Suspicious strings detection (from GitHub)
│   ├── apt_cobaltstrike.yar         # CobaltStrike detection (from GitHub)
│   ├── gen_mimikatz.yar             # Mimikatz detection (from GitHub)
│   └── all_rules.yar                # All rules merged (auto-generated)
│
├── docs/                            # Project documentation
│   ├── PROJECT_DOCUMENTATION.md     # Arabic documentation
│   ├── PROJECT_DOCUMENTATION_EN.md  # English documentation (this file)
│   ├── ARCHITECTURE.md              # Architecture diagrams
│   └── FLOW_DIAGRAMS.md             # Detailed flow diagrams
│
├── package.json                     # Node.js deps (for presentation generation only)
├── pr.js                            # Presentation generation script
└── pr_tech.js                       # Technical presentation generation script
```

---

## 📄 Detailed File Breakdown

---

### 1️⃣ `main.py` — Entry Point

**Purpose:** First file executed — does 3 things:

1. **`check_requirements()`** — Auto-installs missing dependencies:
   - Looks for `pip.exe` inside the Virtual Environment (`venv/Scripts/pip.exe`)
   - If found → runs `pip install -r requirements.txt` silently
   - If not found → falls back to system `pip`

2. **`main()`** — Launches the application:
   - Creates `QApplication` instance
   - Sets font to **Segoe UI, size 10**
   - Sets style to **Fusion** (enables full CSS customization)
   - Instantiates `MainWindow()` and shows it

3. **`if __name__ == "__main__"`** — Standard Python entry guard

---

### 2️⃣ `core/vol_wrapper.py` — Volatility3 Wrapper

**Purpose:** Interfaces with the **Volatility3** CLI tool via subprocess.

#### Class: `VolatilityManager`

**`__init__(self, dump_path)`**
- Stores the memory dump file path
- Locates `vol.exe` (Volatility executable) by checking 3 locations:
  1. Virtual Environment: `venv/Scripts/vol.exe`
  2. System PATH: `shutil.which("vol")`
  3. Fallback: raw `vol` command

**`run_command(self, plugin_name, extra_args=[])`**
- Executes Volatility as a subprocess:
  ```bash
  vol -f <dump_path> -r json <plugin_name> [extra_args]
  ```
- `-r json` flag → output is returned as JSON (not plain text)
- Timeout: **300 seconds** (5 minutes)
- On error → returns empty list `[]`

**`run_pslist()`** — Plugin: `windows.pslist.PsList`
- Returns: PID, Name, PPID, Threads, Handles, Session, CreateTime, ExitTime
- **Goal:** Extract all running/terminated processes from memory

**`run_dlllist()`** — Plugin: `windows.dlllist.DllList`
- Returns: PID, Process, Base Address, Size, DLL Name, Path
- **Goal:** Enumerate all loaded Dynamic-Link Libraries for each process

**`run_netscan()`** — Plugin: `windows.netscan.NetScan`
- Returns: Protocol, LocalAddr, LocalPort, ForeignAddr, ForeignPort, State, PID, Owner
- **Goal:** Recover all network connections (TCP/UDP sockets)

**`run_malfind()`** — Plugin: `windows.malfind.Malfind`
- Returns: PID, Process, Start VPN, End VPN, Protection, Hexdump, Disasm
- **Goal:** Detect injected code — looks for memory regions with `PAGE_EXECUTE_READWRITE` permissions

**`run_hashdump()`** — Plugin: `windows.hashdump`
- Returns: User, RID, LM Hash, NTLM Hash, Type
- **Goal:** Extract Windows SAM database password hashes from memory

**`run_encryption_scan()`** — Multiple Plugins
- Tries **3 plugins** sequentially, combining all results:

| Plugin | Detection Target |
|--------|-----------------|
| `windows.truecrypt.Passphrase` | TrueCrypt encryption passphrases |
| `windows.lsadump.Lsadump` | LSA Secrets (VPN passwords, service credentials, encryption keys) |
| `windows.cachedump.Cachedump` | Cached domain login credentials |

- Returns: User/Source, RID/PID, Hash/Key, Extra, Type
- **Goal:** Recover encryption keys and cached credentials from memory

**`run_yarascan(self, yara_file)`** — Plugin: `windows.vadyarascan.VadYaraScan`
- Takes a YARA rules file as extra argument: `--yara-file <path>`
- Returns: Rule, PID, Process, Offset, Match
- **Goal:** Scan process memory for known malware signatures

---

### 3️⃣ `core/yara_scanner.py` — YARA Scanning System

**Purpose:** Manages YARA rules — downloading, validating, merging, and scanning.

#### Class: `YaraScanner`

**`__init__(self)`**
- Creates `yara_rules/` directory if missing
- Defines **3 download URLs** from GitHub

#### 🌐 External Data Sources

Rules are downloaded from **[Neo23x0/signature-base](https://github.com/Neo23x0/signature-base)** on GitHub (maintained by Florian Roth, a leading Threat Intelligence researcher):

| File | Detection Target |
|------|-----------------|
| `gen_suspicious_strings.yar` | Obfuscated strings, suspicious encoding patterns |
| `apt_cobaltstrike.yar` | CobaltStrike beacon implants and shellcode |
| `gen_mimikatz.yar` | Mimikatz credential harvesting tool signatures |

**`add_custom_rule(self, source)`**
- Accepts **both URLs and local file paths**
- If URL (`http://` or `https://`) → downloads to a temp file first
- Validates syntax using `yara.compile(filepath=...)` (if yara-python installed)
- If syntax is invalid → raises `ValueError` with detailed error message
- If valid → copies/moves the file into `yara_rules/` folder
- On failure → cleans up any temp files automatically

**`download_missing_rules()`**
- Checks each rule file — downloads if missing via `urllib.request.urlretrieve`
- If download fails (no internet) → silently skips without crashing

**`merge_all_rules()`**
- Combines all `.yar` files into a single `all_rules.yar`
- Skips `all_rules.yar` and `_merged_rules.yar` (avoids infinite loop)
- If `yara-python` is installed → compile-tests each file before including
- If a rule file has syntax errors → skips it and continues

**`auto_scan(self, dump_path)`**
- Orchestrates everything automatically:
  1. `download_missing_rules()` — fetch missing rules
  2. `merge_all_rules()` — combine into single file
  3. Creates `VolatilityManager` → runs `run_yarascan()` with merged file

---

### 4️⃣ `gui/main_window.py` — Main Dashboard

**This is the largest file** — contains the entire GUI and pipeline orchestration.

#### Color Palette:
| Variable | Hex | Usage |
|----------|-----|-------|
| `bg_dark` | `#0B0E14` | Main background (deep dark) |
| `bg_panel` | `#111621` | Sidebar background |
| `accent` | `#00E5A0` | Primary accent (neon green) |
| `danger` | `#FF6B6B` | Red for warnings |
| `warning` | `#FFD93D` | Yellow for alerts |
| `info` | `#6CB4EE` | Blue for info |
| `purple` | `#A78BFA` | Purple for YARA matches |

#### Components:

**`VolWorker(QThread)`** — Background thread for Volatility scans
- Runs on a separate thread to keep the GUI responsive
- Signals: `finished(list)` on success, `error(str)` on failure

**`YaraWorker(QThread)`** — Background thread for YARA scanning
- Same pattern — runs `YaraScanner.auto_scan()` in background

**`NavButton(QPushButton)`** — Sidebar navigation button
- Icon + Label, checkable, with active/inactive styling
- Active state: green accent with left border indicator
- Hover effect on inactive state

**`StatCard(QFrame)`** — KPI statistics card
- Displays a large number (process count, connections, etc.)
- Has colored glow effect (`QGraphicsDropShadowEffect`)
- 6 cards: Processes (green) | DLLs (purple) | Connections (blue) | Creds & Keys (yellow) | Malfind Hits (red) | YARA Matches (violet)

**`ForensicsPage(QWidget)`** — Data display page
- Contains: section header + description + data table (`QTableWidget`)
- Column definitions stored in `COLUMN_DEFS` dict for each analysis type
- Supports Ctrl+C copy (copies selected rows as tab-separated text)

**`ScanOptionsDialog(QDialog)`** — Pre-scan options dialog
- Shown after loading a dump, before the pipeline starts
- Two actions: "Add Custom YARA Rule" or "Start Scan"
- Styled with dark theme matching the main application

**`RuleSourceDialog(QDialog)`** — Custom YARA rule input
- Sub-dialog supporting two input methods:
  - **URL paste** (QLineEdit for pasting a GitHub raw URL)
  - **Local file browse** (QPushButton opening QFileDialog)
- Validates syntax before adding to the rules folder
- Shows error popup if validation fails, allows retry

**`MainWindow(QMainWindow)`** — Primary application window
- **Sidebar** (230px width): Brand logo + 6 nav buttons + version footer
- **Top Bar**: Loaded file info + "Load Memory Dump" button
- **Stat Cards Row**: 6 KPI cards
- **Stacked Pages**: 6 pages (one per analysis type) via `QStackedWidget`
- **Status Bar**: Status messages + progress bar

#### Pages:
| Page | Nav Button | Stat Card | Data Source |
|------|-----------|-----------|-------------|
| Processes | ⚙ Processes | Processes | `run_pslist()` |
| Loaded DLLs | 📦 Loaded DLLs | Loaded DLLs | `run_dlllist()` |
| Network | 🌐 Network | Connections | `run_netscan()` |
| Credentials & Keys | 🔑 Credentials & Keys | Creds & Keys | `run_hashdump()` + `run_encryption_scan()` |
| Malware Scan | 🛡 Malware Scan | Malfind Hits | `run_malfind()` |
| YARA Scan | 🔍 YARA Scan | YARA Matches | `auto_scan()` (via YaraWorker) |

---

## 🔄 Execution Flow (Step-by-Step)

### Phase 1: Application Startup

```
User runs: python main.py  (or double-clicks run.bat)
    │
    ▼
main.py → check_requirements()
    │
    ├── Locates pip.exe in venv/Scripts/
    ├── Runs: pip install -r requirements.txt -q
    └── All 5 dependencies installed silently
    │
    ▼
main.py → main()
    │
    ├── QApplication created
    ├── Font set: Segoe UI, 10pt
    ├── Style set: Fusion
    ├── MainWindow() instantiated
    │       │
    │       ├── _build_sidebar()     → 6 NavButtons created
    │       ├── _build_top_bar()     → File label + Load button
    │       ├── _build_stat_cards()  → 6 StatCards (all showing "—")
    │       ├── _build_pages()       → 6 ForensicsPages (empty tables)
    │       └── _build_status_bar()  → Status bar + hidden progress bar
    │
    └── window.show() → GUI appears on screen
        Status: "Ready" | All tables empty | Waiting for user input
```

### Phase 2: Loading a Memory Dump

```
User clicks "📂 Load Memory Dump" button
    │
    ▼
QFileDialog opens → Filter: *.raw *.mem *.dmp *.vmem *.lime *.img
    │
    ▼
User selects a file (e.g., "MemoryDump_Lab1.raw")
    │
    ▼
MainWindow._load_dump()
    │
    ├── Stores path in self.loaded_dump_path
    ├── Displays filename + size in MB on the top bar
    ├── Clears all 6 tables (removes old data)
    ├── Resets all 6 stat cards to "—"
    │
    ▼
ScanOptionsDialog opens
    │
    ├── Option 1: "▶ Start Scan" → Pipeline starts immediately
    │
    └── Option 2: "🔍 Add Custom YARA Rule" → Opens RuleSourceDialog
         │
         ├── User pastes a URL  OR  browses a local .yar file
         ├── Clicks "✅ Add Rule"
         ├── YaraScanner.add_custom_rule(source)
         │    ├── If URL → download to temp file
         │    ├── Validate with yara.compile()
         │    ├── If valid → copy to yara_rules/
         │    └── If invalid → show error, allow retry
         ├── Returns to ScanOptionsDialog
         └── User clicks "▶ Start Scan" → Pipeline starts
```

### Phase 3: The 7-Step Automated Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PIPELINE EXECUTION                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 1/7: Process Extraction                                       │
│  ─────────────────────────────                                      │
│  Status Bar: "⏳ [1/7] Process Extraction (pslist) …"               │
│  Progress Bar: visible (indeterminate)                              │
│  Load Button: disabled                                              │
│                                                                     │
│  MainWindow._run_pslist()                                           │
│      └── VolWorker thread starts                                    │
│           └── VolatilityManager("dump.raw")                         │
│                └── subprocess.run:                                   │
│                    vol -f dump.raw -r json windows.pslist.PsList     │
│                └── JSON parsed → list of rows                       │
│                └── Signal: finished(rows) emitted                   │
│                                                                     │
│  _on_pslist_done(rows):                                             │
│      ├── Populates Processes table                                  │
│      ├── Updates Processes stat card (e.g., "47")                   │
│      ├── Switches view to Processes page                            │
│      └── Calls: _run_dlllist()  →  next step                       │
│                                                                     │
│  On Error: logs warning, skips to _run_dlllist()                    │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 2/7: DLL Enumeration                                          │
│  ─────────────────────────                                          │
│  Status Bar: "⏳ [2/7] DLL Extraction (dlllist) …"                  │
│                                                                     │
│  subprocess.run:                                                    │
│      vol -f dump.raw -r json windows.dlllist.DllList                 │
│                                                                     │
│  _on_dlllist_done(rows):                                             │
│      ├── Populates Loaded DLLs table                                │
│      ├── Updates Loaded DLLs stat card                               │
│      └── Calls: _run_netscan()                                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 3/7: Network Socket Recovery                                   │
│  ─────────────────────────────────                                  │
│  Status Bar: "⏳ [3/7] Network Socket Recovery (netscan) …"         │
│                                                                     │
│  subprocess.run:                                                    │
│      vol -f dump.raw -r json windows.netscan.NetScan                 │
│                                                                     │
│  _on_netscan_done(rows):                                             │
│      ├── Populates Network table                                    │
│      ├── Updates Connections stat card                               │
│      └── Calls: _run_malfind()                                      │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 4/7: Injection Detection                                       │
│  ─────────────────────────────                                      │
│  Status Bar: "⏳ [4/7] Injection Detection (malfind) …"             │
│                                                                     │
│  subprocess.run:                                                    │
│      vol -f dump.raw -r json windows.malfind.Malfind                 │
│                                                                     │
│  _on_malfind_done(rows):                                             │
│      ├── Saves rows to self._malfind_rows                           │
│      ├── Populates Malware Scan table                               │
│      ├── Updates Malfind Hits stat card                              │
│      └── Calls: _run_hashdump()                                     │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 5/7: Credential Recovery                                       │
│  ─────────────────────────────                                      │
│  Status Bar: "⏳ [5/7] Credential Recovery (hashdump) …"            │
│                                                                     │
│  subprocess.run:                                                    │
│      vol -f dump.raw -r json windows.hashdump                        │
│                                                                     │
│  _on_hashdump_done(rows):                                            │
│      ├── Saves rows to self._hashdump_rows                          │
│      ├── Populates Credentials & Keys table                         │
│      ├── Updates Creds & Keys stat card                              │
│      └── Calls: _run_encryption_scan()                              │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 6/7: Encryption Key Detection                                  │
│  ──────────────────────────────────                                  │
│  Status Bar: "⏳ [6/7] Encryption Key Detection …"                  │
│                                                                     │
│  Runs 3 plugins sequentially:                                       │
│      1. vol -f dump.raw -r json windows.truecrypt.Passphrase         │
│      2. vol -f dump.raw -r json windows.lsadump.Lsadump             │
│      3. vol -f dump.raw -r json windows.cachedump.Cachedump          │
│                                                                     │
│  _on_encryption_done(rows):                                          │
│      ├── Appends results to existing hashdump rows                  │
│      ├── Re-populates Credentials & Keys table (combined)           │
│      ├── Updates Creds & Keys card with new total                   │
│      └── Calls: _run_auto_yarascan()                                │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  STEP 7/7: YARA Signature Scan                                       │
│  ─────────────────────────────                                      │
│  Status Bar: "⏳ [7/7] YARA Signature Scan (Neo23x0 rules) …"      │
│                                                                     │
│  YaraWorker thread starts:                                          │
│      └── YaraScanner.auto_scan(dump_path)                           │
│           ├── download_missing_rules()                               │
│           │    └── Downloads 3 .yar files from GitHub (if missing)  │
│           ├── merge_all_rules()                                      │
│           │    └── Combines all .yar → all_rules.yar                │
│           │    └── Includes any custom rules added by user          │
│           └── VolatilityManager.run_yarascan(all_rules.yar)         │
│                └── subprocess.run:                                   │
│                    vol -f dump.raw -r json                           │
│                        windows.vadyarascan.VadYaraScan               │
│                        --yara-file all_rules.yar                    │
│                                                                     │
│  _on_yarascan_done(rows):                                            │
│      ├── Populates YARA Scan page (separate from Malware Scan)     │
│      ├── Updates YARA Matches stat card                             │
│      ├── Hides progress bar                                         │
│      ├── Re-enables Load button                                     │
│      └── Status: "✅ All 7 scans complete — X injections +          │
│                    Y YARA matches"                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Error Handling Flow

```
Any step fails (timeout, plugin error, missing symbols, etc.)
    │
    ▼
_on_<step>_error(msg):
    ├── Sets stat card to "0" for that step
    ├── Shows warning in status bar (no popup!)
    └── Calls next step → Pipeline NEVER stops
```

---

## 🔧 External Tools

### Volatility3
- **What:** The industry-standard open-source memory forensics framework
- **How it works:** CLI tool that parses raw memory images and runs analysis plugins
- **How this app uses it:** Spawns it as a `subprocess` with `-r json` for machine-readable output
- **Plugins used:**

| Plugin | Purpose |
|--------|---------|
| `windows.pslist.PsList` | List all processes (active + terminated) |
| `windows.dlllist.DllList` | Enumerate loaded DLLs per process |
| `windows.netscan.NetScan` | Recover network sockets and connections |
| `windows.malfind.Malfind` | Detect injected/suspicious memory regions |
| `windows.hashdump` | Extract SAM database password hashes |
| `windows.truecrypt.Passphrase` | Extract TrueCrypt encryption passphrases |
| `windows.lsadump.Lsadump` | Extract LSA Secrets (encryption keys, service passwords) |
| `windows.cachedump.Cachedump` | Extract cached domain credentials |
| `windows.vadyarascan.VadYaraScan` | Scan memory with YARA signature rules |

### YARA
- **What:** A pattern-matching tool for identifying malware based on rules
- **How this app uses it:**
  1. `yara-python` library — compile-tests rule files locally before merging
  2. Volatility's `vadyarascan` plugin — performs the actual memory scan using the rules
  3. Custom rules can be added via **URL paste** or **local file browse** before each scan

---

## 🔮 Future Work: Cross-OS Support

The current framework is optimized for **Windows memory images** exclusively. Extending to Linux/macOS would require:

| Requirement | Implementation |
|-------------|---------------|
| OS Auto-Detection | Pre-scan with `banners.Banners` to detect OS profile |
| Plugin Mapping | `linux.pslist` / `mac.pslist` instead of `windows.pslist` |
| Column Adaptation | OS-specific JSON schemas require different `COLUMN_DEFS` |
| Plugin Availability | Some plugins (e.g., `hashdump`) are Windows-only |

> This was deferred to avoid breaking the current stable zero-click pipeline.

---

## 👥 Team

| Name | Role |
|------|------|
| **Eslam Ebrahim** | Developer & Architect |
| **Ahmed Emad** | Developer & Testing |
| **Mohamed Wael** | Developer & Documentation |

**Supervisor:** Dr. Maryam Adel | **Course:** Advanced Digital Forensics

---

## ✅ Quick Reference

| Question | Answer |
|----------|--------|
| What does it do? | Automated Memory Dump analysis (7-step pipeline) |
| Written in? | Python + PyQt5 |
| Analysis engine? | Volatility3 (via subprocess) |
| Malware detection? | malfind + YARA Rules (separate pages) |
| Credential recovery? | hashdump + TrueCrypt + LSA Secrets + Cachedump |
| Rules source? | Neo23x0/signature-base on GitHub + custom rules (URL/file) |
| GUI? | PyQt5 Dashboard with Dark Theme (6 pages, 6 stat cards) |
| How to run? | `python main.py` or `run.bat` |
| Supported files? | `.raw`, `.mem`, `.dmp`, `.vmem`, `.lime`, `.img` |
