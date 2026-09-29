#!/usr/bin/env python3
"""
UART Protocol & Transceiver Engineering Calculator
Calculates Baud Rate Divisors (Integer & Fractional), Clock Error %, 
Frame Timing Budgets, Throughput, and RS-485 Bus Turnaround Delays.

Usage:
    python3 tools/uart_calc.py --baud --clock <Hz|MHz> --baudrate <target_baud> [--oversample <16|8>]
    python3 tools/uart_calc.py --frame --baudrate <baud> [--data-bits <5-9>] [--parity <N|E|O>] [--stop-bits <1|1.5|2>]
    python3 tools/uart_calc.py --rs485 --cable-m <meters> --baudrate <baud> [--driver-enable-ns <ns>]
    python3 tools/uart_calc.py --compare-crystals --baudrate <baud>
"""

import argparse
import sys
import math
from typing import Dict, List, Tuple

def parse_frequency(freq_str: str) -> float:
    freq_str = str(freq_str).strip().upper()
    if freq_str.endswith("MHZ"):
        return float(freq_str[:-3]) * 1_000_000
    elif freq_str.endswith("KHZ"):
        return float(freq_str[:-3]) * 1_000
    elif freq_str.endswith("HZ"):
        return float(freq_str[:-2])
    return float(freq_str)


def calculate_baud_divisors(f_clk: float, target_baud: int, os: int = 16) -> Dict:
    exact_divisor = f_clk / (os * target_baud)
    int_divisor = round(exact_divisor)

    if int_divisor == 0:
        return {"error": f"Clock {f_clk} Hz is too slow for {target_baud} baud at {os}x oversampling."}

    actual_baud_int = f_clk / (os * int_divisor)
    error_pct_int = ((actual_baud_int - target_baud) / target_baud) * 100.0

    # Fractional calculation (4-bit fractional BRR as in STM32 USART)
    mantissa = int(exact_divisor)
    fraction_raw = exact_divisor - mantissa
    fraction_4bit = round(fraction_raw * 16)
    if fraction_4bit >= 16:
        mantissa += 1
        fraction_4bit = 0
    fract_divisor = mantissa + (fraction_4bit / 16.0)
    actual_baud_fract = f_clk / (os * fract_divisor) if fract_divisor > 0 else actual_baud_int
    error_pct_fract = ((actual_baud_fract - target_baud) / target_baud) * 100.0

    bit_period_us = (1.0 / target_baud) * 1e6
    frame_period_us = bit_period_us * 10.0

    return {
        "f_clk": f_clk,
        "target_baud": target_baud,
        "oversampling": os,
        "exact_divisor": exact_divisor,
        "int_divisor": int_divisor,
        "actual_baud_int": actual_baud_int,
        "error_pct_int": error_pct_int,
        "mantissa": mantissa,
        "fraction_4bit": fraction_4bit,
        "actual_baud_fract": actual_baud_fract,
        "error_pct_fract": error_pct_fract,
        "bit_period_us": bit_period_us,
        "frame_period_us": frame_period_us,
        "safe_int": abs(error_pct_int) <= 2.0,
        "safe_fract": abs(error_pct_fract) <= 2.0
    }


def calculate_frame_timing(baud: int, data_bits: int = 8, parity: str = "N", stop_bits: float = 1.0) -> Dict:
    start_bits = 1
    parity_bits = 0 if parity.upper() == "N" else 1
    total_frame_bits = start_bits + data_bits + parity_bits + stop_bits

    bit_period_us = (1.0 / baud) * 1e6
    frame_period_us = bit_period_us * total_frame_bits

    max_characters_per_sec = baud / total_frame_bits
    gross_bitrate_kbps = baud / 1000.0
    net_payload_kbps = (max_characters_per_sec * data_bits) / 1000.0
    protocol_efficiency = (data_bits / total_frame_bits) * 100.0

    return {
        "baud": baud,
        "data_bits": data_bits,
        "parity": parity.upper(),
        "stop_bits": stop_bits,
        "total_frame_bits": total_frame_bits,
        "bit_period_us": bit_period_us,
        "frame_period_us": frame_period_us,
        "max_chars_sec": max_characters_per_sec,
        "gross_kbps": gross_bitrate_kbps,
        "payload_kbps": net_payload_kbps,
        "efficiency": protocol_efficiency
    }


