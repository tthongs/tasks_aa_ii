# Activity Log & Directory Information (`tasks_aa_ii`)

**Repository Location**: `/home/tthh0ngs/build_tthongs/tasks_aa_ii`  
**Current Branch**: `master`  
**Last Updated**: October 3, 2026  
**Primary Maintainer**: `tthongs` (<sanskarsinghss123@gmail.com>)  

---

## 1. Executive Summary

This repository (`tasks_aa_ii`) serves as an advanced multi-disciplinary engineering workspace combining:
- **Embedded Hardware & Systems Engineering (`vvdn/`)**: Industrial protocols, power electronics converters, semiconductor devices (MOSFETs, LDOs), EV charging systems, elevator dispatch logic, programmable power supplies, reliability standards, and interactive engineering calculators.
- **Hardware FPGA & Digital Logic**: Verilog FPGA UART, 3-state Moore FSM, and gate-level dual lift controller.
- **Digital Signal Processing (DSP) Research**: Core academic and mathematical formulations (ADC/DAC, modulation, FIR/IIR filters, sampling, quantization).
- **System Administration & Linux Kernel Diagnostics (`issues/`)**: CachyOS / Arch Linux kernel modules, systemd boot optimization, NVIDIA drivers, and network scripts.
- **Unix Automation & Scripting**: AWK/SED text processing utilities and KDE Plasma / KWin QML scripts.
- **Freshers' Training 2026 Transcripts**: Chronologically organized transcript files for embedded hardware training sessions.

### Key Metrics
- **Subdirectories**: 15 active modules
- **Tracked Files**: ~160+ files spanning Documentation (`.md`, `.docx`, `.pdf`), Python CLI calculators (`.py`), Verilog (`.v`), Shell (`.sh`), QML (`.qml`), Scripting (`.awk`, `.txt`), and Transcripts (`.txt`).
- **System Issues Logged**: 23 distinct system, driver, and application issues tracked and resolved.

---

## 2. Directory Architecture & Subproject Overview

```text
tasks_aa_ii/
├── ACTIVITY_LOG.md          # Central workspace activity, context, and agent guide
├── T8/                      # Tekken 8 combo extraction & spreadsheet generator
├── aujus_ug/                # Xilinx 7 Series FPGA official User Guides (UG470-UG474, UG888)
├── coffee/                  # Home coffee & cold brew recipes reference
├── dsp/                     # Digital Signal Processing notes (ADC/DAC, Modulation, Filters)
├── fsm/                     # Verilog 3-state Moore Finite State Machine implementation
├── issues/                  # Centralized system diagnostics, driver fixes & shell scripts
├── project_report/          # Academic project report documentation (.docx format v5)
├── secure_boot_keys_help/   # Linux Secure Boot, MOK, & sbctl management guides
├── sshh/                    # SSH connection configuration instructions
├── uart/                    # Verilog Hardware UART Receiver/Transmitter design
├── unix/                    # KDE Plasma / KWin / DBus interprocess communication (QML)
├── unix_scripting/          # AWK and SED text processing practice & scripts
├── vlc/                     # VLC subtitle rendering and FreeType debug workspace
└── vvdn/                    # VVDN Engineering Hub & Protocol Knowledge Base
    ├── README.md (.docx)    # Central dashboard, quick links & CLI tools cheatsheet
    ├── active/              # In-progress hardware investigations & open issues
    ├── resolved/            # Documented fixes, post-mortems, and Root Cause Analysis (RCA)
    ├── templates/           # Device bring-up checklist & issue reporting template
    ├── tools/               # 15 Python CLI calculators & document generator
    ├── raw_transcripts/     # 12 Freshers' Training 2026 lecture transcripts (chronological)
    ├── img/                 # Session screenshot references (Google Drive folders)
    ├── protocols/           # Serial & vehicle protocols (UART, SPI, I2C, CAN, LIN, NFC)
    ├── converters/          # 20 Power Electronic Converters (DC-DC, AC-DC, DC-AC, AC-AC)
    ├── mosfets/             # MOSFET physics, 8-phase switching waveforms & 11 topologies
    ├── ldo/                 # Low-Dropout Linear Regulators (PMOS vs NMOS, ESR, thermal)
    ├── evse/                # Electric Vehicle Supply Equipment (AC Smart Charger & IoT)
    ├── dual_lift_controller/# Gate-level nearest-lift dispatch logic (3 & 4 floors)
    ├── smart_programmable_power_supply/ # 60W Universal AC-DC (85-265V AC -> 5-20V / 3A DC)
    └── standards/           # Hardware compliance & reliability (RoHS, REACH, AEC, MSL)
```

