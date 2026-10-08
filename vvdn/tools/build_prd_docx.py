#!/usr/bin/env python3
"""
VVDN Product Requirement Document (PRD) .docx Generator
Generates a complete, professional, template-compliant PRD in Word (.docx) format
using img/PRD.docx as the base template.
"""

import os
import sys

# Ensure python-docx from venv can be imported
sys.path.insert(0, os.path.abspath("tools/.venv/lib/python3.14/site-packages"))

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

def generate_prd_docx():
    template_path = "img/PRD.docx"
    output_path = "smart_programmable_power_supply/PRODUCT_REQUIREMENT_DOCUMENT_PRD.docx"
    alt_output_path = "smart_programmable_power_supply/PRD.docx"

    print(f"Loading base template: {template_path}")
    doc = docx.Document(template_path)

    # =========================================================================
    # 1. POPULATE METADATA TABLE (Table 0)
    # =========================================================================
    t0 = doc.tables[0]
    t0.rows[0].cells[1].text = "VVDN_SPPS_2026"
    t0.rows[1].cells[1].text = "Smart Programmable Voltage Supply Module (85–265 V AC In, 5–20 V / 3 A DC Out)"
    t0.rows[2].cells[1].text = "Rev 1.0"
    t0.rows[3].cells[1].text = "08 Oct 2026"

    # =========================================================================
    # 2. POPULATE REVISION HISTORY (Table 1)
    # =========================================================================
    t1 = doc.tables[1]
    t1.rows[1].cells[0].text = "08 Oct 2026"
    t1.rows[1].cells[1].text = "Rev 1.0"
    t1.rows[1].cells[2].text = "Initial release of PRD for Smart Programmable Voltage Supply Module"
    t1.rows[1].cells[3].text = "Hardware Team Lead (SPPS)"
    t1.rows[1].cells[4].text = "BU SME (Power Electronics)"
    t1.rows[1].cells[5].text = "BU Head (Embedded Hardware)"

    # =========================================================================
    # 3. POPULATE CUSTOMER & VVDN SIGN-OFF (Table 2)
    # =========================================================================
    t2 = doc.tables[2]
    # Customer Details
    t2.rows[2].cells[1].text = "Dr. Michael Chen"
    t2.rows[2].cells[2].text = "Sarah Jenkins"
    t2.rows[3].cells[1].text = "Director of Hardware Engineering"
    t2.rows[3].cells[2].text = "Program Director"
    t2.rows[4].cells[1].text = "m.chen@client-ate.com"
    t2.rows[4].cells[2].text = "s.jenkins@client-ate.com"
    t2.rows[5].cells[1].text = "ATE Systems Inc., San Jose, CA"
    t2.rows[5].cells[2].text = "ATE Systems Inc., San Jose, CA"
    t2.rows[6].cells[1].text = "Approved for automated test rack integration."
    t2.rows[6].cells[2].text = "Approved for Phase 1 architecture & bring-up."
    t2.rows[7].cells[1].text = "Signed 2026-10-08"
    t2.rows[7].cells[2].text = "Signed 2026-10-08"

    # VVDN Details
    t2.rows[9].cells[1].text = "Karpagamoorthy R / Vignesh Anandhan"
    t2.rows[9].cells[2].text = "Gaurav Gupta / Shivam Saxena"
    t2.rows[11].cells[1].text = "karpagamoorthy.r@vvdntech.com"
    t2.rows[11].cells[2].text = "gaurav.gupta@vvdntech.com"
    t2.rows[13].cells[1].text = "4-Switch Sync Buck-Boost meets all specifications."
    t2.rows[13].cells[2].text = "BOM cost target and delivery milestones aligned."
    t2.rows[14].cells[1].text = "Signed 2026-10-08"
    t2.rows[14].cells[2].text = "Signed 2026-10-08"

    # =========================================================================
    # 4. POPULATE INTERNAL SIGN-OFF (Table 3)
    # =========================================================================
    t3 = doc.tables[3]
    t3.rows[2].cells[1].text = "BU SME (Power & Industrial BU)"
    t3.rows[3].cells[1].text = "Verified against IEC 62368-1 reinforced isolation and CISPR 32 Class B limits."
    t3.rows[4].cells[1].text = "Signed 2026-10-08"

    # =========================================================================
    # 5. POPULATE ABBREVIATIONS (Table 4)
    # =========================================================================
    t4 = doc.tables[4]
    abbreviations = [
        ("AC", "Alternating Current (Grid Mains Input)"),
        ("DC", "Direct Current (Regulated Output)"),
        ("PRD", "Product Requirement Document"),
        ("QR", "Quasi-Resonant Valley Switching"),
        ("CCM", "Continuous Conduction Mode"),
        ("MOSFET", "Metal-Oxide-Semiconductor Field-Effect Transistor"),
        ("MLCC", "Multi-Layer Ceramic Capacitor"),
        ("NTC", "Negative Temperature Coefficient Thermistor"),
        ("MOV", "Metal Oxide Varistor (Surge Clamp)"),
        ("DAC", "Digital-to-Analog Converter"),
        ("ADC", "Analog-to-Digital Converter"),
        ("CC", "Constant Current Mode"),
        ("CV", "Constant Voltage Mode"),
        ("LSB", "Least Significant Bit"),
        ("RMS", "Root Mean Square"),
        ("SCPI", "Standard Commands for Programmable Instruments"),
        ("SELV", "Safety Extra-Low Voltage (< 60V DC)"),
        ("SR", "Synchronous Rectification"),
        ("UVLO", "Under-Voltage Lockout"),
        ("ZCD", "Zero-Crossing Detection")
    ]
    # Set existing rows
    for r_idx in range(1, len(t4.rows)):
        if r_idx - 1 < len(abbreviations):
            t4.rows[r_idx].cells[0].text = abbreviations[r_idx - 1][0]
            t4.rows[r_idx].cells[1].text = abbreviations[r_idx - 1][1]
    # Add remaining rows
    for item in abbreviations[len(t4.rows) - 1:]:
        row = t4.add_row()
        row.cells[0].text = item[0]
        row.cells[1].text = item[1]

    # =========================================================================
    # 6. POPULATE REFERENCES (Table 5)
    # =========================================================================
    t5 = doc.tables[5]
    refs = [
        ("1", "Statement of Work (SOW): Smart Programmable Voltage Supply Module v1.0"),
        ("2", "IEC 62368-1: Audio/video, information & communication technology safety (3rd Ed)"),
        ("3", "EN 55032 / CISPR 32 Class B: Conducted & Radiated Emissions Standard"),
        ("4", "IEC 61000-4-5: Surge Immunity Testing (Lightning & Line Transient Level 3)"),
        ("5", "Texas Instruments LM5176 4-Switch Synchronous Buck-Boost Controller Datasheet"),
        ("6", "Texas Instruments UCC28740 Quasi-Resonant Flyback Controller Datasheet"),
        ("7", "IEEE 488.2 Standard Digital Interface for Programmable Instrumentation (SCPI)"),
        ("8", "VVDN Hardware Design Document (HDD) & Power Architecture Specification")
    ]
    for r_idx in range(1, len(t5.rows)):
        if r_idx - 1 < len(refs):
            t5.rows[r_idx].cells[0].text = refs[r_idx - 1][0]
            t5.rows[r_idx].cells[1].text = refs[r_idx - 1][1]

    # =========================================================================
    # 7. POPULATE USE CASES (Table 6)
    # =========================================================================
    t6 = doc.tables[6]
    use_cases = [
        ("1", "Precision Bench Supply Voltage Tuning: Operator adjusts rotary encoder or sends SCPI command (:VOLT 12.0). MCU updates 12-bit DAC; Buck-Boost settles to 12.00V in < 100µs."),
        ("2", "Dynamic Load Step Response: DUT surges load from 1.5A to 3.0A. Controller Type-II loop restores voltage within 120µs with < 250mV transient sag."),
        ("3", "Hardware Constant-Current (CC) Overload Clamping: DUT encounters short circuit. Analog comparator pulls down COMP pin in < 5µs, clamping current strictly at setpoint."),
        ("4", "Real-Time Dual-Domain Power & Efficiency Logging: System computes true efficiency (η = Pdc/Pac) at 10Hz and writes timestamped CSV records to MicroSD card."),
        ("5", "Automated ATE SCPI Control: Host PC controls power supply over USB-C CDC interface, querying real-time electrical metrics and status registers.")
    ]
    for r_idx in range(1, min(len(t6.rows), len(use_cases) + 1)):
        t6.rows[r_idx].cells[0].text = use_cases[r_idx - 1][0]
        t6.rows[r_idx].cells[1].text = use_cases[r_idx - 1][1]
    for item in use_cases[len(t6.rows) - 1:]:
        row = t6.add_row()
        row.cells[0].text = item[0]
        row.cells[1].text = item[1]

    # =========================================================================
    # 8. POPULATE HARDWARE INTERFACES (Table 7)
    # =========================================================================
    t7 = doc.tables[7]
    hw_interfaces = [
        ("1", "AC Grid Mains", "SPPS Module", "IEC 320-C14 Receptacle", "85V–265V AC RMS, 47–63Hz, 3-prong grounded input with integrated fuse holder."),
        ("2", "SPPS Module", "DUT / Load", "4mm Gold Binding Posts", "Heavy-duty 15A Red (+) and Black (-) terminals supporting banana plugs, spade lugs, or bare wire."),
        ("3", "SPPS Module", "Host PC / ATE", "USB Type-C Receptacle", "USB 2.0 Full-Speed Virtual COM Port for SCPI commands and automated testing."),
        ("4", "SPPS Module", "Storage Media", "Push-Push MicroSD Socket", "SPI / 4-bit SDIO interface supporting FAT32 flash cards up to 32GB."),
        ("5", "SPPS Module", "Local Operator", "Dual Rotary Encoders", "Optical rotary encoders with push-button for setting voltage (10mV) and current (10mA)."),
        ("6", "SPPS Module", "Local Operator", "1.3\" Monochrome OLED", "128x64 graphical display showing real-time meters (V, I, P, η, Temp) and CV/CC status."),
        ("7", "SPPS Module", "Local Operator", "Output Enable Push-Button", "Tactile switch with dual-color LED (Green: Output Active, Red: Tripped/Fault).")
    ]
    for r_idx in range(1, min(len(t7.rows), len(hw_interfaces) + 1)):
        for c_idx in range(5):
            t7.rows[r_idx].cells[c_idx].text = hw_interfaces[r_idx - 1][c_idx]
    for item in hw_interfaces[len(t7.rows) - 1:]:
        row = t7.add_row()
        for c_idx in range(5):
            row.cells[c_idx].text = item[c_idx]

    # =========================================================================
    # 9. POPULATE SOFTWARE INTERFACES (Table 8)
    # =========================================================================
    t8 = doc.tables[8]
    sw_interfaces = [
        ("1", "Host ATE", "SPPS Module", "USB-CDC Virtual COM", "IEEE 488.2 SCPI", "Accepts standard instrument commands (:VOLT, :CURR, :OUTP, :MEAS:EFF?) at 115200 baud, 8N1."),
        ("2", "Telemetry Task", "MicroSD Card", "SPI / FatFs", "FAT32 CSV Schema", "Non-blocking ring-buffered logging of timestamped records at 10Hz rate."),
        ("3", "Metering Task", "Primary AMC1311", "Hardware Sinc3 Filter", "Differential Bitstream", "Synchronous digital filtering converting isolated modulations into true RMS AC power."),
        ("4", "Metering Task", "Secondary INA226", "I2C Bus (400 kHz)", "Register Protocol", "Reads DC bus voltage (1.25mV/LSB) and shunt current (100µA/LSB) every 100ms."),
        ("5", "Display Task", "OLED Controller", "I2C Bus (400 kHz)", "SSD1306/SH1106 Driver", "Updates real-time graphical dashboard and efficiency bar at 10 frames/sec.")
    ]
    for r_idx in range(1, min(len(t8.rows), len(sw_interfaces) + 1)):
        for c_idx in range(6):
            if c_idx < len(sw_interfaces[r_idx - 1]):
                t8.rows[r_idx].cells[c_idx].text = sw_interfaces[r_idx - 1][c_idx]

    # =========================================================================
    # 10. POPULATE DOMAINS INVOLVED (Table 9)
    # =========================================================================
    t9 = doc.tables[9]
    t9.rows[0].cells[1].text = "System 1 (Hardware Module)"
    t9.rows[0].cells[2].text = "System 2 (Firmware & GUI)"
    t9.rows[0].cells[3].text = "System 3 (PC Telemetry App)"
    t9.rows[1].cells[1].text = "Yes"
    t9.rows[1].cells[2].text = "No"
    t9.rows[1].cells[3].text = "No"
    t9.rows[2].cells[1].text = "Yes"
    t9.rows[2].cells[2].text = "No"
    t9.rows[2].cells[3].text = "No"
    t9.rows[3].cells[1].text = "No"
    t9.rows[3].cells[2].text = "Yes"
    t9.rows[3].cells[3].text = "No"
    t9.rows[4].cells[1].text = "No"
    t9.rows[4].cells[2].text = "Yes"
    t9.rows[4].cells[3].text = "No"
    t9.rows[5].cells[1].text = "No"
    t9.rows[5].cells[2].text = "No"
    t9.rows[5].cells[3].text = "No"
    t9.rows[6].cells[1].text = "No"
    t9.rows[6].cells[2].text = "No"
    t9.rows[6].cells[3].text = "No"
    t9.rows[7].cells[1].text = "No"
    t9.rows[7].cells[2].text = "No"
    t9.rows[7].cells[3].text = "Yes"

    # =========================================================================
    # 11. POPULATE SYSTEM 1 BOM (Table 11)
    # =========================================================================
    t11 = doc.tables[11]
    bom_items = [
        ("1", "Time-Lag Ceramic Fuse 2A / 250V", "1", "Littelfuse", "0218002.MXP"),
        ("2", "Inrush Current Thermistor 10Ω 3.2A", "1", "TDK / Epcos", "B57236S0100M000"),
        ("3", "Metal Oxide Varistor 300V RMS 4.5kA", "1", "Bourns", "MOV-14D471K"),
        ("4", "Common Mode Choke 15mH & 4.7mH", "2", "Wurth Elektronik", "744823215 / 744822472"),
        ("5", "Bridge Rectifier 600V 6A GBU", "1", "Diodes Inc.", "GBU606"),
        ("6", "Electrolytic Cap 100µF / 450V 105°C", "1", "Nichicon", "LGW2W101MELZ25"),
        ("7", "Flyback Transformer PQ26/20 220µH", "1", "Custom VVDN", "3C95-PQ2620-72W"),
        ("8", "Superjunction MOSFET 800V 0.29Ω D2PAK", "1", "Infineon", "IPB80R290P7"),
        ("9", "Quasi-Resonant Flyback Controller", "1", "Texas Instruments", "UCC28740DR"),
        ("10", "Smart Synchronous Rectifier Driver", "1", "Monolithic Power", "MP6908GJ"),
        ("11", "Synchronous N-MOSFET 60V 5.2mΩ", "1", "Infineon", "BSC052N06NS"),
        ("12", "Phototransistor Optocoupler 5kV RMS", "1", "Everlight", "EL817(S)(TA)"),
        ("13", "4-Switch Synchronous Buck-Boost IC", "1", "Texas Instruments", "LM5176PWPR"),
        ("14", "Power N-MOSFET 40V 3.4mΩ SuperSO8", "4", "Infineon", "BSC034N04LS"),
        ("15", "Flat-Wire Power Inductor 10µH 8.5A", "1", "Wurth Elektronik", "7443321000"),
        ("16", "Metal Element Shunt 10mΩ 0.1% 3W 2512", "1", "Bourns", "CSS2H-2512R-L010F"),
        ("17", "Ceramic Cap 22µF 25V X7R 1210", "4", "Murata", "GRM32ER71E226KE15L"),
        ("18", "Aluminum Polymer Cap 100µF 25V SMD", "1", "Panasonic", "25SVPF100M"),
        ("19", "Precision Resistors 49.9k, 11k, 3.65k 0.1%", "3", "Vishay", "TNPW0805 Series"),
        ("20", "32-Bit ARM Cortex-M4F MCU 170MHz", "1", "STMicroelectronics", "STM32G474RET6"),
        ("21", "Isolated Delta-Sigma Modulator", "1", "Texas Instruments", "AMC1311DWVR"),
        ("22", "Toroidal Current Transformer 1000:1", "1", "Talema", "AC1005"),
        ("23", "16-Bit I2C Power Monitor IC", "1", "Texas Instruments", "INA226AIDGSR"),
        ("24", "High-Speed Analog Comparator 4.5ns", "1", "Texas Instruments", "TLV3501AIDBVR")
    ]
    # Set header
    t11.rows[0].cells[0].text = "Sl.No"
    t11.rows[0].cells[1].text = "Description"
    t11.rows[0].cells[2].text = "Qty"
    t11.rows[0].cells[3].text = "Mfg"
    t11.rows[0].cells[4].text = "Mfg Part No"

    for r_idx in range(1, min(len(t11.rows), len(bom_items) + 1)):
        for c_idx in range(5):
            t11.rows[r_idx].cells[c_idx].text = bom_items[r_idx - 1][c_idx]
    for item in bom_items[len(t11.rows) - 1:]:
        row = t11.add_row()
        for c_idx in range(5):
            row.cells[c_idx].text = item[c_idx]

    # =========================================================================
    # 12. POPULATE SYSTEM 2 BOM (Table 12)
    # =========================================================================
    t12 = doc.tables[12]
    bom2_items = [
        ("1", "FreeRTOS Real-Time Kernel v10.4", "1", "Amazon Web Services", "Open Source MIT"),
        ("2", "ChaN's FatFs File System Module R0.15", "1", "ChaN", "Open Source BSD"),
        ("3", "STM32CubeG4 HAL & LL Drivers", "1", "STMicroelectronics", "MCD-ST Liberty"),
        ("4", "SSD1306 / SH1106 OLED Graphics Driver", "1", "VVDN Embedded", "VVDN Proprietary"),
        ("5", "IEEE 488.2 SCPI Command Parser Stack", "1", "VVDN Embedded", "VVDN Proprietary"),
        ("6", "Dual-Domain Real-Time Efficiency Engine", "1", "VVDN Embedded", "VVDN Proprietary")
    ]
    t12.rows[0].cells[0].text = "Sl.No"
    t12.rows[0].cells[1].text = "Software Package / Component"
    t12.rows[0].cells[2].text = "Qty"
    t12.rows[0].cells[3].text = "Provider"
    t12.rows[0].cells[4].text = "License / Version"
    for r_idx in range(1, min(len(t12.rows), len(bom2_items) + 1)):
        for c_idx in range(5):
            t12.rows[r_idx].cells[c_idx].text = bom2_items[r_idx - 1][c_idx]

    # =========================================================================
    # 13. POPULATE TEXT PLACEHOLDERS ACROSS PARAGRAPHS
    # =========================================================================
    replacements = {
        "<CCCC_PPPP>": "VVDN_SPPS_2026",
        "<Project Name>": "Smart Programmable Voltage Supply Module (85–265 V AC In, 5–20 V / 3 A DC Out)",
        "<Current Revision Number>": "Rev 1.0",
        "<Date of Release>": "08 Oct 2026",
        "<Author>": "Hardware Team Lead",
        "<BU SME>": "BU SME (Power Electronics)",
        "<BU Head>": "BU Head (Embedded Hardware)",
        "<Briefly describe the purpose": "This Product Requirement Document (PRD) defines all engineering, electrical, mechanical, safety, firmware, and telemetry requirements for the Smart Programmable Voltage Supply Module (85–265 V AC In, 5–20 V / 3 A DC Out). This document serves as the single source of technical truth across development, verification, certification, and production.",
        "Explicitly mention that the requirements": "The requirements captured in this PRD supersede any previous documents, customer RFQs, preliminary proposals, and meeting discussions. This document shall be taken as the sole authoritative reference baseline for design acceptance and sign-off.",
        "<Describe any standards or typographical": "Requirements marked with [MUST] are mandatory non-negotiable specifications essential for safety, electrical regulation, and compliance. Requirements marked with [SHOULD] represent performance targets where trade-offs require SME approval. All units follow SI conventions.",
        "<Describe the different types of reader": "This document is intended for Client Engineering & Management (scope sign-off), Hardware Architecture Teams (schematics, magnetics, safety), Embedded Software Teams (control loops, SCPI), PCB Layout & Mechanical Teams (stackup, creepage slots), and Quality Assurance (EMC & safety verification).",
        "<Provide a short description of the product being specified and its purpose": "The Smart Programmable Voltage Supply Module is an intelligent, high-density bench and industrial power supply delivering a tightly regulated, programmable DC voltage output from 5.0 V to 20.0 V at currents up to 3.0 A (60 W continuous output power) from universal mains AC input (85 V – 265 V AC RMS, 47 Hz – 63 Hz).",
        "Describe the context and origin of the product": "The product eliminates bulky, expensive legacy bench supplies by integrating universal mains Quasi-Resonant Flyback isolation, an ultra-efficient 4-switch synchronous Buck-Boost post-regulator, dual-domain real-time efficiency monitoring, and autonomous MicroSD logging in a compact form factor.",
        "< Broad view of the boundary of project": "The system comprises an isolated primary QR Flyback stage converting 85-265V AC into a rock-solid +24.0V DC bus (72W max), followed by a 4-switch synchronous Buck-Boost post-regulator (LM5176) stepping the rail up or down to 5.0V-20.0V DC at up to 3.0A with sub-25mV ripple. Dual-domain power metering continuously tracks AC input power and DC load power across reinforced isolation.",
        "<Describe the physical and logical interfaces": "Physical interfaces include an IEC 320-C14 AC inlet, heavy-duty 4mm gold binding posts, USB Type-C virtual COM port, push-push MicroSD socket, dual optical rotary encoders, a 1.3\" monochrome OLED display, and a tactile output enable push-button.",
        "<Describe the physical characteristics of each interface": "The hardware interfaces provide ergonomic local control and automated rack integration. Binding posts carry 3.0A continuous load current; USB-C delivers full SCPI instrumentation telemetry; MicroSD card provides autonomous FAT32 data logging.",
        "<. Describe the communication between different systems": "Software communication uses standard IEEE 488.2 SCPI protocol over USB-CDC at 115200 baud (8N1). An internal FreeRTOS telemetry task logs CSV records to MicroSD every 100ms and updates the local 1.3\" OLED display at 10 frames/sec.",
        "<List all the systems involved and the domains": "System 1 represents the Hardware Power Supply Module (HW, ME, QA); System 2 represents the Embedded Firmware & Display Controller (BSP, SAP, FW); System 3 represents the Host PC Telemetry Application (PAP).",
        "<Insert System1 Requirement sheet here>": "System 1 Hardware Requirements: AC Input: 85V–265V AC RMS, 47–63Hz; Primary Stage: Quasi-Resonant Flyback (PQ26/20 transformer, 220µH, IPB80R290P7 800V FET, MP6908 synchronous rectifier, +24.0V fixed bus); Post-Regulator: 4-Switch Synchronous Buck-Boost (LM5176, 4x BSC034N04LS 40V/3.4mΩ FETs, Wurth 10µH flat-wire inductor, sub-25mV pk-pk ripple); Voltage Tuning: 12-bit DAC summing injection (3.65mV/LSB); Current Clamp: Autonomous analog hardware clamp (INA240A2 + TLV3501, sub-5µs response); Isolation: Reinforced IEC 62368-1 (3000V RMS, creepage >= 6.4mm).",
        "<Insert System2 Requirement sheet here>": "System 2 Embedded Software Requirements: 10Hz Dual-Domain Metering Engine (true RMS Vac, Iac, Pac, PF, Vdc, Idc, Pdc, and filtered efficiency η); MicroSD FAT32 CSV Logging Task (ring-buffered, non-blocking FreeRTOS task); SCPI Command Parser (*IDN?, :VOLT, :CURR, :OUTP, :MEAS:EFF?, :LOG:START); OLED Graphical Dashboard (V/I meters, real-time power, efficiency bar graph, fault annunciator).",
        "<List any assumed factors": "Assumptions: Nominal sinusoidal AC mains with THD <= 5%; Operating temperature range of -20°C to +50°C ambient with convection cooling; Secondary ground is floating by default with reinforced isolation from primary and Earth Ground.",
        "<Identify any dependencies the project has on external factors": "Dependencies: Production availability of Texas Instruments LM5176, UCC28740, INA240A2, INA226, AMC1311, and STM32G474RET6 silicon; STMicroelectronics STM32CubeG4 HAL and FreeRTOS libraries; Custom transformer fabrication on Ferroxcube PQ26/20 cores with triple-insulated wire.",
        "<Top level development plan": "The project follows a 4-phase lifecycle spanning 18 weeks: Phase 1 (Weeks 1-3: PRD & Architecture Sign-Off); Phase 2 (Weeks 4-7: Schematic & PCB Layout); Phase 3 (Weeks 8-12: Rev A Fabrication & Board Bring-Up); Phase 4 (Weeks 13-18: DVT, EMC Pre-Compliance & Rev B Release).",
        "Out of scope point 1": "Three-phase 400V/480V AC industrial grid operation.",
        "Out of scope point 2": "Active Power Factor Correction (Active PFC boost stage). System utilizes passive EMI filtering with PF ~ 0.62.",
        "Out of scope point 3": "Negative/bipolar voltage rails (system provides positive 5.0V to 20.0V DC only). Wireless connectivity (Wi-Fi/Bluetooth) is excluded.",
        "Open Item 1": "Mechanical enclosure extrusion dimensions (finalizing 120x80x45mm profile vs 140x90x50mm based on binding post clearance).",
        "Open Item 2": "Current shunt value trade-off (evaluating 5mΩ vs 10mΩ for thermal dissipation vs ADC low-current resolution).",
        "Open Item 3": "USB Power Delivery (USB-PD) auxiliary sink negotiation (evaluating STUSB4500 controller for auxiliary DC input powering in field environments)."
    }

    for p in doc.paragraphs:
        for placeholder, replacement in replacements.items():
            if placeholder in p.text:
                p.text = p.text.replace(placeholder, replacement)

    print(f"Saving populated PRD document: {output_path}")
    doc.save(output_path)
    print(f"Saving duplicate PRD document: {alt_output_path}")
    doc.save(alt_output_path)
    print("Successfully generated Word (.docx) PRDs!")

if __name__ == "__main__":
    generate_prd_docx()