def calculate_rs485(cable_m: float, baudrate: int, de_switching_ns: float = 50.0) -> Dict:
    # Standard twisted pair delay: ~5.0 ns/meter
    prop_delay_ns = cable_m * 5.0
    bit_period_ns = (1.0 / baudrate) * 1e9

    # Max safe bus turnaround time should be at least 2x propagation delay + transceiver DE disable time
    min_turnaround_ns = (2.0 * prop_delay_ns) + de_switching_ns
    turnaround_bits = min_turnaround_ns / bit_period_ns

    # ISO/TIA-485 max length vs bitrate rule of thumb
    # Bitrate * Length <= 10^8 (e.g. 100kbps at 1000m, 10Mbps at 10m)
    max_safe_length_m = 1e8 / baudrate if baudrate > 0 else 1200.0
    max_safe_length_m = min(1200.0, max_safe_length_m)

    return {
        "cable_m": cable_m,
        "baudrate": baudrate,
        "prop_delay_ns": prop_delay_ns,
        "bit_period_ns": bit_period_ns,
        "min_turnaround_ns": min_turnaround_ns,
        "turnaround_bits": turnaround_bits,
        "max_safe_length_m": max_safe_length_m,
        "safe_length": cable_m <= max_safe_length_m
    }


def print_baud_report(res: Dict):
    print("\n" + "=" * 65)
    print("        UART BAUD RATE DIVISOR & ERROR ANALYSIS")
    print("=" * 65)
    print(f" Peripheral Clock (f_clk):          {res['f_clk']:,.1f} Hz ({res['f_clk']/1e6:.4f} MHz)")
    print(f" Target Baud Rate:                  {res['target_baud']:,} bps")
    print(f" Oversampling Factor:               {res['oversampling']}x")
    print(f" Exact Floating Divisor:            {res['exact_divisor']:.4f}")
    print("-" * 65)
    print(" INTEGER BRG DIVISOR (Standard 8250 / Legacy UART):")
    print(f"   • Divisor Register Value:        {res['int_divisor']}")
    print(f"   • Actual Achieved Baud:          {res['actual_baud_int']:,.1f} bps")
    print(f"   • Timing Error Percentage:       {res['error_pct_int']:+.2f}%")
    print(f"   • Status:                        {'[ PASS ] Within ±2.0%' if res['safe_int'] else '[ FAIL ] Exceeds ±2.0% limit!'}")
    print("-" * 65)
    print(" FRACTIONAL BRG DIVISOR (Modern STM32 / ARM Cortex USART):")
    print(f"   • Mantissa: {res['mantissa']} | Fraction (4-bit): {res['fraction_4bit']}/16")
    print(f"   • Actual Achieved Baud:          {res['actual_baud_fract']:,.1f} bps")
    print(f"   • Timing Error Percentage:       {res['error_pct_fract']:+.2f}%")
    print(f"   • Status:                        {'[ PASS ] Clean fractional match' if res['safe_fract'] else '[ WARN ] Error exceeds tolerance'}")
    print("-" * 65)
    print(f" Single Bit Period (T_bit):         {res['bit_period_us']:.3f} µs")
    print(f" 8-N-1 Character Duration:          {res['frame_period_us']:.3f} µs")
    print("=" * 65 + "\n")


def print_frame_report(res: Dict):
    print("\n" + "=" * 65)
    print("           UART CHARACTER FRAME TIMING & THROUGHPUT")
    print("=" * 65)
    print(f" Baud Rate:                         {res['baud']:,} bps")
    print(f" Configuration:                     {res['data_bits']}-{res['parity']}-{res['stop_bits']}")
    print(f" Total Bits per Frame:              {res['total_frame_bits']:.1f} bits")
    print("-" * 65)
    print(f" Single Bit Period (T_bit):         {res['bit_period_us']:.3f} µs")
    print(f" Frame Period (T_frame):            {res['frame_period_us']:.3f} µs")
    print(f" Maximum Frame Rate:                {res['max_chars_sec']:,.1f} frames/sec (Bytes/sec)")
    print("-" * 65)
    print(f" Gross Physical Bitrate:            {res['gross_kbps']:.2f} kbps")
    print(f" Net Useful Payload Throughput:     {res['payload_kbps']:.2f} kbps ({res['payload_kbps']/8:.2f} kB/s)")
    print(f" Channel Protocol Efficiency:       {res['efficiency']:.1f}%")
    print("=" * 65 + "\n")


