#!/usr/bin/env python3
"""
EVSE Control Pilot, Charging Current & Power Calculator
VVDN Engineering Hub - EVSE / Smart Charging Engineering Toolkit

Usage:
    # 1. Calculate Allowable Current & Power from PWM Duty Cycle:
    python3 tools/evse_calc.py --mode pwm --duty 53.3 --phase 3

    # 2. Calculate Required PWM Duty Cycle for Target Current:
    python3 tools/evse_calc.py --mode current --current 32 --phase 3

    # 3. Decode Control Pilot (CP) Voltage State:
    python3 tools/evse_calc.py --mode cp --voltage 6.0

    # 4. Decode Proximity Pilot (PP) Cable Resistor:
    python3 tools/evse_calc.py --mode pp --resistance 220

    # 5. Full Charging Session Evaluation:
    python3 tools/evse_calc.py --mode full --current 32 --phase 3 --voltage-grid 400
"""

import argparse
import sys
import math

# IEC 61851-1 / SAE J1772 CP Duty Cycle to Current Formulas
def duty_to_current(duty_pct: float) -> tuple[float, str]:
    """
    Converts CP 1kHz PWM Duty Cycle (%) to Maximum Charging Current (A).
    Returns (current_amperes, description).
    """
    if duty_pct < 3.0:
        return 0.0, "No charging allowed / Error state"
    elif 3.0 <= duty_pct <= 7.0:
        return 0.0, "ISO 15118 / DIN 70121 Digital Communication required (GreenPHY PLC)"
    elif 7.0 < duty_pct < 8.0:
        return 0.0, "Illegal / Reserved Duty Cycle window"
    elif 8.0 <= duty_pct < 10.0:
        return 6.0, "Minimum 6A charging limit"
    elif 10.0 <= duty_pct <= 85.0:
        current = duty_pct * 0.6
        return current, f"Standard Linear Range: Duty * 0.6 = {current:.2f} A"
    elif 85.0 < duty_pct <= 96.0:
        current = (duty_pct - 64.0) * 2.5
        return current, f"High-Current Range: (Duty - 64) * 2.5 = {current:.2f} A"
    elif 96.0 < duty_pct <= 97.0:
        return 80.0, "Maximum allowed AC Level 2 current (80 A)"
    elif duty_pct > 97.0:
        return 0.0, "Continuous 100% HIGH indicates State A/B DC Pilot (No PWM)"
    return 0.0, "Invalid Duty Cycle"

def current_to_duty(current_a: float) -> tuple[float, str]:
    """
    Converts Target Current (A) to required CP 1kHz PWM Duty Cycle (%).
    """
    if current_a < 6.0:
        return 0.0, "Current is below IEC 61851-1 minimum allowable charging current (6 A)"
    elif 6.0 <= current_a <= 51.0:
        duty = current_a / 0.6
        return duty, f"Standard Range: Current / 0.6 = {duty:.2f} %"
    elif 51.0 < current_a <= 80.0:
        duty = (current_a / 2.5) + 64.0
        return duty, f"High-Current Range: (Current / 2.5) + 64 = {duty:.2f} %"
    else:
        return 0.0, "Exceeds maximum allowable AC charging current under IEC 61851-1 (80 A)"

def decode_cp_voltage(v_cp: float) -> tuple[str, str, str]:
    """
    Decodes Control Pilot Voltage into IEC 61851-1 Charging States.
    Returns (State_Letter, Description, Contactor_Status).
    """
    if 11.0 <= v_cp <= 13.0:
        return "State A", "EV Not Connected (Standby / Disconnected)", "Contactor OPEN (De-energized)"
    elif 8.2 <= v_cp <= 9.8:
        return "State B", "EV Connected, Waiting / Not Ready to Charge", "Contactor OPEN (De-energized)"
    elif 5.5 <= v_cp <= 6.5:
        return "State C", "EV Connected, Ready to Charge, Ventilation Not Required", "Contactor CLOSED (Energized / Charging)"
    elif 2.6 <= v_cp <= 3.4:
        return "State D", "EV Connected, Ready to Charge, Ventilation Required", "Contactor CLOSED (Energized if Exhaust ON)"
    elif -1.0 <= v_cp <= 1.0:
        return "State E", "Error / Pilot Shorted to Ground or No EVSE Power", "Contactor OPEN (Emergency Trip)"
    elif -13.0 <= v_cp <= -11.0:
        return "State F", "Critical Error / Missing Vehicle Diode (Diode Fault)", "Contactor OPEN (Lockout)"
    else:
        return "Unknown", f"Voltage {v_cp:.2f}V is out of standard tolerance bounds", "Contactor OPEN (Fault Trip)"

def decode_pp_resistance(r_ohms: float) -> tuple[str, int]:
    """
    Decodes Proximity Pilot (PP) resistor value (IEC 62196 Type 2).
    Returns (Cable_Specification, Max_Current_A).
    """
    # Tolerances are typically +/- 10%
    if 1300 <= r_ohms <= 1700:
        return "13 A Cable Assembly (1.5 kΩ)", 13
    elif 610 <= r_ohms <= 750:
        return "20 A Cable Assembly (680 Ω)", 20
    elif 190 <= r_ohms <= 250:
        return "32 A Cable Assembly (220 Ω)", 32
    elif 90 <= r_ohms <= 120:
        return "63 A Cable Assembly (100 Ω)", 63
    else:
        return f"Unknown / Invalid Resistor ({r_ohms:.1f} Ω)", 0

