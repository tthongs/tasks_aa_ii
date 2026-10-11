import subprocess
import os

def render_diagram(dot_code, base_name, dpi=150):
    dot_file = f"{base_name}.dot"
    png_file = f"{base_name}.png"
    svg_file = f"{base_name}.svg"
    with open(dot_file, "w") as f:
        f.write(dot_code)
    # Render PNG and SVG
    subprocess.run(["dot", f"-Gdpi={dpi}", "-Tpng", dot_file, "-o", png_file], check=True)
    subprocess.run(["dot", "-Tsvg", dot_file, "-o", svg_file], check=True)
    print(f"Rendered {png_file} and {svg_file} successfully.")

# ==============================================================================
# 1. MASTER SYSTEM ARCHITECTURE BLOCK DIAGRAM
# ==============================================================================
master_dot = r"""
digraph MasterArchitecture {
    graph [
        rankdir=LR,
        bgcolor="#FFFFFF",
        compound=true,
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=14,
        nodesep=0.38,
        ranksep=0.65,
        pad="0.25,0.25",
        splines=true
    ];
    node [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=9,
        shape=box,
        style="filled,rounded",
        margin="0.12,0.09",
        penwidth=1.4
    ];
    edge [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=8,
        penwidth=1.6,
        arrowsize=0.75
    ];

    subgraph cluster_ac_frontend {
        label = "MAINS AC FRONTEND & EMI SUPPRESSION (HOT DOMAIN)";
        style = "filled,rounded,dashed";
        fillcolor = "#F0F4F8";
        color = "#37474F";
        penwidth = 1.6;

        ac_in [label="AC Mains Grid Input\n85V - 265V AC RMS\n47 - 63 Hz (IEC C14)", fillcolor="#CFD8DC", color="#263238"];
        ac_prot [label="Input Protection\n• F1: 2A Time-Lag Fuse\n• NTC1: 10Ω Inrush Limiter\n• MOV1: 14D471K Varistor", fillcolor="#FFFFFF", color="#455A64"];
        ac_emi [label="2-Stage EMI Filter\n• L_CM1: 15mH, L_CM2: 4.7mH\n• C_X: 3x Film (220nF, 100nF)\n• C_Y: 2x 2.2nF Safety Caps\n(CISPR 32 Class B)", fillcolor="#FFFFFF", color="#455A64"];
        ac_rect [label="Bridge Rectifier & Bulk Storage\n• BR1: GBU606 (600V, 6A)\n• C_BULK: 100µF/450V + 470nF Film\nBus: +120V to +375V DC", fillcolor="#FFFFFF", color="#455A64"];

        ac_in -> ac_prot [label=" L, N, PE", color="#263238"];
        ac_prot -> ac_emi [label=" Protected AC", color="#263238"];
        ac_emi -> ac_rect [label=" Filtered AC", color="#263238"];
    }

    subgraph cluster_primary_flyback {
        label = "STAGE 1: ISOLATED PRIMARY FLYBACK CONVERTER (HOT DOMAIN)";
        style = "filled,rounded";
        fillcolor = "#FFF3E0";
        color = "#E65100";
        penwidth = 1.6;

        tx_pri [label="Transformer Primary\nPQ26/20 Core (3C95)\nNp = 48T | Lp = 220µH", fillcolor="#FFE0B2", color="#E65100"];
        snubber [label="RCD Clamp Snubber\n50kΩ / 2.2nF / UF4007\nClamps Vds Ringing", fillcolor="#FFFFFF", color="#F57C00"];
        pri_mosfet [label="Primary Switch Q1\nIPB80R290P7 (800V, 0.29Ω)\nSuperjunction D2PAK", fillcolor="#FFFFFF", color="#E65100"];
        pri_ctrl [label="QR Flyback Controller\nTI UCC28740\n• Valley Switching (ZCD)\n• Cycle-by-Cycle Peak CS", fillcolor="#FFFFFF", color="#E65100"];
        pri_rsense [label="Current Sense Shunt\nRsense = 0.2Ω / 2W", fillcolor="#FFFFFF", color="#F57C00"];
        aux_pri [label="Aux Bias Winding\nNaux = 8T (+14V VCC)", fillcolor="#FFE0B2", color="#E65100"];

        ac_rect -> tx_pri [label=" +V_BULK", color="#D84315", penwidth=2.2];
        tx_pri -> pri_mosfet [label=" Drain", color="#D84315", penwidth=2.2];
        pri_mosfet -> snubber [dir=both, style=dashed, color="#E65100"];
        pri_ctrl -> pri_mosfet [label=" Gate", color="#BF360C"];
        pri_mosfet -> pri_rsense [label=" Source", color="#BF360C"];
        pri_rsense -> pri_ctrl [label=" CS", style=dashed, color="#BF360C"];
        aux_pri -> pri_ctrl [label=" Aux Bias / ZCD", color="#E65100"];
    }

    subgraph cluster_barrier {
        label = "REINFORCED SAFETY ISOLATION BARRIER (IEC 62368-1)\nCreepage ≥ 6.4mm | Clearance ≥ 5.2mm | Hipot 3000V RMS | 2.0mm PCB Milled Air Slot";
        style = "filled,rounded,dashed";
        fillcolor = "#FFEBEE";
        color = "#C62828";
        penwidth = 2.0;

        tx_sec [label="Transformer Secondary\nNs = 12T (Triple Insulated Wire)\nReinforced 3kV Isolation", fillcolor="#FFFFFF", color="#C62828"];
        iso_opto [label="Isolated Voltage Feedback\nPC817 / EL817 Optocoupler\n(5kV RMS Isolation)", fillcolor="#FFFFFF", color="#C62828"];
        iso_amc [label="Isolated AC Voltage Sensor\nTI AMC1311 ΔΣ Modulator\n(5kV RMS Isolation)", fillcolor="#FFFFFF", color="#C62828"];
        iso_ct [label="Isolated AC Current Sensor\nTalema AC1005 (1000:1 CT)\nToroidal Magnetic Isolation", fillcolor="#FFFFFF", color="#C62828"];
    }

    subgraph cluster_secondary_flyback {
        label = "STAGE 1: SECONDARY SYNCHRONOUS RECTIFICATION (SELV SAFE)";
        style = "filled,rounded";
        fillcolor = "#E8F5E9";
        color = "#2E7D32";
        penwidth = 1.6;

        sr_stage [label="Synchronous Rectifier\n• MP6908 Smart Driver\n• BSC052N06NS (60V, 5.2mΩ)\nReplaces Lossy Schottky", fillcolor="#FFFFFF", color="#2E7D32"];
        bus_24v [label="+24.0V Intermediate Bus\n• Regulated 24V DC / 72W\n• Ripple: < 40mV pk-pk\n• 2x 470µF Poly + 4x 10µF MLCC", fillcolor="#A5D6A7", color="#1B5E20", penwidth=2.0];
        tl431_fb [label="Precision Shunt Reference\nTL431 + Compensation\nCloses 24V Reg Loop", fillcolor="#FFFFFF", color="#2E7D32"];

        tx_sec -> sr_stage [label=" Switched AC", color="#2E7D32", penwidth=2.2];
        sr_stage -> bus_24v [label=" +24V DC", color="#2E7D32", penwidth=2.2];
        bus_24v -> tl431_fb [label=" Sense", color="#2E7D32"];
        tl431_fb -> iso_opto [label=" Drive", color="#C62828"];
        iso_opto -> pri_ctrl [label=" FB Feedback", color="#C62828"];
    }

    subgraph cluster_buck_boost {
        label = "STAGE 2: 4-SWITCH SYNCHRONOUS BUCK-BOOST POST-REGULATOR";
        style = "filled,rounded";
        fillcolor = "#E0F7FA";
        color = "#00838F";
        penwidth = 1.6;

        bb_ctrl [label="Synchronous BB Controller\nTI LM5176 (250 kHz PWM)\n• Pure Buck (5-18V)\n• Buck-Boost (18-20V)\n• 4x Gate Drivers Inside", fillcolor="#FFFFFF", color="#00838F"];
        h_bridge [label="4-Switch Synchronous H-Bridge\n• Q_A (Buck HS), Q_B (Buck LS)\n• Q_C (Boost LS), Q_D (Boost HS)\n4x Infineon BSC034N04LS (40V, 3.4mΩ)", fillcolor="#B2EBF2", color="#00838F", penwidth=1.8];
        bb_ind [label="Power Inductor L\nWurth 7443321000\n10.0µH, 8.5A RMS, 11.5A Sat\nDCR = 11.8mΩ (WE-HCC)", fillcolor="#FFFFFF", color="#00838F"];
        out_filt [label="Output Filter Bank\n• 4x 22µF 25V X7R MLCC\n• 1x 100µF 25V OS-CON Poly\nESR < 2.5mΩ", fillcolor="#FFFFFF", color="#00838F"];
        dc_shunt [label="Kelvin Shunt Resistor\nBourns CSS2H-2512R-L010F\n10.0mΩ, 0.1% Tol, 3W", fillcolor="#FFFFFF", color="#00838F"];
        dc_terminals [label="Programmable DC Output Rail\n5.0V - 20.0V DC @ 0.1A - 3.0A (60W)\nRipple < 25mV pk-pk | Step < 120µs\nGold-Plated 4mm Binding Posts", fillcolor="#80CBC4", color="#004D40", penwidth=2.2];

        bus_24v -> h_bridge [label=" +24V Bus In", color="#00695C", penwidth=2.2];
        bb_ctrl -> h_bridge [label=" 4x Gate Drives\n(PWM_A..D)", color="#00838F"];
        h_bridge -> bb_ind [label=" SW1 & SW2", color="#00695C", penwidth=2.2];
        bb_ind -> out_filt [label=" Filtered DC", color="#00695C", penwidth=2.2];
        out_filt -> dc_shunt [color="#00695C", penwidth=2.2];
        dc_shunt -> dc_terminals [label=" Regulated DC", color="#004D40", penwidth=2.2];
    }

    subgraph cluster_control_protection {
        label = "MIXED-SIGNAL CLOSED-LOOP CONTROL & HARDWARE PROTECTION";
        style = "filled,rounded";
        fillcolor = "#F3E5F5";
        color = "#6A1B9A";
        penwidth = 1.6;

        dac_summing [label="DAC Voltage Steering Network\nR_top = 49.9kΩ, R_bot = 3.65kΩ\nR_DAC = 11.0kΩ (0.1% Precision)\nInjects offset current into FB node\nLinear Resolution: 3.65mV / LSB", fillcolor="#FFFFFF", color="#6A1B9A"];
        ina240 [label="Fast Current Sense Amp\nTI INA240A2 (Gain = 50 V/V)\n400 kHz BW, 2µs Response", fillcolor="#FFFFFF", color="#6A1B9A"];
        cc_clamp [label="Hardware Fast CC Clamp\nTI TLV3501 (4.5ns Comparator)\nPulls COMP pin down via BAT54\nTrip Latency < 5µs (Zero CPU lag)", fillcolor="#E1BEE7", color="#4A148C", penwidth=1.8];

        dc_terminals -> dac_summing [label=" VOUT Sense", color="#6A1B9A"];
        dac_summing -> bb_ctrl [label=" V_FB (1.20V Ref)", color="#6A1B9A"];
        dc_shunt -> ina240 [label=" Kelvin Sense", color="#6A1B9A"];
        ina240 -> cc_clamp [label=" V_ISENSE", color="#6A1B9A"];
        cc_clamp -> bb_ctrl [label=" Throttles COMP Pin\n(< 5µs CC Clamp)", color="#B71C1C", penwidth=1.8];
    }

    subgraph cluster_telemetry {
        label = "DUAL-DOMAIN POWER SENSING & EFFICIENCY ENGINE";
        style = "filled,rounded";
        fillcolor = "#E8EAF6";
        color = "#283593";
        penwidth = 1.6;

        ac_v_div [label="High-Voltage Divider\n4x 1MΩ + 2kΩ Shunt\n375Vpk -> 187.5mV", fillcolor="#FFFFFF", color="#283593"];
        ct_burden [label="CT Burden Resistor\n100Ω Precision Shunt\n2mA -> 200mV RMS", fillcolor="#FFFFFF", color="#283593"];
        ina226 [label="DC Power Monitor IC\nTI INA226 (16-Bit I2C ADC)\n1.25mV/LSB, 100µA/LSB", fillcolor="#FFFFFF", color="#283593"];

        ac_emi -> ac_v_div [label=" AC Line", color="#1A237E"];
        ac_prot -> iso_ct [label=" Line Loop", color="#1A237E"];
        ac_v_div -> iso_amc [label=" VINP, VINN", color="#1A237E"];
        iso_ct -> ct_burden [label=" 1000:1 Sec", color="#1A237E"];
        dc_shunt -> ina226 [label=" Kelvin Sense", color="#1A237E"];
        dc_terminals -> ina226 [label=" VBUS Sense", color="#1A237E"];
    }

    subgraph cluster_mcu {
        label = "CENTRAL EMBEDDED MICROCONTROLLER SUBSYSTEM";
        style = "filled,rounded";
        fillcolor = "#E1F5FE";
        color = "#0277BD";
        penwidth = 1.8;

        mcu [label="STM32G474RET6 Microcontroller\n• 32-bit ARM Cortex-M4F @ 170 MHz\n• Hardware Sinc3 Decimation Filter\n• Hardware CORDIC / Math Accel\n• Dual 12-Bit Fast DACs & ADCs\n• FreeRTOS Real-Time Kernel", fillcolor="#B3E5FC", color="#01579B", penwidth=2.0];
        eff_calc [label="Real-Time Efficiency Engine (10Hz)\nComputes: η = (P_DC / P_AC) × 100%\n• Instantaneous v(t)·i(t) Integration\n• Active Power Pac, True RMS Vac, Iac, PF\n• True Vdc, Idc, Pdc\n• 8-tap EMA Smoothing Filter", fillcolor="#FFFFFF", color="#0277BD"];

        iso_amc -> mcu [label=" Bitstream (Sinc3)", color="#1565C0", penwidth=1.6];
        ct_burden -> mcu [label=" I_AC Signal", color="#1565C0"];
        ina226 -> mcu [label=" I2C (400kHz)", color="#0277BD", penwidth=1.6];
        mcu -> eff_calc [dir=both, label=" Math Engine", color="#0277BD"];
        mcu -> dac_summing [label=" 12-Bit DAC1 (V_SET)\n0.0V - 3.3V Control", color="#6A1B9A", penwidth=1.8];
        mcu -> cc_clamp [label=" 12-Bit DAC2 (I_SET)\nCurrent Limit Ref", color="#6A1B9A", penwidth=1.8];
    }

    subgraph cluster_hmi_storage {
        label = "USER INTERFACE, STORAGE & TELEMETRY";
        style = "filled,rounded";
        fillcolor = "#FBE9E7";
        color = "#D84315";
        penwidth = 1.6;

        oled [label="1.3\" Monochrome OLED GUI\n128x64 I2C Graphic Display\nReal-time V, I, P, η Gauges", fillcolor="#FFFFFF", color="#D84315"];
        sd_card [label="MicroSD Data Logger\nFAT32 CSV File System (SPI/SDIO)\n10Hz Timestamped Logging", fillcolor="#FFFFFF", color="#D84315"];
        usb_comm [label="USB Type-C Interface\nUSB-CDC Virtual COM Port\nSCPI Commands & Remote ATE", fillcolor="#FFFFFF", color="#D84315"];
        controls [label="Rotary Encoders & Switches\n• Voltage & Current Knobs\n• Output Enable / Status LED", fillcolor="#FFFFFF", color="#D84315"];

        mcu -> oled [label=" I2C Bus", color="#D84315"];
        mcu -> sd_card [label=" SPI / SDIO", color="#D84315"];
        mcu -> usb_comm [label=" USB-CDC (SCPI)", color="#D84315"];
        controls -> mcu [label=" GPIO & Interrupts", color="#D84315"];
    }

    subgraph cluster_aux_power {
        label = "AUXILIARY BIAS POWER DISTRIBUTION";
        style = "filled,rounded";
        fillcolor = "#FFFDE7";
        color = "#F57F17";
        penwidth = 1.6;

        aux_buck [label="Secondary Aux Buck\nTI TPS54202 (24V -> 5.0V / 2A)\nPowers Gate Drivers & Displays", fillcolor="#FFFFFF", color="#F57F17"];
        aux_ldo [label="Clean Logic LDO\nTI TPS7A25 (5.0V -> 3.3V / 500mA)\nPowers MCU & Sensors", fillcolor="#FFFFFF", color="#F57F17"];
        aux_ref [label="Precision VREF\nTI REF3030 (3.000V, 0.2%)\nADC / DAC Reference", fillcolor="#FFFFFF", color="#F57F17"];

        bus_24v -> aux_buck [label=" +24V Bus", color="#F57F17", penwidth=1.6];
        aux_buck -> aux_ldo [label=" +5.0V Rail", color="#F57F17", penwidth=1.6];
        aux_ldo -> aux_ref [label=" +3.3V Rail", color="#F57F17", penwidth=1.6];
    }
}
"""

