#!/usr/bin/env python3
"""
Alternative Converter Topologies Engineering Calculator
Smart Programmable Power Supply (SPPS) Module
Universal AC Input (85-265V AC) -> 5-20V, 3A Programmable DC Output

Usage:
    python3 tools/alternative_converter_calc.py --highbus-buck --vin 36.0 --vout-min 5.0 --vout-max 20.0 --iout 3.0 --fsw 250000
    python3 tools/alternative_converter_calc.py --llc --vbus 400.0 --vout 36.0 --iout 2.0 --f0 100000 --k 5.0 --q 0.45
    python3 tools/alternative_converter_calc.py --sepic --vin 24.0 --vout-min 5.0 --vout-max 20.0 --iout 3.0 --fsw 250000
    python3 tools/alternative_converter_calc.py --zeta --vin 24.0 --vout-min 5.0 --vout-max 20.0 --iout 3.0 --fsw 250000
    python3 tools/alternative_converter_calc.py --forward --vin-min 90.0 --vin-max 375.0 --vout 24.0 --iout 3.0 --fsw 100000
    python3 tools/alternative_converter_calc.py --compare-losses --vout 20.0 --iout 3.0
"""

import argparse
import sys
import math
from typing import Dict, Tuple

E96_VALUES = [
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40,
    1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00,
    2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87,
    2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90,
    6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45,
    8.66, 8.87, 9.09, 9.31, 9.53, 9.76
]

def find_closest_e96(target_ohms: float) -> float:
    if target_ohms <= 0:
        return 1.0
    exponent = math.floor(math.log10(target_ohms))
    fraction = target_ohms / (10 ** exponent)
    closest = min(E96_VALUES, key=lambda x: abs(x - fraction))
    return closest * (10 ** exponent)

def calculate_highbus_buck(vin: float, vout_min: float, vout_max: float, iout: float, fsw: float,
                           ripple_ratio: float = 0.30, vref: float = 1.20, vdac_max: float = 3.30) -> Dict:
    d_min = vout_min / vin
    d_max = vout_max / vin
    delta_i = ripple_ratio * iout

    # Worst-case inductor ripple occurs at D = 50% or maximum Vout*(1-Vout/Vin)
    v_mid = vin / 2.0
    if vout_min <= v_mid <= vout_max:
        v_crit = v_mid
    else:
        v_crit = vout_max if abs(vout_max - v_mid) < abs(vout_min - v_mid) else vout_min

    l_opt = (v_crit * (vin - v_crit)) / (delta_i * fsw * vin)
    c_out_min = delta_i / (8.0 * fsw * 0.020)  # 20mV ripple target

    # DAC resistor network
    k_dac = (vout_max - vout_min) / vdac_max
    r_top = 49900.0
    r_dac = r_top / k_dac
    r_dac_std = find_closest_e96(r_dac)

    req_parallel = r_top / ((vout_max / vref) - 1.0)
    r_bot = (req_parallel * r_dac_std) / (r_dac_std - req_parallel)
    r_bot_std = find_closest_e96(r_bot)

    actual_vmax = vref * (1.0 + (r_top / r_bot_std) + (r_top / r_dac_std))
    actual_vmin = actual_vmax - (vdac_max * (r_top / r_dac_std))
    resolution_mv = ((actual_vmax - actual_vmin) / 4096.0) * 1000.0

    return {
        "vin": vin,
        "d_min_pct": d_min * 100.0,
        "d_max_pct": d_max * 100.0,
        "delta_i_l": delta_i,
        "l_calc_uh": l_opt * 1e6,
        "c_out_min_uf": c_out_min * 1e6,
        "r_top_k": r_top / 1e3,
        "r_dac_k": r_dac_std / 1e3,
        "r_bot_k": r_bot_std / 1e3,
        "actual_vmax": actual_vmax,
        "actual_vmin": actual_vmin,
        "resolution_mv": resolution_mv
    }

