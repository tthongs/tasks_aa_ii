# Alternative Converter Topologies for Smart Programmable Power Supply (85–265 V AC In, 5–20 V / 3 A DC Out)

Welcome to the **VVDN Engineering Hub Alternative Converter Topologies Dossier**. This knowledge base provides an exhaustive engineering analysis of how the **Smart Programmable Power Supply (SPPS)**—originally specified with a Quasi-Resonant (QR) Flyback converter (+24 V intermediate bus) and a 4-switch synchronous Buck-Boost post-regulator—can be engineered using **different converter architectures** across both the isolated AC-DC primary stage and the non-isolated DC-DC post-regulator stage.

---

## 1. Executive Summary & Design Scope

The engineering challenge remains constant across all architectures:
* **AC Input**: Universal mains ($85\,\text{V} \dots 265\,\text{V}$ AC RMS, $47\,\text{Hz} \dots 63\,\text{Hz}$).
* **DC Output**: Digitally programmable $5.0\,\text{V} \dots 20.0\,\text{V}$ DC at currents up to $3.0\,\text{A}$ ($60\,\text{W}$ continuous output, $72\,\text{W}$ peak intermediate stage power).
* **Control & Telemetry**: Dual-domain power metering, real-time efficiency computation ($\eta = P_{DC} / P_{AC}$ at $10\,\text{Hz}$), MicroSD logging, and USB SCPI interface.

While the baseline two-stage architecture (**QR Flyback @ 24V + 4-Switch Sync Buck-Boost**) delivers a balanced trade-off between component count, efficiency, and dynamic response, alternative topologies offer superior performance in specific application domains, such as **ultra-low BOM cost**, **lab-grade sub-millivolt output noise**, **extreme power density**, or **simplified single-mode digital control**.

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                 TOPOLOGY DESIGN SPACE: ISOLATED AC-DC & DC-DC POST-REGULATION                                  │
├────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────┤
│ ISOLATED PRIMARY AC-DC CONVERTER OPTIONS               │ NON-ISOLATED DC-DC POST-REGULATOR OPTIONS                              │
├────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ 1. **Quasi-Resonant (QR) Flyback** (Baseline, 24V bus) │ A. **4-Switch Synchronous Buck-Boost** (Baseline, 24V in -> 5-20V out) │
│ 2. **Active Boost PFC + Half-Bridge LLC Resonant**     │ B. **High-Bus Pure Synchronous Buck** (+36V bus in -> 5-20V out)       │
│ 3. **Two-Switch Forward Converter** (Clamped 24V bus)  │ C. **Coupled-Inductor Synchronous SEPIC** (24V in -> 5-20V out)        │
│ 4. **Direct Variable QR Flyback** (5V-20V direct out)  │ D. **Synchronous Zeta Converter** (24V in -> 5-20V out)                │
│                                                        │ E. **Hybrid Tracking Buck + Ultra-Low-Noise LDO** (Lab grade)          │
└────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Comprehensive Comparative Topology Matrix

