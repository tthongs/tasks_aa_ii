#!/usr/bin/env python3
"""
LIN (Local Interconnect Network) Bus Timing, Frame, PID & Checksum Calculator
Usage:
    python3 tools/lin_calc.py --baud <bps> [--data-bytes <1..8>]
    python3 tools/lin_calc.py --pid <id_hex_or_dec>
    python3 tools/lin_calc.py --checksum --pid <id_hex> --data <hex_bytes...> [--classic]
    python3 tools/lin_calc.py --autobaud --timer-clk <Hz> --baud <bps>
    python3 tools/lin_calc.py --bus-load --slaves <N> [--cbus <nF>]
"""

import argparse
import sys
from typing import List, Tuple, Dict

def calculate_pid(lin_id: int) -> Tuple[int, int, int]:
    """
    Calculate parity bits P0 and P1 for a 6-bit LIN ID (0x00 - 0x3F).
    P0 = ID0 ^ ID1 ^ ID2 ^ ID4
    P1 = !(ID1 ^ ID3 ^ ID4 ^ ID5)
    PID = (P1 << 7) | (P0 << 6) | (ID & 0x3F)
    """
    if lin_id < 0 or lin_id > 0x3F:
        raise ValueError(f"LIN ID must be between 0x00 and 0x3F (0..63), got 0x{lin_id:X}")
        
    id0 = (lin_id >> 0) & 1
    id1 = (lin_id >> 1) & 1
    id2 = (lin_id >> 2) & 1
    id3 = (lin_id >> 3) & 1
    id4 = (lin_id >> 4) & 1
    id5 = (lin_id >> 5) & 1
    
    p0 = id0 ^ id1 ^ id2 ^ id4
    p1 = 1 ^ (id1 ^ id3 ^ id4 ^ id5) # Inverted
    
    pid = (p1 << 7) | (p0 << 6) | (lin_id & 0x3F)
    return pid, p0, p1

def calculate_checksum(pid: int, data_bytes: List[int], is_classic: bool = False) -> int:
    """
    Calculate LIN checksum:
    Classic Checksum (LIN 1.3): Inverted modulo-256 sum of data bytes only (used for IDs 0x3C, 0x3D).
    Enhanced Checksum (LIN 2.x): Inverted modulo-256 sum with carry addition of PID + data bytes.
    """
    chk = 0
    if not is_classic:
        chk += pid
        
    for b in data_bytes:
        chk += (b & 0xFF)
        if chk > 0xFF:
            chk = (chk & 0xFF) + 1  # Add carry over
            
    # Bitwise NOT (one's complement)
    return (~chk) & 0xFF

def calculate_frame_timing(baud: int, num_data_bytes: int) -> Dict:
    """
    Calculate nominal and maximum LIN frame timing as defined in LIN 2.1 / ISO 17987.
    T_bit = 1 / Baud
    T_header_nom = 34 * T_bit  (Break 13 + Delim 1 + Sync 10 + PID 10)
    T_response_nom = 10 * (N_data + 1) * T_bit  (Data bytes + Checksum)
    T_frame_nom = T_header_nom + T_response_nom
    T_frame_max = 1.4 * T_frame_nom
    """
    t_bit_us = (1.0 / baud) * 1_000_000.0
    
    # Break: 13 dominant bits + 1 delimiter bit = 14 bits (or 13 + 1)
    # Sync byte: 1 start + 8 data + 1 stop = 10 bits
    # PID byte: 1 start + 8 data + 1 stop = 10 bits
    # Header total = 34 bits
    header_bits = 34
    
    # Response: each byte has 1 start + 8 data + 1 stop = 10 bits
    # N_data bytes + 1 Checksum byte
    response_bits = 10 * (num_data_bytes + 1)
    
    total_nom_bits = header_bits + response_bits
    t_header_nom_ms = (header_bits * t_bit_us) / 1000.0
    t_response_nom_ms = (response_bits * t_bit_us) / 1000.0
    t_frame_nom_ms = (total_nom_bits * t_bit_us) / 1000.0
    t_frame_max_ms = 1.4 * t_frame_nom_ms
    
    return {
        "baud": baud,
        "t_bit_us": t_bit_us,
        "header_bits": header_bits,
        "response_bits": response_bits,
        "total_nom_bits": total_nom_bits,
        "t_header_nom_ms": t_header_nom_ms,
        "t_response_nom_ms": t_response_nom_ms,
        "t_frame_nom_ms": t_frame_nom_ms,
        "t_frame_max_ms": t_frame_max_ms,
        "max_frame_rate": 1000.0 / t_frame_max_ms if t_frame_max_ms > 0 else 0
    }

