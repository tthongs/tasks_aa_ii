#!/usr/bin/env python3
"""
I2C Pull-Up Resistor, Bus Capacitance & Timing Calculator
VVDN Engineering Hub - Hardware & Embedded Protocol Toolkit

Usage:
    # 1. Calculate Pull-Up Resistor Range (Rp min & Rp max):
    python3 tools/i2c_calc.py --mode rp --vdd 3.3 --cap 150 --speed fast

    # 2. Estimate Rise Time and Validate against I2C Spec:
    python3 tools/i2c_calc.py --mode tr --vdd 3.3 --cap 200 --rp 2.2k --speed fast

    # 3. Decode & Convert 7-bit / 8-bit I2C Slave Addresses:
    python3 tools/i2c_calc.py --mode addr --address 0x50

    # 4. Full Bus Timing & Parameter Analysis:
    python3 tools/i2c_calc.py --mode full --vdd 3.3 --cap 180 --rp 4.7k --speed fast
"""

import argparse
import sys
import math

# Standard I2C Specification Limits (NXP UM10204)
I2C_SPECS = {
    "standard": {
        "name": "Standard-mode (Sm)",
        "max_freq_khz": 100,
        "max_tr_ns": 1000,
        "max_tf_ns": 300,
        "max_cb_pf": 400,
        "min_tlow_us": 4.7,
        "min_thigh_us": 4.0,
        "min_tsu_dat_ns": 250,
        "max_thd_dat_us": 3.45,
        "min_tsu_sta_us": 4.7,
        "min_thd_sta_us": 4.0,
        "min_tsu_sto_us": 4.0,
        "min_tbuf_us": 4.7,
        "standard_iol_ma": 3.0,
        "standard_vol_v": 0.4,
    },
    "fast": {
        "name": "Fast-mode (Fm)",
        "max_freq_khz": 400,
        "max_tr_ns": 300,
        "max_tf_ns": 300,
        "max_cb_pf": 400,
        "min_tlow_us": 1.3,
        "min_thigh_us": 0.6,
        "min_tsu_dat_ns": 100,
        "max_thd_dat_us": 0.9,
        "min_tsu_sta_us": 0.6,
        "min_thd_sta_us": 0.6,
        "min_tsu_sto_us": 0.6,
        "min_tbuf_us": 1.3,
        "standard_iol_ma": 3.0,
        "standard_vol_v": 0.4,
    },
    "fastplus": {
        "name": "Fast-mode Plus (Fm+)",
        "max_freq_khz": 1000,
        "max_tr_ns": 120,
        "max_tf_ns": 120,
        "max_cb_pf": 550,
        "min_tlow_us": 0.5,
        "min_thigh_us": 0.26,
        "min_tsu_dat_ns": 50,
        "max_thd_dat_us": 0.45,
        "min_tsu_sta_us": 0.26,
        "min_thd_sta_us": 0.26,
        "min_tsu_sto_us": 0.26,
        "min_tbuf_us": 0.5,
        "standard_iol_ma": 20.0,
        "standard_vol_v": 0.4,
    },
    "highspeed": {
        "name": "High-speed mode (Hs-mode)",
        "max_freq_khz": 3400,
        "max_tr_ns": 80,  # for Cb = 100 pF
        "max_tf_ns": 40,
        "max_cb_pf": 400,
        "min_tlow_us": 0.16,
        "min_thigh_us": 0.06,
        "min_tsu_dat_ns": 10,
        "max_thd_dat_us": 0.07,
        "min_tsu_sta_us": 0.16,
        "min_thd_sta_us": 0.16,
        "min_tsu_sto_us": 0.16,
        "min_tbuf_us": 0.16,
        "standard_iol_ma": 3.0,
        "standard_vol_v": 0.4,
    },
}

# Standard E24 Resistor values
E24_VALUES = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

def get_standard_resistors(r_min: float, r_max: float):
    """Find all standard E24 resistor values that fit within [r_min, r_max]."""
    matches = []
    decades = [100, 1000, 10000, 100000]
    for dec in decades:
        for val in E24_VALUES:
            r = val * dec
            if r_min <= r <= r_max:
                matches.append(r)
    return matches

def parse_resistance(r_str: str) -> float:
    """Parse resistor string such as 2.2k, 4k7, 4700, 10K."""
    r_str = r_str.strip().lower()
    if 'k' in r_str:
        if r_str.endswith('k'):
            return float(r_str[:-1]) * 1000.0
        parts = r_str.split('k')
        if len(parts) == 2 and parts[1].isdigit():
            return float(f"{parts[0]}.{parts[1]}") * 1000.0
        return float(parts[0]) * 1000.0
    return float(r_str)

