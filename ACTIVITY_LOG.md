# Activity Log & Directory Information (`tasks_aa_ii`)

**Repository Location**: `/home/tthh0ngs/build_tthongs/tasks_aa_ii`  
**Current Branch**: `master`  
**Last Updated**: July 30, 2026  
**Primary Maintainer**: `tthongs` (<sanskarsinghss123@gmail.com>)  

---

## 1. Executive Summary

This directory (`tasks_aa_ii`) serves as a multi-disciplinary technical workspace combining hardware engineering (Verilog FPGA designs), digital signal processing (DSP) research, system administration & CachyOS Linux kernel diagnostics, Unix text processing automation, academic reporting, and multimedia/gaming utilities.

### Key Metrics
- **Subdirectories**: 14 active modules
- **Tracked Files**: ~50 files spanning Verilog (`.v`), Shell (`.sh`), Documentation (`.md`, `.pdf`, `.docx`), QML (`.qml`), Scripting (`.awk`, `.txt`), and Media (`.xlsx`, `.mp4`, `.srt`, `.jpg`)
- **System Issues Logged**: 11 distinct system, driver, and application issues tracked and resolved.

---

## 2. Directory Architecture & Subproject Overview

Below is the complete architectural breakdown of all 14 subdirectories present in `tasks_aa_ii`:

```
tasks_aa_ii/
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
└── vlc/                     # VLC subtitle rendering and FreeType debug workspace
```

### Detailed Subproject Descriptions

#### 1. `T8/` - Gaming Data Extraction & Analytics
- **Purpose**: Extracted combo notations and input sequences for Fahkumram in *Tekken 8*.
- **Workflow**: Derived from YouTube ReVanced video screenshots, processed using Tesseract OCR pre-filtering, Python Pillow image segmentation, and compiled into an Excel spreadsheet.
- **Key Files**:
  - [`T8/Fahkumram_Tekken_8_Combos.xlsx`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/T8/Fahkumram_Tekken_8_Combos.xlsx): Formatted Excel sheet containing Combo IDs, Launchers, Inputs, Just-Frame timings, and Notes.
  - [`T8/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/T8/GEMINI.md): Technical notes on OCR, extraction methodology, and Tekken move legend.

#### 2. `aujus_ug/` - Xilinx 7 Series FPGA Reference Documentation
- **Purpose**: Centralized technical repository for Xilinx Artix-7, Kintex-7, and Virtex-7 FPGA architectures and Vivado Design Suite.
- **Key Files**:
  - [`aujus_ug/ug470_7Series_Config.pdf`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/ug470_7Series_Config.pdf): FPGA Configuration User Guide.
  - [`aujus_ug/ug471_7Series_SelectIO.pdf`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/ug471_7Series_SelectIO.pdf): SelectIO Resources & I/O Standards.
  - [`aujus_ug/ug472_7Series_Clocking.pdf`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/ug472_7Series_Clocking.pdf): Clocking Resources (MMCM, PLL, CMT).
  - [`aujus_ug/ug473_7Series_Memory_Resources.pdf`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/ug473_7Series_Memory_Resources.pdf): Block RAM, FIFO, and Memory.
  - [`aujus_ug/ug474.pdf`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/ug474.pdf): Configurable Logic Block (CLB), LUTs, Slices.
  - [`aujus_ug/ug888-vivado-design-flows-overview-tutorial.pdf`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/ug888-vivado-design-flows-overview-tutorial.pdf): Vivado Design Flow Tutorial.
  - [`aujus_ug/UG888_Summary.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/UG888_Summary.md): Concise student summary for UG888.
  - [`aujus_ug/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/aujus_ug/GEMINI.md): Overview and cross-references.

#### 3. `coffee/` - Home Brewing Documentation
- **Purpose**: Collection of coffee and cold brew concentrate recipes for home brewing.
- **Key Files**:
  - [`coffee/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/coffee/GEMINI.md): Recipe guides (Hot Simply Good Coffee, Cold Brew Concentrate, Nespresso Iced Coffee).

