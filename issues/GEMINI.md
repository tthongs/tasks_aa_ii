# Project Issues & Task Management

## Directory Overview
This directory (`issues/`) serves as the centralized hub for tracking bugs,
feature requests, and administrative tasks across the entire repository. Given
the diverse nature of this workspace—which includes FPGA documentation,
hardware designs (Verilog), Digital Signal Processing (DSP) notes, and Unix
scripting—this directory ensures that all developmental and maintenance hurdles
are documented and resolved systematically.

## Repository Context
The broader repository contains several specialized sub-projects:
*   **aujus_ug/**: Technical documentation and summaries for Xilinx 7 Series
    FPGAs (UG470-UG474, UG888).
*   **dsp/**: Comprehensive notes on Digital Signal Processing concepts.
*   **uart/ & fsm/**: Hardware implementation files in Verilog.
*   **unix_scripting/**: Practice scripts for `awk` and `sed`.
*   **project_report/**: Finalized project documentation and reports.

## Current Issues & Tasks
*   **ISSUE_002**: Browsers (Chrome/Brave) show "did not shut down properly". [RESOLVED]
*   **ISSUE_003**: Further Boot Optimization: Service Level Bottlenecks. [RESOLVED]
*   **ISSUE_004**: Further Boot Optimization: Loader Phase Bottleneck. [RESOLVED]
*   **ISSUE_005**: System Maintenance and Upgrade. [RESOLVED]
*   **ISSUE_006**: AUR Malware Audit (June 2026). [RESOLVED]
*   **ISSUE_007**: SSD Mount Issues and Intermittent Disconnections. [IN PROGRESS]
*   **ISSUE_008**: RQuickShare Discovery Failure on Android Devices. [RESOLVED]
*   **ISSUE_009**: Bluetooth Firmware Loading Failure (MT7922). [RESOLVED]
*   **ISSUE_010**: Fix Tekken 8 Lag on Hybrid Graphics Laptop. [RESOLVED]
*   **ISSUE_011**: Fix Microphone Static Noise & Audio Driver Calibration. [RESOLVED]
*   **ISSUE_012**: KDE Connect Availability & UFW Firewall Configuration. [RESOLVED]
*   **ISSUE_013**: Automatic Git Repository Push on Logged Issue. [RESOLVED]
*   **ISSUE_014**: Update GRUB Bootloader Timeout to 50 Seconds. [RESOLVED]
*   **ISSUE_015**: Add Custom Power Off Entry to GRUB Menu. [RESOLVED]

## Usage
To maintain consistency, please follow these guidelines when creating or
managing issues:

1.  **File Naming**: Use the format `ISSUE_XXX_description.md`.
    *   Example: `ISSUE_001_fix_uart_baud_rate.md`
2.  **Issue Categories**:
    *   `[BUG]`: For errors in code or documentation.
    *   `[TASK]`: For general maintenance or planned improvements.
    *   `[DOCS]`: For issues specifically related to the technical user guides.
3.  **Cross-Referencing**: Always specify which sub-directory the issue
    pertains to so that context-specific tools can be applied correctly.

## Issue Template
When creating a new issue, use the following structure:

```markdown
# Issue Title (e.g., [BUG] Fix UART Parity Check)

**Status**: Open / In Progress / Resolved
**Priority**: Low / Medium / High
**Affected Directory**: (e.g., /uart)

## Description
A clear and concise description of the issue or task.

## Steps to Reproduce (if applicable)
1. ...
2. ...

## Proposed Solution / Action Items
- [ ] Task 1
- [ ] Task 2

## Notes
Any additional context or references to external documentation (e.g., UG470).
```

## Development Conventions
*   **Surgical Edits**: When fixing bugs identified here, prioritize minimal,
    high-impact changes to the relevant sub-directories.
*   **Verification**: All resolved issues should include a brief note on how
    the fix was verified (e.g., "Ran `uart_rx.v` through testbench").
*   **Mandatory Issue & Command Logging Directive**: Every time any system modification, bug fix, or task is executed:
    1. Create/update a dedicated issue log (`ISSUE_XXX_description.md` or `REPORT_XXX_description.md`) in `issues/`.
    2. Append any new or updated Unix commands (with context, breakdown, and rationale) to `unix_issues_cmds.txt`.
    3. Update `GEMINI.md` to reflect the new issue status.
    4. Commit changes and push to remote repository (`git commit` automatically triggers `.githooks/post-commit` auto-push).
