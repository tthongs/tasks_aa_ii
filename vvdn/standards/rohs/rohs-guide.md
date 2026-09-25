# RoHS Compliance: Architecture, Regulatory Framework, and Hardware Engineering Guide

## 1. What is RoHS?

**RoHS** stands for **Restriction of Hazardous Substances**. It is a mandatory European Union directive that restricts the use of specific hazardous materials in the manufacture of Electrical and Electronic Equipment (EEE). 

The primary goals of RoHS are:
- To reduce the environmental and health impacts of electronic waste (e-waste).
- To prevent toxic heavy metals and persistent chemicals from leaching into groundwater and soil from municipal landfills.
- To protect workers in recycling facilities from toxic chemical exposure.
- To facilitate environmentally sound recovery and recycling of end-of-life electronic equipment.

### Regulatory Evolution:

| Directive | Official Name | Effective Date | Key Changes & Scope |
| :--- | :--- | :--- | :--- |
| **RoHS 1** | Directive 2002/95/EC | July 1, 2006 | Restricted 6 substances (Pb, Hg, Cd, Cr6+, PBB, PBDE). Narrow product category scope. |
| **RoHS 2** | Directive 2011/65/EU | January 2, 2013 | Integrated into **CE marking**. Requires formal **EU Declaration of Conformity (DoC)** and **Technical Documentation** under harmonized standard EN IEC 63000 (formerly EN 50581). Expanded scope to Category 11 ("open scope" covering all EEE). |
| **RoHS 3** | Delegated Directive (EU) 2015/863 | July 22, 2019 *(July 2021 for medical/industrial)* | Added **4 phthalates** (plasticizers) to the restricted list, bringing the total number of restricted substances to **10**. |

> [!IMPORTANT]
> Under RoHS 2 and RoHS 3, compliance is a **legal prerequisite for affixing the CE mark**. An electronic product cannot legally carry the CE mark or be placed on the EU Single Market without meeting RoHS requirements.

---

## 2. The 10 Restricted Substances and Threshold Limits

RoHS does not require 100% absence of restricted chemicals; it defines **Maximum Concentration Values (MCVs)** by weight in each **homogeneous material**.

| Restricted Substance | CAS Number | Maximum Permissible Limit (% by weight) | Maximum Permissible Limit (ppm) | Typical Electronic Application / Historical Usage |
| :--- | :--- | :--- | :--- | :--- |
| **Lead (Pb)** | 7439-92-1 | **0.1%** | **1,000 ppm** | Traditional Sn63/Pb37 solder alloys, component pin terminations, cable sheathing, brass machining alloys. |
| **Mercury (Hg)** | 7439-97-6 | **0.1%** | **1,000 ppm** | CCFL backlights in legacy LCD displays, tilt switches, relay contacts. |
| **Cadmium (Cd)** | 7440-43-9 | **0.01%** | **100 ppm** *(Strict!)* | Solar cells, NiCd batteries, pigments in plastics, electrical contacts, anti-corrosion plating. |
| **Hexavalent Chromium ($\text{Cr}^{6+}$)** | 18540-29-9 | **0.1%** | **1,000 ppm** | Chromate conversion coatings (passivation) on aluminum and galvanized steel chassis to prevent corrosion. |
| **Polybrominated Biphenyls (PBB)** | Various | **0.1%** | **1,000 ppm** | Brominated flame retardants in PCB laminates, connector plastics, and structural enclosures. |
| **Polybrominated Diphenyl Ethers (PBDE)** | Various | **0.1%** | **1,000 ppm** | Brominated flame retardants in plastics and PCB resins. |
| **Bis(2-ethylhexyl) phthalate (DEHP)** | 117-81-7 | **0.1%** | **1,000 ppm** | Plasticizer used to make PVC cables, heat-shrink tubing, grommets, and rubber flexible. |
| **Butyl benzyl phthalate (BBP)** | 85-68-7 | **0.1%** | **1,000 ppm** | Plasticizer in synthetic rubbers, adhesives, cable jackets. |
| **Dibutyl phthalate (DBP)** | 84-74-2 | **0.1%** | **1,000 ppm** | Plasticizer in sealants, coatings, and elastomeric components. |
| **Diisobutyl phthalate (DIBP)** | 84-69-5 | **0.1%** | **1,000 ppm** | Alternative plasticizer often substituted for DBP in polyurethane and rubber. |

> [!CAUTION]
> Notice that **Cadmium (Cd)** has a limit of **0.01% (100 ppm)**, which is 10 times more stringent than the 0.1% (1000 ppm) limit applied to all other 9 substances.

---

## 3. The Core Concept: "Homogeneous Material"

The single most critical concept in RoHS compliance is that concentration limits apply to **each homogeneous material individually**, **never to the overall component or finished assembly weight**.