# ==============================================================================
# 2. STAGE 1 AC-DC FLYBACK CONVERTER DETAILED DIAGRAM
# ==============================================================================
flyback_dot = r"""
digraph Stage1Flyback {
    graph [
        rankdir=LR,
        bgcolor="#FFFFFF",
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=13,
        nodesep=0.35,
        ranksep=0.55,
        pad="0.2,0.2",
        splines=true
    ];
    node [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=9,
        shape=box,
        style="filled,rounded",
        margin="0.12,0.08",
        penwidth=1.4
    ];
    edge [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=8,
        penwidth=1.6,
        arrowsize=0.75
    ];

    subgraph cluster_mains {
        label = "AC INPUT & PROTECTION";
        style = "filled,rounded";
        fillcolor = "#ECEFF1";
        color = "#37474F";
        ac_line [label="AC Mains Input\n85V - 265V AC RMS\n47 - 63 Hz", fillcolor="#CFD8DC", color="#263238"];
        fuse [label="F1: Time-Lag Fuse\n2A / 250V AC", fillcolor="#FFFFFF", color="#37474F"];
        ntc [label="NTC1: Thermistor\n10Ω (Inrush < 37.5A)", fillcolor="#FFFFFF", color="#37474F"];
        mov [label="MOV1: Varistor\n14D471K (300V RMS)", fillcolor="#FFFFFF", color="#37474F"];
        emi [label="2-Stage EMI Filter\n• L_CM1 (15mH) & L_CM2 (4.7mH)\n• 3x X2 Film Caps (220nF/100nF)\n• 2x Y Safety Caps (2.2nF)", fillcolor="#FFFFFF", color="#37474F"];

        ac_line -> fuse -> ntc -> emi;
        fuse -> mov [style=dashed];
    }

    subgraph cluster_rect {
        label = "RECTIFICATION & BULK BUS";
        style = "filled,rounded";
        fillcolor = "#F5F5F5";
        color = "#616161";
        bridge [label="GBU606 Bridge Rectifier\n600V / 6A Glass Passivated", fillcolor="#FFFFFF", color="#616161"];
        cbulk [label="C_BULK Storage\n100µF / 450V Electrolytic\n+ 470nF / 450V HF Film\n(+120V to +375V DC)", fillcolor="#EEEEEE", color="#424242", penwidth=1.8];
        emi -> bridge -> cbulk [color="#D84315", penwidth=2.0];
    }

    subgraph cluster_primary_switch {
        label = "PRIMARY POWER STAGE (HOT GND_PRI)";
        style = "filled,rounded";
        fillcolor = "#FFF3E0";
        color = "#E65100";
        pri_wind [label="Transformer Primary Winding\nPQ26/20 Core (3C95 Ferrite)\nNp = 48 Turns | Lp = 220µH", fillcolor="#FFE0B2", color="#E65100"];
        snubber_rcd [label="RCD Snubber Clamp\n50kΩ / 2.2nF / UF4007\nDamps Leakage Inductance Ring", fillcolor="#FFFFFF", color="#F57C00"];
        fet_q1 [label="Primary MOSFET Q1\nInfineon IPB80R290P7\n800V Superjunction, 0.29Ω", fillcolor="#FFFFFF", color="#E65100"];
        rsense_pri [label="Current Sense Shunt\nRsense = 0.2Ω / 2W", fillcolor="#FFFFFF", color="#F57C00"];
        ctrl_ucc [label="QR Flyback Controller\nTI UCC28740\n• Valley Switching ZCD\n• Cycle Peak Current Mode", fillcolor="#FFFFFF", color="#E65100"];
        aux_wind [label="Aux Bias Winding\nNaux = 8T -> +14V VCC", fillcolor="#FFE0B2", color="#E65100"];

        cbulk -> pri_wind [label=" +V_BULK", color="#D84315", penwidth=2.2];
        pri_wind -> fet_q1 [label=" Drain", color="#D84315", penwidth=2.2];
        fet_q1 -> snubber_rcd [dir=both, style=dashed, color="#E65100"];
        ctrl_ucc -> fet_q1 [label=" Gate", color="#BF360C"];
        fet_q1 -> rsense_pri [label=" Source", color="#BF360C"];
        rsense_pri -> ctrl_ucc [label=" CS", style=dashed, color="#BF360C"];
        aux_wind -> ctrl_ucc [label=" VCC & ZCD", color="#E65100"];
    }

    subgraph cluster_sec_barrier {
        label = "REINFORCED ISOLATION BARRIER (IEC 62368-1)\nReinforced 3kV RMS / Creepage ≥ 6.4mm / Clearance ≥ 5.2mm";
        style = "filled,rounded,dashed";
        fillcolor = "#FFEBEE";
        color = "#C62828";
        sec_wind [label="Transformer Secondary\nNs = 12 Turns\nTriple Insulated Wire (TEX-E)", fillcolor="#FFFFFF", color="#C62828"];
        opto_fb [label="PC817 Optocoupler\n5kV RMS Isolation\nIsolated Voltage Feedback", fillcolor="#FFFFFF", color="#C62828"];
    }

    subgraph cluster_sec_sr {
        label = "SECONDARY SYNCHRONOUS RECTIFIER (GND_SEC)";
        style = "filled,rounded";
        fillcolor = "#E8F5E9";
        color = "#2E7D32";
        sr_mosfet [label="SR MOSFET Q_SR\nInfineon BSC052N06NS\n60V, 5.2mΩ SuperSO8", fillcolor="#C8E6C9", color="#2E7D32"];
        sr_driver [label="Smart SR Controller\nMonolithic Power MP6908\nFast Vds Zero-Crossing Sensing", fillcolor="#FFFFFF", color="#2E7D32"];
        out_cap_24v [label="Intermediate Bus Filter\n2x 470µF Polymer + 4x 10µF MLCC\nUltra-low ESR Bank", fillcolor="#FFFFFF", color="#2E7D32"];
        bus_out [label="+24.0V Intermediate DC Rail\n72W Max Power | Ripple < 40mV pk-pk\nPowers Stage 2 Buck-Boost", fillcolor="#A5D6A7", color="#1B5E20", penwidth=2.0];
        tl431 [label="Precision Shunt Regulator\nTI TL431 (2.495V Reference)\nType-II Loop Compensation", fillcolor="#FFFFFF", color="#2E7D32"];

        sec_wind -> sr_mosfet [label=" AC Pulse", color="#2E7D32", penwidth=2.0];
        sr_driver -> sr_mosfet [label=" Gate", color="#2E7D32"];
        sr_mosfet -> out_cap_24v -> bus_out [color="#2E7D32", penwidth=2.2];
        bus_out -> tl431 [label=" Bus Sense", color="#2E7D32"];
        tl431 -> opto_fb [label=" LED Drive", color="#C62828"];
        opto_fb -> ctrl_ucc [label=" FB Feedback", color="#C62828"];
    }
}
"""