def check_reserved_address(addr_7bit: int) -> str:
    """Check if a 7-bit address falls in I2C reserved groups."""
    if addr_7bit == 0x00:
        return "General Call / START Byte"
    elif addr_7bit == 0x01:
        return "CBUS Address"
    elif addr_7bit == 0x02:
        return "Reserved for different bus format"
    elif addr_7bit == 0x03:
        return "Reserved for future purpose"
    elif 0x04 <= addr_7bit <= 0x07:
        return "High-Speed (Hs) Mode Master Code"
    elif 0x78 <= addr_7bit <= 0x7B:
        return "10-bit Target Addressing Header"
    elif 0x7C <= addr_7bit <= 0x7F:
        return "Device ID / Reserved"
    return "Standard Target Address"

def calculate_rp(vdd: float, cb_pf: float, mode_key: str, iol_ma: float, vol_v: float):
    spec = I2C_SPECS[mode_key]
    tr_max_ns = spec["max_tr_ns"]
    
    # Rp(min) = (Vdd - Vol) / Iol
    rp_min_ohms = (vdd - vol_v) / (iol_ma * 1e-3)
    
    # Rp(max) = tr_max / (0.8473 * Cb)
    # where ln(0.7) - ln(0.3) = 0.8472978...
    k = 0.84729786
    rp_max_ohms = (tr_max_ns * 1e-9) / (k * (cb_pf * 1e-12))
    
    return rp_min_ohms, rp_max_ohms

def calculate_rise_time(rp_ohms: float, cb_pf: float) -> float:
    """Calculate 30% to 70% rise time in nanoseconds."""
    k = 0.84729786
    tr_s = k * rp_ohms * (cb_pf * 1e-12)
    return tr_s * 1e9

