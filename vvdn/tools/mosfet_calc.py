#!/usr/bin/env python3
"""
MOSFET Power Loss, Thermal Design, Gate Drive & Diode Recovery Calculator
Usage:
    python3 tools/mosfet_calc.py --loss --vds <V> --id <A> --rdson <Ohm> --trise <s|ns> --tfall <s|ns> --fsw <Hz|kHz> --vgs <V> --qg <C|nC> [--coss <pF>] [--theta-ja <C/W>] [--ta <C>]
    python3 tools/mosfet_calc.py --gate --vdrv <V> --vplat <V> --qgd <C|nC> [--target-dt <ns>] [--idriver-max <A>]
    python3 tools/mosfet_calc.py --diode --vds <V> --iload <A> --vsd <V> --tdead <ns> --qrr <nC> --fsw <Hz|kHz>
    python3 tools/mosfet_calc.py --compare --vds <V> --id <A> --fsw <kHz>
"""

import argparse
import sys
import math
from typing import Dict

def parse_engineering_value(val_str: str) -> float:
    """Parse string with engineering units like 150k, 25n, 100u, 10m."""
    val_str = str(val_str).strip().lower()
    multipliers = {
        'g': 1e9,
        'm': 1e6,  # Caution: if 'm' is after digit or followed by hz/etc
        'k': 1e3,
        'u': 1e-6,
        'n': 1e-9,
        'p': 1e-12
    }
    # Special handling for common unit suffixes
    for suffix in ['hz', 's', 'c', 'v', 'a', 'ohm', 'f']:
        if val_str.endswith(suffix):
            val_str = val_str[:-len(suffix)]

    # Check for milli 'm' vs mega 'meg'/'m'
    if val_str.endswith('m'):
        return float(val_str[:-1]) * 1e-3
    for prefix, mult in [('meg', 1e6), ('k', 1e3), ('u', 1e-6), ('n', 1e-9), ('p', 1e-12)]:
        if val_str.endswith(prefix):
            return float(val_str[:-len(prefix)]) * mult

    return float(val_str)


def calculate_loss(
    vds: float,
    id_rms: float,
    rdson_25: float,
    trise: float,
    tfall: float,
    fsw: float,
    vgs_drv: float,
    qg: float,
    coss: float = 0.0,
    theta_ja: float = 40.0,
    ta: float = 25.0,
    temp_coeff_pct: float = 0.5,
    tj_est: float = 100.0
) -> Dict:
    """
    Calculate conduction, switching, gate drive, Coss losses and junction temperature.
    Iteratively solves for Tj considering positive temperature coefficient of Rdson.
    """
    # Iterative solver for junction temperature
    tj = tj_est
    for _ in range(15):
        # Rdson derating with temperature: Rdson(Tj) = Rdson(25) * (1 + alpha * (Tj - 25))
        rdson_tj = rdson_25 * (1.0 + (temp_coeff_pct / 100.0) * max(0.0, tj - 25.0))
        
        # Conduction loss
        p_cond = (id_rms ** 2) * rdson_tj
        
        # Switching loss: Psw = 0.5 * Vds * Id * (trise + tfall) * fsw
        p_sw = 0.5 * vds * id_rms * (trise + tfall) * fsw
        
        # Gate drive loss: Pgate = Qg * Vgs * fsw
        p_gate = qg * vgs_drv * fsw
        
        # Output capacitance loss: Pcoss = 0.5 * Coss * Vds^2 * fsw
        p_coss = 0.5 * coss * (vds ** 2) * fsw
        
        p_total = p_cond + p_sw + p_gate + p_coss
        tj_next = ta + p_total * theta_ja
        
        if abs(tj_next - tj) < 0.05:
            tj = tj_next
            break
        tj = 0.5 * (tj + tj_next)

    tj_max = 150.0  # Standard Silicon limit
    thermal_margin = tj_max - tj

    return {
        "vds": vds,
        "id_rms": id_rms,
        "fsw": fsw,
        "rdson_25": rdson_25,
        "rdson_tj": rdson_tj,
        "p_cond": p_cond,
        "p_sw": p_sw,
        "p_gate": p_gate,
        "p_coss": p_coss,
        "p_total": p_total,
        "tj": tj,
        "ta": ta,
        "theta_ja": theta_ja,
        "margin": thermal_margin,
        "safe": tj < tj_max
    }