def calculate_power(current_a: float, grid_voltage_v: float, phases: int, pf: float = 1.0) -> float:
    """Calculates active charging power in kW."""
    if phases == 1:
        # P = V * I * PF
        return (grid_voltage_v * current_a * pf) / 1000.0
    elif phases == 3:
        # P = sqrt(3) * V_LL * I * PF
        return (math.sqrt(3) * grid_voltage_v * current_a * pf) / 1000.0
    return 0.0

def main():
    parser = argparse.ArgumentParser(
        description="EVSE Control Pilot, Charging Current & Power Calculator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 tools/evse_calc.py --mode pwm --duty 53.3 --phase 3
  python3 tools/evse_calc.py --mode current --current 32 --phase 3 --voltage-grid 400
  python3 tools/evse_calc.py --mode cp --voltage 6.0
  python3 tools/evse_calc.py --mode pp --resistance 220
  python3 tools/evse_calc.py --mode full --current 16 --phase 1 --voltage-grid 230
        """
    )
    parser.add_argument("--mode", choices=["pwm", "current", "cp", "pp", "full"], default="full",
                        help="Calculation mode: pwm, current, cp (pilot), pp (proximity), or full")
    parser.add_argument("--duty", type=float, default=53.3, help="CP PWM Duty Cycle in percentage (e.g., 53.3 for 32A)")
    parser.add_argument("--current", type=float, default=32.0, help="Target charging current in Amperes (6A to 80A)")
    parser.add_argument("--phase", type=int, choices=[1, 3], default=3, help="Grid phases: 1 (Single-phase) or 3 (Three-phase)")
    parser.add_argument("--voltage-grid", type=float, default=None, help="Grid Line Voltage in Volts (e.g., 230 for 1-ph, 400 for 3-ph)")
    parser.add_argument("--voltage", type=float, default=6.0, help="Measured Control Pilot Voltage in Volts (e.g. 12, 9, 6, 3, 0, -12)")
    parser.add_argument("--resistance", type=float, default=220.0, help="Measured PP Resistor in Ohms (e.g. 1500, 680, 220, 100)")
    parser.add_argument("--pf", type=float, default=0.99, help="Power Factor (default: 0.99)")

    args = parser.parse_args()

    # Determine default grid voltage if not specified
    if args.voltage_grid is None:
        grid_v = 230.0 if args.phase == 1 else 400.0
    else:
        grid_v = args.voltage_grid

    print("=" * 72)
    print("      VVDN EVSE LOW VOLTAGE CONTROLLER: PILOT & POWER REPORT")
    print("=" * 72)

    if args.mode in ["pwm", "full"]:
        curr, desc = duty_to_current(args.duty)
        p_kw = calculate_power(curr, grid_v, args.phase, args.pf)
        print(f"\n[1] CONTROL PILOT PWM DUTY CYCLE ANALYSIS (Duty = {args.duty:.2f}%):")
        print(f"  • Allowable AC Current       : {curr:.2f} A")
        print(f"  • IEC 61851-1 Formula        : {desc}")
        print(f"  • Grid Topology              : {args.phase}-Phase ({grid_v:.0f} V AC Line-to-Line)")
        print(f"  • Maximum Active Power       : {p_kw:.2f} kW (@ PF = {args.pf})")

    if args.mode in ["current", "full"]:
        duty, desc = current_to_duty(args.current)
        p_kw = calculate_power(args.current, grid_v, args.phase, args.pf)
        print(f"\n[2] TARGET CHARGING CURRENT SIZING (Current = {args.current:.1f} A):")
        print(f"  • Required PWM Duty Cycle    : {duty:.2f} % (1.0 kHz frequency)")
        print(f"  • IEC 61851-1 Formula        : {desc}")
        print(f"  • Grid Power Transfer        : {p_kw:.2f} kW ({args.phase}-Phase, {grid_v:.0f} V)")

    if args.mode in ["cp", "full"]:
        state, s_desc, c_status = decode_cp_voltage(args.voltage)
        print(f"\n[3] CONTROL PILOT (CP) VOLTAGE DECODING (V_cp = {args.voltage:.2f} V):")
        print(f"  • Vehicle Operational State  : {state}")
        print(f"  • State Description          : {s_desc}")
        print(f"  • AC Main Contactor Action   : {c_status}")

    if args.mode in ["pp", "full"]:
        cable_spec, max_a = decode_pp_resistance(args.resistance)
        print(f"\n[4] PROXIMITY PILOT (PP) CABLE RATING (R_pp = {args.resistance:.1f} Ω):")
        print(f"  • Cable Harness Rating       : {cable_spec}")
        print(f"  • Hardware Current Interlock : Max {max_a} A allowed by cable")
        if args.mode == "full" and args.current > max_a and max_a > 0:
            print(f"  [!] SAFETY FAULT: Target current ({args.current}A) exceeds cable capability ({max_a}A)!")
            print(f"      Action: EVSE firmware must clamp PWM duty cycle to match {max_a}A max.")

    # RCM Fault Response Times (IEC 62955)
    if args.mode == "full":
        print("\n[5] RESIDUAL CURRENT MONITORING (RCM) SAFETY BENCHMARKS (IEC 62955):")
        print("  • 6 mA DC Fault Trip Time    : < 10.0 s (Contactor trip mandatory)")
        print("  • 60 mA DC Fault Trip Time   : < 150 ms")
        print("  • 300 mA DC Fault Trip Time  : < 40 ms (Instantaneous trip)")
        print("  • 30 mA AC Fault Trip Time   : < 300 ms (General RCD protection)")

    print("=" * 72)

if __name__ == "__main__":
    main()
