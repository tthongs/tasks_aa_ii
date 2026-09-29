#!/usr/bin/env python3
"""
CAN (Controller Area Network) & CAN FD Timing, Bitrate and Bus Load Calculator
Usage:
    python3 tools/can_calc.py --clock <Hz_or_MHz> --baud <bps> [--sp <target_sample_point>]
    python3 tools/can_calc.py --fd --clock <Hz> --nom-baud <bps> --data-baud <bps>
    python3 tools/can_calc.py --frame --id <hex> --dlc <bytes> [--fd] [--baud <bps>]
    python3 tools/can_calc.py --arbitrate --id1 <hex> --id2 <hex>
"""

import argparse
import sys
import math
from typing import Tuple, List, Dict

def parse_frequency(freq_str: str) -> float:
    freq_str = str(freq_str).strip().upper()
    if freq_str.endswith("MHZ"):
        return float(freq_str[:-3]) * 1_000_000
    elif freq_str.endswith("KHZ"):
        return float(freq_str[:-3]) * 1_000
    elif freq_str.endswith("HZ"):
        return float(freq_str[:-2])
    return float(freq_str)

def calculate_can_timing(f_clk: float, target_baud: int, target_sp: float = 87.5) -> Dict:
    """
    Calculate optimal BRP, Prop_Seg, Phase_Seg1, Phase_Seg2 for CAN 2.0 / Nominal CAN FD
    Standard constraints:
      - Total Tq in NBT: 8 to 25
      - Sync_Seg = 1 Tq
      - Phase_Seg2 >= 2 Tq
      - SJW = min(4, Phase_Seg1)
    """
    best_match = None
    min_sp_error = float("inf")
    
    # Try prescalers BRP from 1 to 128
    for brp in range(1, 129):
        tq_clk = f_clk / brp
        total_tq = tq_clk / target_baud
        
        # Check if total_tq is an integer within 8 to 25
        if abs(total_tq - round(total_tq)) < 1e-4:
            total_tq_int = int(round(total_tq))
            if 8 <= total_tq_int <= 25:
                # Sync_Seg is always 1 Tq
                remaining_tq = total_tq_int - 1
                
                # Sample point = (1 + Prop_Seg + Phase_Seg1) / total_tq * 100
                ideal_tseg1 = (target_sp / 100.0) * total_tq_int - 1.0
                tseg1_int = int(round(ideal_tseg1))
                tseg2_int = remaining_tq - tseg1_int
                
                if tseg1_int >= 2 and tseg2_int >= 2:
                    # Prop_Seg + Phase_Seg1 = tseg1_int
                    prop_seg = math.ceil(tseg1_int / 2.0)
                    phase_seg1 = tseg1_int - prop_seg
                    phase_seg2 = tseg2_int
                    
                    actual_sp = ((1 + tseg1_int) / total_tq_int) * 100.0
                    sp_error = abs(actual_sp - target_sp)
                    
                    if sp_error < min_sp_error:
                        min_sp_error = sp_error
                        sjw = min(4, phase_seg1)
                        best_match = {
                            "brp": brp,
                            "total_tq": total_tq_int,
                            "sync_seg": 1,
                            "prop_seg": prop_seg,
                            "phase_seg1": phase_seg1,
                            "phase_seg2": phase_seg2,
                            "tseg1": tseg1_int,
                            "tseg2": phase_seg2,
                            "sjw": sjw,
                            "sample_point": actual_sp,
                            "tq_ns": (1.0 / tq_clk) * 1e9,
                            "bit_time_ns": (1.0 / target_baud) * 1e9,
                            "actual_baud": target_baud,
                            "baud_error_pct": 0.0
                        }
    return best_match

