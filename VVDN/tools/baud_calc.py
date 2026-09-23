#!/usr/bin/env python3
"""
UART Baud Rate & Timing Calculator for Embedded Bring-up
Usage:
    python3 baud_calc.py --clock <Hz_or_MHz> --baud <target_baud> [--oversample <16|8>]
Examples:
    python3 baud_calc.py --clock 16MHz --baud 115200
    python3 baud_calc.py --clock 48000000 --baud 921600 --oversample 8
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
    parser = argparse.ArgumentParser(description="UART Baud Rate Divisor & Error Calculator")
    parser.add_argument("--clock", "-c", required=True, help="Peripheral clock frequency (e.g., '16MHz', '48000000', '11.0592MHz')")
    parser.add_argument("--baud", "-b", type=int, default=115200, help="Target baud rate (default: 115200)")
    parser.add_argument("--oversample", "-o", type=int, choices=[8, 16], default=16, help="Oversampling factor (default: 16)")
    args = parser.parse_args()

    f_clk = parse_frequency(args.clock)
    target_baud = args.baud
    os = args.oversample

    exact_divisor = f_clk / (os * target_baud)
    int_divisor = round(exact_divisor)

    if int_divisor == 0:
        print(f"Error: Peripheral clock ({f_clk} Hz) is too slow for {target_baud} baud at {os}x oversampling.")
        sys.exit(1)

    actual_baud_int = f_clk / (os * int_divisor)
    error_pct_int = ((actual_baud_int - target_baud) / target_baud) * 100.0

    # Fractional calculation (assuming 4-bit fraction like STM32 / standard UART)
    mantissa = int(exact_divisor)
    fraction_raw = exact_divisor - mantissa
    fraction_4bit = round(fraction_raw * 16)
    fract_divisor = mantissa + (fraction_4bit / 16.0)
    actual_baud_fract = f_clk / (os * fract_divisor) if fract_divisor > 0 else actual_baud_int
    error_pct_fract = ((actual_baud_fract - target_baud) / target_baud) * 100.0

    bit_period_us = (1.0 / target_baud) * 1_000_000
    frame_period_us = bit_period_us * 10  # 8-N-1 = 10 bits
    payload_kbps = (target_baud / 10.0) / 1024.0

    print("=" * 65)
    print(" UART BAUD RATE & TIMING CALCULATION REPORT")
    print("=" * 65)
    print(f"Peripheral Clock (f_clk) : {f_clk:,.1f} Hz ({f_clk/1e6:.4f} MHz)")
    print(f"Target Baud Rate         : {target_baud:,} bps")
    print(f"Oversampling Factor (OS) : {os}x")
    print("-" * 65)
    print(f"Single Bit Period (T_bit): {bit_period_us:.4f} µs ({bit_period_us*1000:.2f} ns)")
    print(f"8-N-1 Frame Time (10b)   : {frame_period_us:.4f} µs")
    print(f"Max Payload Throughput   : {payload_kbps:.2f} KB/s ({target_baud/10:,.0f} Bytes/s)")
    print("-" * 65)
    print(f"Exact Calculated Divisor : {exact_divisor:.5f}")
    print()
    print("--- 1. INTEGER DIVISOR (Standard UART / AVR / 8051 / 16550) ---")
    print(f"Divisor Register Value   : {int_divisor}")
    print(f"Actual Baud Rate         : {actual_baud_int:,.2f} bps")
    print(f"Baud Rate Error          : {error_pct_int:+.2f}%")
    if abs(error_pct_int) <= 2.5:
        print("Verdict                  : [PASS] Reliable for 8-N-1 framing (< ±2.5%)")
    elif abs(error_pct_int) <= 3.0:
        print("Verdict                  : [WARNING] Marginal; risk of framing errors under thermal/crystal drift")
    else:
        print("Verdict                  : [FAIL] Too high! (> ±3.0%). Will cause framing/corrupted bytes!")

    print()
    print("--- 2. FRACTIONAL DIVISOR (STM32 BRR / Modern SoCs) ---")
    print(f"Mantissa: {mantissa}, Fraction (4-bit): {fraction_4bit}/16 (Register: 0x{mantissa:X}{fraction_4bit:X})")
    print(f"Effective Divisor        : {fract_divisor:.4f}")
    print(f"Actual Baud Rate         : {actual_baud_fract:,.2f} bps")
    print(f"Baud Rate Error          : {error_pct_fract:+.2f}%")
    if abs(error_pct_fract) <= 2.5:
        print("Verdict                  : [PASS] Excellent accuracy")
    else:
        print("Verdict                  : [FAIL]")
    print("=" * 65)

if __name__ == "__main__":
    main()