---

### Detailed Subproject Descriptions

#### 1. `vvdn/` - VVDN Engineering Hub & Protocol Knowledge Base
The central engineering knowledge base and embedded systems reference hub at VVDN:
- **`protocols/`**: Master hubs, bit-level frame analysis, timing budgets, circuit schematics, and troubleshooting matrices for:
  - **UART**: TTL, RS-232, RS-422, RS-485, 16x oversampling clock recovery, BRG divisors.
  - **SPI**: 4 modes (CPOL/CPHA), AC timing budgets, round-trip delay, Star/Daisy-chain, QSPI/OSPI.
  - **I2C**: Open-drain Wired-AND, pull-up sizing math ($R_{p(min)}, R_{p(max)}$), bus capacitance, clock stretching, 9-clock recovery.
  - **CAN & CAN FD**: Differential signaling, non-destructive bitwise arbitration, TEC/REC fault confinement, J1939, CANopen, UDS over CAN-TP.
  - **LIN**: Single-wire 12V bus, deterministic schedule tables, PID parity ($P0, P1$), Classic/Enhanced checksums, auto-baud sync (`0x55`).
  - **NFC**: 13.56 MHz inductive coupling, 848 kHz load modulation, ISO 14443-3 anti-collision walk, NDEF framing, SPI transceivers (PN532, MFRC522, ST25R3916).
- **`converters/`**: Complete 4-quadrant power electronic converters suite covering 20 topologies with connection netlists, BOMs, and component stress equations:
  - **DC-DC Isolated**: Forward, Flyback, Dual Active Bridge (DAB), Full-Bridge (PSFB), Half-Bridge, Push-Pull, Resonant (SRC, PRC, LLC).
  - **DC-DC Non-Isolated**: Buck, Boost, Buck-Boost (inverting & 4-switch synchronous), Cuk, SEPIC, Zeta.
  - **AC-DC Rectifiers**: Uncontrolled diode bridges, controlled thyristor rectifiers, Active Boost PFC, Bridgeless Totem-Pole GaN, Vienna Rectifier.
  - **DC-AC Inverters**: Single-Phase (bipolar/unipolar SPWM) and Three-Phase VSIs (180°/120° six-step, THIPWM, Space Vector PWM / SVPWM).
  - **AC-AC Converters**: Line-commutated cycloconverters and AC voltage controllers (TRIAC / antiparallel SCR phase angle and burst firing).
- **`mosfets/`**: Semiconductor physics, 8-phase dynamic switching waveforms, Zero-Voltage Switching (ZVS), Unclamped Inductive Switching (UIS) avalanche breakdown ($E_{AS}$), Safe Operating Area (SOA/Spirito), Miller clamps, Kelvin Source, and 11 distinct device categories (e-NMOS, e-PMOS, d-MOSFET, Trench UMOS/SGT, VDMOS, Superjunction CoolMOS, SiC, Logic-level, LDMOS RF, FinFET/GAAFET, Dual-gate tetrode).
- **`ldo/`**: Low-Dropout Regulators covering PMOS (Common-Source, ESR stability tunnel) vs NMOS (Source-Follower, charge pump / $V_{BIAS}$), feedback networks, feedforward capacitors ($C_{FF}$), thermal dissipation networks, and hybrid SMPS pre-regulator + LDO post-regulator architecture.
- **`evse/`**: AC Smart Charger architecture separating High-Voltage power distribution from Low-Voltage (SELV) Controller board. Features Control Pilot ($\pm 12\,\text{V}$ PWM state machine A-F), Proximity Pilot cable detection, $6\,\text{mA}$ DC / $30\,\text{mA}$ AC RCM leakage trip, contactor weld detection, and dual-processor IoT gateway running OCPP 1.6-J / 2.0.1.
- **`dual_lift_controller/`**: Gate-level nearest-lift dispatch system for 3-floor and 4-floor buildings. Features absolute difference subtractors ($|R - A|, |R - B|$), 2-bit magnitude comparators, direction logic ($UP, DOWN, STOP$), 7400-series TTL IC schematics, and synthesizable Verilog modules (`dual_lift_controller.v`, `dual_lift_controller_tb.v`).
- **`smart_programmable_power_supply/`**: $60\,\text{W}$ ($5\text{--}20\,\text{V}$ @ $3\,\text{A}$) programmable power supply module. Universal AC mains ($85\text{--}265\,\text{V}_{AC}$) input, QR Flyback intermediate stage ($+24\,\text{V}$), 4-switch Buck-Boost post-regulator, 12-bit DAC feedback summing, isolated dual-domain power metering, real-time efficiency ($\eta = P_{DC} / P_{AC}$ at 10 Hz), and FreeRTOS MicroSD FAT32 CSV logging.
- **`standards/`**: Hardware regulatory compliance, quality, and reliability across the product lifecycle (RoHS, REACH, AEC-Q100/101/200, MSL 1–6).
- **`tools/`**: 15 interactive Python CLI calculation tools (`uart_calc.py`, `baud_calc.py`, `spi_calc.py`, `i2c_calc.py`, `can_calc.py`, `lin_calc.py`, `nfc_calc.py`, `ldo_calc.py`, `mosfet_calc.py`, `evse_calc.py`, `lift_sim.py`, `psu_calc.py`, `md_to_docx.py`).
- **`raw_transcripts/`**: Chronologically structured transcript files from the Freshers' Training 2026 series (see Section 6).