# ==============================================================================
# 3. STAGE 2 SYNCHRONOUS BUCK-BOOST DETAILED DIAGRAM
# ==============================================================================
buckboost_dot = r"""
digraph Stage2BuckBoost {
    graph [
        rankdir=LR,
        bgcolor="#FFFFFF",
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=13,
        nodesep=0.35,
        ranksep=0.55,
        pad="0.2,0.2",
        splines=true
    ];
    node [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=9,
        shape=box,
        style="filled,rounded",
        margin="0.12,0.08",
        penwidth=1.4
    ];
    edge [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=8,
        penwidth=1.6,
        arrowsize=0.75
    ];

    subgraph cluster_bb_in {
        label = "INPUT DC BUS";
        style = "filled,rounded";
        fillcolor = "#E8F5E9";
        color = "#2E7D32";
        vin_24v [label="+24.0V DC Bus In\nFrom Primary Stage 1\nLow Ripple Intermediate Rail", fillcolor="#A5D6A7", color="#1B5E20"];
        in_caps [label="Input Decoupling\n2x 10µF 50V X7R MLCC", fillcolor="#FFFFFF", color="#2E7D32"];
        vin_24v -> in_caps;
    }

    subgraph cluster_hbridge {
        label = "4-SWITCH SYNCHRONOUS H-BRIDGE POWER STAGE";
        style = "filled,rounded";
        fillcolor = "#E0F7FA";
        color = "#00838F";
        buck_leg [label="Buck Half-Bridge (Node SW1)\n• Q_A (High-Side Switch)\n• Q_B (Low-Side Synchronous)\n2x BSC034N04LS (40V, 3.4mΩ)", fillcolor="#B2EBF2", color="#00838F"];
        power_ind [label="Flat-Wire Power Inductor L\nWurth 7443321000 (WE-HCC)\nL = 10.0µH, Irms = 8.5A, Isat = 11.5A\nDCR = 11.8mΩ Ultra-low Loss", fillcolor="#FFFFFF", color="#00838F", penwidth=1.8];
        boost_leg [label="Boost Half-Bridge (Node SW2)\n• Q_C (Low-Side Switch)\n• Q_D (High-Side Synchronous)\n2x BSC034N04LS (40V, 3.4mΩ)", fillcolor="#B2EBF2", color="#00838F"];

        in_caps -> buck_leg [label=" +24V", color="#00695C", penwidth=2.2];
        buck_leg -> power_ind [label=" SW1 Node", color="#00695C", penwidth=2.2];
        power_ind -> boost_leg [label=" SW2 Node", color="#00695C", penwidth=2.2];
    }

    subgraph cluster_bb_controller {
        label = "LM5176 SYNCHRONOUS BUCK-BOOST CONTROLLER";
        style = "filled,rounded";
        fillcolor = "#E1F5FE";
        color = "#0277BD";
        ctrl_lm5176 [label="TI LM5176 Controller\n• 250 kHz Fixed Switching Frequency\n• Peak Current-Mode Control\n• Internal 5V Gate Drivers\n• Bootstrap Floating Bias for Q_A, Q_D", fillcolor="#FFFFFF", color="#0277BD"];
        modes [label="Automatic Mode Transition\n• Pure Buck: Vout = 5-18V (Q_D 100% ON, Q_C OFF)\n• Buck-Boost: Vout = 18-20V (Smooth Multi-mode)\n• Peak Efficiency ≥ 96.5% @ 15V/3A", fillcolor="#B3E5FC", color="#01579B"];
        ctrl_lm5176 -> modes [style=dotted];
        ctrl_lm5176 -> buck_leg [label=" PWM_A, PWM_B", color="#00838F"];
        ctrl_lm5176 -> boost_leg [label=" PWM_C, PWM_D", color="#00838F"];
    }

    subgraph cluster_bb_out {
        label = "OUTPUT FILTER BANK & MEASUREMENT SHUNT";
        style = "filled,rounded";
        fillcolor = "#E8F8F5";
        color = "#117A65";
        cout_bank [label="Output Capacitor Bank\n• 4x 22µF 25V X7R 1210 Ceramic\n• 1x 100µF 25V OS-CON Polymer\nCombined ESR < 2.5mΩ\nOutput Ripple < 25mV pk-pk", fillcolor="#FFFFFF", color="#117A65"];
        kelvin_shunt [label="Kelvin Current Shunt\nBourns CSS2H-2512R-L010F\n10.0mΩ, 0.1% Tol, 3W, 15ppm/°C", fillcolor="#FFFFFF", color="#117A65"];
        terminals [label="DC Output Rail (4mm Binding Posts)\n5.0V - 20.0V DC Programmable\n0.1A - 3.0A Continuous (60W Max)\nTransient Recovery < 120µs to 1%", fillcolor="#80CBC4", color="#004D40", penwidth=2.2];

        boost_leg -> cout_bank [label=" Switched DC", color="#00695C", penwidth=2.2];
        cout_bank -> kelvin_shunt [color="#00695C", penwidth=2.2];
        kelvin_shunt -> terminals [label=" Regulated DC", color="#004D40", penwidth=2.2];
    }
}
"""

