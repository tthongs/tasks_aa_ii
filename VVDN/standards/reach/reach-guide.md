# REACH Compliance: Architecture, Regulatory Obligations, and Electronics Hardware Guide

## 1. What is REACH?

**REACH** stands for **Registration, Evaluation, Authorisation, and Restriction of Chemicals**. It is a cornerstone regulation of the European Union—**Regulation (EC) No 1907/2006**—overseen by the **ECHA** (European Chemicals Agency) based in Helsinki, Finland.

Unlike RoHS, which is an industry-specific directive targeting electrical and electronic equipment, REACH is an overarching horizontal regulation encompassing **all chemical substances across all industries**, whether used in industrial chemical processes, daily consumer goods, paints, textiles, or advanced electronic assemblies.

### The Four Pillars of REACH:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                              THE 4 PILLARS OF REACH                         │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. REGISTRATION    Manufacturers & importers of raw chemical substances    │
│                    must register chemical dossiers with ECHA (≥ 1 tonne/yr).│
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. EVALUATION      ECHA and EU Member States evaluate dossiers to assess   │
│                    health, aquatic toxicity, and environmental risks.       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. AUTHORISATION   Substances of Very High Concern (SVHC) listed on Annex  │
│                    XIV are phased out unless specific authorization is won. │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. RESTRICTION     Annex XVII prohibits or strictly limits the manufacture, │
│                    marketing, or use of specific dangerous substances.      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. REACH Terminology for Hardware Engineers: Substances, Mixtures, and Articles

Understanding REACH requires distinguishing between three regulatory definitions established in Article 3 of the regulation:

| Term | Legal Definition (Article 3) | Examples in Hardware Engineering | REACH Regulatory Focus |
| :--- | :--- | :--- | :--- |
| **Substance** | A chemical element and its compounds in the natural state or obtained by any manufacturing process. | Pure Copper ($Cu$), pure Gold ($Au$), Lead metal ($Pb$), Silicon ($Si$). | Substance registration (Article 6). |
| **Mixture / Preparation** | A mixture or solution composed of two or more substances. | Solder paste, liquid flux, adhesive epoxies, conformal coatings, thermal greases. | Safety Data Sheets (SDS), volume registration. |
| **Article** | An object which during production is given a **special shape, surface, or design** which determines its function to a greater degree than does its chemical composition. | **Finished IC packages, printed circuit boards (PCBs), connectors, resistors, screws, cables, chassis enclosures, complete PCBAs.** | Article 33 Duty to Communicate; SCIP reporting; Annex XVII restrictions. |

> [!NOTE]
> Electronic systems integrators and ODM/EMS providers like VVDN primarily design, assemble, and import **Articles** and **Complex Objects** (assemblies made up of multiple individual articles).

---

## 3. SVHC (Substances of Very High Concern) & The Candidate List

A substance is classified as a **Substance of Very High Concern (SVHC)** if it meets the rigorous hazard criteria defined in **Article 57** of REACH:
1. **CMR**: Carcinogenic, Mutagenic, or Toxic for Reproduction (Category 1A or 1B).
2. **PBT**: Persistent, Bioaccumulative, and Toxic (per Annex XIII criteria).
3. **vPvB**: Very Persistent and Very Bioaccumulative.
4. **Equivalent Level of Concern**: Substances such as **endocrine disruptors** that cause serious effects on humans or ecosystems equivalent to CMR or PBT.

### The Candidate List Update Dynamic
- When an SVHC is proposed and approved, it is placed on the **ECHA Candidate List for Authorisation**.
- **Update Frequency**: The Candidate List is updated **twice every year** (typically in **January** and **June/July**).
- **Living Document**: The list has grown continuously from 15 substances in 2008 to **over 240+ substances**.
- **Immediate Effect**: The legal obligations for an article manufacturer/importer trigger **on the exact day** a substance is published on the Candidate List. There is no multi-year transition grace period.

### Common SVHCs Encountered in Hardware & Electronics

| Substance Name | CAS Number | Why It Appears in Electronics Hardware |
| :--- | :--- | :--- |
| **Lead Metal ($Pb$)** | 7439-92-1 | Added to Candidate List in June 2018. Present in brass connectors (up to 4% Pb under RoHS exemption 6c), high-temp solders (RoHS exemption 7a). |
| **Lead Monoxide ($PbO$) / Lead Dioxide ($PbO_2$)** | 1317-36-8 | Constituent of glass passivations in thick-film SMD resistors and diodes (RoHS exemption 7c-I). |
| **Lead Titanium Zirconium Oxide (PZT)** | 12626-81-2 | Piezoelectric buzzers, ultrasound transducers, ceramic resonators. |
| **Octamethylcyclotetrasiloxane (D4)** / **Decamethylcyclopentasiloxane (D5)** | 556-67-2 / 541-02-6 | Residual monomer impurities in silicone thermal pads, silicone gaskets, and potting compounds. |
| **2-Benzyl-2-dimethylamino-4'-morpholinobutyrophenone** | 119313-12-1 | Photoinitiator used in UV-curable solder masks and photoresists. |
| **Dechlorane Plus** | 13560-89-9 | Flame retardant used in cable insulation, electrical tape, and structural plastics. |
| **Melamine** | 108-78-1 | Flame retardant additive in polymer housings and terminal blocks. |

