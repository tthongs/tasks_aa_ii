# Hardware Compliance, Quality, and Reliability Standards

Welcome to the **Hardware Compliance, Quality, and Reliability Knowledge Base** at VVDN. This directory provides comprehensive, production-grade engineering documentation on mandatory regulatory compliance frameworks, environmental directives, automotive qualification standards, and component handling protocols.

---

## 1. Quick Navigation & Topic Index

| Topic | Standard / Directive | Governing Body | Domain | Primary Focus | Guides Available |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **RoHS** | Directive 2011/65/EU + (EU) 2015/863 (RoHS 3) | European Union (CE Mark) | Environmental & Chemical Compliance | Restriction of 10 hazardous substances (Pb, Cd, Hg, Cr6+, phthalates) at homogeneous material level | [Markdown Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/rohs/rohs-guide.md) \| [Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/rohs/rohs-guide.docx) |
| **REACH** | Regulation (EC) No 1907/2006 | ECHA (European Chemicals Agency) | Chemical Safety & Material Declaration | Registration, evaluation, authorization of chemicals; SVHC declaration (>0.1% w/w) & SCIP reporting | [Markdown Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/reach/reach-guide.md) \| [Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/reach/reach-guide.docx) |
| **AEC** | AEC-Q100, Q101, Q102, Q103, Q104, Q200 | Automotive Electronics Council | Component Reliability & Stress Qualification | Failure-mechanism-based qualification testing, temperature grades (-40°C to +150°C), zero-defect criteria | [Markdown Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/aec/aec-guide.md) \| [Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/aec/aec-guide.docx) |
| **MSL** | IPC/JEDEC J-STD-020 & J-STD-033 | IPC / JEDEC | SMT Manufacturing & Packaging Reliability | Classification of moisture sensitivity (Levels 1–6), floor life tracking, desiccant packaging, and baking | [Markdown Guide](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/msl/msl-guide.md) \| [Word DOCX](file:///home/tthhongs/build_tthongs/tasks_aa_ii/VVDN/standards/msl/msl-guide.docx) |

---

## 2. Hardware Lifecycle Mapping

Hardware compliance and reliability are not afterthoughts; they are enforced at distinct stages of the product development lifecycle:

```text
┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                                HARDWARE PRODUCT LIFECYCLE                                    │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
  1. Component Selection & Architecture
     ├── AEC-Q100/Q101/Q200: Select automotive-grade silicon & passives based on operating temp
     ├── RoHS: Verify lead-free package terminations, verify RoHS 3 (10 substances) compliance
     └── REACH: Screen BOM against latest ECHA SVHC Candidate List (avoid SVHC > 0.1% w/w)
                                     │
                                     ▼
  2. Sourcing, Procurement & Supplier Quality
     ├── Collect Full Material Disclosures (FMD) / IPC-1752A XML declarations
     ├── Collect Supplier Certificates of Compliance (CoC) and test reports (IEC 62321)
     └── Review supplier Part Submission Warrant (PSW) & PPAP Level 3 documentation
                                     │
                                     ▼
  3. Warehouse, Storage & Inventory
     ├── MSL: Inspect Moisture Barrier Bags (MBB), verify Desiccant & Humidity Indicator Card (HIC)
     └── Track floor life consumption upon unsealing; maintain dry cabinets (<5% / <10% RH)
                                     │
                                     ▼
  4. SMT Manufacturing & Assembly
     ├── MSL: Bake components exceeding floor life according to J-STD-033 before reflow
     ├── RoHS: Implement Lead-Free solder alloys (SAC305) with 245°C–260°C peak reflow profiles
     └── Assembly Quality: Inspect solder joints (IPC-A-610 Class 2/3) & prevent tin whiskering
                                     │
                                     ▼
  5. Regulatory Certification & Market Delivery
     ├── Compile Technical Documentation File under EN IEC 63000 (CE DoC for RoHS)
     ├── Submit SCIP notifications to ECHA for articles with SVHC > 0.1% w/w
     └── Automotive OEM: Deliver PPAP packages and ISO 26262 functional safety audit trails
```

---

## 3. High-Level Comparison Matrix

| Parameter | RoHS | REACH | AEC Qualifications | MSL (IPC/JEDEC) |
| :--- | :--- | :--- | :--- | :--- |
| **Type of Rule** | Mandatory EU Directive (statutory law, CE mark) | Mandatory EU Regulation (statutory law) | Industry standard (automotive OEM customer requirement) | Industry standard (IPC/JEDEC assembly guideline) |
| **Target Object** | Finished Electrical & Electronic Equipment (EEE) | Chemical substances, mixtures, and articles (all goods) | Individual electronic components (ICs, discretes, passives) | Surface Mount Devices (SMD plastic ICs, LEDs, connectors) |
| **Key Threshold** | Strict concentration limits (e.g., 0.1% / 1000 ppm) per homogeneous material | 0.1% w/w per individual article (SVHC notification threshold) | Zero defects allowed ($c=0$) across stress test sample lots | Floor life duration (e.g., 168 hours for MSL 3 at $\le 30^{\circ}\text{C} / 60\%\text{ RH}$) |
| **Failure Mode Addressed** | Environmental toxicity, landfill leaching, heavy metal poisoning | Human health hazards (carcinogens, mutagens, endocrine disruptors) | Mechanical/thermal/electrical degradation under automotive stress | Solder reflow steam explosion ("popcorning"), internal delamination |
| **Key Documents** | CE Declaration of Conformity (DoC), IEC 62321 test lab reports | Full Material Declaration (FMD), SCIP submission number | AEC qualification report, PPAP package, Part Submission Warrant (PSW) | Moisture Caution Label (MBB label), HIC card, factory bake records |

---

## 4. Directory Structure

```text
standards/
├── README.md (.docx)                  # Master index and engineering lifecycle mapping
├── rohs/
│   ├── rohs-guide.md                  # Comprehensive Markdown documentation
│   └── rohs-guide.docx                # Formatted Word document for mentor / review
├── reach/
│   ├── reach-guide.md                 # Comprehensive Markdown documentation
│   └── reach-guide.docx                # Formatted Word document for mentor / review
├── aec/
│   ├── aec-guide.md                   # Comprehensive Markdown documentation
│   └── aec-guide.docx                 # Formatted Word document for mentor / review
└── msl/
    ├── msl-guide.md                   # Comprehensive Markdown documentation
    └── msl-guide.docx                 # Formatted Word document for mentor / review
```