def calculate_gate_drive(
    vdrv: float,
    vplat: float,
    qgd: float,
    target_dt: float = 30e-9,
    idriver_max: float = 2.0,
    r_driver_internal: float = 1.5
) -> Dict:
    """
    Size series gate resistor for Miller plateau switching duration and peak driver current limit.
    """
    # In the Miller plateau: Imiller = (Vdrv - Vplat) / (Rgate + Rdriver)
    # Required Miller current to meet target switching duration:
    i_miller_req = qgd / target_dt
    
    # Required total gate loop resistance for target switching duration:
    r_total_target = (vdrv - vplat) / i_miller_req
    r_gate_target = max(0.0, r_total_target - r_driver_internal)
    
    # Minimum gate resistor to protect driver from exceeding peak current limit:
    # Ipeak = Vdrv / (Rgate + Rdriver) <= Idriver_max
    r_total_min_current = vdrv / idriver_max
    r_gate_min_current = max(0.0, r_total_min_current - r_driver_internal)
    
    # Recommended resistor is max of target speed and driver protection limit
    r_gate_recommended = max(r_gate_target, r_gate_min_current)
    actual_r_total = r_gate_recommended + r_driver_internal
    actual_i_peak = vdrv / actual_r_total
    actual_i_miller = (vdrv - vplat) / actual_r_total
    actual_dt = qgd / actual_i_miller if actual_i_miller > 0 else float("inf")
    
    return {
        "vdrv": vdrv,
        "vplat": vplat,
        "qgd": qgd,
        "target_dt": target_dt,
        "idriver_max": idriver_max,
        "r_driver_internal": r_driver_internal,
        "r_gate_recommended": r_gate_recommended,
        "actual_i_peak": actual_i_peak,
        "actual_dt": actual_dt
    }


def calculate_diode_loss(
    vds: float,
    iload: float,
    vsd: float,
    tdead: float,
    qrr: float,
    fsw: float
) -> Dict:
    """
    Calculate body diode dead-time conduction and reverse recovery losses.
    """
    # Conduction loss during dead time: Pdiode_cond = Vsd * Iload * 2 * tdead * fsw (both turn-on and turn-off)
    p_diode_cond = vsd * iload * 2.0 * tdead * fsw
    
    # Reverse recovery loss: Prr = Qrr * Vds * fsw
    p_rr = qrr * vds * fsw
    
    p_total_diode = p_diode_cond + p_rr
    
    return {
        "vds": vds,
        "iload": iload,
        "vsd": vsd,
        "tdead": tdead,
        "qrr": qrr,
        "fsw": fsw,
        "p_diode_cond": p_diode_cond,
        "p_rr": p_rr,
        "p_total_diode": p_total_diode
    }