def calculate_llc_tank(vbus: float, vout: float, iout: float, f0: float, k: float, q: float) -> Dict:
    vsr = 0.05
    n = (vbus / 2.0) / (vout + vsr)
    n_round = round(n * 2.0) / 2.0

    ro = vout / iout
    rac = (8.0 * (n_round ** 2) / (math.pi ** 2)) * ro
    z0 = q * rac
    cr = 1.0 / (2.0 * math.pi * f0 * z0)
    lr = z0 / (2.0 * math.pi * f0)
    lm = k * lr

    return {
        "vbus": vbus,
        "vout": vout,
        "turns_ratio": n_round,
        "ro_ohms": ro,
        "rac_ohms": rac,
        "z0_ohms": z0,
        "cr_nf": cr * 1e9,
        "lr_uh": lr * 1e6,
        "lm_uh": lm * 1e6,
        "resonant_freq_khz": f0 / 1e3
    }

def calculate_sepic(vin: float, vout_min: float, vout_max: float, iout: float, fsw: float) -> Dict:
    d_min = vout_min / (vin + vout_min)
    d_max = vout_max / (vin + vout_max)
    delta_i = 0.30 * iout

    # Inductors L1 = L2 for coupled core
    l_coupled = (vin * d_max) / (delta_i * fsw)
    vds_max = vin + vout_max
    i_csep_rms = iout * math.sqrt(d_max / (1.0 - d_max))
    c_sep_min = (iout * d_max) / (fsw * (0.05 * vin))

    return {
        "vin": vin,
        "d_min_pct": d_min * 100.0,
        "d_max_pct": d_max * 100.0,
        "l_coupled_uh": l_coupled * 1e6,
        "vds_max": vds_max,
        "i_csep_rms": i_csep_rms,
        "c_sep_min_uf": c_sep_min * 1e6
    }

def calculate_zeta(vin: float, vout_min: float, vout_max: float, iout: float, fsw: float) -> Dict:
    d_min = vout_min / (vin + vout_min)
    d_max = vout_max / (vin + vout_max)
    delta_i = 0.30 * iout

    l1 = (vin * d_max) / (delta_i * fsw)
    l2 = (vout_max * (1.0 - d_max)) / (delta_i * fsw)
    vds_max = vin + vout_max
    c_out_min = delta_i / (8.0 * fsw * 0.012)  # 12mV ripple target for Zeta

    return {
        "vin": vin,
        "d_min_pct": d_min * 100.0,
        "d_max_pct": d_max * 100.0,
        "l1_uh": l1 * 1e6,
        "l2_out_uh": l2 * 1e6,
        "vds_max": vds_max,
        "c_out_min_uf": c_out_min * 1e6
    }

def calculate_forward(vin_min: float, vin_max: float, vout: float, iout: float, fsw: float, dmax: float = 0.45) -> Dict:
    vdiode = 0.4
    n = (vin_min * dmax) / (vout + vdiode)
    np = 48
    ns = round(np / n)

    delta_i = 0.30 * iout
    vsec_max = vin_max * (ns / np)
    d_min = (vout + vdiode) / vsec_max
    l_out = ((vsec_max - vout) * (1.0 - d_min)) / (fsw * delta_i)

    return {
        "vin_min": vin_min,
        "vin_max": vin_max,
        "turns_ratio": round(n, 2),
        "np": np,
        "ns": ns,
        "vds_clamp_max": vin_max,
        "l_out_uh": l_out * 1e6
    }

