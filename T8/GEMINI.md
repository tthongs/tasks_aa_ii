# Tekken 8 - Fahkumram Combo Extraction Project

This project contains extracted combo notations for Fahkumram in Tekken 8,
retrieved from a collection of YouTube ReVanced video screenshots located in
the `scr/` directory. The extracted combos have been compiled into an organized
and professionally styled Excel spreadsheet.

## Project Structure

```
T8/
├── scr/                                 # Directory containing screenshots
│   └── Screenshot_20260629_*.jpg        # 56 video screenshots of combos
├── Fahkumram_Tekken_8_Combos.xlsx       # Styled Excel spreadsheet of combos
└── GEMINI.md                            # Project documentation (this file)
```

## Compilation and Extraction Methodology

1. **OCR Pre-filtering**: A local Tesseract-OCR environment was set up to
   read headers and tooltips from the screenshots.
2. **Visual Verification**: Custom image segmentation and projection profiling
   were designed in Python using Pillow to identify individual icon sequences.
3. **Manual Verification**: High-resolution multiclass visualization was used
   to double-check every move notation and group related images.
4. **Data Aggregation**: The compiled data was structured into a pandas
   DataFrame and written to Excel with advanced formatting using `openpyxl`.

## Combo Sheet Column Structure

The generated spreadsheet `Fahkumram_Tekken_8_Combos.xlsx` includes the
following fields:

- **ID**: Unique combo identifier.
- **Category**: Action category (e.g., Normal Hit, Counter Hit, Heat Active,
  Wall Splat, Wall Carry, Mini-Combo).
- **Launcher**: The primary launcher move for the combo.
- **Alternative Launcher(s)**: Optional launchers that can initiate the same
  combo sequence.
- **Combo Notation**: The button inputs and directional movements in standard
  Tekken notation (1P right-facing).
- **Tooltip / Notes**: Execution tips, just-frame timings, and stage-specific
  hazard instructions.
- **Source Screenshots**: The specific file name(s) in `scr/` corresponding
  to the source image.

## Legend & Button Notation Guide

- **f, b, d, u**: Forward, Back, Down, Up (directions).
- **df, db, uf, ub**: Diagonal directions.
- **n**: Neutral (no input).
- **1**: Left Punch.
- **2**: Right Punch.
- **3**: Left Kick.
- **4**: Right Kick.
- **1+2, 3+4**: Simultaneous button presses.
- **[button] / [1+2]**: Square brackets indicate a Just Frame input (press
  extremely quickly).
- **(button)**: Parentheses indicate optional hits, or hits that must whiff/be
  blocked before executing the follow-up.
- **Tornado**: Tornado spin launcher (used for combo extensions).
- **Heat Dash / Heat Burst**: Heat mechanic movements.