def calculate_frame_bits(id_val: int, dlc: int, is_ext: bool = False, is_fd: bool = False) -> Dict:
    """
    Calculate nominal and worst-case bit counts including bit-stuffing overhead.
    """
    if not is_fd:
        # Classical CAN
        # Base frame without data:
        # Standard: SOF(1) + ID(11) + RTR(1) + IDE(1) + r0(1) + DLC(4) = 19 bits (stuffed)
        # CRC(15) = 15 bits (stuffed)
        # Total stuffed zone = 34 bits + (DLC * 8 bits)
        # Fixed un-stuffed zone: CRC Delimiter(1) + ACK(1) + ACK Delim(1) + EOF(7) + IFS(3) = 13 bits
        if not is_ext:
            base_stuffed = 34
            fixed_unstuffed = 13
            frame_type = "Classical CAN 2.0A (11-bit ID)"
        else:
            # Extended: SOF(1)+BaseID(11)+SRR(1)+IDE(1)+ExtID(18)+RTR(1)+r1(1)+r0(1)+DLC(4) = 39 bits
            # CRC(15) = 15 bits
            # Total stuffed = 54 bits
            base_stuffed = 54
            fixed_unstuffed = 13
            frame_type = "Classical CAN 2.0B (29-bit Extended ID)"
        
        payload_bits = dlc * 8
        nominal_bits = base_stuffed + payload_bits + fixed_unstuffed
        
        # Worst-case bit stuffing in CAN 2.0:
        # A stuff bit every 5 bits: worst case adds floor((stuffed_bits - 1) / 4)
        total_stuffed = base_stuffed + payload_bits
        max_stuff_bits = math.floor((total_stuffed - 1) / 4)
        worst_case_bits = nominal_bits + max_stuff_bits
        
        return {
            "type": frame_type,
            "dlc_bytes": dlc,
            "nominal_bits": nominal_bits,
            "max_stuff_bits": max_stuff_bits,
            "worst_case_bits": worst_case_bits,
            "efficiency_nominal": (payload_bits / nominal_bits) * 100.0 if nominal_bits > 0 else 0,
            "efficiency_worst": (payload_bits / worst_case_bits) * 100.0 if worst_case_bits > 0 else 0
        }
    else:
        # CAN FD
        crc_bits = 17 if dlc <= 16 else 21
        # CAN FD stuff count = 4 bits (3-bit Gray code + parity)
        # Fixed stuff bits every 4 or 5 bits in CRC field
        fixed_crc_stuff_bits = 6 if dlc <= 16 else 7
        nominal_bits = (32 if not is_ext else 52) + (dlc * 8) + crc_bits + 4 + fixed_crc_stuff_bits + 13
        worst_case_bits = int(nominal_bits * 1.15) # approx 15% dynamic stuff margin
        payload_bits = dlc * 8
        return {
            "type": "CAN FD (Flexible Data-rate)" + (" 29-bit" if is_ext else " 11-bit"),
            "dlc_bytes": dlc,
            "nominal_bits": nominal_bits,
            "max_stuff_bits": fixed_crc_stuff_bits + 8,
            "worst_case_bits": worst_case_bits,
            "efficiency_nominal": (payload_bits / nominal_bits) * 100.0 if nominal_bits > 0 else 0,
            "efficiency_worst": (payload_bits / worst_case_bits) * 100.0 if worst_case_bits > 0 else 0
        }

def arbitrate(id1: int, id2: int, ext1: bool = False, ext2: bool = False) -> Dict:
    """
    Simulate CAN bitwise arbitration between two message identifiers.
    Dominant = 0, Recessive = 1. Lower numeric ID wins.
    """
    id1_bin = f"{id1:029b}" if ext1 else f"{id1:011b}"
    id2_bin = f"{id2:029b}" if ext2 else f"{id2:011b}"
    
    # Pad to equal length if needed
    max_len = max(len(id1_bin), len(id2_bin))
    id1_str = id1_bin.zfill(max_len)
    id2_str = id2_bin.zfill(max_len)
    
    losing_bit = -1
    winner = None
    for bit_idx in range(max_len):
        b1 = id1_str[bit_idx]
        b2 = id2_str[bit_idx]
        if b1 != b2:
            losing_bit = bit_idx
            winner = "Message 1 (0x{:X})".format(id1) if b1 == '0' else "Message 2 (0x{:X})".format(id2)
            break
            
    if winner is None:
        winner = "Tie (Identical IDs - Content/RTR/IDE arbitration applies)"
        
    return {
        "id1_hex": hex(id1),
        "id2_hex": hex(id2),
        "id1_bin": id1_str,
        "id2_bin": id2_str,
        "winner": winner,
        "arbitration_bit_index": losing_bit
    }

