#!/usr/bin/env python3
"""
Smart Programmable Power Supply (SPPS) Engineering Design Calculator
Universal AC Input (85-265V AC) -> 5-20V, 3A Programmable DC Output

Usage:
    python3 tools/psu_calc.py --flyback --vin-min 85 --vin-max 265 --vout 24 --iout 3.0 --fsw 65000
    python3 tools/psu_calc.py --snubber --vin-max 265 --vout 24 --turns-ratio 4.0 --leakage-ind 3.3e-6 --ipeak 3.45 --fsw 70000
    python3 tools/psu_calc.py --buckboost --vin 24 --vout-min 5.0 --vout-max 20.0 --iout 3.0 --fsw 250000
    python3 tools/psu_calc.py --feedback --vout-min 5.0 --vout-max 20.0 --vdac-max 3.3 --vref 1.20
    python3 tools/psu_calc.py --efficiency --vac 230 --iac 0.35 --pac 72.5 --vdc 20.0 --idc 3.0
"""

import argparse
import sys
import math
from typing import Dict, Tuple

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

def find_closest_e96(target_ohms: float) -> float:
    if target_ohms <= 0:
        return 1.0
    exponent = math.floor(math.log10(target_ohms))
    fraction = target_ohms / (10 ** exponent)
    closest = min(E96_VALUES, key=lambda x: abs(x - fraction))
    return closest * (10 ** exponent)

def calculate_flyback(vin_min: float, vin_max: float, vout: float, iout: float, fsw: float,
                      eff: float = 0.88, vr: float = 100.0, ae_mm2: float = 119.0, bmax_t: float = 0.28) -> Dict:
    vbulk_min = vin_min * math.sqrt(2) - 2.0 - 15.0  # AC min peak minus diode and ripple
    vbulk_max = vin_max * math.sqrt(2)
    pout = vout * iout
    pin = pout / eff

    # Duty cycle
    dmax = vr / (vr + vbulk_min)
    ipk = (2.0 * pin) / (vbulk_min * dmax)
    lp = (vbulk_min * dmax) / (ipk * fsw)

    # Turns ratio
    vsr = 0.10  # Synchronous rectifier drop
    n = vr / (vout + vsr)
    n_int = round(n)

    # Core parameters (PQ26/20 Ae in m^2)
    ae_m2 = ae_mm2 * 1e-6
    np_min = (lp * ipk) / (bmax_t * ae_m2)
    np = math.ceil(np_min / n_int) * n_int  # round to multiple of n
    if np < 24:
        np = 48
    ns = round(np / n_int)
    naux = round(ns * (16.0 + 0.7) / (vout + vsr))

    # Air gap (meters)
    mu_0 = 4.0 * math.pi * 1e-7
    lg_m = (mu_0 * (np ** 2) * ae_m2) / lp
    lg_mm = lg_m * 1000.0

    return {
        "pin_watts": pin,
        "pout_watts": pout,
        "vbulk_min": vbulk_min,
        "vbulk_max": vbulk_max,
        "dmax_pct": dmax * 100.0,
        "ipk_amps": ipk,
        "lp_uh": lp * 1e6,
        "turns_ratio": n_int,
        "np_turns": np,
        "ns_turns": ns,
        "naux_turns": naux,
        "air_gap_mm": lg_mm,
        "vds_max": vbulk_max + (n_int * (vout + vsr)) + 80.0
    }

def calculate_snubber(vin_max: float, vout: float, turns_ratio: float, leakage_ind: float,
                      ipeak: float, fsw: float, vsnub_target: float = 180.0) -> Dict:
    vbulk_max = vin_max * math.sqrt(2)
    vsr = 0.10
    v_reflect = turns_ratio * (vout + vsr)
    e_leak = 0.5 * leakage_ind * (ipeak ** 2)
    p_snub = e_leak * fsw * (vsnub_target / (vsnub_target - v_reflect))
    r_snub = (vsnub_target ** 2) / p_snub
    c_snub = vsnub_target / (0.10 * vsnub_target * r_snub * fsw)

    r_snub_std = find_closest_e96(r_snub)

    return {
        "v_reflect": v_reflect,
        "e_leak_uj": e_leak * 1e6,
        "p_snub_watts": p_snub,
        "r_snub_calc_kohm": r_snub / 1000.0,
        "r_snub_std_kohm": r_snub_std / 1000.0,
        "c_snub_calc_nf": c_snub * 1e9,
        "c_snub_std_nf": 2.2,
        "total_fet_vds_stress": vbulk_max + vsnub_target
    }