The table below contrasts the baseline against all major alternative configurations across 10 critical engineering metrics:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                     COMPARATIVE CONVERTER TOPOLOGY BENCHMARK MATRIX                                                    │
├───────────────────────┬────────────┬─────────────┬───────────┬─────────────┬─────────────┬───────────┬─────────────┬─────────────┬─────────────────────┤
│ Architectural         │ Stage 1    │ Stage 2     │ Peak Eff. │ Active Pwr  │ Magnetic    │ Output    │ Control     │ Relative    │ Best Suited         │
│ Configuration         │ Topology   │ Topology    │ (20V/3A)  │ Switches    │ Components  │ Ripple    │ Complexity  │ BOM Cost    │ Application         │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Baseline Design**   │ QR Flyback │ 4-Switch BB │ 87.5%     │ 1 Pri + 1 SR│ 1 Xfmr (PQ) │ < 25 mV   │ Medium      │ 1.00x       │ General-purpose     │
│                       │ (+24V Bus) │ (LM5176)    │           │ + 4 BB FETs │ + 1 Inductor│ pk-pk     │ (Buck-Boost)│ (Reference) │ bench & industrial  │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 1:      │ QR Flyback │ Sync Buck   │ 88.8%     │ 1 Pri + 1 SR│ 1 Xfmr (PQ) │ < 18 mV   │ Low         │ 0.88x       │ Cost-optimized,     │
│ High-Bus Pure Buck**  │ (+36V Bus) │ (2-Switch)  │           │ + 2 Buck FET│ + 1 Inductor│ pk-pk     │ (Pure Buck) │ (-12% BOM)  │ simplified controls │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 2:      │ PFC Boost  │ Sync Buck   │ 92.4%     │ 1 PFC + 2 HB│ 1 PFC Choke │ < 15 mV   │ High        │ 1.45x       │ Premium lab supply, │
│ PFC + LLC + Buck**    │ + HB LLC   │ (2-Switch)  │           │ + 2 SR + 2 B│ + 1 Resonant│ pk-pk     │ (Resonant + │ (+45% BOM)  │ high PF, low EMI,   │
│                       │ (400V/36V) │             │           │ = 7 Total   │ + 1 Inductor│           │ multi-stage)│             │ high efficiency     │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 3:      │ Two-Switch │ 4-Switch BB │ 88.2%     │ 2 Pri + 2 SR│ 1 Xfmr (ETD)│ < 22 mV   │ Medium      │ 1.15x       │ High reliability,   │
│ Two-Switch Forward**  │ Forward    │ (LM5176)    │           │ + 4 BB FETs │ + 1 Out L   │ pk-pk     │ (Buck-Boost)│ (+15% BOM)  │ clamped Vds stress, │
│                       │ (+24V Bus) │             │           │ = 8 Total   │ + 1 BB Ind. │           │             │             │ telecom/industrial  │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 4:      │ Direct QR  │ None        │ 86.0%     │ 1 Pri FET   │ 1 Xfmr (PQ) │ > 65 mV   │ High        │ 0.62x       │ Lowest BOM cost,    │
│ Single-Stage Direct** │ Flyback    │ (Direct Out)│           │ + 1 SR FET  │ only        │ pk-pk     │ (Opto CTR & │ (-38% BOM)  │ compact consumer/   │
│                       │ (5V-20V)   │             │           │ = 2 Total   │ (0 post L)  │ (100Hz rip│ wide-range) │             │ OEM power adapter   │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 5:      │ QR Flyback │ Coupled-L   │ 86.2%     │ 1 Pri + 1 SR│ 1 Xfmr (PQ) │ < 20 mV   │ Low         │ 0.92x       │ Inherent short Ckt  │
│ Coupled SEPIC**       │ (+24V Bus) │ SEPIC (Sync)│           │ + 2 SEPIC   │ + 1 Coupled │ pk-pk     │ (Ground ref │ (-8% BOM)   │ isolation, low-side │
│                       │            │             │           │ = 4 Total   │ SEPIC L     │           │ drive only) │             │ gate drive only     │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 6:      │ QR Flyback │ Synchronous │ 86.8%     │ 1 Pri + 1 SR│ 1 Xfmr (PQ) │ < 12 mV   │ Medium      │ 0.94x       │ Continuous output   │
│ Synchronous Zeta**    │ (+24V Bus) │ Zeta Conv.  │           │ + 2 Zeta FET│ + 2 Zeta L  │ pk-pk     │ (Buck-like  │ (-6% BOM)   │ inductor current,   │
│                       │            │             │           │ = 4 Total   │ (or coupled)│           │ out stage)  │             │ low output ripple   │
├───────────────────────┼────────────┼─────────────┼───────────┼─────────────┼─────────────┼───────────┼─────────────┼─────────────┼─────────────────────┤
│ **Alternative 7:      │ QR Flyback │ Buck + LDO  │ 85.5%     │ 1 Pri + 1 SR│ 1 Xfmr (PQ) │ < 0.8 mV  │ Low         │ 1.10x       │ RF/Analog testing,  │
│ Tracking Buck + LDO** │ (+28V Bus) │ Post-Reg    │           │ + 2 Buck FET│ + 1 Inductor│ pk-pk     │ (Tracking   │ (+10% BOM)  │ ultra-low noise lab │
│                       │            │ (TPS7A4701) │           │ + 1 LDO Pass│             │ (<15µV RMS│ loop)       │             │ precision supply    │
└───────────────────────┴────────────┴─────────────┴───────────┴─────────────┴─────────────┴───────────┴─────────────┴─────────────┴─────────────────────┘
```

---

## 3. Key Findings & Engineering Trade-Offs

### 3.1 Why the High-Bus Pure Synchronous Buck (+36 V Bus) is the Strongest Alternative:
By adjusting the primary Flyback stage transformer turns ratio ($N_p/N_s = 3.0$ instead of $4.0$) to regulate a $+36.0\,\text{V}$ intermediate bus instead of $+24.0\,\text{V}$:
1. **Elimination of Two Power MOSFETs**: The 4-switch Buck-Boost H-bridge collapses into a **2-switch synchronous buck converter** ($Q_A, Q_B$).
2. **Duty Cycle Always in Buck Regime**:
   $$D = \frac{V_{OUT}}{V_{IN}} \implies D_{min} = \frac{5.0\,\text{V}}{36.0\,\text{V}} = 13.9\%, \quad D_{max} = \frac{20.0\,\text{V}}{36.0\,\text{V}} = 55.6\%$$
3. **No Mode Hopping**: The complex Buck-to-Boost transition region (where jitter, EMI spikes, and transfer-function phase dips occur) is completely eliminated.
4. **BOM Savings**: Saves 2 power MOSFETs, 1 high-side bootstrap driver circuit, reduces PCB footprint by $18\%$, and lowers BOM cost by $12\%$.

### 3.2 Why Active PFC + LLC Resonant is the Gold Standard for Premium Lab Instruments:
For commercial precision lab bench supplies where power factor ($PF > 0.98$), line harmonics (IEC 61000-3-2 Class D), and efficiency ($> 92\%$) are strict requirements:
1. **Zero-Voltage Switching (ZVS)**: The half-bridge LLC primary switches turn on with zero voltage, virtually eliminating switching losses and capacitive dump currents.
2. **Near-Zero EMI**: The resonant sinusoidal currents eliminate hard-switched $di/dt$ spikes, drastically reducing common-mode EMI filter bulk.
3. **High Primary Bus**: Active boost PFC creates a rock-solid $400\,\text{V}$ DC bus regardless of mains fluctuation ($85\,\text{V} \dots 265\,\text{V}$ AC).

### 3.3 The Hidden Challenges of Single-Stage Direct Variable Flyback:
Attempting to control the flyback converter directly from $5.0\,\text{V}$ to $20.0\,\text{V}$ (4:1 output voltage swing) without a post-regulator introduces major engineering hurdles:
1. **Auxiliary VCC Collapse**: The auxiliary bias winding tracking the secondary collapses at $5\,\text{V}$ output ($V_{aux} \approx 5\,\text{V} \times \frac{N_{aux}}{N_s} \approx 4.0\,\text{V}$), plunging the controller below UVLO ($14\,\text{V}$) and shutting down the supply.
2. **Optocoupler Loop Bandwidth**: The loop bandwidth of an optocoupled feedback network is severely bandwidth-limited ($< 3\,\text{kHz}$), resulting in sluggish dynamic response ($> 8\,\text{ms}$) during 3A load steps.
3. **100/120 Hz Line Ripple Bleed**: Without a post-regulator, low-frequency line ripple from the bulk capacitor passes directly to the output terminals unless massive secondary electrolytic capacitors are used.

### 3.4 Why Tracking Buck + Linear LDO is Mandatory for RF/Precision Loads:
1. **Sub-Millivolt Residual Ripple**: Standard switching post-regulators produce $15\,\text{mV} \dots 25\,\text{mV}_{\text{pk-pk}}$ ripple at $250\,\text{kHz}$.
2. **LDO Power Supply Rejection Ratio (PSRR)**: A cascaded LDO with $> 60\,\text{dB}$ PSRR at $250\,\text{kHz}$ attenuates this ripple down to $< 0.8\,\text{mV}_{\text{pk-pk}}$ and $< 15\,\mu\text{V}_{\text{RMS}}$ wideband noise.
3. **Dynamic Pre-Tracking**: The buck pre-regulator dynamically tracks $V_{OUT} + 350\,\text{mV}$, keeping LDO dissipation fixed at only $P_{diss} = 0.35\,\text{V} \times 3.0\,\text{A} = 1.05\,\text{W}$.

---

## 4. Documentation Suite Structure

This directory is organized into four technical dossiers accompanied by a Python calculation utility:

```text
smart_programmable_power_supply_alternatives/
├── README.md                                       # Master Overview, comparative matrix & roadmap
├── isolated-ac-dc-topologies.md                    # PFC+LLC, Two-Switch Forward & Direct Variable Flyback
├── non-isolated-dc-dc-topologies.md                # High-Bus Buck, SEPIC, Zeta & Tracking Buck+LDO
├── comparative-analysis-and-benchmarking.md        # Mathematical loss models, stress analysis & BOM comparison
└── tools/
    └── alternative_converter_calc.py               # Complete CLI sizing & multi-topology loss calculator
```

### [1. Isolated AC-DC Primary Topologies](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply_alternatives/isolated-ac-dc-topologies.md)
* **Active Boost PFC + Half-Bridge LLC Resonant**: Resonant tank equations ($L_r, C_r, L_m$), ZVS condition, $400\,\text{V}$ bus design, and schematic.
* **Two-Switch Forward Converter**: Demagnetization clamp diodes to $V_{bulk}$, $D_{max} < 50\%$, output LC inductor sizing, and schematic.
* **Direct Variable Flyback (5V–20V Direct)**: Auxiliary winding bootstrap solutions (dual-tapped winding vs. buck bias) and dynamic opto-loop stability.

### [2. Non-Isolated DC-DC Post-Regulator Topologies](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply_alternatives/non-isolated-dc-dc-topologies.md)
* **High-Bus (+36V DC) Synchronous Buck**: 2-switch design, duty cycles, inductor sizing, DAC summing network, and schematic.
* **Coupled-Inductor Synchronous SEPIC**: Ground-referenced switch, series DC blocking capacitor $C_{sep}$, zero-ripple steering, and schematic.
* **Synchronous Zeta Converter**: Continuous output inductor current, buck-like low ripple, and schematic.
* **Hybrid Tracking Buck + Linear LDO**: Lab-grade sub-millivolt noise ($< 15\,\mu\text{V}_{\text{RMS}}$), dynamic headroom tracking, and schematic.

### [3. Quantitative Comparative Analysis & Benchmarking](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply_alternatives/comparative-analysis-and-benchmarking.md)
* Semiconductor voltage and current stresses across all topologies.
* Mathematical power loss breakdown models (conduction, switching, gate drive, core, snubber).
* Quantitative efficiency curves across load ($0.5\,\text{A} \dots 3.0\,\text{A}$) and output voltage ($5\,\text{V}, 12\,\text{V}, 20\,\text{V}$).
* Decision matrix and architecture selection flowchart based on target market priorities.

### [4. CLI Sizing & Multi-Topology Calculator](file:///home/tthhongs/build_tthongs/tasks_aa_ii/vvdn/smart_programmable_power_supply_alternatives/tools/alternative_converter_calc.py)
* Complete Python CLI utility to size each alternative converter and compare power losses side-by-side.