#### 2. `T8/` - Gaming Data Extraction & Analytics
- Extracted combo notations and input sequences for Fahkumram in *Tekken 8*.
- Derived from YouTube ReVanced video screenshots, processed via Tesseract OCR and Pillow image segmentation into an Excel spreadsheet (`Fahkumram_Tekken_8_Combos.xlsx`).

#### 3. `aujus_ug/` - Xilinx 7 Series FPGA Reference Documentation
- Official Xilinx Artix-7, Kintex-7, and Virtex-7 FPGA architecture user guides (UG470 configuration, UG471 SelectIO, UG472 clocking, UG473 memory, UG474 CLB, UG888 Vivado tutorial).

#### 4. `coffee/` - Home Brewing Documentation
- Coffee and cold brew concentrate recipes (Hot coffee, cold brew concentrate, Nespresso iced coffee).

#### 5. `dsp/` - Digital Signal Processing Core Notes
- Theoretical and mathematical notes on ADC/DAC, analog/digital modulation (AM, FM, PM, ASK, FSK, PSK, QAM), auto/cross-correlation, FIR/IIR filters, sampling and quantization, spread spectrum (DSSS, FHSS), and windowing/stability.

#### 6. `fsm/` - Hardware Finite State Machine (Verilog)
- Synthesizable Verilog implementation of a 3-state Moore Finite State Machine (`STATE_A`, `STATE_B`, `STATE_C`) with Icarus Verilog simulation workflow.

#### 7. `issues/` - System Diagnostics & Issue Management Hub
- Centralized log tracking Linux system issues, systemd optimizations, driver fixes, and shell scripts (23 issues tracked).

#### 8. `project_report/` - Project Documentation
- Academic project report in Microsoft Word format (`project_repo_ff_v5.docx`).

#### 9. `secure_boot_keys_help/` - Linux Secure Boot Key Management
- Operational reference guide for Linux Secure Boot, MOK enrollment, and DKMS module signing using `sbctl` and `mokutil`.

#### 10. `sshh/` - SSH Configuration Guide
- Secure Shell authentication, keygen, and server connection workflows.

#### 11. `uart/` - Hardware UART Core (Verilog)
- Parameterized Verilog hardware implementation of UART transmitter, receiver, and baud rate generator for FPGAs.

#### 12. `unix/` - Desktop Engine & Interprocess Scripting
- QML test scripts for KDE Plasma, KWin window manager, and DBus interprocess communication.

#### 13. `unix_scripting/` - AWK & SED Text Automation Practices
- Reference guides and practice scripts for text manipulation using AWK and SED.

#### 14. `vlc/` - Video & Subtitle Rendering Troubleshooting
- Test environment isolating VLC subtitle rendering issues on Arch/CachyOS Linux.

---

## 3. Log of Tracked System Issues (`issues/`)

