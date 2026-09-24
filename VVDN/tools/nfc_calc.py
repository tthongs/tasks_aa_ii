#!/usr/bin/env python3
"""
NFC Antenna Inductance, Matching Network, Q-Factor & NDEF Calculator
VVDN Engineering Hub & Protocol Knowledge Base

Usage:
    python3 nfc_calc.py --antenna --width-mm 45 --height-mm 35 --turns 4 --track-mm 0.5 --space-mm 0.5
    python3 nfc_calc.py --matching --inductance-uh 1.85 --r-ant 1.1 --q-target 25 --r-load 50
    python3 nfc_calc.py --ndef-uri "https://vvdntech.com"
    python3 nfc_calc.py --ndef-text "Hello VVDN NFC" --lang "en"
"""

import argparse
import math
import sys

FC = 13.56e6  # 13.56 MHz carrier frequency
OMEGA = 2 * math.pi * FC
MU0 = 4 * math.pi * 1e-7  # Permeability of free space

URI_PREFIXES = {
    0x00: "",
    0x01: "http://www.",
    0x02: "https://www.",
    0x03: "http://",
    0x04: "https://",
    0x05: "telnet://",
    0x06: "mailto:",
    0x07: "ftp://anonymous:anonymous@",
    0x08: "ftp://ftp.",
    0x09: "ftps://",
    0x0A: "sftp://",
    0x0D: "tel:",
}


def calc_rectangular_inductance(w_mm: float, h_mm: float, turns: int, track_w_mm: float, space_mm: float) -> float:
    """
    Calculate planar rectangular loop antenna inductance on PCB in microhenries (uH)
    using the modified Wheeler / Harold formula.
    """
    # Outer dimensions in meters
    a_out = w_mm * 1e-3
    b_out = h_mm * 1e-3
    t_w = track_w_mm * 1e-3
    t_s = space_mm * 1e-3
    t_thick = 35e-6  # 1 oz copper thickness = 35 um

    # Inner dimensions
    a_in = a_out - 2 * turns * t_w - 2 * (turns - 1) * t_s
    b_in = b_out - 2 * turns * t_w - 2 * (turns - 1) * t_s

    if a_in <= 0 or b_in <= 0:
        raise ValueError("Antenna dimensions too small for the specified number of turns and spacing!")

    a = (a_out + a_in) / 2.0
    b = (b_out + b_in) / 2.0

    # Geometric mean distance approximation for planar spiral coil
    d_diag = math.sqrt(a**2 + b**2)
    term1 = -2 * (a + b) + 2 * d_diag
    term2 = -a * math.log((a + d_diag) / b) - b * math.log((b + d_diag) / a)
    term3 = a * math.log((2 * a) / (t_w + t_thick)) + b * math.log((2 * b) / (t_w + t_thick))

    l_single = (MU0 / math.pi) * (term1 + term2 + term3)
    l_total_h = l_single * (turns ** 1.8)
    return l_total_h * 1e6  # Return in uH


def calc_matching_network(l_uh: float, r_ant: float, q_target: float, r_load: float, l0_nh: float = 560.0):
    """
    Calculate damping resistor, matching capacitors, and EMC filter.
    """
    l_h = l_uh * 1e-6
    # Natural Q without damping
    q_natural = (OMEGA * l_h) / r_ant
    bw_natural_khz = (FC / q_natural) / 1e3

    # Total resistance required for target Q
    r_total_req = (OMEGA * l_h) / q_target
    r_q_series = max(0.0, (r_total_req - r_ant) / 2.0)  # Divided across TX1 and TX2

    bw_target_khz = (FC / q_target) / 1e3

    # Parallel matching capacitance (Cp)
    c_p = (1.0 / (OMEGA**2 * l_h)) * (1.0 - (r_total_req / r_load))
    if c_p < 0:
        c_p = 1.0 / (OMEGA**2 * l_h)

    # Series matching capacitance (Cs)
    c_s = 1.0 / (OMEGA * math.sqrt(r_load * r_total_req))

    # EMC Filter cutoff and C0 (assuming standard 20 MHz cutoff)
    l0_h = l0_nh * 1e-9
    f_emc = 20.0e6
    c0 = 1.0 / (4 * (math.pi**2) * (f_emc**2) * l0_h)

    return {
        "q_natural": q_natural,
        "bw_natural_khz": bw_natural_khz,
        "r_total_req": r_total_req,
        "r_q_series": r_q_series,
        "bw_target_khz": bw_target_khz,
        "c_parallel_pf": c_p * 1e12,
        "c_series_pf": c_s * 1e12,
        "c0_emc_pf": c0 * 1e12,
        "l0_emc_nh": l0_nh,
    }


