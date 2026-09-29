#!/usr/bin/env python3
"""
LDO (Low-Dropout Linear Voltage Regulator) Design, Thermal & Sizing Calculator
Usage:
    python3 tools/ldo_calc.py --thermal --vin <V> --vout <V> --iload <A> --theta-ja <C/W> [--ta <C>] [--iq <mA>]
    python3 tools/ldo_calc.py --feedback --vout <V> [--vref <V>] [--r2 <kOhm>]
    python3 tools/ldo_calc.py --stability --cout <uF> --esr <mOhm> [--cff <pF>] [--r1 <kOhm>] [--r2 <kOhm>]
    python3 tools/ldo_calc.py --compare --vin <V> --vout <V> --iload <A>
"""

import argparse
import sys
import math
from typing import Dict, Tuple, List

# Standard 1% EIA-96 resistor decade values
E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40,
    1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
    2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87,
    2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90,
    6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
    8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

def get_standard_e96_resistors(target_ratio: float, max_r2: float = 100e3) -> Tuple[float, float, float, float]:
    """
    Find best standard E96 resistor pair for R1 and R2 given target ratio R1/R2.
    Ratio = (Vout / Vref) - 1
    """
    best_error = float("inf")
    best_r1, best_r2 = 0.0, 0.0
    best_actual_ratio = 0.0

    decades = [1e2, 1e3, 1e4, 1e5]
    resistor_pool = [val * dec for dec in decades for val in E96_VALUES]

    for r2 in resistor_pool:
        if r2 > max_r2:
            continue
        ideal_r1 = target_ratio * r2
        if ideal_r1 < 100 or ideal_r1 > 1e6:
            continue
        # Find closest R1 in pool
        closest_r1 = min(resistor_pool, key=lambda x: abs(x - ideal_r1))
        actual_ratio = closest_r1 / r2
        err = abs(actual_ratio - target_ratio) / target_ratio
        if err < best_error:
            best_error = err
            best_r1 = closest_r1
            best_r2 = r2
            best_actual_ratio = actual_ratio

    return best_r1, best_r2, best_actual_ratio, best_error * 100.0

def calculate_thermal(vin: float, vout: float, iload: float, theta_ja: float, ta: float = 25.0, iq_ma: float = 1.0) -> Dict:
    vdrop = vin - vout
    iq_a = iq_ma / 1000.0
    p_pass = vdrop * iload
    p_iq = vin * iq_a
    p_total = p_pass + p_iq
    efficiency = (vout * iload) / (vin * (iload + iq_a)) * 100.0 if (iload + iq_a) > 0 else 0
    delta_t = p_total * theta_ja
    tj = ta + delta_t
    max_safe_tj = 125.0
    safe = tj <= max_safe_tj
    max_allowable_theta_ja = (max_safe_tj - ta) / p_total if p_total > 0 else float("inf")

    return {
        "vdrop": vdrop,
        "p_pass_w": p_pass,
        "p_iq_w": p_iq,
        "p_total_w": p_total,
        "efficiency_pct": efficiency,
        "delta_t_c": delta_t,
        "tj_c": tj,
        "safe": safe,
        "max_theta_ja": max_allowable_theta_ja
    }

def calculate_stability(cout_uf: float, esr_mohm: float, cff_pf: float = 0.0, r1_k: float = 0.0, r2_k: float = 0.0) -> Dict:
    cout_f = cout_uf * 1e-6
    esr_ohm = esr_mohm / 1000.0
    f_zero_esr = (1.0 / (2.0 * math.pi * esr_ohm * cout_f)) if (esr_ohm > 0 and cout_f > 0) else float("inf")

    cff_f = cff_pf * 1e-12
    r1_ohm = r1_k * 1e3
    r2_ohm = r2_k * 1e3
    f_z_ff = 0.0
    f_p_ff = 0.0
    if cff_f > 0 and r1_ohm > 0:
        f_z_ff = 1.0 / (2.0 * math.pi * r1_ohm * cff_f)
        if r2_ohm > 0:
            r_par = (r1_ohm * r2_ohm) / (r1_ohm + r2_ohm)
            f_p_ff = 1.0 / (2.0 * math.pi * r_par * cff_f)

    return {
        "cout_uf": cout_uf,
        "esr_mohm": esr_mohm,
        "f_zero_esr_hz": f_zero_esr,
        "cff_pf": cff_pf,
        "f_z_ff_hz": f_z_ff,
        "f_p_ff_hz": f_p_ff
    }

