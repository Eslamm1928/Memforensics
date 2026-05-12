# 🔄 MemForensics — Flow Diagrams

---

## 1. Application Startup Flow

```mermaid
flowchart TD
    A["🖱️ User runs python main.py or run.bat"] --> B["check_requirements()"]
    B --> C{"venv/Scripts/pip.exe exists?"}
    C -->|Yes| D["pip install -r requirements.txt"]
    C -->|No| E["Use system pip"]
    D --> F["main()"]
    E --> F
    F --> G["QApplication created"]
    G --> H["Font: Segoe UI 10pt"]
    H --> I["Style: Fusion"]
    I --> J["MainWindow() instantiated"]
    J --> K["Build Sidebar"]
    J --> L["Build Top Bar"]
    J --> M["Build Stat Cards"]
    J --> N["Build 4 Pages"]
    J --> O["Build Status Bar"]
    K & L & M & N & O --> P["window.show()"]
    P --> Q["✅ GUI Ready — Waiting for user"]
```

---

## 2. Memory Dump Loading Flow

```mermaid
flowchart TD
    A["📂 User clicks Load Memory Dump"] --> B["QFileDialog opens"]
    B --> C{"File selected?"}
    C -->|No| D["❌ Nothing happens"]
    C -->|Yes| E["Store dump path"]
    E --> F["Display filename + size in MB"]
    F --> G["Clear all 4 tables"]
    G --> H["Reset all 4 stat cards to —"]
    H --> I["🚀 Start Pipeline: _run_pslist()"]

    style I fill:#00E5A0,color:#000,stroke:#00C78A
```

---

## 3. The 5-Step Analysis Pipeline

```mermaid
flowchart TD
    START["📂 Memory Dump Loaded"] --> S1

    subgraph S1["Step 1/5 — Process Extraction"]
        S1A["VolWorker Thread starts"] --> S1B["vol -f dump -r json windows.pslist.PsList"]
        S1B --> S1C{"Success?"}
        S1C -->|Yes| S1D["Populate Processes table\nUpdate stat card"]
        S1C -->|No| S1E["Log warning\nCard = 0"]
    end

    S1D --> S2
    S1E --> S2

    subgraph S2["Step 2/5 — Network Recovery"]
        S2A["VolWorker Thread starts"] --> S2B["vol -f dump -r json windows.netscan.NetScan"]
        S2B --> S2C{"Success?"}
        S2C -->|Yes| S2D["Populate Network table\nUpdate stat card"]
        S2C -->|No| S2E["Log warning\nCard = 0"]
    end

    S2D --> S3
    S2E --> S3

    subgraph S3["Step 3/5 — Injection Detection"]
        S3A["VolWorker Thread starts"] --> S3B["vol -f dump -r json windows.malfind.Malfind"]
        S3B --> S3C{"Success?"}
        S3C -->|Yes| S3D["Populate Malware table\nSave rows for later"]
        S3C -->|No| S3E["Log warning\nCard = 0"]
    end

    S3D --> S4
    S3E --> S4

    subgraph S4["Step 4/5 — Credential Recovery"]
        S4A["VolWorker Thread starts"] --> S4B["vol -f dump -r json windows.hashdump"]
        S4B --> S4C{"Success?"}
        S4C -->|Yes| S4D["Populate Credentials table\nUpdate stat card"]
        S4C -->|No| S4E["Log warning\nCard = 0"]
    end

    S4D --> S5
    S4E --> S5

    subgraph S5["Step 5/5 — YARA Signature Scan"]
        S5A["YaraWorker Thread starts"] --> S5B["Download missing rules\nfrom GitHub"]
        S5B --> S5C["Merge all .yar → all_rules.yar"]
        S5C --> S5D["vol -f dump -r json windows.yarascan.YaraScan\n--yara-file all_rules.yar"]
        S5D --> S5E{"Success?"}
        S5E -->|Yes| S5F["Append YARA matches\nto Malware table"]
        S5E -->|No| S5G["Skip YARA results"]
    end

    S5F --> DONE
    S5G --> DONE

    DONE["✅ Pipeline Complete\nAll 5 scans finished"]

    style START fill:#6CB4EE,color:#000
    style DONE fill:#00E5A0,color:#000
```

