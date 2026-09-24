#!/usr/bin/env python3
"""
SPI Timing Budget, Round-Trip Delay & Throughput Calculator for Embedded Bring-up
Usage:
    python3 spi_calc.py --clock <Hz_or_MHz> [options]
Examples:
    python3 spi_calc.py --clock 50MHz --trace-cm 5 --tco 7 --tsu 3
    python3 spi_calc.py --clock 10MHz --trace-cm 5 --cable-cm 30 --isolator-ns 25 --tco 15 --tsu 5
    python3 spi_calc.py --clock 104MHz --qspi
"""

import argparse
import sys

def parse_frequency(freq_str: str) -> float:
    freq_str = freq_str.strip().upper()
    if freq_str.endswith("MHZ"):
        return float(freq_str[:-3]) * 1_000_000
    elif freq_str.endswith("KHZ"):
        return float(freq_str[:-3]) * 1_000
    elif freq_str.endswith("HZ"):
        return float(freq_str[:-2])
    return float(freq_str)

def main():
    parser = argparse.ArgumentParser(description="SPI Timing Budget & Throughput Calculator")
    parser.add_argument("--clock", "-c", required=True, help="Target SPI SCLK frequency (e.g. '50MHz', '10MHz', '8000000')")
    parser.add_argument("--trace-cm", type=float, default=5.0, help="PCB trace length in cm (default: 5.0 cm)")
    parser.add_argument("--cable-cm", type=float, default=0.0, help="Off-board ribbon/wire cable length in cm (default: 0.0 cm)")
    parser.add_argument("--isolator-ns", type=float, default=0.0, help="Galvanic isolator or level shifter delay in ns (default: 0.0 ns)")
    parser.add_argument("--tco", type=float, default=8.0, help="Peripheral Clock-to-Output valid delay tCO in ns (default: 8.0 ns)")
    parser.add_argument("--tsu", type=float, default=3.0, help="Controller input Data Setup time tSU in ns (default: 3.0 ns)")
    parser.add_argument("--margin", type=float, default=2.0, help="Recommended engineering margin in ns (default: 2.0 ns)")
    parser.add_argument("--rise-time-ns", type=float, default=1.5, help="SCLK signal rise time in ns (default: 1.5 ns)")
    parser.add_argument("--qspi", action="store_true", help="Highlight Quad-SPI / Octal-SPI metrics")
    args = parser.parse_args()

    f_sclk = parse_frequency(args.clock)
    t_sclk_ns = (1.0 / f_sclk) * 1e9

    # Propagation delays
    # FR4 microstrip trace: ~65 ps/cm (0.065 ns/cm)
    t_trace_ns = args.trace_cm * 0.065
    # Ribbon cable delay: ~50 ps/cm (0.05 ns/cm)
    t_cable_ns = args.cable_cm * 0.050
    t_isolator_ns = args.isolator_ns

    t_prop_oneway_ns = t_trace_ns + t_cable_ns + t_isolator_ns
    t_roundtrip_prop_ns = 2.0 * t_prop_oneway_ns

    # Total round-trip timing requirement for safe MISO read:
    # TSCLK > 2 * t_prop + tCO + tSU + t_margin
    t_sclk_min_ns = t_roundtrip_prop_ns + args.tco + args.tsu + args.margin
    f_max_safe_hz = 1e9 / t_sclk_min_ns

    # Transmission line critical length
    # l_crit = t_rise / (2 * 0.065 ns/cm)
    l_crit_cm = args.rise_time_ns / (2.0 * 0.065)

    # Throughput calculations (continuous streaming assuming ~96% efficiency)
    tp_std_mbps = (f_sclk * 1.0) / 1e6
    tp_std_mbytes = tp_std_mbps / 8.0

    tp_dual_mbps = (f_sclk * 2.0) / 1e6
    tp_dual_mbytes = tp_dual_mbps / 8.0

    tp_quad_mbps = (f_sclk * 4.0) / 1e6
    tp_quad_mbytes = tp_quad_mbps / 8.0

    tp_octal_mbps = (f_sclk * 8.0) / 1e6
    tp_octal_mbytes = tp_octal_mbps / 8.0

    print("=" * 70)
    print(" SPI TIMING BUDGET, PROPAGATION DELAY & THROUGHPUT REPORT")
    print("=" * 70)
    print(f"Target Clock Frequency (f_SCLK) : {f_sclk:,.1f} Hz ({f_sclk/1e6:.3f} MHz)")
    print(f"Clock Period (T_SCLK)           : {t_sclk_ns:.2f} ns (High: {t_sclk_ns/2:.2f} ns, Low: {t_sclk_ns/2:.2f} ns)")
    print("-" * 70)
    print("--- 1. PHYSICAL PATH DELAY BREAKDOWN ---")
    print(f"PCB Trace Length                : {args.trace_cm:.1f} cm (Delay: {t_trace_ns:.3f} ns)")
    if args.cable_cm > 0:
        print(f"External Cable Length           : {args.cable_cm:.1f} cm (Delay: {t_cable_ns:.3f} ns)")
    if args.isolator_ns > 0:
        print(f"Digital Isolator / Level Shifter: {t_isolator_ns:.2f} ns")
    print(f"Total One-Way Delay (t_prop)    : {t_prop_oneway_ns:.3f} ns")
    print(f"Total Round-Trip Wire Delay     : {t_roundtrip_prop_ns:.3f} ns")
    print()
    print("--- 2. TIMING BUDGET & MAXIMUM READ CLOCK ---")
    print(f"Peripheral Clock-to-Out (tCO)   : {args.tco:.2f} ns")
    print(f"Controller Setup Time (tSU)     : {args.tsu:.2f} ns")
    print(f"Safety Margin                   : {args.margin:.2f} ns")
    print(f"Minimum Safe Clock Period       : {t_sclk_min_ns:.2f} ns")
    print(f"Maximum Safe Read Frequency     : {f_max_safe_hz/1e6:.2f} MHz ({f_max_safe_hz:,.0f} Hz)")
    print("-" * 70)

    if f_sclk <= f_max_safe_hz:
        slack_ns = t_sclk_ns - t_sclk_min_ns
        print(f"Timing Verdict                  : [PASS] Positive timing slack (+{slack_ns:.2f} ns)")
        print("                                  Controller will reliably capture MISO data.")
    else:
        deficit_ns = t_sclk_min_ns - t_sclk_ns
        print(f"Timing Verdict                  : [FAIL] Negative timing slack (-{deficit_ns:.2f} ns)")
        print("                                  MISO data will arrive AFTER Controller sampling edge!")
        print(f"                                  Action: Reduce clock to <= {f_max_safe_hz/1e6:.1f} MHz")
        print("                                  or use delayed-sampling / phase-shifted RX clock.")

    print()
    print("--- 3. TRANSMISSION LINE & SIGNAL INTEGRITY ---")
    print(f"SCLK Edge Rise Time (t_rise)    : {args.rise_time_ns:.2f} ns")
    print(f"Critical Trace Length (l_crit)  : {l_crit_cm:.1f} cm ({l_crit_cm/2.54:.1f} inches)")
    if (args.trace_cm + args.cable_cm) > l_crit_cm:
        print("Transmission Line Behavior      : [YES] Trace length exceeds critical limit.")
        print("                                  Requires 22Ω - 33Ω series termination on SCLK/MOSI.")
    else:
        print("Transmission Line Behavior      : [NO] Lumped circuit regime; reflections minimal.")

    print()
    print("--- 4. THEORETICAL DATA THROUGHPUT ---")
    print(f"Standard SPI (1-bit full duplex): {tp_std_mbps:6.2f} Mbps | {tp_std_mbytes:6.2f} MB/s")
    print(f"Dual SPI     (2-bit half duplex): {tp_dual_mbps:6.2f} Mbps | {tp_dual_mbytes:6.2f} MB/s")
    print(f"Quad SPI     (4-bit QSPI)       : {tp_quad_mbps:6.2f} Mbps | {tp_quad_mbytes:6.2f} MB/s")
    if args.qspi or f_sclk >= 50e6:
        print(f"Octal SPI    (8-bit OSPI SDR)   : {tp_octal_mbps:6.2f} Mbps | {tp_octal_mbytes:6.2f} MB/s")
        print(f"Octal SPI    (8-bit OSPI DTR)   : {tp_octal_mbps*2:6.2f} Mbps | {tp_octal_mbytes*2:6.2f} MB/s")
    print("=" * 70)

if __name__ == "__main__":
    main()