### 3.1 Definition
A **homogeneous material** is defined as one material of uniform composition throughout, or a material consisting of a combination of materials that cannot be disjointed or separated into different materials by mechanical actions such as:
- Unscrewing
- Cutting
- Crushing
- Grinding
- Abrasive processes

### 3.2 Real-World Component Breakdown

Consider an everyday surface-mount IC (e.g., an SOIC-8 or QFN microcontroller):

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                      SMD INTEGRATED CIRCUIT BREAKDOWN                      │
├───────────────────────────────────────────────────────────────────────────┤
│ 1. Epoxy Mold Compound (Plastic Body)    ──► Homogeneous Material #1      │
│ 2. Silicon Die (Silicon substrate)       ──► Homogeneous Material #2      │
│ 3. Die Attach Epoxy (Silver conductive)  ──► Homogeneous Material #3      │
│ 4. Internal Wire Bonds (Gold / Copper)   ──► Homogeneous Material #4      │
│ 5. Copper Leadframe (Base metal)         ──► Homogeneous Material #5      │
│ 6. Leadframe Plating (Matte Tin / NiPdAu)──► Homogeneous Material #6      │
└───────────────────────────────────────────────────────────────────────────┘
```

#### Why Component-Averaging is Prohibited:
Suppose a connector weighs $10.0\,\text{g}$ and contains a small PVC wire grommet weighing $0.2\,\text{g}$.
- The grommet contains $2,000\,\text{ppm}$ of DEHP plasticizer (exceeding the $1,000\,\text{ppm}$ limit).
- Averaged over the whole connector: $\frac{0.2\,\text{g} \times 0.002}{10.0\,\text{g}} = 40\,\text{ppm}$.
- Under RoHS, **this connector is NON-COMPLIANT**. The PVC grommet is a distinct homogeneous material, and its local concentration of $2,000\,\text{ppm}$ violates the directive.

---

## 4. RoHS Exemptions (Annex III and IV)

Because viable technological alternatives do not yet exist for every application, the EU Commission grants temporary exemptions listed under **Annex III** (General EEE) and **Annex IV** (Medical devices and monitoring/control instruments).

### 4.1 Common Annex III Hardware Exemptions

| Exemption Code | Description | Typical Industry Application | Engineering Watch-out |
| :--- | :--- | :--- | :--- |
| **6(a) / 6(a)-I** | Lead as an alloying element in **machining steel** containing up to 0.35% lead by weight. | Screws, standoffs, chassis threaded inserts, mechanical fasteners. | Check supplier certificates for brass vs steel specs. |
| **6(b) / 6(b)-I / 6(b)-II** | Lead as an alloying element in **aluminum** containing up to 0.4% lead by weight. | Machined heatsinks, extruded enclosure profiles. | Split into distinct sub-clauses depending on machining grade. |
| **6(c)** | Copper alloy containing up to **4% lead by weight**. | **Brass connectors**, D-sub pins, RF SMA connectors, screw terminals. | Extremely common in hardware. Check renewal expiry dates regularly. |
| **7(a)** | Lead in **high melting temperature type solders** (i.e. lead-based alloys containing **85% by weight or more lead**). | Internal die-attach solders for power MOSFETs, diodes, high-power bridge rectifiers. | Does NOT permit Pb in board-level SMT reflow or wave soldering. |
| **7(c)-I** | Electrical and electronic components containing **lead in a glass or ceramic** other than dielectric ceramic in capacitors. | Thick-film chip resistors (ruthenium oxide cermet glass matrix), piezoelectric sensors. | Found on almost all standard SMD chip resistors (0402, 0603, 0805, 1206). |
| **7(c)-II** | Lead in dielectric ceramic in capacitors for a rated voltage of $125\,\text{V AC}$ or $250\,\text{V DC}$ or higher. | High-voltage MLCCs (Multi-layer Ceramic Capacitors). | Standard low-voltage decoupling caps (e.g. 16V, 50V) must be lead-free. |

### 4.2 Exemption Life Cycles & Sunsetting
Exemptions are not permanent. Industry associations must formally submit renewal applications 18 months prior to expiration. If denied or unrenewed, the exemption enters a phase-out transition window (typically 12 to 18 months). Hardware engineering teams must continuously audit their component BOMs for expiring exemptions.

---

## 5. Impact of RoHS on Hardware Design & Manufacturing

The mandatory transition away from traditional Tin-Lead ($\text{Sn63/Pb37}$) eutectic solder altered electrical and manufacturing engineering fundamentally.

### 5.1 Lead-Free Solder Alloys

| Solder Alloy | Composition | Melting Point | Applications & Trade-offs |
| :--- | :--- | :--- | :--- |
| **Sn63/Pb37 (Legacy)** | $63\%\,\text{Sn},\, 37\%\,\text{Pb}$ | **$183^{\circ}\text{C}$ (Eutectic)** | Excellent wetting, bright shiny joints, low thermal stress on components. Restricted under RoHS. |
| **SAC305 (Industry Standard)** | $96.5\%\,\text{Sn},\, 3.0\%\,\text{Ag},\, 0.5\%\,\text{Cu}$ | **$217^{\circ}\text{C} - 220^{\circ}\text{C}$** | Dominant lead-free SMT alloy. Good fatigue strength, but higher cost and dull joint appearance. |
| **SAC0307 / SACX** | $99.0\%\,\text{Sn},\, 0.3\%\,\text{Ag},\, 0.7\%\,\text{Cu} + \text{dopants}$ | **$217^{\circ}\text{C} - 227^{\circ}\text{C}$** | Lower silver content to reduce cost in consumer wave soldering. |
| **Sn99.3/Cu0.7 (SC100N)** | $99.3\%\,\text{Sn},\, 0.7\%\,\text{Cu} + \text{trace Ni/Ge}$ | **$227^{\circ}\text{C}$** | Common in selective and wave soldering pots. |
| **Sn42/Bi58 (Low-Temp)** | $42\%\,\text{Sn},\, 58\%\,\text{Bi}$ | **$138^{\circ}\text{C}$ (Eutectic)** | Used for heat-sensitive optics, flex-PCBs, and step-soldering; brittle intermetallics. |

### 5.2 Thermal Profiles & SMT Reflow Impact

The jump in melting point from $183^{\circ}\text{C}$ to $217^{\circ}\text{C}$ required raising peak reflow temperatures significantly:
- **SnPb reflow peak**: $210^{\circ}\text{C} - 225^{\circ}\text{C}$.
- **Lead-free (SAC305) reflow peak**: **$240^{\circ}\text{C} - 260^{\circ}\text{C}$**.

```text
Temperature (°C)
  260 ┼─────────────────────────────── Peak Reflow (240°C - 260°C)
      │                                  ┌───┐
  217 ┼─────────────────── Lead-Free TL ─┘   └─ Liquidus Zone (TAL: 60 - 90s)
      │               ┌───────────────────────┐
  183 ┼── SnPb TL ─── │                       │
      │         ┌─────┘                       └─────── Cooling (> -2°C/s to -4°C/s)
  150 ┼─────────┘ Soak / Flux Activation Zone
      │         (150°C - 200°C, 60 - 120s)
      │  Ramp-up (1°C - 3°C/s)
    0 ┴──────────────────────────────────────────────────── Time (seconds)