# ==============================================================================
# 4. MIXED-SIGNAL CONTROL & HARDWARE CC CLAMPING DETAILED DIAGRAM
# ==============================================================================
control_dot = r"""
digraph ControlFeedback {
    graph [
        rankdir=LR,
        bgcolor="#FFFFFF",
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=13,
        nodesep=0.35,
        ranksep=0.55,
        pad="0.2,0.2",
        splines=true
    ];
    node [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=9,
        shape=box,
        style="filled,rounded",
        margin="0.12,0.08",
        penwidth=1.4
    ];
    edge [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=8,
        penwidth=1.6,
        arrowsize=0.75
    ];

    subgraph cluster_mcu_control {
        label = "STM32G474 MICROCONTROLLER CONTROL PLANE";
        style = "filled,rounded";
        fillcolor = "#E1F5FE";
        color = "#0277BD";
        dac1_volt [label="12-Bit Fast DAC1 (V_SET)\nGenerates 0.00V - 3.30V\nCalibrated Output Voltage Command", fillcolor="#FFFFFF", color="#0277BD"];
        dac2_curr [label="12-Bit Fast DAC2 (I_SET)\nGenerates Current Limit Reference\nV_ISET = I_LIMIT × 0.50 V/A", fillcolor="#FFFFFF", color="#0277BD"];
        user_input [label="Operator / SCPI Command\n• Voltage Set: 5.0V - 20.0V (10mV Step)\n• Current Limit: 0.1A - 3.0A (10mA Step)", fillcolor="#B3E5FC", color="#01579B"];
        user_input -> dac1_volt;
        user_input -> dac2_curr;
    }

    subgraph cluster_volt_loop {
        label = "CONSTANT VOLTAGE (CV) PROGRAMMING LOOP";
        style = "filled,rounded";
        fillcolor = "#F3E5F5";
        color = "#6A1B9A";
        summing_node [label="Feedback Summing Node (V_FB)\n• R_top = 49.9kΩ (to VOUT)\n• R_bot = 3.65kΩ (to AGND)\n• R_DAC = 11.0kΩ (from DAC1)\n0.1% Thin Film Resistors", fillcolor="#FFFFFF", color="#6A1B9A"];
        kcl_eq [label="KCL Current Balance Equation\nVout = 1.20 × (1 + Rtop/Rbot + Rtop/Rdac)\n- Vdac × (Rtop/Rdac)\nLinear Transfer: 3.65 mV / LSB", fillcolor="#EDE7F6", color="#5E35B1"];
        err_amp [label="LM5176 Internal Error Amplifier\nInverting Input clamps V_FB = 1.200V\nType-II Frequency Compensation", fillcolor="#FFFFFF", color="#6A1B9A"];

        dac1_volt -> summing_node [label=" DAC1 Voltage Injection", color="#6A1B9A", penwidth=1.8];
        summing_node -> kcl_eq [style=dotted];
        summing_node -> err_amp [label=" V_FB (1.20V Ref)", color="#6A1B9A", penwidth=2.0];
    }

    subgraph cluster_curr_loop {
        label = "AUTONOMOUS HARDWARE CONSTANT CURRENT (CC) CLAMP";
        style = "filled,rounded";
        fillcolor = "#FFEBEE";
        color = "#C62828";
        ina240 [label="High-Speed Current Sense Amp\nTI INA240A2 (Gain = 50 V/V)\n400 kHz Bandwidth, 2µs Slew\nV_ISENSE = 0.50 V/A", fillcolor="#FFFFFF", color="#C62828"];
        comp_tlv [label="Ultra-Fast Analog Comparator\nTI TLV3501 (4.5ns Propagation Delay)\nCompares V_ISENSE vs DAC2 (I_SET)", fillcolor="#FFFFFF", color="#C62828"];
        clamp_diode [label="BAT54 Schottky Clamp Diode\nPulls down LM5176 COMP pin\nZero CPU firmware intervention!", fillcolor="#FFCDD2", color="#B71C1C", penwidth=1.8];

        ina240 -> comp_tlv [label=" V_ISENSE (0.5V/A)", color="#C62828", penwidth=1.8];
        dac2_curr -> comp_tlv [label=" DAC2 (I_SET Limit)", color="#C62828", penwidth=1.8];
        comp_tlv -> clamp_diode [label=" Trips on Overload", color="#B71C1C", penwidth=2.0];
    }

    subgraph cluster_power_stage {
        label = "BUCK-BOOST POWER CONTROLLER INTERACTION";
        style = "filled,rounded";
        fillcolor = "#E0F7FA";
        color = "#00838F";
        comp_pin [label="LM5176 COMP Pin\nControls Inner PWM Duty Cycle", fillcolor="#FFFFFF", color="#00838F"];
        err_amp -> comp_pin [label=" Linear CV Output", color="#6A1B9A"];
        clamp_diode -> comp_pin [label=" Hard Clamps COMP in < 5µs!\nStrict Current Limiting", color="#B71C1C", penwidth=2.2];
    }
}
"""