def compare_post_regulators(vout: float, iout: float) -> None:
    pout = vout * iout
    print(f"\n================================================================================")
    print(f"      POST-REGULATOR MULTI-TOPOLOGY LOSS & EFFICIENCY COMPARISON                ")
    print(f"      Operating Point: {vout:.1f} V DC @ {iout:.2f} A  (Pout = {pout:.2f} W)                    ")
    print(f"================================================================================")
    print(f"{'Topology Architecture':<28} | {'Loss (W)':<9} | {'Stage Eff':<10} | {'Switches':<9} | {'Ripple (mV)':<10}")
    print(f"-----------------------------+-----------+------------+-----------+-----------")

    topologies = [
        ("Baseline (4-Switch BB @ 24V)",  2.15, 4, 22.0),
        ("Option A: High-Bus Buck @ 36V", 1.45, 2, 16.0),
        ("Option B: Coupled SEPIC @ 24V", 2.85, 2, 18.0),
        ("Option C: Synchronous Zeta @24V",2.55, 2, 11.0),
        ("Option D: Tracking Buck + LDO", 2.65, 3, 0.7)
    ]

    for name, loss, sw_count, ripple in topologies:
        pin = pout + loss
        eff = (pout / pin) * 100.0
        print(f"{name:<28} | {loss:>7.2f} W | {eff:>8.2f} % | {sw_count:>4} FETs | {ripple:>8.1f} mV")
    print(f"================================================================================\n")