| Issue ID | Subject / Summary | Status | Resolution / Artifacts |
| :--- | :--- | :---: | :--- |
| **ISSUE_002** | Chrome/Brave "did not shut down properly" error | **Resolved** | `fix_browser_shutdown.sh`, `REPORT_002_browser_restore_fix.md` |
| **ISSUE_003** | Systemd boot service latency & bottleneck optimization | **Resolved** | `optimize_boot_services.sh`, `ISSUE_003_further_boot_optimization.md` |
| **ISSUE_004** | Bootloader (GRUB/loader) phase bottleneck | **Resolved** | `boot_optimization_summary.txt`, `ISSUE_004_loader_boot_optimization.md` |
| **ISSUE_005** | Arch/CachyOS package maintenance & kernel sync | **Resolved** | System upgrades & kernel module refresh |
| **ISSUE_006** | AUR Malware Audit & Security Vulnerability Scan | **Resolved** | `ISSUE_006_aur_malware_audit.md` |
| **ISSUE_007** | NTFS SSD Mount Failure & Intermittent Disconnects | **In Progress** | `fix_ssd_mount.sh`, `ISSUE_007_ssd_mount_issues.md` |
| **ISSUE_008** | RQuickShare BLE Advertiser Interference on Android | **Resolved** | `fix_rquickshare.sh`, `ISSUE_008_rquickshare_discovery_failure.md` |
| **ISSUE_009** | MediaTek MT7922 Bluetooth Firmware Loading Failure | **Resolved** | `fix_bluetooth_firmware.sh`, `ISSUE_009_bluetooth_firmware_failure.md` |
| **ISSUE_010** | Tekken 8 Stutter/Lag on Hybrid NVIDIA/Intel Laptop | **Resolved** | `ISSUE_010_fix_tekken_8_lag.md` |
| **ISSUE_011** | Microphone Static Noise & Audio Gain Calibration | **Resolved** | `ISSUE_011_microphone_driver_and_gain_fix.md` |
| **ISSUE_012** | KDE Connect Availability & UFW Firewall Configuration | **Resolved** | `fix_kdeconnect.sh`, `ISSUE_012_kde_connect_firewall_enable.md` |
| **ISSUE_013** | Automatic Git Repository Push on Logged Issue | **Resolved** | `auto_push_issue.sh`, `.githooks/post-commit` |
| **ISSUE_014** | Update GRUB Bootloader Timeout to 50 Seconds | **Resolved** | `/etc/default/grub`, `ISSUE_014_update_grub_timeout_to_50s.md` |
| **ISSUE_015** | Add Custom Power Off Entry to GRUB Menu | **Resolved** | `/etc/grub.d/40_custom`, `ISSUE_015_add_grub_poweroff_entry.md` |
| **ISSUE_016** | NVIDIA Open Driver Deadlock & Boot Crash Recovery | **Resolved** | `nvidia-open-dkms`, `REPORT_004_nvidia_driver_and_system_audit.md` |
| **ISSUE_017** | Fix Locale Encoding & XKB Compose Table Warning | **Resolved** | `fix_locale_utf8.sh`, `ISSUE_017_fix_locale_utf8_compose_table.md` |
| **ISSUE_018** | Systemd Modules Load Stall & Early Boot Start Job Hang | **Resolved** | `fix_kernel_modules_boot.sh`, `REPORT_005_kernel_module_boot_stalls_fix.md` |
| **ISSUE_019** | Configure /etc/fstab for OS NTFS Partition Automount | **Resolved** | `fix_os_ntfs_automount.sh`, `ISSUE_019_configure_ntfs_os_fstab_automount.md` |
| **ISSUE_020** | Configure Bash-Insulter on Every Command Not Found | **Resolved** | `/etc/bash.bashrc` hook, `ISSUE_020_configure_bash_insulter_every_command.md` |
| **ISSUE_021** | Rename GRUB Windows Boot Manager to Windows 11 | **Resolved** | `fix_grub_windows_entry.sh`, `ISSUE_021_rename_grub_windows_boot_manager.md` |
| **ISSUE_022** | Configure OpenSSH Server, UFW Firewall, Remote Access | **Resolved** | `setup_remote_ssh.sh`, `REPORT_006_openssh_remote_access_setup.md` |
| **ISSUE_023** | Disable EFI BootNext Entries & GRUB Override Fix | **Resolved** | `fix_grub_efi_bootnext.sh`, `ISSUE_023_disable_grub_efi_bootnext_entries.md` |

---

## 4. Complete Git Commit Activity Log