```

#### Engineering Consequences:
1. **Component Thermal Damage**: Components (connectors, electrolytic capacitors, IC packages) must withstand up to $260^{\circ}\text{C}$ without blistering or deforming.
2. **Moisture Sensitivity**: Higher temperatures accelerate internal steam explosion in plastic IC packages, making **MSL management** significantly more critical.
3. **PCB Substrate Selection**: FR4 laminates require a higher Glass Transition Temperature ($T_g \ge 150^{\circ}\text{C} - 170^{\circ}\text{C}$) and Decomposition Temperature ($T_d \ge 340^{\circ}\text{C}$) to prevent delamination and z-axis thermal expansion vias cracking.

### 5.3 PCB Surface Finishes

With Hot Air Solder Leveling (HASL) using lead banned under RoHS, alternative finishes emerged:

| Surface Finish | Advantages | Disadvantages | SMT Suitability |
| :--- | :--- | :--- | :--- |
| **Lead-Free HASL (LF-HASL)** | Low cost, long shelf life, rugged | Uneven pad coplanarity, high thermal shock during coating | Poor for fine-pitch QFN/BGA ($<0.5\,\text{mm}$) |
| **ENIG (Electroless Nickel Immersion Gold)** | Exceptionally flat surface, excellent shelf life, wire bondable | Higher cost, risk of "Black Pad" (nickel corrosion) causing brittle solder fracture | Preferred for fine-pitch BGAs and high-reliability designs |
| **ENEPIG (ENIG + Electroless Palladium)** | Universal finish, zero black pad risk, gold/aluminum wire bondable | Highest cost | High-rel automotive, aerospace, telecom |
| **OSP (Organic Solderability Preservative)** | Low cost, perfectly flat, simple application | Sensitive to handling, degraded by multiple reflow cycles, short shelf life | High-volume consumer products |
| **Immersion Silver (ImmAg)** | Very flat, good RF performance, moderate cost | Susceptible to tarnishing from atmospheric sulfur ($H_2S$), risk of micro-voiding | RF/High-speed digital designs |
| **Immersion Tin (ImmSn)** | Flat, good for press-fit connectors | Prone to tin whisker formation during storage, limited reflow cycles | Automotive press-fit backplanes |

### 5.4 The Tin Whisker Phenomenon

When pure tin electroplating was introduced on leadframes to replace tin-lead plating, the electronics industry encountered **Tin Whiskers**: spontaneous, needle-like single-crystal eruptions of tin that grow out from the surface over weeks, months, or years.

```text
       Pure Tin Plating Layer
  ┌─────────────────────────────────┐
  │         /\                      │  <-- Tin Whisker (Can grow 1µm to 10mm!)
  │        /  \                     │      Causes: Electrical short circuits
  │       │    │                    │      between adjacent pins or flashover arcs
  │       │    │                    │
  ├───────┴────┴────────────────────┤
  │   Intermetallic Layer (Cu6Sn5)  │  <-- Irregular growth creates internal compressive stress
  ├─────────────────────────────────┤
  │     Copper Leadframe Base       │
  └─────────────────────────────────┘