def calculate_bus_parameters(num_slaves: int, c_bus_nf: float = 4.7) -> Dict:
    """
    Calculate LIN bus pull-up equivalent resistance and RC time constant.
    Master pull-up: 1 kOhm in series with diode (~0.7V).
    Slave pull-up: 30 kOhm in series with diode each.
    R_bus_eq = 1k || (30k / N_slaves)
    """
    r_master = 1000.0
    r_slave = 30000.0
    r_slaves_combined = r_slave / num_slaves if num_slaves > 0 else float("inf")
    r_bus_eq = (r_master * r_slaves_combined) / (r_master + r_slaves_combined)
    
    # RC time constant tau = R * C
    c_f = c_bus_nf * 1e-9
    tau_us = (r_bus_eq * c_f) * 1e6
    t_rise_us = 2.2 * tau_us  # 10% to 90% rise time
    
    return {
        "num_slaves": num_slaves,
        "r_master_ohm": r_master,
        "r_slaves_combined_ohm": r_slaves_combined,
        "r_bus_eq_ohm": r_bus_eq,
        "c_bus_nf": c_bus_nf,
        "tau_us": tau_us,
        "t_rise_us": t_rise_us
    }

def main():
    parser = argparse.ArgumentParser(description="LIN (Local Interconnect Network) Timing & Protocol Calculator")
    parser.add_argument("--baud", "-b", type=int, default=19200, help="LIN Baud rate (default: 19200, common: 9600, 2400)")
    parser.add_argument("--data-bytes", "-d", type=int, default=8, choices=range(1, 9), help="Number of payload data bytes (1..8)")
    parser.add_argument("--pid", type=lambda x: int(x, 0), help="Calculate PID for specified 6-bit LIN ID (0x00 to 0x3F)")
    parser.add_argument("--checksum", action="store_true", help="Calculate LIN Checksum for given PID and data bytes")
    parser.add_argument("--data", nargs="+", type=lambda x: int(x, 0), help="Data bytes in hex for checksum calculation")
    parser.add_argument("--classic", action="store_true", help="Use Classic Checksum (LIN 1.3) instead of Enhanced (LIN 2.x)")
    parser.add_argument("--autobaud", action="store_true", help="Calculate auto-baud timer capture parameters")
    parser.add_argument("--timer-clk", type=str, default="48MHz", help="MCU input capture timer clock (e.g., '48MHz', '16MHz')")
    parser.add_argument("--bus-load", action="store_true", help="Calculate LIN bus electrical RC parameters")
    parser.add_argument("--slaves", type=int, default=8, help="Number of slave nodes on the LIN bus (1..15)")
    parser.add_argument("--cbus", type=float, default=4.7, help="Total bus capacitance in nF (max 10 nF per ISO 17987)")
    
    args = parser.parse_args()
    
    if args.pid is not None and not args.checksum:
        pid, p0, p1 = calculate_pid(args.pid)
        print("=" * 65)
        print(" LIN PROTECTED IDENTIFIER (PID) CALCULATION")
        print("=" * 65)
        print(f"Raw LIN ID      : 0x{args.pid:02X} ({args.pid} decimal)")
        print(f"Binary ID (5..0): {args.pid:06b} (ID5..ID0)")
        print(f"Parity Bit P0   : {p0} (ID0 ^ ID1 ^ ID2 ^ ID4)")
        print(f"Parity Bit P1   : {p1} (![ID1 ^ ID3 ^ ID4 ^ ID5])")
        print(f"Calculated PID  : 0x{pid:02X} (Binary: {pid:08b})")
        if args.pid <= 0x3B:
            frame_class = "Unconditional / Signal-Carrying Frame"
        elif args.pid == 0x3C:
            frame_class = "Diagnostic Master Request Frame (Classic Checksum)"
        elif args.pid == 0x3D:
            frame_class = "Diagnostic Slave Response Frame (Classic Checksum)"
        elif args.pid == 0x3E:
            frame_class = "User Defined Diagnostic Frame"
        else:
            frame_class = "Reserved Frame"
        print(f"Frame Category  : {frame_class}")
        print("=" * 65)
        return
        
    if args.checksum:
        if args.pid is None:
            print("Error: --pid is required when computing checksum.")
            sys.exit(1)
        if not args.data:
            print("Error: --data bytes are required when computing checksum.")
            sys.exit(1)
            
        pid, _, _ = calculate_pid(args.pid)
        chk = calculate_checksum(pid, args.data, args.classic)
        mode_str = "Classic Checksum (LIN 1.3 - Data bytes only)" if args.classic else "Enhanced Checksum (LIN 2.x - PID + Data bytes)"
        
        print("=" * 65)
        print(" LIN CHECKSUM CALCULATION REPORT")
        print("=" * 65)
        print(f"Mode            : {mode_str}")
        print(f"Protected ID    : 0x{pid:02X} (Raw ID: 0x{args.pid:02X})")
        print(f"Data Bytes ({len(args.data)}): " + " ".join(f"0x{b:02X}" for b in args.data))
        print(f"Checksum Byte   : 0x{chk:02X} (Decimal: {chk}, Binary: {chk:08b})")
        print("=" * 65)
        return
        
    if args.autobaud:
        # Parse timer clock
        t_clk_str = args.timer_clk.upper()
        if t_clk_str.endswith("MHZ"):
            t_clk = float(t_clk_str[:-3]) * 1e6
        elif t_clk_str.endswith("KHZ"):
            t_clk = float(t_clk_str[:-3]) * 1e3
        else:
            t_clk = float(t_clk_str)
            
        t_bit_us = (1.0 / args.baud) * 1e6
        # Sync byte 0x55 has 5 falling edges:
        # Edge 1: Start bit falling edge
        # Edge 5: Bit 7 falling edge
        # Distance between Edge 1 and Edge 5 = exactly 8 bit periods
        sync_window_us = 8.0 * t_bit_us
        sync_window_s = sync_window_us / 1e6
        timer_ticks = sync_window_s * t_clk
        ticks_per_bit = timer_ticks / 8.0
        
        print("=" * 68)
        print(" LIN AUTO-BAUD SLAVE SYNCHRONIZATION REPORT")
        print("=" * 68)
        print(f"Target Baud Rate         : {args.baud} bps (Bit Time: {t_bit_us:.2f} µs)")
        print(f"Timer Clock Frequency    : {t_clk:,.0f} Hz ({t_clk/1e6:.2f} MHz)")
        print(f"Sync Byte (0x55) Edges   : 5 Falling Edges (Start, Bit1, Bit3, Bit5, Bit7)")
        print(f"Sync Window (8 T_bit)    : {sync_window_us:.2f} µs")
        print(f"Expected Timer Ticks (8T): {timer_ticks:.1f} ticks (Round: {round(timer_ticks)})")
        print(f"Ticks Per Bit Time       : {ticks_per_bit:.2f} ticks")
        print(f"Clock Resolution         : {(1.0/t_clk)*1e9:.2f} ns/tick")
        print(f"Clock Error per ±1 Tick  : {(1.0 / timer_ticks) * 100:.3f}% (Tolerance requirement: ±1.5%)")
        print("=" * 68)
        return

    # Default: Frame Timing & Bus parameters
    timing = calculate_frame_timing(args.baud, args.data_bytes)
    bus_p = calculate_bus_parameters(args.slaves, args.cbus)
    
    print("=" * 70)
    print(" LIN BUS TIMING, SLOTS & ELECTRICAL LOAD REPORT")
    print("=" * 70)
    print(f"Baud Rate                : {timing['baud']} bps")
    print(f"Bit Duration (T_bit)     : {timing['t_bit_us']:.2f} µs")
    print(f"Payload Size             : {args.data_bytes} Data Bytes")
    print("-" * 70)
    print(" 1. FRAME TIMING & SCHEDULE SLOT SIZING")
    print("-" * 70)
    print(f"  Header Duration (Nom)  : {timing['t_header_nom_ms']:.2f} ms ({timing['header_bits']} bits: Break 14 + Sync 10 + PID 10)")
    print(f"  Response Duration(Nom) : {timing['t_response_nom_ms']:.2f} ms ({timing['response_bits']} bits: {args.data_bytes} Data + 1 Checksum)")
    print(f"  Total Nominal Duration : {timing['t_frame_nom_ms']:.2f} ms ({timing['total_nom_bits']} bits)")
    print(f"  Max Frame Slot Time    : {timing['t_frame_max_ms']:.2f} ms (1.4x Nominal Slot Budget)")
    print(f"  Max Possible Bus Load  : {timing['max_frame_rate']:.1f} frames/second")
    print("-" * 70)
    print(" 2. ELECTRICAL BUS LOAD & RC RISE TIME")
    print("-" * 70)
    print(f"  Connected Slaves       : {bus_p['num_slaves']} (Master: 1kΩ, Each Slave: 30kΩ)")
    print(f"  Slaves Parallel Pull-up: {bus_p['r_slaves_combined_ohm']:.1f} Ω")
    print(f"  Equivalent Bus Pull-up : {bus_p['r_bus_eq_ohm']:.1f} Ω (Allowed: 500Ω to 1000Ω)")
    print(f"  Total Bus Capacitance  : {bus_p['c_bus_nf']} nF (Max allowable: 10.0 nF)")
    print(f"  RC Time Constant (tau) : {bus_p['tau_us']:.2f} µs")
    print(f"  Passive Rise Time (tr) : {bus_p['t_rise_us']:.2f} µs (Must be <= 0.2 * T_bit = {0.2*timing['t_bit_us']:.2f} µs)")
    if bus_p['t_rise_us'] <= 0.2 * timing['t_bit_us']:
        print("  Signal Integrity Check : PASS (Rise time comfortably within bit budget)")
    else:
        print("  Signal Integrity Check : WARNING: Rise time exceeds 20% of bit period! Reduce bus capacitance.")
    print("=" * 70)

if __name__ == '__main__':
    main()