def print_loss_report(res: Dict):
    print("\n" + "=" * 65)
    print("        MOSFET POWER LOSS & THERMAL SIZING REPORT")
    print("=" * 65)
    print(f" Operating Bus Voltage (Vds):       {res['vds']:.1f} V")
    print(f" RMS Load Current (Id):             {res['id_rms']:.2f} A")
    print(f" Switching Frequency (fsw):         {res['fsw'] / 1e3:.1f} kHz")
    print("-" * 65)
    print(f" Static Rdson (@25°C):              {res['rdson_25'] * 1e3:.2f} mΩ")
    print(f" Thermal Rdson (@Tj={res['tj']:.1f}°C):       {res['rdson_tj'] * 1e3:.2f} mΩ  (+{((res['rdson_tj']/res['rdson_25'])-1)*100:.1f}%)")
    print("-" * 65)
    print(" POWER DISSIPATION BREAKDOWN:")
    print(f"   • Conduction Loss (Pcond):       {res['p_cond']:.3f} W  ({res['p_cond']/res['p_total']*100:.1f}%)")
    print(f"   • Switching Loss (Psw):          {res['p_sw']:.3f} W  ({res['p_sw']/res['p_total']*100:.1f}%)")
    print(f"   • Gate Drive Loss (Pgate):       {res['p_gate']:.3f} W  ({res['p_gate']/res['p_total']*100:.1f}%)")
    print(f"   • Coss Stored Loss (Pcoss):      {res['p_coss']:.3f} W  ({res['p_coss']/res['p_total']*100:.1f}%)")
    print(f" TOTAL POWER LOSS:                  {res['p_total']:.3f} W")
    print("-" * 65)
    print(f" Ambient Temperature (Ta):          {res['ta']:.1f} °C")
    print(f" Thermal Resistance (θJA):          {res['theta_ja']:.1f} °C/W")
    print(f" CALCULATED JUNCTION TEMP (Tj):     {res['tj']:.1f} °C")
    print(f" Maximum Allowable Temp (Tj,max):   150.0 °C")
    print(f" Thermal Headroom Margin:           {res['margin']:.1f} °C")
    
    if res['safe']:
        if res['margin'] >= 30.0:
            print(" STATUS: [ PASS ] Robust thermal margin (> 30°C headroom).")
        else:
            print(" STATUS: [ CAUTION ] Low thermal margin (< 30°C). Consider heatsink.")
    else:
        print(" STATUS: [ CRITICAL WARNING ] Junction temperature exceeds 150°C! Device will fail.")
    print("=" * 65 + "\n")


def print_gate_report(res: Dict):
    print("\n" + "=" * 65)
    print("          MOSFET GATE RESISTOR & DRIVE SIZING REPORT")
    print("=" * 65)
    print(f" Gate Driver Output Voltage (Vdrv): {res['vdrv']:.1f} V")
    print(f" Miller Plateau Voltage (Vplat):    {res['vplat']:.1f} V")
    print(f" Gate-Drain Charge (Qgd):           {res['qgd'] * 1e9:.2f} nC")
    print(f" Target Switching Time (dt):        {res['target_dt'] * 1e9:.1f} ns")
    print(f" Driver Max Peak Current Rating:    {res['idriver_max']:.2f} A")
    print(f" Internal Driver Resistance (Rint): {res['r_driver_internal']:.1f} Ω")
    print("-" * 65)
    print(f" RECOMMENDED SERIES GATE RESISTOR:  {res['r_gate_recommended']:.2f} Ω (Standard 1%: {round(res['r_gate_recommended'], 1)} Ω)")
    print(f" Resulting Peak Driver Inrush:      {res['actual_i_peak']:.2f} A  ({'SAFE' if res['actual_i_peak'] <= res['idriver_max'] else 'OVERLOAD'})")
    print(f" Achieved Miller Duration (dt):     {res['actual_dt'] * 1e9:.1f} ns")
    print("=" * 65 + "\n")