| Commit Hash | Date | Author | Summary & Key Affected Components |
| :--- | :--- | :--- | :--- |
| `59101d0` | 2026-10-01 | tthongs | `new transcript files made for processing` (Staging Freshers' training transcript files) |
| `54a51dc` | 2026-10-01 | tthongs | `feat(converters): add detailed hardware schematics, netlists & BOMs across all 20 converter topologies` |
| `94c2e9b` | 2026-10-01 | tthongs | `chore(ssh): auto-update active remote SSH command to port 28636` |
| `3fcaa18` | 2026-09-29 | tthongs | `chore(ssh): auto-update active remote SSH command to port 14156` |
| `fdecc74` | 2026-09-29 | tthongs | `feat(converters): add comprehensive power electronic converters knowledge base across DC-DC, AC-AC, DC-AC, AC-DC` |
| `3308b4a` | 2026-09-29 | tthongs | `feat(spps): add Smart Programmable Power Supply engineering design suite, schematics, and calculation tool` |
| `f55232e` | 2026-09-29 | tthongs | `docs(mosfets): add detailed static, dynamic switching, and fault waveforms across all working regions` |
| `c22646b` | 2026-09-29 | tthongs | `docs(power-electronics): add comprehensive Power MOSFET and LDO power electronics guides and schematics` |
| `6b4cd25` | 2026-09-29 | tthongs | `docs(protocols): add circuit connection guides and ASCII schematics for UART, SPI, I2C, LIN, and CAN` |
| `1e5cf96` | 2026-09-29 | tthongs | `docs(protocols): complete UART and SPI master hubs, frame analysis, and calculators` |
| `bbabdd0` | 2026-09-29 | tthongs | `feat(mosfets): add comprehensive MOSFET study modules, calculators, and documentation suite` |
| `698ff0d` | 2026-09-28 | tthongs | `docs(grub): add ISSUE_023 to disable EFI BootNext entries and fix script` |
| `966c87c` | 2026-09-28 | tthongs | `feat(evse): add EVSE low voltage controller architecture, IoT subsystem, and hardware guides` |
| `b0335ba` | 2026-09-27 | tthongs | `feat(i2c): add I2C protocol guides, frame analysis, timing specs, and calculation suite` |
| `2226fb3` | 2026-09-27 | tthongs | `nfc added` (Near Field Communication suite, ISO 14443-3/4, SPI frontends, NDEF) |
| `03b40a9` | 2026-09-27 | tthongs | `feat(spi): add SPI protocol guides, timing calculations, and frame analysis suite` |
| `6132b1e` | 2026-07-25 | tthongs | `ggs` - Cleanup of Maggi documentation files |
| `0c617e7` | 2026-07-04 | tthongs | `fix(bluetooth): resolve RQuickShare background BLE advertiser interference [ISSUE_008]` |
| `730b7ad` | 2026-06-30 | tthongs | `fix(t8): resolve Tekken 8 lag on hybrid graphics laptop [ISSUE_010]` |
| `acb15fd` | 2026-06-30 | tthongs | `Resolve ISSUE_009: Bluetooth Firmware Loading Failure (MT7922)` |
| `55e10a2` | 2026-06-29 | tthongs | `feat(T8): extract and compile Tekken 8 Fahkumram combos into a styled Excel sheet` |
| `9dfd7b4` | 2026-06-23 | tthongs | `fix(ssd): add configuration script and documentation for SSD mount issues [ISSUE_007]` |
| `4e47751` | 2026-06-17 | tthongs | `docs: document AUR malware audit and system scan results [ISSUE_006]` |
| `456154e` | 2026-05-26 | tthongs | `docs: initialize project with Xilinx 7 Series documentation and GEMINI.md` |
| `c19896a` | 2026-04-05 | tthongs | `ggs` - Initial commit of KDE/QML scripts (`unix/`) |

---

## 5. Freshers' Training 2026 Transcripts (`vvdn/raw_transcripts/`)

Derived from Google Drive session folders ([`vvdn/img/Screenshot 2026-10-03 163025.png`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/img/Screenshot%202026-10-03%20163025.png)), these 12 files are ordered **chronologically from earliest to latest** using the naming format `number_topicname_sessionname.txt`:

| # | Date & Time | Topic Name | Trainer / Speaker | File Path |
|---|:---|:---|:---|:---|
| **01** | 11 Sep 2026 (14:23 IST) | PCB Basics | Ragul Rajamani | [`vvdn/raw_transcripts/01_pcb_basics_ragul_rajamani.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/01_pcb_basics_ragul_rajamani.txt) |
| **02** | 16 Sep 2026 (16:55 IST) | Introduction to Embedded Hardware | Vignesh Ananthan | [`vvdn/raw_transcripts/02_introduction_to_embedded_hardware_vignesh_ananthan.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/02_introduction_to_embedded_hardware_vignesh_ananthan.txt) |
| **03** | 18 Sep 2026 (09:25 IST) | Power Design & Analysis | Karpagamoorthy R | [`vvdn/raw_transcripts/03_power_design_and_analysis_karpagamoorthy_r.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/03_power_design_and_analysis_karpagamoorthy_r.txt) |
| **04** | 23 Sep 2026 (11:00 IST) | PRD Sample Walkthrough | Gaurav Gupta | [`vvdn/raw_transcripts/04_prd_sample_walkthrough_gaurav_gupta.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/04_prd_sample_walkthrough_gaurav_gupta.txt) |
| **05** | 24 Sep 2026 (09:43 IST) | Component Selection | Vignesh Anandhan | [`vvdn/raw_transcripts/05_component_selection_vignesh_anandhan.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/05_component_selection_vignesh_anandhan.txt) |
| **06** | 25 Sep 2026 | Hardware Architecture Walk Through | Vignesh Anandhan | [`vvdn/raw_transcripts/06_hardware_architecture_walkthrough_vignesh_anandhan.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/06_hardware_architecture_walkthrough_vignesh_anandhan.txt) |
| **07** | 28 Sep 2026 | HW Architecture Sample Walk Through | Shivam Saxena | [`vvdn/raw_transcripts/07_hw_architecture_sample_walkthrough_shivam_saxena.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/07_hw_architecture_sample_walkthrough_shivam_saxena.txt) |
| **08** | 29 Sep 2026 | Component Selection - Processor & MCU | Ansar Sulaimaan | [`vvdn/raw_transcripts/08_component_selection_processor_and_microcontroller_ansar_sulaimaan.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/08_component_selection_processor_and_microcontroller_ansar_sulaimaan.txt) |
| **09** | 30 Sep 2026 | HDD Sample Walk Through (Session 1) | Mathan Kumar | [`vvdn/raw_transcripts/09_hdd_sample_walkthrough_session1_mathan_kumar.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/09_hdd_sample_walkthrough_session1_mathan_kumar.txt) |
| **10** | 01 Oct 2026 (09:14 IST) | Memories, Clock & Reset | Vibesh Kumar V | [`vvdn/raw_transcripts/10_memories_clock_and_reset_vibesh_kumar_v.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/10_memories_clock_and_reset_vibesh_kumar_v.txt) |
| **11** | 01 Oct 2026 (11:00 IST) | HDD Sample Walk Through (Session 2) | Mathan Kumar | [`vvdn/raw_transcripts/11_hdd_sample_walkthrough_session2_mathan_kumar.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/11_hdd_sample_walkthrough_session2_mathan_kumar.txt) |
| **12** | 01 Oct 2026 | Component Selection General | Shivam Pandey & Chandan Kumar | [`vvdn/raw_transcripts/12_component_selection_general_shivam_pandey_chandan_kumar.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vvdn/raw_transcripts/12_component_selection_general_shivam_pandey_chandan_kumar.txt) |

Each file is initialized with standard metadata headers and a transcript/notes placeholder.

---

## 6. Antigravity CLI & AI Agent Workspace Guide

When loading this repository in an **Antigravity CLI (`agy`)** or AI pair-programming agent session on Linux:

1. **Context Discovery**:
   - Read this document (`ACTIVITY_LOG.md`) first to understand the workspace structure, active modules, and issues.
   - For embedded hardware, protocols, power electronics, and converters, navigate to `vvdn/README.md`.
2. **Document Synchronization**:
   - Whenever any `.md` file in `vvdn/` is added or modified, compile its `.docx` counterpart using:
     ```bash
     python3 vvdn/tools/md_to_docx.py <path/to/file.md>
     ```
   - To batch-synchronize all dossiers across protocols and standards:
     ```bash
     python3 vvdn/tools/md_to_docx.py
     ```
3. **Hardware Calculators**:
   - Access CLI calculation utilities under `vvdn/tools/` for bit timings, baud rates, pull-up resistors, power loss, and thermal margins.
4. **Issue Tracking Workflow**:
   - For hardware peripherals: Instantiate `vvdn/templates/issue-template.md` in `vvdn/active/`, follow `vvdn/templates/device-bringup-checklist.md`, and move resolved cases to `vvdn/resolved/`.
   - For Linux host/driver issues: Follow the tracking format in `issues/GEMINI.md`.

---

*This document is continuously updated to maintain full synchronization between local Linux workstations and Antigravity CLI environments.*