#### 4. `dsp/` - Digital Signal Processing (DSP) Core Notes
- **Purpose**: Academic notes and mathematical reference material covering key signal processing concepts.
- **Key Files**:
  - [`dsp/adc_dac_converters.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/adc_dac_converters.md): Analog-to-Digital and Digital-to-Analog conversion processes.
  - [`dsp/analog_modulation.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/analog_modulation.md): AM, FM, PM modulation analysis.
  - [`dsp/correlation.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/correlation.md): Auto-correlation and cross-correlation equations and applications.
  - [`dsp/digital_filters.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/digital_filters.md): FIR vs IIR filter structures.
  - [`dsp/digital_modulation.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/digital_modulation.md): ASK, FSK, PSK, QAM digital schemes.
  - [`dsp/dsp_concepts.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/dsp_concepts.md): Core DSP principles.
  - [`dsp/sampling_and_quantization.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/sampling_and_quantization.md): Nyquist-Shannon theorem, aliasing, quantization noise.
  - [`dsp/signals_and_systems.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/signals_and_systems.md): Continuous vs discrete-time systems.
  - [`dsp/spread_spectrum.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/spread_spectrum.md): DSSS and FHSS communications.
  - [`dsp/windowing_and_stability.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/windowing_and_stability.md): Windowing functions (Hamming, Hanning, Blackman) and stability criteria.
  - [`dsp/topics`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/dsp/topics): Topic index.

#### 5. `fsm/` - Hardware Finite State Machine (Verilog)
- **Purpose**: A Verilog implementation of a 3-state Moore Finite State Machine (`STATE_A`, `STATE_B`, `STATE_C`).
- **Key Files**:
  - [`fsm/fsm.v`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/fsm/fsm.v): Verilog source file.
  - [`fsm/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/fsm/GEMINI.md): Simulation instructions using Icarus Verilog (`iverilog`, `vvp`).

#### 6. `issues/` - System Diagnostics & Issue Management Hub
- **Purpose**: Centralized log tracking Linux system issues, systemd optimizations, driver fixes, and shell scripts.
- **Key Files**:
  - [`issues/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/issues/GEMINI.md): Directory issue management standards and templates.
  - [`issues/unix_issues_cmds.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/issues/unix_issues_cmds.txt): Accumulated shell command reference log.
  - Shell automation scripts: `fix_bluetooth_firmware.sh`, `fix_browser_shutdown.sh`, `fix_rquickshare.sh`, `fix_ssd_mount.sh`, `optimize_boot_services.sh`.

#### 7. `project_report/` - Project Documentation
- **Purpose**: Academic/technical project reports in Microsoft Word format.
- **Key Files**:
  - [`project_report/project_repo_ff_v5.docx`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/project_report/project_repo_ff_v5.docx): Finalized version 5 project report document with numeric table of contents.

#### 8. `secure_boot_keys_help/` - Linux Secure Boot Key Management
- **Purpose**: Operational reference guide for Linux Secure Boot, MOK enrollment, and DKMS module signing.
- **Key Files**:
  - [`secure_boot_keys_help/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/secure_boot_keys_help/GEMINI.md): Guide covering PK, KEK, db, dbx, MOK, `mokutil`, and `sbctl` tools.

#### 9. `sshh/` - SSH Configuration Guide
- **Purpose**: Setup guide for Secure Shell authentication and server connection workflows.
- **Key Files**:
  - [`sshh/Instructions_SSH.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/sshh/Instructions_SSH.md): Detailed SSH key generation, config file management, and server authorization steps.
  - [`sshh/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/sshh/GEMINI.md): Context notes.

#### 10. `uart/` - Hardware UART Core (Verilog)
- **Purpose**: Verilog hardware implementation of a parameterized UART interface for FPGAs.
- **Key Files**:
  - [`uart/uart.v`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/uart/uart.v): Top-level UART wrapper module.
  - [`uart/uart_tx.v`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/uart/uart_tx.v): UART Transmitter module.
  - [`uart/uart_rx.v`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/uart/uart_rx.v): UART Receiver module.
  - [`uart/README.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/uart/README.md): Architecture description, timing diagrams, and simulation guide.

#### 11. `unix/` - Desktop Engine & Interprocess Scripting
- **Purpose**: QML test scripts for KDE Plasma, KWin window manager, and DBus interprocess communication.
- **Key Files**:
  - [`unix/test_dbus.qml`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix/test_dbus.qml): DBus interface test script.
  - [`unix/test_kwin.qml`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix/test_kwin.qml): KWin window management script.
  - [`unix/test_kwin_engine.qml`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix/test_kwin_engine.qml): KWin engine diagnostic script.
  - [`unix/test_vd.qml`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix/test_vd.qml): Virtual desktop QML script.

#### 12. `unix_scripting/` - AWK & SED Text Automation Practices
- **Purpose**: Scripts and reference material for text manipulation using AWK and SED.
- **Key Files**:
  - [`unix_scripting/README.txt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix_scripting/README.txt): Comprehensive Unix scripting reference.
  - [`unix_scripting/awk_command/indx.awk`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix_scripting/awk_command/indx.awk): Index lookup AWK script.
  - [`unix_scripting/awk_command/smallest.awk`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix_scripting/awk_command/smallest.awk): Minimum value finding script.
  - [`unix_scripting/awk_command/smallest_n.awk`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix_scripting/awk_command/smallest_n.awk): N-smallest numbers extraction script.
  - [`unix_scripting/awk_command/test.awk`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/unix_scripting/awk_command/test.awk): AWK testing logic.