---

## 4. YARA Scanner Internal Flow

```mermaid
flowchart TD
    A["auto_scan(dump_path)"] --> B["download_missing_rules()"]

    B --> C1{"gen_suspicious_strings.yar\nexists locally?"}
    C1 -->|No| D1["Download from\nGitHub Neo23x0"]
    C1 -->|Yes| C2

    D1 --> C2{"apt_cobaltstrike.yar\nexists locally?"}
    C2 -->|No| D2["Download from\nGitHub Neo23x0"]
    C2 -->|Yes| C3

    D2 --> C3{"gen_mimikatz.yar\nexists locally?"}
    C3 -->|No| D3["Download from\nGitHub Neo23x0"]
    C3 -->|Yes| E

    D3 --> E["merge_all_rules()"]
    E --> F["Scan yara_rules/*.yar"]
    F --> G{"For each .yar file"}
    G --> H{"Is it all_rules.yar?"}
    H -->|Yes| I["Skip"]
    H -->|No| J{"yara-python installed?"}
    J -->|Yes| K{"Compile test passes?"}
    K -->|Yes| L["Append to all_rules.yar"]
    K -->|No| M["Skip broken file"]
    J -->|No| L
    I & M --> G
    L --> G

    G -->|Done| N["Return all_rules.yar path"]
    N --> O["VolatilityManager.run_yarascan(all_rules.yar)"]
    O --> P["Return matched rows"]

    style A fill:#a78bfa,color:#000
    style P fill:#00E5A0,color:#000
```

---

## 5. Volatility Command Execution Flow

```mermaid
flowchart TD
    A["run_command(plugin_name)"] --> B["Build command:\nvol -f dump -r json plugin"]
    B --> C["subprocess.run()\ntimeout=300s"]
    C --> D{"Return code == 0?"}
    D -->|Yes| E["Parse JSON output"]
    D -->|No| F["Print error to console"]
    E --> G["Return list of rows"]
    F --> H["Return empty list"]

    style G fill:#00E5A0,color:#000
    style H fill:#FF6B6B,color:#000
```

---

## 6. Error Handling Strategy

```mermaid
flowchart LR
    A["Step fails"] --> B["_on_error callback"]
    B --> C["Set stat card = 0"]
    C --> D["Show ⚠ in status bar"]
    D --> E["Call next step"]
    E --> F["Pipeline continues ✅"]

    style A fill:#FF6B6B,color:#000
    style F fill:#00E5A0,color:#000
```

---

## 7. Overall Architecture

```mermaid
flowchart TB
    subgraph USER["👤 User"]
        U1["Clicks Load Dump"]
    end

    subgraph GUI["🖥️ gui/main_window.py"]
        MW["MainWindow"]
        VW["VolWorker (QThread)"]
        YW["YaraWorker (QThread)"]
        NB["NavButtons"]
        SC["StatCards"]
        FP["ForensicsPages"]
    end

    subgraph CORE["⚙️ core/"]
        VM["vol_wrapper.py\nVolatilityManager"]
        YS["yara_scanner.py\nYaraScanner"]
    end

    subgraph EXTERNAL["🌐 External"]
        VOL["Volatility3 CLI\n(vol.exe)"]
        GH["GitHub\nNeo23x0/signature-base"]
        DUMP["Memory Dump\n(.raw/.mem/.dmp)"]
    end

    subgraph RULES["📁 yara_rules/"]
        R1["example.yar"]
        R2["gen_suspicious_strings.yar"]
        R3["apt_cobaltstrike.yar"]
        R4["gen_mimikatz.yar"]
        R5["all_rules.yar"]
    end

    U1 --> MW
    MW --> VW
    MW --> YW
    VW --> VM
    YW --> YS
    YS --> GH
    YS -->|merge| RULES
    VM -->|subprocess| VOL
    VOL -->|reads| DUMP
    VOL -->|uses| R5
    VM -->|JSON rows| VW
    VW -->|signal| MW
    YW -->|signal| MW
    MW --> SC
    MW --> FP

    style GUI fill:#111621,color:#E6EDF3
    style CORE fill:#161B28,color:#E6EDF3
    style EXTERNAL fill:#1C2333,color:#E6EDF3
```