def calculate_buckboost(vin: float, vout_min: float, vout_max: float, iout: float,
                        fsw: float, ripple_ratio: float = 0.30) -> Dict:
    delta_il = ripple_ratio * iout

    # Inductor sizing evaluated at 12V output (worst-case buck duty cycle)
    l_buck = (12.0 * (vin - 12.0)) / (delta_il * fsw * vin)

    # Peak current at max output (20V/3A in transition mode)
    d_max = vout_max / (vin + vout_max)
    iin_max = (vout_max * iout) / (vin * 0.95)
    il_peak = iin_max + iout + (delta_il / 2.0)
    il_rms = math.sqrt(iout**2 + (delta_il**2)/12.0)

    # Minimum Cout for < 25mV ripple
    target_ripple_v = 0.025
    cout_min = delta_il / (8.0 * fsw * target_ripple_v)
    max_esr_mohm = (0.015 / delta_il) * 1000.0

    return {
        "delta_il_amps": delta_il,
        "l_calc_uh": l_buck * 1e6,
        "l_recommended_uh": 10.0,
        "il_peak_amps": il_peak,
        "il_rms_amps": il_rms,
        "cout_min_uf": cout_min * 1e6,
        "cout_recommended_uf": 88.0,  # 4x 22uF MLCC
        "max_esr_mohm": max_esr_mohm
    }

def calculate_feedback(vout_min: float, vout_max: float, vdac_max: float = 3.3, vref: float = 1.20) -> Dict:
    # Target K_DAC = (Vout_max - Vout_min) / Vdac_max
    k_dac = (vout_max - vout_min) / vdac_max
    r_top = 49.9e3  # standard precision 0.1%

    r_dac_ideal = r_top / k_dac
    r_dac_std = find_closest_e96(r_dac_ideal)

    # Now solve for R_bot from Vout_max = Vref * (1 + R_top/R_bot + R_top/R_dac)
    # (Vout_max / Vref) - 1 - (R_top / R_dac) = R_top / R_bot
    bracket = (vout_max / vref) - 1.0 - (r_top / r_dac_std)
    r_bot_ideal = r_top / bracket
    r_bot_std = find_closest_e96(r_bot_ideal)

    # Compute actual endpoints with standard resistors
    vout_actual_max = vref * (1.0 + (r_top / r_bot_std) + (r_top / r_dac_std))
    vout_actual_min = vout_actual_max - (vdac_max * (r_top / r_dac_std))
    step_mv = ((vout_actual_max - vout_actual_min) / 4096.0) * 1000.0

    return {
        "k_dac_gain": k_dac,
        "r_top_kohm": r_top / 1000.0,
        "r_dac_kohm": r_dac_std / 1000.0,
        "r_bot_kohm": r_bot_std / 1000.0,
        "vout_actual_max": vout_actual_max,
        "vout_actual_min": vout_actual_min,
        "dac_12bit_step_mv": step_mv
    }

def calculate_efficiency(vac: float, iac: float, pac: float, vdc: float, idc: float) -> Dict:
    pdc = vdc * idc
    s_apparent = vac * iac
    pf = pac / s_apparent if s_apparent > 0 else 0.0
    eff = (pdc / pac) * 100.0 if pac > 0 else 0.0
    loss = pac - pdc

    return {
        "pac_watts": pac,
        "pdc_watts": pdc,
        "loss_watts": loss,
        "apparent_power_va": s_apparent,
        "power_factor": pf,
        "efficiency_pct": eff
    }

