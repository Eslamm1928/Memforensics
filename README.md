<div align="center">

# 🧠 Memory Forensics & Volatile Data Analysis Framework

**A zero-click, automated desktop application for parsing RAM dumps,
extracting forensic artifacts, and detecting malware signatures — before volatile data is lost forever.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PyQt5](https://img.shields.io/badge/PyQt5-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)](https://riverbankcomputing.com/software/pyqt/)
[![Volatility3](https://img.shields.io/badge/Volatility3-Engine-FF6F00?style=for-the-badge)](https://github.com/volatilityfoundation/volatility3)
[![YARA](https://img.shields.io/badge/YARA-Signatures-E74C3C?style=for-the-badge)](https://virustotal.github.io/yara/)

---

</div>

## 📋 Table of Contents

- [Problem Statement](#-problem-statement)
- [Our Solution](#-our-solution)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Project Architecture](#-project-architecture)
- [Installation & Usage](#-installation--usage)
- [Automated Pipeline](#-automated-pipeline)
- [YARA Threat Intelligence](#-yara-threat-intelligence)
- [Credits](#-credits)

---

## 🔍 Problem Statement

In digital forensics, **volatile data** — running processes, active network connections, encryption keys, and loaded malware — resides exclusively in **RAM**. The moment a system is powered off, this critical evidence is **permanently destroyed**.

Traditional forensic tools require extensive manual configuration, plugin-by-plugin execution, and deep command-line expertise. This creates a significant barrier for incident responders who need rapid, actionable intelligence from memory images.

## 💡 Our Solution

**MemForensics** is a **fully automated, zero-click desktop framework** that transforms raw memory dumps into structured forensic intelligence. An investigator simply loads a memory image, and the framework automatically executes a **7-step analysis pipeline** — extracting processes, enumerating DLLs, recovering network sockets, detecting injected code, dumping credentials, scanning for encryption keys, and matching malware signatures using industry-standard YARA rules.

> **Zero manual intervention. Zero command-line interaction. Full forensic coverage.**

---

## ✨ Key Features

| # | Feature | Volatility3 Plugin | Description |
|---|---------|-------------------|-------------|
| 1 | **Process Extraction** | `windows.pslist` | Lists all running/terminated processes with PID, PPID, threads, handles, and timestamps |
| 2 | **DLL Enumeration** | `windows.dlllist` | Extracts loaded Dynamic-Link Libraries for each process with base address, size, and full path |
| 3 | **Network Socket Recovery** | `windows.netscan` | Recovers active TCP/UDP connections, listening ports, local/remote IPs, and owning processes |
| 4 | **Injection Detection** | `windows.malfind` | Identifies suspicious memory regions with `PAGE_EXECUTE_READWRITE` permissions — a hallmark of code injection |
| 5 | **Credential Recovery** | `windows.hashdump` | Extracts Windows SAM database entries including usernames, RIDs, LM hashes, and NTLM hashes |
| 6 | **Encryption Key Detection** | `windows.truecrypt` / `windows.bitlocker` / `windows.cachedump` | Scans for TrueCrypt passphrases, BitLocker FVEKs, and cached domain credentials |
| 7 | **YARA Malware Scan** | `windows.vadyarascan` | Auto-fetches **Neo23x0/signature-base** threat intelligence rules and scans process memory for known malware signatures |

### Additional Highlights

- 🎨 **Modern Dark-Themed Dashboard** — Professional PyQt5 interface with glassmorphism-inspired cards, real-time stat counters, and smooth progress tracking
- ⚡ **Non-Blocking Architecture** — All scans execute on background `QThread` workers, keeping the GUI fully responsive
- 🛡 **Resilient Pipeline** — If any scan fails, the pipeline gracefully continues to the next step without blocking popups
- 📦 **Auto-Setup** — Dependencies are automatically installed from `requirements.txt` on first launch
- 🔍 **Custom YARA Rules** — Add custom rules via local file or URL before each scan (with syntax validation)
- 🔐 **Encryption Key Recovery** — Automatic detection of TrueCrypt, BitLocker, and cached domain credentials

---

## 🛠 Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Language** | Python 3.10+ | Core application logic |
| **GUI Framework** | PyQt5 | Desktop dashboard with dark theme |
| **Forensics Engine** | Volatility3 | Memory image parsing and plugin execution |
| **Malware Detection** | YARA-Python | Signature-based malware scanning |
| **Crypto Support** | PyCryptodome, Cryptography | Required by Volatility for credential extraction |

---

## 📁 Project Architecture

```
MemForensics_Framework/
│
├── main.py                     # Entry point — auto-installs deps & launches GUI
├── requirements.txt            # All Python dependencies
├── run.bat                     # One-click launcher (activates venv)
│
├── core/
│   ├── __init__.py
│   ├── vol_wrapper.py          # VolatilityManager — CLI wrapper with JSON parsing
│   └── yara_scanner.py         # YaraScanner — auto-fetch, merge, and scan
│
├── gui/
│   ├── __init__.py
│   └── main_window.py          # PyQt5 dashboard — full UI + 7-step pipeline
│
└── yara_rules/
    ├── example.yar             # Sample custom rule
    ├── gen_suspicious_strings.yar   # Neo23x0 — obfuscation detection
    ├── apt_cobaltstrike.yar         # Neo23x0 — CobaltStrike beacons
    └── gen_mimikatz.yar             # Neo23x0 — Mimikatz credential dumper
```

---

## 🚀 Installation & Usage

### Prerequisites

- **Python 3.10+** installed on your system
- A **Windows memory dump** file (`.raw`, `.mem`, `.dmp`, `.vmem`)

### Quick Start

**1. Create and activate a virtual environment:**

```bash
python -m venv venv
venv\Scripts\activate
```

**2. Launch the framework:**

```bash
python main.py
```

> On first launch, `main.py` automatically installs all required dependencies from `requirements.txt` into your virtual environment. No manual `pip install` needed.

**3. Alternatively, use the one-click launcher:**

```bash
run.bat
```

**4. In the GUI:**

- Click **📂 Load Memory Dump** and select your memory image
- The **5-step pipeline starts automatically** — sit back and watch the results populate

---

## ⚙ Automated Pipeline

When a memory dump is loaded, the framework executes the following pipeline with **zero user interaction**:

```
📂 Load Dump
    │
    ├──▶ [1/5]  Process Extraction    (pslist)      →  Processes table + stat card
    ├──▶ [2/5]  Network Recovery      (netscan)     →  Network table + stat card
    ├──▶ [3/5]  Injection Detection   (malfind)     →  Malware table + stat card
    ├──▶ [4/5]  Credential Recovery   (hashdump)    →  Credentials table + stat card
    └──▶ [5/5]  YARA Signature Scan   (yarascan)    →  Appended to Malware table
                                                        ✅ All scans complete
```

- Each step runs on a **background thread** (non-blocking GUI)
- If a step fails, the pipeline **gracefully continues** to the next
- YARA results are **appended** to the Malware table with `[YARA]` prefix to distinguish from `malfind` hits
- The **Malware Hits** stat card shows the **combined total** (injections + YARA matches)

---

## 🛡 YARA Threat Intelligence

The framework automatically fetches high-impact YARA rules from **[Neo23x0/signature-base](https://github.com/Neo23x0/signature-base)** — one of the most widely used open-source threat intelligence repositories maintained by Florian Roth.

| Rule File | Detection Target |
|-----------|-----------------|
| `gen_suspicious_strings.yar` | Obfuscated strings, suspicious encoding patterns |
| `apt_cobaltstrike.yar` | CobaltStrike beacon implants and shellcode |
| `gen_mimikatz.yar` | Mimikatz credential harvesting tool signatures |

Rules are downloaded **silently on first scan** and cached in the `yara_rules/` directory. Custom `.yar` files can be added to the same directory for automatic inclusion.

---

## 👥 Credits

### Team Members

| Name | Role |
|------|------|
| **Eslam Ebrahim** | Developer & Architect |
| **Ahmed Emad** | Developer & Testing |
| **Mohamed Wael** | Developer & Documentation |

### Academic Supervisor

> **Dr. Maryam Adel**

---

## 📄 License

This project was developed as part of an academic assignment for the **Advanced Digital Forensics** course.

---

## 🔮 Future Work

### Cross-OS Support (Linux / macOS)

The current framework is optimized for **Windows memory images** exclusively (`windows.*` plugin prefix). Extending to Linux and macOS dumps would require:

1. **OS Auto-Detection**: Implementing a pre-scan step using `banners.Banners` or `configwriter.ConfigWriter` to detect the OS profile of the loaded memory dump before running any analysis plugins.

2. **Dynamic Plugin Mapping**: Creating an OS-to-plugin mapping table:
   | OS | Process List | Network | Injection | Hashes |
   |---|---|---|---|---|
   | Windows | `windows.pslist` | `windows.netscan` | `windows.malfind` | `windows.hashdump` |
   | Linux | `linux.pslist` | `linux.sockstat` | `linux.malfind` | N/A |
   | macOS | `mac.pslist` | `mac.netstat` | `mac.malfind` | N/A |

3. **Column Adaptation**: Each OS returns different JSON schemas, requiring OS-specific column definitions in the `ForensicsPage.COLUMN_DEFS` dictionary.

4. **Credential Plugin Availability**: Not all credential plugins are available for all OS types (e.g., `hashdump` is Windows-only).

> **Decision Rationale**: This enhancement was deferred to avoid breaking the current stable zero-click pipeline. The architectural change touches every layer (backend, GUI columns, stat cards, error handling) and requires extensive testing with verified Linux/macOS memory dumps.

---

<div align="center">

**Built with 🔬 for Digital Forensics & Incident Response**

</div>
</div>