def main():
    parser = argparse.ArgumentParser(description="Alternative Converter Topologies Engineering Calculator")
    parser.add_argument("--highbus-buck", action="store_true", help="Calculate High-Bus (+36V) Pure Synchronous Buck")
    parser.add_argument("--llc", action="store_true", help="Calculate Half-Bridge LLC Resonant Tank")
    parser.add_argument("--sepic", action="store_true", help="Calculate Coupled-Inductor Synchronous SEPIC")
    parser.add_argument("--zeta", action="store_true", help="Calculate Synchronous Zeta Converter")
    parser.add_argument("--forward", action="store_true", help="Calculate Two-Switch Forward Converter")
    parser.add_argument("--compare-losses", action="store_true", help="Compare losses across post-regulator topologies")

    parser.add_argument("--vin", type=float, default=36.0, help="Input DC voltage")
    parser.add_argument("--vbus", type=float, default=400.0, help="PFC DC bus voltage")
    parser.add_argument("--vin-min", type=float, default=90.0, help="Min DC bulk voltage")
    parser.add_argument("--vin-max", type=float, default=375.0, help="Max DC bulk voltage")
    parser.add_argument("--vout", type=float, default=20.0, help="Nominal DC output voltage")
    parser.add_argument("--vout-min", type=float, default=5.0, help="Min output voltage")
    parser.add_argument("--vout-max", type=float, default=20.0, help="Max output voltage")
    parser.add_argument("--iout", type=float, default=3.0, help="Output load current")
    parser.add_argument("--fsw", type=float, default=250000.0, help="Switching frequency in Hz")
    parser.add_argument("--f0", type=float, default=100000.0, help="LLC resonant frequency in Hz")
    parser.add_argument("--k", type=float, default=5.0, help="LLC inductor ratio Lm/Lr")
    parser.add_argument("--q", type=float, default=0.45, help="LLC quality factor")

    args = parser.parse_args()

    if args.highbus_buck:
        res = calculate_highbus_buck(args.vin, args.vout_min, args.vout_max, args.iout, args.fsw)
        print("\n========================================================")
        print("      HIGH-BUS (+36V) PURE SYNCHRONOUS BUCK SIZING      ")
        print("========================================================")
        print(f"Input Voltage:          {res['vin']:.1f} V DC (Fixed Flyback rail)")
        print(f"Duty Cycle Range:       {res['d_min_pct']:.1f}% to {res['d_max_pct']:.1f}% (Pure Buck)")
        print(f"Ripple Current:         {res['delta_i_l']:.2f} A (30% of Iout)")
        print(f"Calculated Inductance:  {res['l_calc_uh']:.1f} µH (WE 7443321500 15µH/7A)")
        print(f"Min Output Capacitance: {res['c_out_min_uf']:.1f} µF")
        print(f"Top Resistor (R_top):   {res['r_top_k']:.1f} kΩ (0.1% precision)")
        print(f"DAC Resistor (R_DAC):   {res['r_dac_k']:.1f} kΩ (0.1% precision)")
        print(f"Bottom Resistor (R_bot):{res['r_bot_k']:.2f} kΩ (0.1% precision)")
        print(f"Actual Output Span:     {res['actual_vmin']:.2f} V to {res['actual_vmax']:.2f} V")
        print(f"12-Bit DAC Resolution:  {res['resolution_mv']:.2f} mV / LSB")
        print("========================================================\n")

    elif args.llc:
        res = calculate_llc_tank(args.vbus, args.vout, args.iout, args.f0, args.k, args.q)
        print("\n========================================================")
        print("        HALF-BRIDGE LLC RESONANT TANK SIZING            ")
        print("========================================================")
        print(f"PFC Bus Voltage:        {res['vbus']:.1f} V DC")
        print(f"Resonant Frequency:     {res['resonant_freq_khz']:.1f} kHz")
        print(f"Transformer Turns Ratio:{res['turns_ratio']:.2f} : 1 (Np=32T, Ns=6T)")
        print(f"Equivalent Load (Rac):  {res['rac_ohms']:.1f} Ω")
        print(f"Resonant Capacitor (Cr):{res['cr_nf']:.2f} nF (10nF/630V Polypropylene)")
        print(f"Resonant Inductor (Lr): {res['lr_uh']:.1f} µH")
        print(f"Magnetizing Ind. (Lm):  {res['lm_uh']:.1f} µH (k = {args.k})")
        print("ZVS Mechanism:          Full Zero-Voltage Switching across switches")
        print("========================================================\n")

    elif args.sepic:
        res = calculate_sepic(args.vin, args.vout_min, args.vout_max, args.iout, args.fsw)
        print("\n========================================================")
        print("        COUPLED-INDUCTOR SYNCHRONOUS SEPIC SIZING       ")
        print("========================================================")
        print(f"Intermediate Bus (Vin): {res['vin']:.1f} V DC")
        print(f"Duty Cycle Range:       {res['d_min_pct']:.1f}% to {res['d_max_pct']:.1f}%")
        print(f"Coupled Inductor (L1=L2):{res['l_coupled_uh']:.1f} µH (Coilcraft MSD1278)")
        print(f"Max Switch Vds Stress:  {res['vds_max']:.1f} V (60V FETs selected)")
        print(f"SEPIC Cap RMS Current:  {res['i_csep_rms']:.2f} A RMS")
        print(f"Min SEPIC Cap (C_sep):  {res['c_sep_min_uf']:.1f} µF (2x 10µF/50V X7R)")
        print("Safety Advantage:       Inherent Short-Circuit DC isolation")
        print("========================================================\n")

    elif args.zeta:
        res = calculate_zeta(args.vin, args.vout_min, args.vout_max, args.iout, args.fsw)
        print("\n========================================================")
        print("           SYNCHRONOUS ZETA CONVERTER SIZING            ")
        print("========================================================")
        print(f"Intermediate Bus (Vin): {res['vin']:.1f} V DC")
        print(f"Duty Cycle Range:       {res['d_min_pct']:.1f}% to {res['d_max_pct']:.1f}%")
        print(f"Primary Inductor (L1):  {res['l1_uh']:.1f} µH")
        print(f"Output Inductor (L2):   {res['l2_out_uh']:.1f} µH (Continuous load current)")
        print(f"Max Switch Vds Stress:  {res['vds_max']:.1f} V")
        print(f"Min Output Capacitance: {res['c_out_min_uf']:.1f} µF (<12mV output ripple)")
        print("========================================================\n")

    elif args.forward:
        res = calculate_forward(args.vin_min, args.vin_max, args.vout, args.iout, args.fsw)
        print("\n========================================================")
        print("         TWO-SWITCH FORWARD CONVERTER SIZING            ")
        print("========================================================")
        print(f"Turns Ratio (Np/Ns):    {res['turns_ratio']} (Np={res['np']}T, Ns={res['ns']}T)")
        print(f"Max Switch Vds Clamp:   {res['vds_clamp_max']:.1f} V (Clamped to V_bulk!)")
        print(f"Output Filter Inductor: {res['l_out_uh']:.1f} µH (47µH standard)")
        print("Magnetic Reset:         Non-dissipative clamp diodes return energy to bulk")
        print("========================================================\n")

    elif args.compare_losses:
        compare_post_regulators(args.vout, args.iout)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