```

#### Mitigation Techniques:
- **Matte Tin over Nickel Barrier**: An underplate of $1.5\,\mu\text{m} - 3.0\,\mu\text{m}$ Nickel prevents Copper-Tin intermetallic diffusion that generates compressive stress.
- **Post-Plate Annealing (Baking)**: Heating plated components to $150^{\circ}\text{C}$ for 1 hour relieves internal lattice stress.
- **Conformal Coating**: Polyurethane, silicone, or parylene coatings form a mechanical barrier that prevents shorting if whiskers detach.

---

## 6. Global RoHS Regulations

Following the EU's lead, multiple international jurisdictions implemented localized RoHS frameworks:

| Jurisdiction | Regulation | Distinct Characteristics |
| :--- | :--- | :--- |
| **China** | **China RoHS 2** (MIIT Order No. 32) | Two-step process: 1) Marking & Disclosure for all EEE (Green "e" logo if compliant; Orange logo with Environment Friendly Use Period / EFUP in years + Hazardous Substance table). 2) Catalog of managed products requiring conformity assessment. |
| **United States (California)** | **California RoHS** (SB 20/SB 50) | Scope covers video displays with screens $> 4\text{ inches}$ (monitors, TVs, laptops). Aligned with EU substance limits. |
| **Taiwan** | **CNS 15663** | Mandatory marking of presence/absence of 6 restricted substances on the product label and user manual under BSMI certification. |
| **South Korea** | **Korea RoHS** (Act on Resource Circulation of EEE and Vehicles) | Similar 10 substances, aligns with EU RoHS scope and exemptions. |
| **Eurasian Union** | **TR EAEU 037/2016** | Mandatory RoHS certification for Russia, Belarus, Kazakhstan, Armenia, Kyrgyzstan with EAC mark. |

---

## 7. Testing, Verification, and CE Technical File

Compliance with RoHS must be substantiated with documented evidence conforming to harmonized standard **EN IEC 63000:2018** (*Technical documentation for the assessment of electrical and electronic products with respect to the restriction of hazardous substances*).

### 7.1 Analytical Testing Methods (IEC 62321)

To confirm substance concentrations in homogeneous materials, testing laboratories utilize standardized analytical test suites defined in **IEC 62321**:

```text
Raw Material / Component
           │
           ▼
[IEC 62321-3-1: XRF Screening (X-Ray Fluorescence)]
           │
           ├──► Result well below limit (e.g. Pb < 300 ppm) ──► PASS (Screening sufficient)
           │
           └──► Result inconclusive or borderline (e.g. 700 - 1300 ppm)
                     │
                     ▼
           [Confirmatory Wet Chemical Testing]
           ├── ICP-OES / ICP-MS (IEC 62321-4 / 5): Precise Pb, Cd, Hg detection
           ├── UV-Vis Spectrophotometry (IEC 62321-7-1 / 7-2): Hexavalent Chromium (Cr6+)
           └── GC-MS (Gas Chromatography-Mass Spectrometry, IEC 62321-6 / 8): PBB, PBDE, Phthalates
```

### 7.2 Required Documentation Checklist for Hardware Engineers

To prepare a product for commercial launch and regulatory audit:
1. **Full Material Disclosure (FMD)** or **IPC-1752A XML** files for all custom and off-the-shelf components.
2. **Supplier Declarations of Conformity (CoC)** explicitly citing Directive 2011/65/EU and Delegated Directive (EU) 2015/863.
3. **Bill of Materials (BOM) Scrub Report**: Verification that every line item has active RoHS-compliant part numbers.
4. **Exemption Tracking Sheet**: Explicitly recording all claimed exemptions (e.g., 6c for brass standoffs, 7c-I for thick-film resistors) and their expiration timelines.
5. **EU Declaration of Conformity (DoC)**: Legal document signed by company officer listing RoHS alongside EMC, LVD, and RED directives.
6. **Retention Period**: The Technical Documentation File must be retained for at least **10 years** after the last unit is placed on the market.