def print_rs485_report(res: Dict):
    print("\n" + "=" * 65)
    print("          RS-485 DIFFERENTIAL BUS TIMING & DELAYS")
    print("=" * 65)
    print(f" Cable Length:                      {res['cable_m']:.1f} meters")
    print(f" Target Baud Rate:                  {res['baudrate']:,} bps")
    print(f" Twisted Pair One-Way Delay:        {res['prop_delay_ns']:.1f} ns")
    print(f" Single Bit Period:                 {res['bit_period_ns']:.1f} ns")
    print("-" * 65)
    print(f" Minimum Required Turnaround Time:  {res['min_turnaround_ns']:.1f} ns ({res['turnaround_bits']:.3f} bit periods)")
    print(f" Maximum Safe Cable Length at {res['baudrate']//1000}k: {res['max_safe_length_m']:.1f} meters")
    print(f" Cable Length Compliance:           {'[ PASS ] Within safe TIA-485 envelope' if res['safe_length'] else '[ WARNING ] Cable too long for this bitrate!'}")
    print("-" * 65)
    print(" HARDWARE TERMINATION GUIDELINES:")
    print("   • Place 120Ω 1% metal film resistors across A and B at BOTH extreme ends of bus.")
    print("   • Avoid star/tee taps; keep stubs shorter than 30 cm.")
    print("   • Install fail-safe biasing (560Ω pull-up to 5V on A, 560Ω pull-down to GND on B).")
    print("=" * 65 + "\n")


def main():
    parser = argparse.ArgumentParser(description="UART & RS-485 Engineering Sizing Calculator")
    parser.add_argument("--baud", action="store_true", help="Calculate BRG divisors and clock error percentage")
    parser.add_argument("--frame", action="store_true", help="Calculate frame duration, throughput, and efficiency")
    parser.add_argument("--rs485", action="store_true", help="Calculate RS-485 propagation delay and bus turnaround")
    
    parser.add_argument("--clock", "-c", type=str, default="16MHz", help="Peripheral clock frequency (e.g. '16MHz', '48MHz')")
    parser.add_argument("--baudrate", "-b", type=int, default=115200, help="Target baud rate (default: 115200)")
    parser.add_argument("--oversample", "-o", type=int, choices=[8, 16], default=16, help="Oversampling factor (8 or 16)")
    
    parser.add_argument("--data-bits", type=int, default=8, choices=[5, 6, 7, 8, 9], help="Data bits per frame (default: 8)")
    parser.add_argument("--parity", type=str, default="N", choices=["N", "E", "O", "n", "e", "o"], help="Parity (N, E, O)")
    parser.add_argument("--stop-bits", type=float, default=1.0, choices=[1.0, 1.5, 2.0], help="Stop bits (1, 1.5, 2)")
    
    parser.add_argument("--cable-m", type=float, default=50.0, help="RS-485 cable length in meters (default: 50m)")
    parser.add_argument("--driver-enable-ns", type=float, default=50.0, help="Transceiver DE switching delay in ns")

    args = parser.parse_args()

    if args.baud:
        f_clk = parse_frequency(args.clock)
        res = calculate_baud_divisors(f_clk, args.baudrate, args.oversample)
        print_baud_report(res)
    elif args.frame:
        res = calculate_frame_timing(args.baudrate, args.data_bits, args.parity, args.stop_bits)
        print_frame_report(res)
    elif args.rs485:
        res = calculate_rs485(args.cable_m, args.baudrate, args.driver_enable_ns)
        print_rs485_report(res)
    else:
        # Default: print baud report
        f_clk = parse_frequency(args.clock)
        res = calculate_baud_divisors(f_clk, args.baudrate, args.oversample)
        print_baud_report(res)

if __name__ == "__main__":
    main()