#### 13. `vlc/` - Video & Subtitle Rendering Troubleshooting
- **Purpose**: Environment designed to isolate and resolve VLC subtitle rendering issues on Arch/CachyOS Linux.
- **Key Files**:
  - [`vlc/test.mp4`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vlc/test.mp4): Minimal 5-second black video stream generated via FFmpeg.
  - [`vlc/test.srt`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vlc/test.srt): Standard SubRip subtitle file for text overlay verification.
  - [`vlc/GEMINI.md`](file:///home/tthh0ngs/build_tthongs/tasks_aa_ii/vlc/GEMINI.md): Diagnostic report on FreeType, libass, and font cache dependencies.

---

## 3. Log of Tracked System Issues (`issues/`)

The repository actively tracks system issues encountered across Linux installations, hardware setups, and software environments:

| Issue ID | Subject / Summary | Status | Resolution / Artifacts |
| :--- | :--- | :---: | :--- |
| **ISSUE_002** | Chrome/Brave "did not shut down properly" error | **Resolved** | `fix_browser_shutdown.sh`, `fix_browser_shutdown.desktop`, `REPORT_002_browser_restore_fix.md` |
| **ISSUE_003** | Systemd boot service latency & bottleneck optimization | **Resolved** | `optimize_boot_services.sh`, `ISSUE_003_further_boot_optimization.md` |
| **ISSUE_004** | Bootloader (GRUB/loader) phase bottleneck | **Resolved** | `boot_optimization_summary.txt`, `ISSUE_004_loader_boot_optimization.md` |
| **ISSUE_005** | Arch/CachyOS package maintenance & kernel sync | **Resolved** | System upgrades & kernel module refresh |
| **ISSUE_006** | AUR Malware Audit & Security Vulnerability Scan | **Resolved** | Security audit notes in `ISSUE_006_aur_malware_audit.md` |
| **ISSUE_007** | NTFS SSD Mount Failure & Intermittent Disconnects | **In Progress** | `fix_ssd_mount.sh`, `ntfs_f.txt`, `ISSUE_007_ssd_mount_issues.md` |
| **ISSUE_008** | RQuickShare BLE Advertiser Interference on Android | **Resolved** | `fix_rquickshare.sh`, `ISSUE_008_rquickshare_discovery_failure.md` |
| **ISSUE_009** | MediaTek MT7922 Bluetooth Firmware Loading Failure | **Resolved** | `fix_bluetooth_firmware.sh`, `ISSUE_009_bluetooth_firmware_failure.md` |
| **ISSUE_010** | Tekken 8 Stutter/Lag on Hybrid NVIDIA/Intel Laptop | **Resolved** | `ISSUE_010_fix_tekken_8_lag.md` (VKD3D & DXVK cache fixes) |
| **ISSUE_011** | Microphone Static Noise & Audio Gain Calibration | **Resolved** | `ISSUE_011_microphone_driver_and_gain_fix.md` (PipeWire/WirePlumber gain filter) |

---

## 4. Complete Git Commit Activity Log

Below is the chronological history of git commits performed within this repository:

| Commit Hash | Date | Author | Commit Message & Affected Components |
| :--- | :--- | :--- | :--- |
| `6132b1e` | 2026-07-25 | tthongs | `ggs` - Cleanup of Maggi documentation files |
| `0c617e7` | 2026-07-04 | tthongs | `fix(bluetooth): resolve RQuickShare background BLE advertiser interference [ISSUE_008]` |
| `b070889` | 2026-06-30 | tthongs | `docs(t8): document black screen resolution and prefix cleanup [ISSUE_010]` |
| `730b7ad` | 2026-06-30 | tthongs | `fix(t8): resolve Tekken 8 lag on hybrid graphics laptop [ISSUE_010]` |
| `acb15fd` | 2026-06-30 | tthongs | `Resolve ISSUE_009: Bluetooth Firmware Loading Failure (MT7922)` |
| `55e10a2` | 2026-06-29 | tthongs | `feat(T8): extract and compile Tekken 8 Fahkumram combos into a styled Excel sheet` |
| `9dfd7b4` | 2026-06-23 | tthongs | `fix(ssd): add configuration script and documentation for SSD mount issues [ISSUE_007]` |
| `4e47751` | 2026-06-17 | tthongs | `docs: document AUR malware audit and system scan results [ISSUE_006]` |
| `520d0bd` | 2026-05-29 | tthongs | `tasks_aa_ii updated` - Browser restore fix & boot optimization scripts |
| `87e8507` | 2026-05-29 | tthongs | `docs: generate comprehensive GEMINI.md for issues directory` |
| `8c25e29` | 2026-05-26 | tthongs | `docs: add simplified student summary for UG888` |
| `456154e` | 2026-05-26 | tthongs | `docs: initialize project with Xilinx 7 Series documentation and GEMINI.md` |
| `c3ee9d3` | 2026-05-26 | tthongs | `gh` - Added Secure Boot keys guide and project report update |
| `55b5748` | 2026-05-04 | tthongs | `docs: finalize project report with strictly numeric TOC and body cleanup` |
| `ca0b450` | 2026-05-01 | tthongs | `Generate comprehensive GEMINI.md for project context` |
| `372fa3b` | 2026-05-01 | tthongs | `Update Table of Contents to include headings up to x.xx.xx depth` |
| `d7b0089` | 2026-05-01 | tthongs | `Restore and add finalized project report with Appendix and updated TOC` |
| `a93ba50` | 2026-05-01 | tthongs | `Add Appendix with List of Figures/Tables and update Table of Contents` |
| `934263b` | 2026-05-01 | tthongs | `Add captions to previously unlabeled figures in project report` |
| `c19896a` | 2026-04-05 | tthongs | `ggs` - Initial commit of KDE/QML scripts (`unix/`) |

---

## 5. File Inventory & Manifest

| File Path | Subdirectory | Type | Description |
| :--- | :--- | :--- | :--- |
| `T8/Fahkumram_Tekken_8_Combos.xlsx` | `T8/` | Excel (`.xlsx`) | Formatted combo sheet for Tekken 8 character Fahkumram |
| `T8/GEMINI.md` | `T8/` | Markdown (`.md`) | OCR combo extraction workflow documentation |
| `aujus_ug/UG888_Summary.md` | `aujus_ug/` | Markdown (`.md`) | Simplified student summary for UG888 Vivado tutorial |
| `aujus_ug/ug470_7Series_Config.pdf` | `aujus_ug/` | PDF | Xilinx 7 Series Configuration User Guide |
| `aujus_ug/ug471_7Series_SelectIO.pdf` | `aujus_ug/` | PDF | Xilinx 7 Series SelectIO Resources Guide |
| `aujus_ug/ug472_7Series_Clocking.pdf` | `aujus_ug/` | PDF | Xilinx 7 Series Clocking Resources Guide |
| `aujus_ug/ug473_7Series_Memory_Resources.pdf` | `aujus_ug/` | PDF | Xilinx 7 Series Memory Resources Guide |
| `aujus_ug/ug474.pdf` | `aujus_ug/` | PDF | Xilinx 7 Series CLB User Guide |
| `aujus_ug/ug888-vivado-design-flows-overview-tutorial.pdf` | `aujus_ug/` | PDF | Vivado Design Flows Tutorial |
| `dsp/adc_dac_converters.md` | `dsp/` | Markdown (`.md`) | Analog-to-Digital & Digital-to-Analog conversion guide |
| `dsp/analog_modulation.md` | `dsp/` | Markdown (`.md`) | Comprehensive notes on AM, FM, PM analog modulation |
| `dsp/correlation.md` | `dsp/` | Markdown (`.md`) | Auto-correlation and cross-correlation reference |
| `dsp/digital_filters.md` | `dsp/` | Markdown (`.md`) | FIR and IIR digital filter design fundamentals |
| `dsp/digital_modulation.md` | `dsp/` | Markdown (`.md`) | ASK, FSK, PSK, and QAM modulation notes |
| `dsp/dsp_concepts.md` | `dsp/` | Markdown (`.md`) | Fundamental DSP terms and theorems |
| `dsp/sampling_and_quantization.md` | `dsp/` | Markdown (`.md`) | Nyquist sampling theorem & quantization noise analysis |
| `dsp/signals_and_systems.md` | `dsp/` | Markdown (`.md`) | Continuous and discrete time system classification |
| `dsp/spread_spectrum.md` | `dsp/` | Markdown (`.md`) | DSSS and FHSS communications notes |
| `dsp/windowing_and_stability.md` | `dsp/` | Markdown (`.md`) | Window functions and BIBO system stability |
| `fsm/fsm.v` | `fsm/` | Verilog (`.v`) | 3-state Moore Finite State Machine implementation |
| `issues/ISSUE_002_browser_restore_fix.md` | `issues/` | Markdown (`.md`) | Chrome/Brave clean shutdown issue resolution |
| `issues/ISSUE_003_further_boot_optimization.md` | `issues/` | Markdown (`.md`) | Systemd user service boot optimization log |
| `issues/ISSUE_004_loader_boot_optimization.md` | `issues/` | Markdown (`.md`) | Bootloader loader phase bottleneck analysis |
| `issues/ISSUE_006_aur_malware_audit.md` | `issues/` | Markdown (`.md`) | AUR package security audit results |
| `issues/ISSUE_007_ssd_mount_issues.md` | `issues/` | Markdown (`.md`) | NTFS volume dirtiness & mounting issue log |
| `issues/ISSUE_008_rquickshare_discovery_failure.md` | `issues/` | Markdown (`.md`) | Bluetooth LE advertiser collision fix |
| `issues/ISSUE_009_bluetooth_firmware_failure.md` | `issues/` | Markdown (`.md`) | MT7922 Bluetooth kernel firmware fix |
| `issues/ISSUE_010_fix_tekken_8_lag.md` | `issues/` | Markdown (`.md`) | Tekken 8 VKD3D shader cache & hybrid GPU fix |
| `issues/ISSUE_011_microphone_driver_and_gain_fix.md` | `issues/` | Markdown (`.md`) | PipeWire microphone noise filter configuration |
| `issues/fix_bluetooth_firmware.sh` | `issues/` | Shell (`.sh`) | Automated MT7922 bluetooth firmware update script |
| `issues/fix_browser_shutdown.desktop` | `issues/` | Desktop (`.desktop`) | Systemd shutdown trigger desktop launcher |
| `issues/fix_browser_shutdown.sh` | `issues/` | Shell (`.sh`) | Clean browser termination bash script |
| `issues/fix_rquickshare.sh` | `issues/` | Shell (`.sh`) | Script to fix BLE advertising for QuickShare |
| `issues/fix_ssd_mount.sh` | `issues/` | Shell (`.sh`) | NTFS repair & automount script |
| `issues/optimize_boot_services.sh` | `issues/` | Shell (`.sh`) | Systemd service disablement script |
| `issues/unix_issues_cmds.txt` | `issues/` | Text (`.txt`) | Central command line execution log |
| `project_report/project_repo_ff_v5.docx` | `project_report/` | Word (`.docx`) | Finalized project report document |
| `secure_boot_keys_help/GEMINI.md` | `secure_boot_keys_help/` | Markdown (`.md`) | Linux Secure Boot & sbctl setup manual |
| `sshh/Instructions_SSH.md` | `sshh/` | Markdown (`.md`) | SSH keygen & configuration walkthrough |
| `uart/uart.v` | `uart/` | Verilog (`.v`) | Top-level UART transmitter & receiver module |
| `uart/uart_rx.v` | `uart/` | Verilog (`.v`) | UART receiver module with baud rate generator |
| `uart/uart_tx.v` | `uart/` | Verilog (`.v`) | UART transmitter module with serializer |
| `unix/test_dbus.qml` | `unix/` | QML (`.qml`) | DBus IPC test script |
| `unix/test_kwin.qml` | `unix/` | QML (`.qml`) | KWin window manager test script |
| `unix/test_kwin_engine.qml` | `unix/` | QML (`.qml`) | KWin script engine diagnostic |
| `unix/test_vd.qml` | `unix/` | QML (`.qml`) | Virtual desktop switcher QML script |
| `unix_scripting/README.txt` | `unix_scripting/` | Text (`.txt`) | Detailed reference for AWK and SED commands |
| `unix_scripting/awk_command/indx.awk` | `unix_scripting/` | AWK (`.awk`) | AWK script for index extraction |
| `unix_scripting/awk_command/smallest.awk` | `unix_scripting/` | AWK (`.awk`) | AWK script for finding minimum value |
| `unix_scripting/awk_command/smallest_n.awk` | `unix_scripting/` | AWK (`.awk`) | AWK script for N-smallest numbers |
| `vlc/test.mp4` | `vlc/` | MP4 (`.mp4`) | Black test video for VLC subtitle verification |
| `vlc/test.srt` | `vlc/` | SRT (`.srt`) | Sample subtitle file for rendering verification |

---

*This document was automatically compiled by Antigravity based on repository activity, git history, and local file analysis.*