def encode_ndef_uri(uri: str) -> bytes:
    prefix_code = 0x00
    suffix = uri

    # Find longest matching prefix
    for code, prefix in sorted(URI_PREFIXES.items(), key=lambda x: len(x[1]), reverse=True):
        if prefix and uri.startswith(prefix):
            prefix_code = code
            suffix = uri[len(prefix):]
            break

    payload = bytes([prefix_code]) + suffix.encode("utf-8")
    type_field = b"U"

    mb = 1
    me = 1
    cf = 0
    sr = 1 if len(payload) <= 255 else 0
    il = 0
    tnf = 0x01  # Well-Known

    header = (mb << 7) | (me << 6) | (cf << 5) | (sr << 4) | (il << 3) | tnf

    ndef = bytearray()
    ndef.append(header)
    ndef.append(len(type_field))
    if sr:
        ndef.append(len(payload))
    else:
        ndef.extend(len(payload).to_bytes(4, byteorder="big"))
    ndef.extend(type_field)
    ndef.extend(payload)
    return bytes(ndef)


def encode_ndef_text(text: str, lang: str = "en") -> bytes:
    lang_bytes = lang.encode("ascii")
    status_byte = len(lang_bytes) & 0x3F  # UTF-8 (bit 7 = 0)
    payload = bytes([status_byte]) + lang_bytes + text.encode("utf-8")
    type_field = b"T"

    header = (1 << 7) | (1 << 6) | (0 << 5) | (1 << 4) | (0 << 3) | 0x01
    ndef = bytearray()
    ndef.append(header)
    ndef.append(len(type_field))
    ndef.append(len(payload))
    ndef.extend(type_field)
    ndef.extend(payload)
    return bytes(ndef)