def main():
    parser = argparse.ArgumentParser(
        description="Smart Programmable Power Supply (SPPS) Engineering Design Calculator"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--flyback", action="store_true", help="Size QR Flyback transformer and primary parameters")
    group.add_argument("--snubber", action="store_true", help="Calculate primary RCD clamp snubber parameters")
    group.add_argument("--buckboost", action="store_true", help="Size 4-switch Buck-Boost inductor and capacitors")
    group.add_argument("--feedback", action="store_true", help="Calculate DAC summing feedback resistor network")
    group.add_argument("--efficiency", action="store_true", help="Compute real-time conversion efficiency and power factor")

    # Flyback args
    parser.add_argument("--vin-min", type=float, default=85.0, help="Min AC input voltage RMS (V)")
    parser.add_argument("--vin-max", type=float, default=265.0, help="Max AC input voltage RMS (V)")
    parser.add_argument("--vout", type=float, default=24.0, help="Output voltage (V)")
    parser.add_argument("--iout", type=float, default=3.0, help="Output current (A)")
    parser.add_argument("--fsw", type=float, default=65000.0, help="Switching frequency (Hz)")

    # Snubber args
    parser.add_argument("--turns-ratio", type=float, default=4.0, help="Transformer primary-to-secondary turns ratio")
    parser.add_argument("--leakage-ind", type=float, default=3.3e-6, help="Primary leakage inductance (H)")
    parser.add_argument("--ipeak", type=float, default=3.45, help="Primary peak current (A)")

    # Buck-Boost args
    parser.add_argument("--vin", type=float, default=24.0, help="Intermediate DC bus voltage (V)")
    parser.add_argument("--vout-min", type=float, default=5.0, help="Min programmable output voltage (V)")
    parser.add_argument("--vout-max", type=float, default=20.0, help="Max programmable output voltage (V)")

    # Feedback args
    parser.add_argument("--vdac-max", type=float, default=3.3, help="Max DAC output voltage (V)")
    parser.add_argument("--vref", type=float, default=1.20, help="Controller reference voltage (V)")

    # Efficiency args
    parser.add_argument("--vac", type=float, default=230.0, help="AC input voltage RMS (V)")
    parser.add_argument("--iac", type=float, default=0.35, help="AC input current RMS (A)")
    parser.add_argument("--pac", type=float, default=72.5, help="Real active AC input power (W)")
    parser.add_argument("--vdc", type=float, default=20.0, help="DC output voltage (V)")
    parser.add_argument("--idc", type=float, default=3.0, help="DC output current (A)")

    args = parser.parse_args()

    if args.flyback:
        res = calculate_flyback(args.vin_min, args.vin_max, args.vout, args.iout, args.fsw)
        print("\n========================================================")
        print("   QUASI-RESONANT FLYBACK TRANSFORMER DESIGN (PQ26/20)   ")
        print("========================================================")
        print(f"Output Power:           {res['pout_watts']:.1f} W")
        print(f"Input Power (88% eff):  {res['pin_watts']:.1f} W")
        print(f"Min DC Bulk Voltage:    {res['vbulk_min']:.1f} V (at {args.vin_min}V AC)")
        print(f"Max DC Bulk Voltage:    {res['vbulk_max']:.1f} V (at {args.vin_max}V AC)")
        print(f"Max Duty Cycle (Dmax):  {res['dmax_pct']:.1f} %")
        print(f"Primary Peak Current:   {res['ipk_amps']:.2f} A")
        print(f"Primary Inductance (Lp):{res['lp_uh']:.1f} µH")
        print(f"Turns Ratio (Np/Ns):    {res['turns_ratio']:.1f} : 1")
        print(f"Primary Turns (Np):     {res['np_turns']} Turns (Sandwich layer)")
        print(f"Secondary Turns (Ns):   {res['ns_turns']} Turns (Litz wire)")
        print(f"Auxiliary Turns (Naux): {res['naux_turns']} Turns (+16V VCC)")
        print(f"Transformer Air Gap:    {res['air_gap_mm']:.2f} mm")
        print(f"Max MOSFET Vds Stress:  {res['vds_max']:.1f} V (800V FET selected)")
        print("========================================================\n")

    elif args.snubber:
        res = calculate_snubber(args.vin_max, args.vout, args.turns_ratio, args.leakage_ind, args.ipeak, args.fsw)
        print("\n========================================================")
        print("          PRIMARY RCD CLAMP SNUBBER SIZING              ")
        print("========================================================")
        print(f"Reflected Voltage (VR): {res['v_reflect']:.1f} V")
        print(f"Leakage Energy/Cycle:   {res['e_leak_uj']:.2f} µJ")
        print(f"Snubber Dissipation:    {res['p_snub_watts']:.2f} W")
        print(f"Calculated R_snub:      {res['r_snub_calc_kohm']:.1f} kΩ")
        print(f"Recommended R_snub:     {res['r_snub_std_kohm']:.1f} kΩ (2x 100kΩ/2W in parallel)")
        print(f"Recommended C_snub:     {res['c_snub_std_nf']:.1f} nF / 1kV Ceramic")
        print(f"Total Clamped Vds Peak: {res['total_fet_vds_stress']:.1f} V")
        print("========================================================\n")

    elif args.buckboost:
        res = calculate_buckboost(args.vin, args.vout_min, args.vout_max, args.iout, args.fsw)
        print("\n========================================================")
        print("      4-SWITCH SYNCHRONOUS BUCK-BOOST SIZING            ")
        print("========================================================")
        print(f"Target Ripple Current:  {res['delta_il_amps']:.2f} A (30% of Iout)")
        print(f"Calculated Inductance:  {res['l_calc_uh']:.1f} µH")
        print(f"Recommended Inductor:   {res['l_recommended_uh']:.1f} µH / 8.5A Flat-Wire (WE 7443321000)")
        print(f"Peak Inductor Current:  {res['il_peak_amps']:.2f} A")
        print(f"RMS Inductor Current:   {res['il_rms_amps']:.2f} A")
        print(f"Min Output Capacitance: {res['cout_min_uf']:.1f} µF")
        print(f"Recommended Cap Bank:   {res['cout_recommended_uf']:.1f} µF (4x 22µF MLCC + 100µF Polymer)")
        print(f"Max Allowable ESR:      {res['max_esr_mohm']:.1f} mΩ")
        print("========================================================\n")

    elif args.feedback:
        res = calculate_feedback(args.vout_min, args.vout_max, args.vdac_max, args.vref)
        print("\n========================================================")
        print("      DAC FEEDBACK SUMMING NETWORK RESISTOR SIZING      ")
        print("========================================================")
        print(f"Top Resistor (R_top):   {res['r_top_kohm']:.1f} kΩ (0.1% precision)")
        print(f"DAC Resistor (R_DAC):   {res['r_dac_kohm']:.1f} kΩ (0.1% precision)")
        print(f"Bottom Resistor (R_bot):{res['r_bot_kohm']:.2f} kΩ (0.1% precision)")
        print(f"Actual Max Vout (0.0V): {res['vout_actual_max']:.2f} V")
        print(f"Actual Min Vout (3.3V): {res['vout_actual_min']:.2f} V")
        print(f"12-Bit DAC Resolution:  {res['dac_12bit_step_mv']:.2f} mV / LSB (Exceeds 10mV target)")
        print("========================================================\n")

    elif args.efficiency:
        res = calculate_efficiency(args.vac, args.iac, args.pac, args.vdc, args.idc)
        print("\n========================================================")
        print("       DUAL-DOMAIN POWER & REAL-TIME EFFICIENCY         ")
        print("========================================================")
        print(f"AC Input Power:         {res['pac_watts']:.2f} W (Apparent: {res['apparent_power_va']:.2f} VA)")
        print(f"AC Power Factor:        {res['power_factor']:.2f}")
        print(f"DC Output Power:        {res['pdc_watts']:.2f} W ({args.vdc}V @ {args.idc}A)")
        print(f"Total System Losses:    {res['loss_watts']:.2f} W (Thermal dissipation)")
        print(f"Conversion Efficiency:  {res['efficiency_pct']:.2f} %")
        print("========================================================\n")

if __name__ == "__main__":
    main()