def print_diode_report(res: Dict):
    print("\n" + "=" * 65)
    print("      BODY DIODE CONDUCTION & REVERSE RECOVERY REPORT")
    print("=" * 65)
    print(f" Reverse Bus Voltage (Vds):         {res['vds']:.1f} V")
    print(f" Freewheeling Load Current:         {res['iload']:.2f} A")
    print(f" Body Diode Forward Drop (Vsd):     {res['vsd']:.2f} V")
    print(f" Dead-Time Duration (tdead):        {res['tdead'] * 1e9:.1f} ns")
    print(f" Reverse Recovery Charge (Qrr):     {res['qrr'] * 1e9:.1f} nC")
    print(f" Switching Frequency (fsw):         {res['fsw'] / 1e3:.1f} kHz")
    print("-" * 65)
    print(f" Dead-Time Conduction Loss:         {res['p_diode_cond']:.3f} W")
    print(f" Reverse Recovery Loss (Prr):       {res['p_rr']:.3f} W")
    print(f" TOTAL BODY DIODE LOSS:             {res['p_total_diode']:.3f} W")
    if res['p_rr'] > res['p_diode_cond']:
        print(" NOTE: Reverse recovery dominates diode losses. Consider SiC MOSFET or CFD variant.")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="MOSFET Design, Loss & Thermal Engineering Calculator")
    parser.add_argument("--loss", action="store_true", help="Calculate conduction, switching, and thermal junction temperature")
    parser.add_argument("--gate", action="store_true", help="Calculate gate drive resistor and peak current")
    parser.add_argument("--diode", action="store_true", help="Calculate body diode conduction and reverse recovery losses")
    
    # Common parameters
    parser.add_argument("--vds", type=str, default="48", help="Drain-to-Source operating bus voltage (V)")
    parser.add_argument("--id", type=str, default="10", help="Drain RMS current (A)")
    parser.add_argument("--rdson", type=str, default="0.01", help="Static Rdson at 25°C (Ohms)")
    parser.add_argument("--trise", type=str, default="25n", help="Switching rise time (s, ns)")
    parser.add_argument("--tfall", type=str, default="20n", help="Switching fall time (s, ns)")
    parser.add_argument("--fsw", type=str, default="100k", help="Switching frequency (Hz, kHz)")
    parser.add_argument("--vgs", type=str, default="10", help="Gate drive voltage (V)")
    parser.add_argument("--qg", type=str, default="30n", help="Total gate charge (C, nC)")
    parser.add_argument("--coss", type=str, default="200p", help="Output capacitance Coss (F, pF)")
    parser.add_argument("--theta-ja", type=float, default=40.0, help="Junction-to-ambient thermal resistance (°C/W)")
    parser.add_argument("--ta", type=float, default=25.0, help="Ambient temperature (°C)")
    
    # Gate parameters
    parser.add_argument("--vdrv", type=str, default="12", help="Driver rail voltage (V)")
    parser.add_argument("--vplat", type=str, default="4.5", help="Miller plateau voltage (V)")
    parser.add_argument("--qgd", type=str, default="10n", help="Gate-to-drain Miller charge (C, nC)")
    parser.add_argument("--target-dt", type=str, default="30n", help="Target switching duration (s, ns)")
    parser.add_argument("--idriver-max", type=float, default=2.0, help="Max driver peak current rating (A)")
    
    # Diode parameters
    parser.add_argument("--iload", type=str, default="10", help="Load current during dead time (A)")
    parser.add_argument("--vsd", type=str, default="1.0", help="Body diode forward voltage drop (V)")
    parser.add_argument("--tdead", type=str, default="100n", help="Dead time duration (s, ns)")
    parser.add_argument("--qrr", type=str, default="400n", help="Body diode reverse recovery charge (C, nC)")

    args = parser.parse_args()

    if args.loss:
        res = calculate_loss(
            vds=parse_engineering_value(args.vds),
            id_rms=parse_engineering_value(args.id),
            rdson_25=parse_engineering_value(args.rdson),
            trise=parse_engineering_value(args.trise),
            tfall=parse_engineering_value(args.tfall),
            fsw=parse_engineering_value(args.fsw),
            vgs_drv=parse_engineering_value(args.vgs),
            qg=parse_engineering_value(args.qg),
            coss=parse_engineering_value(args.coss),
            theta_ja=args.theta_ja,
            ta=args.ta
        )
        print_loss_report(res)
    elif args.gate:
        res = calculate_gate_drive(
            vdrv=parse_engineering_value(args.vdrv),
            vplat=parse_engineering_value(args.vplat),
            qgd=parse_engineering_value(args.qgd),
            target_dt=parse_engineering_value(args.target_dt),
            idriver_max=args.idriver_max
        )
        print_gate_report(res)
    elif args.diode:
        res = calculate_diode_loss(
            vds=parse_engineering_value(args.vds),
            iload=parse_engineering_value(args.iload),
            vsd=parse_engineering_value(args.vsd),
            tdead=parse_engineering_value(args.tdead),
            qrr=parse_engineering_value(args.qrr),
            fsw=parse_engineering_value(args.fsw)
        )
        print_diode_report(res)
    else:
        # Default run demo loss calculation
        res = calculate_loss(
            vds=48.0,
            id_rms=15.0,
            rdson_25=0.005,
            trise=25e-9,
            tfall=20e-9,
            fsw=150e3,
            vgs_drv=10.0,
            qg=35e-9,
            coss=450e-12,
            theta_ja=35.0,
            ta=40.0
        )
        print_loss_report(res)

if __name__ == "__main__":
    main()