---

## 4. Article 33 Duty to Communicate & Consumer Requests

Article 33 of REACH imposes a statutory obligation throughout the commercial supply chain regarding SVHCs:

### 4.1 Business-to-Business (B2B) Communication (Article 33(1))
If any article supplied contains an SVHC in a concentration exceeding **$0.1\%$ weight-by-weight ($w/w$)**, the supplier **must automatically provide the recipient** with:
- The **name of the SVHC** present.
- **Sufficient information** available to ensure the safe handling and use of the article (e.g., disposal guidelines, skin contact warnings).

### 4.2 Business-to-Consumer (B2C) Communication (Article 33(2))
Any consumer can ask a retailer or manufacturer whether an article contains an SVHC $> 0.1\%\,w/w$.
- The supplier is legally bound to provide this information **free of charge** within **45 calendar days** of the request.

---

## 5. The Landmark ECJ Ruling: "Once an Article, Always an Article" (O5A)

Historically, some manufacturers interpreted the $0.1\%\,w/w$ threshold by calculating the weight of the SVHC against the **total weight of the entire finished product** (e.g., dividing the lead in a micro-resistor by the weight of an entire 5 kg server).

On **September 10, 2015**, the European Court of Justice (ECJ) delivered a landmark ruling in **Case C-106/14**:

> **"Once an Article, Always an Article" (O5A)**:
> An article remains an article as long as it retains its shape, surface, or design. When individual articles are assembled or joined together into a "complex object" (such as a PCBA, sub-assembly, or complete device), **each individual sub-article retains its independent duty of notification**.

### Mathematical Worked Example: Why Dilution is Illegal

```text
       ┌─────────────────────────────────────────────────────────────┐
       │ COMPLEX OBJECT: Server Motherboard (Total Weight: 1000.0 g)  │
       │                                                             │
       │   ┌─────────────────────────────────────────────────────┐   │
       │   │ SUB-ARTICLE: SMT Thick-Film Resistor                │   │
       │   │ Component Total Weight: 0.002 g                     │   │
       │   │ Glass Layer contains Lead Monoxide (PbO): 0.0001 g  │   │
       │   └─────────────────────────────────────────────────────┘   │
       └─────────────────────────────────────────────────────────────┘
```

#### Incorrect Dilution Calculation (Illegal):
$$\text{Concentration} = \frac{\text{Mass of PbO}}{\text{Total Motherboard Weight}} = \frac{0.0001\,\text{g}}{1000.0\,\text{g}} = 0.00001\% = 0.1\,\text{ppm} \quad (\ll 0.1\%)$$
Under this flawed logic, no disclosure would be made.

#### Correct O5A Legal Calculation (Mandatory):
The resistor is an independent article before assembly into the complex board:
$$\text{Concentration} = \frac{\text{Mass of PbO}}{\text{Total Resistor Weight}} = \frac{0.0001\,\text{g}}{0.002\,\text{g}} = 5.0\%\,w/w$$
Since $5.0\% > 0.1\%$, **Article 33 notification IS MANDATORY**. The manufacturer must disclose that the PCBA contains Lead Monoxide in its thick-film chip resistors.

---

## 6. Annex XVII (Restrictions) vs Annex XIV (Authorisation)

| Parameter | Annex XVII (Restricted Substances) | Annex XIV (Authorisation List) |
| :--- | :--- | :--- |
| **Purpose** | Immediate or scheduled **ban or strict cap** on specific uses where an unacceptable risk to human health or the environment is proven. | Mechanism to encourage industry to phase out SVHCs and replace them with safer alternatives. |
| **Enforcement Mechanism** | Prohibits placing on the market or using the substance for specified restricted applications. | The substance **cannot be used in the EU after a specific "Sunset Date"**, unless the user holds a specific, approved Authorization granted by the European Commission. |
| **Applies to Articles?** | **YES**. Many restrictions specifically govern finished articles (e.g. nickel release on smartwatch cases). | Strictly governs **manufacturing operations inside the EU**. Imported finished articles do not require Annex XIV authorization (though they remain subject to Article 33, SCIP, and Annex XVII). |
| **Key Hardware Examples** | - **Entry 27 (Nickel)**: Restricts nickel release ($< 0.5\,\mu\text{g/cm}^2/\text{week}$) on items with prolonged skin contact (wearable fitness bands, smartwatches).<br>- **Entry 51/52 (Phthalates)**: Restricts DEHP, DBP, BBP, DIBP in toys and childcare equipment.<br>- **Entry 63 (Lead)**: Restricts lead in jewelry and articles that children could mouth. | - Hexavalent chromium compounds used in surface plating facilities within the EU.<br>- Certain industrial phthalates used as plasticizers in EU-based polymer processing plants. |