# ==============================================================================
# 5. DUAL-DOMAIN SENSING & REAL-TIME EFFICIENCY ENGINE DETAILED DIAGRAM
# ==============================================================================
telemetry_dot = r"""
digraph TelemetryEfficiency {
    graph [
        rankdir=LR,
        bgcolor="#FFFFFF",
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=13,
        nodesep=0.35,
        ranksep=0.55,
        pad="0.2,0.2",
        splines=true
    ];
    node [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=9,
        shape=box,
        style="filled,rounded",
        margin="0.12,0.08",
        penwidth=1.4
    ];
    edge [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=8,
        penwidth=1.6,
        arrowsize=0.75
    ];

    subgraph cluster_ac_metering {
        label = "PRIMARY HIGH-VOLTAGE AC DOMAIN SENSING";
        style = "filled,rounded";
        fillcolor = "#ECEFF1";
        color = "#37474F";
        ac_grid [label="Mains AC Line\n85V - 265V AC RMS", fillcolor="#CFD8DC", color="#263238"];
        v_divider [label="HV Resistor Divider\n4x 1MΩ (1206) + 2kΩ 0.1%\nScales 375Vpk -> 187.5mV", fillcolor="#FFFFFF", color="#37474F"];
        ct_sensor [label="Toroidal Current Transformer\nTalema AC1005 (1000:1 CT)\n2A RMS Line -> 2mA Sec", fillcolor="#FFFFFF", color="#37474F"];
        ct_burden [label="100Ω Precision Burden\n2mA -> 200mV RMS", fillcolor="#FFFFFF", color="#37474F"];

        ac_grid -> v_divider;
        ac_grid -> ct_sensor -> ct_burden;
    }

    subgraph cluster_iso_mod {
        label = "REINFORCED ISOLATION BARRIER (5kV RMS)";
        style = "filled,rounded,dashed";
        fillcolor = "#FFEBEE";
        color = "#C62828";
        amc1311 [label="TI AMC1311 Modulator\nIsolated ΔΣ Modulator\nReinforced 5kV Isolation\nDigital Bitstream Out", fillcolor="#FFFFFF", color="#C62828", penwidth=1.8];
        v_divider -> amc1311 [label=" VINP, VINN", color="#C62828"];
    }

    subgraph cluster_dc_metering {
        label = "SECONDARY DC LOAD DOMAIN SENSING";
        style = "filled,rounded";
        fillcolor = "#E8F5E9";
        color = "#2E7D32";
        dc_shunt [label="10mΩ 0.1% Shunt\nKelvin Connections", fillcolor="#FFFFFF", color="#2E7D32"];
        ina226 [label="TI INA226 Power Monitor\n16-Bit I2C Digital ADC\n• 1.25 mV/LSB (VBUS)\n• 100 µA/LSB (Current)\n• Hardware Multiplier (Pdc)", fillcolor="#C8E6C9", color="#2E7D32", penwidth=1.8];
        dc_shunt -> ina226 [label=" Kelvin Sense", color="#2E7D32"];
    }

    subgraph cluster_mcu_eff {
        label = "CENTRAL MCU EFFICIENCY ENGINE (STM32G474)";
        style = "filled,rounded";
        fillcolor = "#E1F5FE";
        color = "#0277BD";
        sinc3_filter [label="Hardware Sinc3 Decimation Filter\nDirect on-chip peripheral\nReconstructs True AC Waveform", fillcolor="#FFFFFF", color="#0277BD"];
        ac_calc [label="Instantaneous Integration (10 kHz)\n• Pac = (1/N) Σ v(t)·i(t) [True Watts]\n• True RMS Vac & Iac\n• Power Factor PF = Pac / (Vac·Iac)", fillcolor="#FFFFFF", color="#0277BD"];
        dc_read [label="I2C Telemetry Task (10 Hz)\nReads INA226 Registers:\nVdc, Idc, Pdc [Watts]", fillcolor="#FFFFFF", color="#0277BD"];
        eff_core [label="Real-Time Efficiency Engine\nη(t) = [ P_DC(t) / P_AC(t) ] × 100%\n8-tap Exponential Moving Average Filter\nUpdates at 10 Hz (100ms interval)", fillcolor="#B3E5FC", color="#01579B", penwidth=2.0];

        amc1311 -> sinc3_filter [label=" Differential Bitstream", color="#1565C0", penwidth=1.8];
        ct_burden -> ac_calc [label=" AC Current Analog", color="#1565C0"];
        sinc3_filter -> ac_calc;
        ina226 -> dc_read [label=" I2C Bus (400kHz)", color="#2E7D32", penwidth=1.8];
        ac_calc -> eff_core [label=" Pac (Active Watts)", color="#0277BD"];
        dc_read -> eff_core [label=" Pdc (True Watts)", color="#0277BD"];
    }

    subgraph cluster_telemetry_out {
        label = "TELEMETRY & USER DISPATCH";
        style = "filled,rounded";
        fillcolor = "#FBE9E7";
        color = "#D84315";
        oled_disp [label="1.3\" OLED GUI Display\nReal-time V, I, P, η Gauges", fillcolor="#FFFFFF", color="#D84315"];
        sd_log [label="MicroSD FAT32 CSV Logger\n10Hz Continuous File Records", fillcolor="#FFFFFF", color="#D84315"];
        scpi_comm [label="USB Type-C SCPI Parser\nAutomated Test ATE Queries", fillcolor="#FFFFFF", color="#D84315"];

        eff_core -> oled_disp [color="#D84315"];
        eff_core -> sd_log [color="#D84315"];
        eff_core -> scpi_comm [color="#D84315"];
    }
}
"""