def main():
    parser = argparse.ArgumentParser(description="NFC RF Antenna & NDEF Protocol Calculator")
    parser.add_argument("--antenna", action="store_true", help="Calculate loop antenna inductance from geometry")
    parser.add_argument("--width-mm", type=float, default=45.0, help="Antenna outer width in mm (default: 45)")
    parser.add_argument("--height-mm", type=float, default=35.0, help="Antenna outer height in mm (default: 35)")
    parser.add_argument("--turns", "-n", type=int, default=4, help="Number of turns (default: 4)")
    parser.add_argument("--track-mm", type=float, default=0.5, help="Conductor trace width in mm (default: 0.5)")
    parser.add_argument("--space-mm", type=float, default=0.5, help="Inter-turn spacing in mm (default: 0.5)")

    parser.add_argument("--matching", action="store_true", help="Calculate matching network capacitors and Q damping")
    parser.add_argument("--inductance-uh", type=float, default=1.85, help="Antenna inductance in uH (default: 1.85)")
    parser.add_argument("--r-ant", type=float, default=1.1, help="Antenna series resistance in Ohms (default: 1.1)")
    parser.add_argument("--q-target", type=float, default=25.0, help="Target Q factor (default: 25.0 for 106 kbps)")
    parser.add_argument("--r-load", type=float, default=50.0, help="Transceiver target load resistance in Ohms (default: 50.0)")

    parser.add_argument("--ndef-uri", type=str, help="Generate binary NDEF URI record (e.g. 'https://vvdntech.com')")
    parser.add_argument("--ndef-text", type=str, help="Generate binary NDEF Text record (e.g. 'Hello NFC')")
    parser.add_argument("--lang", type=str, default="en", help="Language code for text record (default: 'en')")

    args = parser.parse_args()

    if not (args.antenna or args.matching or args.ndef_uri or args.ndef_text):
        parser.print_help()
        sys.exit(0)

    print("================================================================================")
    print("           VVDN Engineering Hub - NFC & RFID Protocol Calculator               ")
    print("================================================================================")

    if args.antenna:
        try:
            l_uh = calc_rectangular_inductance(args.width_mm, args.height_mm, args.turns, args.track_mm, args.space_mm)
            c_res_pf = (1.0 / (OMEGA**2 * (l_uh * 1e-6))) * 1e12
            print(f"[*] Antenna Dimensions     : {args.width_mm:.1f} mm x {args.height_mm:.1f} mm")
            print(f"[*] Conductor Turns        : {args.turns} turns (Trace: {args.track_mm} mm, Space: {args.space_mm} mm)")
            print(f"[*] Calculated Inductance  : {l_uh:.3f} uH")
            print(f"[*] 13.56 MHz Tuning Cap   : {c_res_pf:.1f} pF (Total tank capacitance required)")
            print("--------------------------------------------------------------------------------")
        except Exception as e:
            print(f"[!] Error in antenna calculation: {e}")

    if args.matching:
        res = calc_matching_network(args.inductance_uh, args.r_ant, args.q_target, args.r_load)
        print(f"[*] Inputs: L_ant = {args.inductance_uh:.2f} uH, R_ant = {args.r_ant:.2f} Ohm, Target Q = {args.q_target:.1f}")
        print(f"[*] Natural Un-damped Q    : {res['q_natural']:.1f} (Bandwidth: {res['bw_natural_khz']:.1f} kHz)")
        print(f"[*] Target Bandwidth (-3dB): {res['bw_target_khz']:.1f} kHz")
        print(f"[*] Damping Resistors (RQ) : 2x {res['r_q_series']:.2f} Ohms (one per differential TX leg)")
        print(f"[*] Parallel Cap (C_par)   : {res['c_parallel_pf']:.1f} pF (C0G / NP0, 50V rated)")
        print(f"[*] Series Cap (C_ser)     : {res['c_series_pf']:.1f} pF (C0G / NP0, 50V rated)")
        print(f"[*] EMC Low-Pass Filter    : L0 = {res['l0_emc_nh']:.0f} nH, C0 = {res['c0_emc_pf']:.1f} pF (~20 MHz cutoff)")
        if args.q_target > 30:
            print("[!] WARNING: Target Q > 30 may cause pause ringing in ISO 14443A and subcarrier attenuation!")
        elif args.q_target < 10:
            print("[!] NOTE: Target Q < 10 provides excellent 848 kbps bandwidth, but shortens operating distance.")
        else:
            print("[+] Target Q is optimal for standard ISO 14443 Type A (106 kbps).")
        print("--------------------------------------------------------------------------------")

    if args.ndef_uri:
        ndef_bytes = encode_ndef_uri(args.ndef_uri)
        hex_str = " ".join(f"{b:02X}" for b in ndef_bytes)
        t2t_tlv = f"03 {len(ndef_bytes):02X} {hex_str} FE"
        print(f"[*] Target URI             : {args.ndef_uri}")
        print(f"[*] NDEF Binary Record     : {hex_str}")
        print(f"[*] Record Length          : {len(ndef_bytes)} bytes")
        print(f"[*] Type 2 Tag TLV Wrapper : {t2t_tlv}")
        print("--------------------------------------------------------------------------------")

    if args.ndef_text:
        ndef_bytes = encode_ndef_text(args.ndef_text, args.lang)
        hex_str = " ".join(f"{b:02X}" for b in ndef_bytes)
        t2t_tlv = f"03 {len(ndef_bytes):02X} {hex_str} FE"
        print(f"[*] Target Text            : \"{args.ndef_text}\" [lang: {args.lang}]")
        print(f"[*] NDEF Binary Record     : {hex_str}")
        print(f"[*] Record Length          : {len(ndef_bytes)} bytes")
        print(f"[*] Type 2 Tag TLV Wrapper : {t2t_tlv}")
        print("--------------------------------------------------------------------------------")


if __name__ == "__main__":
    main()