---

## 7. SCIP Database Reporting (EU Waste Framework Directive)

Under the revised **Waste Framework Directive (Directive (EU) 2018/851)**, Article 9(1)(i) mandates that any company producing, importing, or distributing articles containing Candidate List SVHCs $> 0.1\%\,w/w$ on the EU market must submit detailed product data to the **SCIP Database** managed by ECHA.

- **Mandatory Live Date**: January 5, 2021.
- **Acronym**: **S**ubstances of **C**oncern **I**n articles as such or in complex objects (**P**roducts).
- **Target Audience**: Waste operators, recyclers, and consumers seeking circular economy disassembly data.

```text
Hardware Manufacturer / Importer
               │
               ▼
[Scrub BOM for Articles with SVHC > 0.1% w/w]
               │
               ▼
[Prepare SCIP Dossier (IUCLID Format)]
├── Primary Article Identifier (Part Number / EAN / GTIN)
├── TARIC / CN Customs Code
├── Safe Use Instructions & Disassembly Guidance
└── Material Category & Linking to Specific Sub-Articles
               │
               ▼
[Submit via ECHA Submission Portal]
               │
               ▼
Receives Unique SCIP Number (UUID) ──► Shared with downstream EU distributors
```

---

## 8. Detailed Comparison: RoHS vs REACH

Engineers often confuse RoHS and REACH because both are EU environmental regulations covering hazardous chemicals. Their legal architectures, however, differ fundamentally:

| Comparison Dimension | RoHS (Directive 2011/65/EU + 2015/863) | REACH (Regulation (EC) No 1907/2006) |
| :--- | :--- | :--- |
| **Legal Nature** | **Directive**: Must be transposed into national laws of each EU Member State. | **Regulation**: Directly applicable and legally binding in all EU Member States without national transposition. |
| **Scope of Products** | Specifically **Electrical & Electronic Equipment (EEE)** operating $\le 1000\,\text{V AC}$ or $\le 1500\,\text{V DC}$. | **All physical goods, chemicals, and articles** (electronics, clothing, toys, automotive, chemicals). |
| **Number of Substances** | **Exactly 10 restricted substances** (Pb, Cd, Hg, Cr6+, PBB, PBDE, and 4 phthalates). | **240+ substances on Candidate List (SVHC)**, plus hundreds in Annex XVII and Annex XIV. |
| **Threshold Calculation Basis** | Per **Homogeneous Material** (e.g., pin plating, solder joint, mold compound). | Per **Individual Article** under the O5A ruling (e.g., entire resistor, bare screw, connector housing). |
| **What Happens if Exceeded?** | **BANNED**. Product cannot be placed on the EU market unless an explicit Annex III/IV exemption applies. | **ALLOWED (usually)**, but triggers **mandatory reporting** (Article 33 customer disclosure and SCIP database filing). *(Annex XVII bans specific uses).* |
| **CE Marking** | **MANDATORY**. RoHS is a direct CE marking directive; product requires an EU Declaration of Conformity (DoC). | **NO CE MARK**. REACH does not grant or govern the CE mark. |
| **Exemptions Mechanism** | Fixed list in Annex III and IV with defined expiration dates. | Authorisation (Annex XIV) or socio-economic derogations. |

---

## 9. Hardware Engineering Compliance Workflow at VVDN

To ensure continuous REACH compliance during product design, component procurement, and manufacturing:

1. **Bi-Annual Candidate List Audits**:
   - Establish automated alerts whenever ECHA updates the SVHC list (every January and June/July).
   - Re-screen existing Bills of Materials (BOMs) against newly added substance CAS numbers.

2. **Supply Chain Data Collection**:
   - Request **Full Material Disclosure (FMD)** in **IPC-1752A Class D** XML format from semiconductor vendors.
   - For custom passive, plastic, or mechanical parts, obtain signed REACH SVHC Declarations specifying the active Candidate List version.

3. **Complex Object Hierarchy Modeling**:
   - Maintain product assembly trees in PLM/ERP software to track which specific sub-tier articles contain SVHCs (e.g., brass standoffs containing lead $> 0.1\%\,w/w$).

4. **SCIP Dossier Generation**:
   - Before shipping products to European customers, generate the ECHA IUCLID dossier and file the SCIP submission.
   - Transmit the resulting SCIP UUID to European distributors and sales channels.