def main():
    parser = argparse.ArgumentParser(description="LDO Linear Regulator Design, Stability & Thermal Calculator")
    parser.add_argument("--thermal", action="store_true", help="Calculate power dissipation and junction temperature")
    parser.add_argument("--vin", type=float, default=5.0, help="Input Voltage in Volts (e.g., 5.0, 3.3)")
    parser.add_argument("--vout", type=float, default=3.3, help="Output Voltage in Volts (e.g., 3.3, 1.8, 1.2)")
    parser.add_argument("--iload", type=float, default=0.5, help="Load Current in Amperes (e.g., 0.5, 1.0, 2.0)")
    parser.add_argument("--theta-ja", type=float, default=45.0, help="Thermal Resistance Junction-to-Ambient in C/W (e.g., 45.0 for SOT-223)")
    parser.add_argument("--ta", type=float, default=25.0, help="Ambient Temperature in Celsius (default: 25.0)")
    parser.add_argument("--iq", type=float, default=1.5, help="Quiescent Ground Current in mA (default: 1.5)")

    parser.add_argument("--feedback", action="store_true", help="Calculate standard feedback resistor divider network")
    parser.add_argument("--vref", type=float, default=1.2, help="Internal Reference Voltage in Volts (e.g., 1.2, 0.8, 0.5)")
    parser.add_argument("--max-r2", type=float, default=50.0, help="Max R2 value in kOhms to maintain low noise (default: 50k)")

    parser.add_argument("--stability", action="store_true", help="Calculate output capacitor ESR zero and Cff feedforward pole/zero")
    parser.add_argument("--cout", type=float, default=10.0, help="Output Capacitance in uF (e.g., 10.0, 22.0)")
    parser.add_argument("--esr", type=float, default=15.0, help="Output Capacitor ESR in mOhms (e.g., 15 for MLCC, 250 for Tantalum)")
    parser.add_argument("--cff", type=float, default=47.0, help="Feedforward Capacitor in pF (default: 47)")
    parser.add_argument("--r1", type=float, default=21.0, help="Feedback R1 in kOhms (default: 21.0)")
    parser.add_argument("--r2", type=float, default=12.0, help="Feedback R2 in kOhms (default: 12.0)")

    parser.add_argument("--compare", action="store_true", help="Compare NMOS vs PMOS pass element attributes for operating point")

    args = parser.parse_args()

    if args.feedback:
        if args.vout <= args.vref:
            print(f"Error: Target Vout ({args.vout}V) must be greater than Vref ({args.vref}V) for an adjustable LDO.")
            sys.exit(1)
        target_ratio = (args.vout / args.vref) - 1.0
        r1, r2, actual_ratio, err_pct = get_standard_e96_resistors(target_ratio, args.max_r2 * 1e3)
        actual_vout = args.vref * (1.0 + actual_ratio)
        divider_current_ua = (actual_vout / (r1 + r2)) * 1e6

        print("=" * 68)
        print(" LDO FEEDBACK RESISTOR NETWORK SIZING REPORT")
        print("=" * 68)
        print(f"Target Output Voltage (Vout)   : {args.vout:.3f} V")
        print(f"Reference Voltage (Vref)       : {args.vref:.3f} V")
        print(f"Ideal Ratio (R1 / R2)          : {target_ratio:.4f}")
        print("-" * 68)
        print(f"Standard E96 R1 (Top Resistor) : {r1/1e3:.2f} kΩ ({r1:,.0f} Ω)")
        print(f"Standard E96 R2 (Bottom Res.)  : {r2/1e3:.2f} kΩ ({r2:,.0f} Ω)")
        print(f"Actual Ratio (R1 / R2)         : {actual_ratio:.4f}")
        print(f"Actual Output Voltage (Vout)   : {actual_vout:.4f} V")
        print(f"Output Voltage Error           : {err_pct:.3f}%")
        print(f"Divider Bleed Current          : {divider_current_ua:.1f} µA")
        print(f"Total Feedback Resistance      : {(r1+r2)/1e3:.2f} kΩ")
        print("=" * 68)
        return

    if args.stability:
        stab = calculate_stability(args.cout, args.esr, args.cff, args.r1, args.r2)
        print("=" * 70)
        print(" LDO FREQUENCY COMPENSATION & ESR STABILITY REPORT")
        print("=" * 70)
        print(f"Output Capacitance (Cout)      : {stab['cout_uf']:.2f} µF")
        print(f"Capacitor ESR                  : {stab['esr_mohm']:.1f} mΩ ({stab['esr_mohm']/1000.0:.4f} Ω)")
        if stab['f_zero_esr_hz'] < float("inf"):
            print(f"ESR Zero Frequency (f_z_esr)   : {stab['f_zero_esr_hz']/1e3:.2f} kHz ({stab['f_zero_esr_hz']:,.0f} Hz)")
        else:
            print("ESR Zero Frequency (f_z_esr)   : None (0 mΩ ideal capacitor)")
        if stab['cff_pf'] > 0:
            print("-" * 70)
            print(f"Feedforward Capacitor (Cff)    : {stab['cff_pf']:.1f} pF")
            print(f"Feedback Resistors (R1, R2)    : R1 = {args.r1:.1f} kΩ, R2 = {args.r2:.1f} kΩ")
            print(f"Feedforward Zero (f_z_ff)      : {stab['f_z_ff_hz']/1e3:.2f} kHz (Provides phase boost)")
            print(f"Feedforward Pole (f_p_ff)      : {stab['f_p_ff_hz']/1e3:.2f} kHz")
        print("=" * 70)
        return

    if args.compare:
        print("=" * 74)
        print(" NMOS vs. PMOS PASS ELEMENT ARCHITECTURE BENCHMARK")
        print("=" * 74)
        print(f"Operating Conditions: Vin = {args.vin:.2f}V, Vout = {args.vout:.2f}V, Iload = {args.iload:.2f}A")
        vdrop = args.vin - args.vout
        print(f"Headroom Voltage (Vin - Vout): {vdrop:.3f} V")
        print("-" * 74)
        print("Attribute                 PMOS Pass Transistor      NMOS Pass Transistor")
        print("-" * 74)
        print("Circuit Configuration     Common-Source (CS)        Source-Follower (CD)")
        print("Gate Drive Required       Vgate < Vin (to Ground)   Vgate > Vout + Vgs (> Vin!)")
        print("Bias Rail Needed?         NO (Single Supply Vin)    YES (Vbias or Charge Pump)")
        print("Output Impedance (Rout)   HIGH (ro || Rload)        LOW (~1/gm)")
        print("Loop Stability Challenge  High (2 dominant poles)   Low (1 dominant pole)")
        print("MLCC Ceramic Cap Stable?  Requires ESR zero / comp  Inherent wide stability")
        print("Transient Step Response   Slower (Relies on EA)     Ultra-Fast (Local Vgs loop)")
        print("Reverse Current Path      Body Diode (Vout -> Vin)  Blocked if Vgate=0")
        print("Silicon Die Size (W/L)    Large (Lower hole mu)     Small (2-3x higher electron mu)")
        print("Ideal Application         Low-power portable sys    Ultra-low Vout core power")
        print("=" * 74)
        return

    # Default: Thermal calculation
    res = calculate_thermal(args.vin, args.vout, args.iload, args.theta_ja, args.ta, args.iq)
    print("=" * 70)
    print(" LDO THERMAL DISSIPATION & JUNCTION TEMPERATURE REPORT")
    print("=" * 70)
    print(f"Input Voltage (Vin)            : {args.vin:.3f} V")
    print(f"Output Voltage (Vout)          : {args.vout:.3f} V")
    print(f"Dropout / Voltage Drop (Vdrop) : {res['vdrop']:.3f} V")
    print(f"Load Current (Iload)           : {args.iload:.3f} A ({args.iload*1000.0:.1f} mA)")
    print(f"Quiescent Current (Iq)         : {args.iq:.2f} mA")
    print(f"Ambient Temperature (Ta)       : {args.ta:.1f} °C")
    print(f"Thermal Resistance (Theta-JA)  : {args.theta_ja:.1f} °C/W")
    print("-" * 70)
    print(f"Pass Element Power (P_pass)    : {res['p_pass_w']:.3f} W")
    print(f"Quiescent Power (P_iq)         : {res['p_iq_w']:.4f} W")
    print(f"Total Power Dissipated (P_d)   : {res['p_total_w']:.3f} W")
    print(f"Regulator Efficiency           : {res['efficiency_pct']:.2f}%")
    print(f"Temperature Rise (Delta T)     : +{res['delta_t_c']:.1f} °C")
    print(f"Calculated Junction Temp (Tj)  : {res['tj_c']:.1f} °C")
    print("-" * 70)
    if res['safe']:
        margin = 125.0 - res['tj_c']
        print(f"THERMAL STATUS                 : PASS (Tj < 125°C, Safety Margin: {margin:.1f}°C)")
    else:
        overshoot = res['tj_c'] - 125.0
        print(f"THERMAL STATUS                 : >>> THERMAL OVERLOAD <<< (Exceeds 125°C by {overshoot:.1f}°C)")
        print(f"Max Safe Theta-JA Needed       : {res['max_theta_ja']:.1f} °C/W (Heatsink or thermal vias required!)")
    print("=" * 70)

if __name__ == '__main__':
    main()