def main():
    parser = argparse.ArgumentParser(description="CAN & CAN FD Bit Timing and Bus Calculation Tool")
    parser.add_argument("--clock", "-c", type=str, default="80MHz", help="CAN peripheral clock (e.g., '80MHz', '40MHz', '16MHz')")
    parser.add_argument("--baud", "-b", type=int, default=500000, help="Target nominal bitrate (bps, default: 500000)")
    parser.add_argument("--sp", type=float, default=87.5, help="Target Sample Point %% (default: 87.5)")
    parser.add_argument("--fd", action="store_true", help="Enable CAN FD mode")
    parser.add_argument("--data-baud", type=int, default=2000000, help="Target CAN FD data phase bitrate (bps, default: 2000000)")
    parser.add_argument("--frame", action="store_true", help="Calculate frame duration and efficiency")
    parser.add_argument("--dlc", type=int, default=8, help="Data payload in bytes (0-8 for CAN, 0-64 for CAN FD)")
    parser.add_argument("--ext", action="store_true", help="Use 29-bit Extended CAN Identifier")
    parser.add_argument("--arbitrate", action="store_true", help="Simulate arbitration between two IDs")
    parser.add_argument("--id1", type=lambda x: int(x, 0), default=0x120, help="Identifier 1 (hex or int)")
    parser.add_argument("--id2", type=lambda x: int(x, 0), default=0x123, help="Identifier 2 (hex or int)")
    
    args = parser.parse_args()
    
    if args.arbitrate:
        res = arbitrate(args.id1, args.id2, args.ext, args.ext)
        print("=" * 68)
        print(" CAN BITWISE ARBITRATION RESOLUTION REPORT")
        print("=" * 68)
        print(f"Message 1 ID : {res['id1_hex']} (Binary: {res['id1_bin']})")
        print(f"Message 2 ID : {res['id2_hex']} (Binary: {res['id2_bin']})")
        print(f"Arbiter Bit  : Bit {res['arbitration_bit_index']} (MSB = 0)")
        print(f"Outcome      : >>> {res['winner']} WINS BUS ACCESS <<<")
        print("Rule         : Dominant (0) overwrites Recessive (1). Zero-latency preemption.")
        print("=" * 68)
        return

    f_clk = parse_frequency(args.clock)
    
    print("=" * 72)
    print(" CAN / CAN FD BIT TIMING & BUS PARAMETER REPORT")
    print("=" * 72)
    print(f"Peripheral Clock (f_clk) : {f_clk:,.0f} Hz ({f_clk/1e6:.2f} MHz)")
    print(f"Target Nominal Bitrate   : {args.baud:,} bps ({args.baud/1e3:.1f} kbps)")
    print(f"Target Sample Point      : {args.sp:.1f}%")
    
    nom_timing = calculate_can_timing(f_clk, args.baud, args.sp)
    if not nom_timing:
        print(f"Error: Unable to find valid CAN timing divisor for f_clk={f_clk}Hz and baud={args.baud}bps.")
        sys.exit(1)
        
    print("-" * 72)
    print(" 1. NOMINAL (ARBITRATION) BIT TIMING REGISTERS")
    print("-" * 72)
    print(f"  Prescaler (BRP)        : {nom_timing['brp']}")
    print(f"  Time Quantum (tq)      : {nom_timing['tq_ns']:.2f} ns")
    print(f"  Nominal Bit Time (NBT) : {nom_timing['bit_time_ns']:.2f} ns ({nom_timing['total_tq']} Tq)")
    print(f"  Sync_Seg               : {nom_timing['sync_seg']} Tq")
    print(f"  Prop_Seg               : {nom_timing['prop_seg']} Tq")
    print(f"  Phase_Seg1             : {nom_timing['phase_seg1']} Tq")
    print(f"  Phase_Seg2             : {nom_timing['phase_seg2']} Tq")
    print(f"  TSEG1 (Prop + Phase1)  : {nom_timing['tseg1']} Tq")
    print(f"  TSEG2 (Phase2)         : {nom_timing['tseg2']} Tq")
    print(f"  SJW (Sync Jump Width)  : {nom_timing['sjw']} Tq")
    print(f"  Actual Sample Point    : {nom_timing['sample_point']:.2f}% (Error: {abs(nom_timing['sample_point'] - args.sp):.2f}%)")
    
    if args.fd:
        print("-" * 72)
        print(" 2. CAN FD FAST DATA PHASE BIT TIMING")
        print("-" * 72)
        print(f"  Target Data Bitrate    : {args.data_baud:,} bps ({args.data_baud/1e6:.2f} Mbps)")
        data_timing = calculate_can_timing(f_clk, args.data_baud, target_sp=75.0)
        if data_timing:
            print(f"  Data Prescaler (DBRP)  : {data_timing['brp']}")
            print(f"  Data Time Quantum (tq) : {data_timing['tq_ns']:.2f} ns")
            print(f"  Data Bit Time (DBT)    : {data_timing['bit_time_ns']:.2f} ns ({data_timing['total_tq']} Tq)")
            print(f"  DTSEG1 (Prop + Phase1) : {data_timing['tseg1']} Tq")
            print(f"  DTSEG2 (Phase2)        : {data_timing['tseg2']} Tq")
            print(f"  DSJW                   : {data_timing['sjw']} Tq")
            print(f"  Data Sample Point      : {data_timing['sample_point']:.2f}%")
        else:
            print("  Warning: No exact integer timing found for data phase. Consider using an 80MHz or 40MHz CAN clock.")
            
    print("-" * 72)
    print(" 3. FRAME DURATION & BUS EFFICIENCY ANALYSIS")
    print("-" * 72)
    frame_info = calculate_frame_bits(args.id1, args.dlc, args.ext, args.fd)
    t_bit_us = nom_timing['bit_time_ns'] / 1000.0
    nom_duration_us = frame_info['nominal_bits'] * t_bit_us
    worst_duration_us = frame_info['worst_case_bits'] * t_bit_us
    
    print(f"  Frame Architecture     : {frame_info['type']}")
    print(f"  Data Payload (DLC)     : {frame_info['dlc_bytes']} Bytes ({frame_info['dlc_bytes']*8} bits)")
    print(f"  Nominal Frame Bits     : {frame_info['nominal_bits']} bits ({nom_duration_us:.2f} µs)")
    print(f"  Worst-Case Frame Bits  : {frame_info['worst_case_bits']} bits ({worst_duration_us:.2f} µs with stuff bits)")
    print(f"  Payload Efficiency     : {frame_info['efficiency_nominal']:.1f}% (Nominal) | {frame_info['efficiency_worst']:.1f}% (Worst-Case)")
    print(f"  Max Frames/sec (100%)  : {1_000_000.0 / worst_duration_us:,.0f} msgs/s at full bus load")
    print("=" * 72)

if __name__ == '__main__':
    main()