def main():
    parser = argparse.ArgumentParser(
        description="I2C Pull-Up Resistor, Bus Capacitance & Timing Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/i2c_calc.py --mode rp --vdd 3.3 --cap 150 --speed fast
  python3 tools/i2c_calc.py --mode tr --vdd 3.3 --cap 200 --rp 4.7k --speed fast
  python3 tools/i2c_calc.py --mode addr --address 0x68
  python3 tools/i2c_calc.py --mode full --vdd 3.3 --cap 180 --rp 2.2k --speed fast
        """
    )
    parser.add_argument("--mode", choices=["rp", "tr", "addr", "full"], default="full",
                        help="Calculation mode: 'rp' (sizing), 'tr' (rise time), 'addr' (address decoder), 'full' (all)")
    parser.add_argument("--vdd", type=float, default=3.3, help="Bus supply voltage in Volts (e.g., 3.3, 5.0, 1.8)")
    parser.add_argument("--cap", type=float, default=150.0, help="Total bus capacitance Cb in pF (default: 150 pF)")
    parser.add_argument("--rp", type=str, default="2.2k", help="Pull-up resistor value (e.g., '2.2k', '4.7k', '10k')")
    parser.add_argument("--speed", choices=["standard", "fast", "fastplus", "highspeed"], default="fast",
                        help="I2C speed mode (default: 'fast' 400kHz)")
    parser.add_argument("--iol", type=float, default=None, help="Sink current capacity Iol in mA (default: 3mA for Sm/Fm, 20mA for Fm+)")
    parser.add_argument("--vol", type=float, default=0.4, help="Target maximum output low voltage Vol in V (default: 0.4V)")
    parser.add_argument("--address", type=str, default="0x50", help="I2C Address to analyze (e.g. '0x50', '0x68', '104')")
    
    args = parser.parse_args()
    mode_key = args.speed
    spec = I2C_SPECS[mode_key]
    
    iol_ma = args.iol if args.iol is not None else spec["standard_iol_ma"]
    vol_v = args.vol
    vdd = args.vdd
    cb_pf = args.cap
    rp_ohms = parse_resistance(args.rp)
    
    print("=" * 70)
    print("           VVDN I2C HARDWARE & TIMING CALCULATION REPORT")
    print("=" * 70)
    print(f" Protocol Profile        : {spec['name']} (up to {spec['max_freq_khz']} kHz)")
    print(f" Bus Voltage (Vdd)       : {vdd:.2f} V")
    print(f" Bus Capacitance (Cb)    : {cb_pf:.1f} pF (Max standard allowed: {spec['max_cb_pf']} pF)")
    print(f" Sink Current (Iol)      : {iol_ma:.1f} mA @ Vol={vol_v:.2f} V")
    print("-" * 70)
    
    if args.mode in ["rp", "full"]:
        rp_min, rp_max = calculate_rp(vdd, cb_pf, mode_key, iol_ma, vol_v)
        e24_candidates = get_standard_resistors(rp_min, rp_max)
        
        print("\n[1] PULL-UP RESISTOR SIZING (Rp):")
        print(f"  • Minimum Resistance (Rp_min) : {rp_min:.1f} Ω ({rp_min/1000.0:.2f} kΩ)")
        print(f"    Formula: (Vdd - Vol) / Iol = ({vdd} - {vol_v}) / {iol_ma*1e-3:.4f} A")
        print(f"  • Maximum Resistance (Rp_max) : {rp_max:.1f} Ω ({rp_max/1000.0:.2f} kΩ)")
        print(f"    Formula: tr_max / (0.8473 * Cb) = {spec['max_tr_ns']}ns / (0.8473 * {cb_pf}pF)")
        
        if rp_min > rp_max:
            print("\n  [!] CRITICAL WARNING: Rp_min > Rp_max!")
            print(f"      Total bus capacitance ({cb_pf} pF) is too high to achieve required rise time")
            print(f"      ({spec['max_tr_ns']} ns) while maintaining safe Iol sink current ({iol_ma} mA).")
            print("      Action: Reduce bus trace length, isolate devices with bus buffers, or upgrade to Fm+.")
        else:
            print(f"\n  • Recommended Standard E24 Values: ", end="")
            formatted_res = [f"{r/1000:.1f}kΩ" if r >= 1000 else f"{r:.0f}Ω" for r in e24_candidates]
            print(", ".join(formatted_res) if formatted_res else "None directly in E24 range")
            if e24_candidates:
                # Pick a balanced value near 40% of the range
                nominal_pick = e24_candidates[len(e24_candidates)//2]
                print(f"  • Best Balanced Choice       : {nominal_pick/1000.0:.1f} kΩ (Optimizes rise time vs power)")

    if args.mode in ["tr", "full"]:
        tr_est_ns = calculate_rise_time(rp_ohms, cb_pf)
        print(f"\n[2] RISE TIME & SIGNAL INTEGRITY (with selected Rp = {rp_ohms/1000.0:.2f} kΩ):")
        print(f"  • Estimated Rise Time (tr)   : {tr_est_ns:.1f} ns")
        print(f"  • Max Allowed Spec (tr_max)  : {spec['max_tr_ns']} ns")
        
        if tr_est_ns <= spec['max_tr_ns']:
            margin_pct = ((spec['max_tr_ns'] - tr_est_ns) / spec['max_tr_ns']) * 100.0
            print(f"  • Compliance Status          : PASS (Timing margin: +{margin_pct:.1f}%)")
        else:
            violation_pct = ((tr_est_ns - spec['max_tr_ns']) / spec['max_tr_ns']) * 100.0
            print(f"  • Compliance Status          : FAIL (Exceeds spec by +{violation_pct:.1f}%)")
            print("    Action: Decrease Rp value towards Rp_min to speed up the RC pull-up edge.")
            
        # Static bus power consumption when bus pulled low
        p_low_mw = ((vdd - vol_v)**2 / rp_ohms) * 1000.0
        print(f"  • Active Low Dissipation     : {p_low_mw:.2f} mW per active line (SDA or SCL)")

    if args.mode in ["addr", "full"]:
        raw_addr = args.address.strip()
        addr_val = int(raw_addr, 0)
        
        # Check if user entered 7-bit or 8-bit format
        is_8bit = addr_val > 0x7F
        if is_8bit:
            addr_7bit = addr_val >> 1
            write_byte = addr_val & 0xFE
            read_byte = addr_val | 0x01
        else:
            addr_7bit = addr_val
            write_byte = (addr_7bit << 1) & 0xFE
            read_byte = ((addr_7bit << 1) | 0x01) & 0xFF
            
        print(f"\n[3] I2C ADDRESS MATRIX & DECODING (Input: {raw_addr}):")
        if is_8bit:
            print("  [Note: Input address interpreted as 8-bit shifted address byte]")
        print(f"  • 7-Bit Target Address       : 0x{addr_7bit:02X} (Decimal: {addr_7bit})")
        print(f"  • 7-Bit Binary Representation : 0b{addr_7bit:07b}")
        print(f"  • 8-Bit Write Byte (R/W = 0)  : 0x{write_byte:02X} (0b{write_byte:08b})")
        print(f"  • 8-Bit Read Byte  (R/W = 1)  : 0x{read_byte:02X} (0b{read_byte:08b})")
        print(f"  • Address Classification      : {check_reserved_address(addr_7bit)}")

    print("=" * 70)

if __name__ == "__main__":
    main()