# ==============================================================================
# 6. AUXILIARY POWER DISTRIBUTION & GROUND DOMAIN ARCHITECTURE DIAGRAM
# ==============================================================================
aux_dot = r"""
digraph AuxPower {
    graph [
        rankdir=LR,
        bgcolor="#FFFFFF",
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=13,
        nodesep=0.35,
        ranksep=0.55,
        pad="0.2,0.2",
        splines=true
    ];
    node [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=9,
        shape=box,
        style="filled,rounded",
        margin="0.12,0.08",
        penwidth=1.4
    ];
    edge [
        fontname="DejaVu Sans, Arial, Helvetica, sans-serif",
        fontsize=8,
        penwidth=1.6,
        arrowsize=0.75
    ];

    subgraph cluster_pri_aux {
        label = "PRIMARY AUXILIARY BIAS (GND_PRI)";
        style = "filled,rounded";
        fillcolor = "#FFF3E0";
        color = "#E65100";
        naux [label="Transformer Aux Winding Naux (8T)\nFlyback Coupling during Off-time", fillcolor="#FFE0B2", color="#E65100"];
        pri_rect [label="Fast Diode (ES1J) + 22µF/35V Cap\nGenerates +14.0V Primary VCC", fillcolor="#FFFFFF", color="#E65100"];
        ucc_vcc [label="TI UCC28740 VDD Pin\nPrimary Flyback Controller Bias", fillcolor="#FFFFFF", color="#E65100"];

        naux -> pri_rect -> ucc_vcc [label=" +14V VCC", color="#E65100"];
    }

    subgraph cluster_sec_aux {
        label = "SECONDARY MULTI-RAIL POWER TREE (GND_SEC)";
        style = "filled,rounded";
        fillcolor = "#FFFDE7";
        color = "#F57F17";
        bus_24v [label="+24.0V Intermediate DC Bus\nMain Secondary Power Distribution", fillcolor="#A5D6A7", color="#1B5E20", penwidth=1.8];
        buck_5v [label="TI TPS54202 Synchronous Buck\n24V -> 5.0V / 2.0A (92% Eff.)\nSecondary Auxiliary Rail", fillcolor="#FFFFFF", color="#F57F17"];
        ldo_3v3 [label="TI TPS7A25 Ultra-Low-Noise LDO\n5.0V -> 3.3V / 500mA (High PSRR)\nClean Digital / Sensor VDD", fillcolor="#FFFFFF", color="#F57F17"];
        vref_3v [label="TI REF3030 Precision Reference\n3.000V Reference (0.2% Tol, 15ppm/°C)\nUltra-Clean ADC & DAC Reference", fillcolor="#FFFFFF", color="#F57F17"];

        bus_24v -> buck_5v [label=" +24V Bus", color="#F57F17", penwidth=2.0];
        buck_5v -> ldo_3v3 [label=" +5.0V Rail", color="#F57F17", penwidth=1.8];
        ldo_3v3 -> vref_3v [label=" +3.3V Rail", color="#F57F17", penwidth=1.8];
    }

    subgraph cluster_loads {
        label = "SYSTEM IC POWER CONSUMERS";
        style = "filled,rounded";
        fillcolor = "#F3E5F5";
        color = "#6A1B9A";
        load_drivers [label="Gate Drivers & Displays\n• LM5176 Internal Drivers (+5V)\n• 1.3\" OLED Display VCC (+5V)", fillcolor="#FFFFFF", color="#6A1B9A"];
        load_digital [label="Digital Logic & Memory\n• STM32G474RET6 MCU Core (+3.3V)\n• TI INA226 Power Monitor (+3.3V)\n• MicroSD Flash Card (+3.3V)", fillcolor="#FFFFFF", color="#6A1B9A"];
        load_analog [label="Precision Analog Subsystems\n• MCU VDDA & VREF+ (+3.000V)\n• 12-Bit DAC Steering Network (+3.000V)\n• High-Speed Comparators (+3.000V)", fillcolor="#FFFFFF", color="#6A1B9A"];

        buck_5v -> load_drivers [label=" +5.0V Aux", color="#6A1B9A"];
        ldo_3v3 -> load_digital [label=" +3.3V VDD", color="#6A1B9A"];
        vref_3v -> load_analog [label=" +3.000V VREF", color="#6A1B9A"];
    }

    subgraph cluster_grounds {
        label = "GROUND DOMAIN PARTITIONING & STAR TOPOLOGY";
        style = "filled,rounded,dashed";
        fillcolor = "#EFEBE9";
        color = "#4E342E";
        gnd_pri [label="GND_PRI\nPrimary Rectified Hot Ground\nIsolated from Secondary", fillcolor="#D7CCC8", color="#4E342E"];
        gnd_pwr [label="GND_SEC_PWR\nSecondary Switched Power Ground\nCarries Buck-Boost Pulses", fillcolor="#D7CCC8", color="#4E342E"];
        gnd_ana [label="GND_SEC_ANA\nQuiet Secondary Analog Ground\nSensors, ADC/DAC & TL431", fillcolor="#D7CCC8", color="#4E342E"];
        star_point [label="Single-Point Star Ground\nLocated directly beneath\nOutput Capacitor return pad", fillcolor="#FFFFFF", color="#4E342E", penwidth=1.8];

        gnd_pwr -> star_point [label=" Star Tie", color="#4E342E"];
        gnd_ana -> star_point [label=" Star Tie", color="#4E342E"];
    }
}
"""

# Render all diagrams
diagrams = [
    (master_dot, "smart_programmable_power_supply_system_block_diagram", 150),
    (flyback_dot, "block_diagram_stage1_flyback", 150),
    (buckboost_dot, "block_diagram_stage2_buckboost", 150),
    (control_dot, "block_diagram_control_feedback", 150),
    (telemetry_dot, "block_diagram_telemetry_efficiency", 150),
    (aux_dot, "block_diagram_aux_power_distribution", 150),
]

for dot, name, dpi in diagrams:
    render_diagram(dot, name, dpi)

print("\nAll 6 Architecture Block Diagrams generated in both SVG and high-DPI PNG successfully!")
