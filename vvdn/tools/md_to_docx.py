#!/usr/bin/env python3
"""
Markdown to DOCX Converter for VVDN Engineering Hub
Translates structured Markdown documents (Headings, Tables, Lists, Callouts, Code Blocks)
into professionally styled Microsoft Word (.docx) documents suitable for executive and mentor review.
"""

import sys
import os
import re
from pathlib import Path

# Add local venv site-packages if present
venv_site = Path(__file__).parent / ".venv" / "lib"
if venv_site.exists():
    for p in venv_site.glob("python*/site-packages"):
        sys.path.insert(0, str(p))

try:
    import docx
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn
except ImportError:
    print("Error: python-docx is required. Please install it or use tools/.venv/bin/python.")
    sys.exit(1)


# Color Palette
COLOR_PRIMARY = RGBColor(24, 76, 120)     # VVDN Deep Blue
COLOR_SECONDARY = RGBColor(70, 130, 180)  # Steel Blue
COLOR_DARK = RGBColor(40, 44, 52)         # Off-black body text
COLOR_MUTED = RGBColor(100, 110, 125)     # Gray
HEX_HEADER_BG = "204A6E"                  # Dark blue for table headers
HEX_ZEBRA_BG = "F4F7F9"                   # Subtle table zebra striping
HEX_CODE_BG = "F5F6F8"                    # Code background
HEX_CALLOUT_NOTE = "EBF3FA"               # Light blue
HEX_CALLOUT_WARN = "FFF8E6"               # Light amber
HEX_CALLOUT_CAUTION = "FDF0ED"            # Light red
HEX_CALLOUT_BORDER = "31708F"


def set_cell_background(cell, hex_color):
    """Set the background fill color of a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding/margins for a table cell (in dxa: 20 dxa = 1 pt)."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)


def set_callout_border(cell, hex_color="2B6CB0"):
    """Set a thick left border on a single-cell callout table."""
    tcPr = cell._element.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:top w:val="none"/>
            <w:left w:val="single" w:sz="36" w:space="0" w:color="{hex_color}"/>
            <w:bottom w:val="none"/>
            <w:right w:val="none"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)


def set_table_borders(table, hex_color="D0D7DE"):
    """Set subtle, professional borders on a table."""
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>
                <w:left w:val="none"/>
                <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{hex_color}"/>
                <w:right w:val="none"/>
                <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{hex_color}"/>
                <w:insideV w:val="none"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)


def format_inline_runs(paragraph, text, base_font_size=Pt(10.5), base_color=COLOR_DARK, is_italic=False):
    """Parses markdown inline bold (**text**), italics (*text*), inline code (`code`), and links."""
    # Pattern to tokenize: bold-italic, bold, italic, code, links, normal text
    pattern = re.compile(
        r'(\*\*\*.*?\*\*\*|\*\*.*?\*\*|\*.*?\*|`.*?`|\[.*?\]\(.*?\)|\$.*?\$)'
    )
    parts = pattern.split(text)

    for part in parts:
        if not part:
            continue
        if part.startswith('***') and part.endswith('***'):
            run = paragraph.add_run(part[3:-3])
            run.bold = True
            run.italic = True
            run.font.size = base_font_size
            run.font.color.rgb = base_color
        elif part.startswith('**') and part.endswith('**'):
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.font.size = base_font_size
            run.font.color.rgb = base_color
        elif part.startswith('*') and part.endswith('*'):
            run = paragraph.add_run(part[1:-1])
            run.italic = True
            run.font.size = base_font_size
            run.font.color.rgb = base_color
        elif part.startswith('`') and part.endswith('`'):
            run = paragraph.add_run(part[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(base_font_size.pt * 0.9)
            run.font.color.rgb = RGBColor(180, 40, 60)
        elif part.startswith('$') and part.endswith('$'):
            # Math formulas: clean up LaTeX markers for Word
            clean_math = part[1:-1].replace(r'\text{', '').replace(r'}', '').replace(r'^{\circ}', '°').replace(r'\le', '≤').replace(r'\ge', '≥').replace(r'\mu', 'µ').replace(r'\times', '×').replace(r'\pm', '±')
            run = paragraph.add_run(clean_math)
            run.italic = True
            run.font.size = base_font_size
            run.font.color.rgb = RGBColor(20, 90, 160)
        elif part.startswith('[') and '](' in part and part.endswith(')'):
            m = re.match(r'\[(.*?)\]\((.*?)\)', part)
            if m:
                label, url = m.groups()
                run = paragraph.add_run(label)
                run.underline = True
                run.font.color.rgb = RGBColor(0, 102, 204)
                run.font.size = base_font_size
        else:
            run = paragraph.add_run(part)
            run.font.size = base_font_size
            run.font.color.rgb = base_color
            if is_italic:
                run.italic = True


def convert_md_to_docx(md_path: Path, docx_path: Path = None) -> Path:
    """Converts a single Markdown file to a styled .docx file."""
    if docx_path is None:
        docx_path = md_path.with_suffix('.docx')

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    doc = Document()

    # Configure Page Margins (0.8 inches all around)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        
        # Add Page numbering in footer
        footer = section.footer
        f_p = footer.paragraphs[0]
        f_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        f_run = f_p.add_run(f"VVDN Engineering Hub  |  {md_path.stem.upper()}")
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = COLOR_MUTED

    # Setup Default Styles
    style_normal = doc.styles['Normal']
    style_normal.font.name = 'Segoe UI'
    style_normal.font.size = Pt(10.5)
    style_normal.font.color.rgb = COLOR_DARK
    style_normal.paragraph_format.line_spacing = 1.15
    style_normal.paragraph_format.space_after = Pt(4)

    lines = md_content.split('\n')
    i = 0
    total_lines = len(lines)

    in_code_block = False
    code_block_lines = []
    in_table = False
    table_rows = []

    while i < total_lines:
        line = lines[i]

        # Handle Code Fences
        if line.strip().startswith('```'):
            if in_code_block:
                # Flush code block
                tbl = doc.add_table(rows=1, cols=1)
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                cell = tbl.cell(0, 0)
                set_cell_background(cell, HEX_CODE_BG)
                set_cell_margins(cell, top=80, bottom=80, left=140, right=140)
                
                # Single left border
                tcPr = cell._element.get_or_add_tcPr()
                borders = parse_xml(f'<w:tcBorders {nsdecls("w")}><w:left w:val="single" w:sz="18" w:space="0" w:color="CBD5E0"/><w:top w:val="none"/><w:right w:val="none"/><w:bottom w:val="none"/></w:tcBorders>')
                tcPr.append(borders)

                p = cell.paragraphs[0]
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(0)
                run = p.add_run('\n'.join(code_block_lines))
                run.font.name = 'Consolas'
                run.font.size = Pt(9.0)
                run.font.color.rgb = RGBColor(45, 55, 72)

                doc.add_paragraph()  # spacing
                code_block_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

        # Handle Tables
        if line.strip().startswith('|') and line.strip().endswith('|'):
            table_rows.append(line.strip())
            i += 1
            # Check if table continues
            if i < total_lines and lines[i].strip().startswith('|'):
                continue
            else:
                # Process collected table
                if len(table_rows) >= 2:
                    # Parse header and rows
                    headers = [c.strip() for c in table_rows[0].strip('|').split('|')]
                    # row 1 is separator |:---|:---|
                    data_rows = []
                    for r in table_rows[2:]:
                        data_rows.append([c.strip() for c in r.strip('|').split('|')])

                    cols_count = len(headers)
                    tbl = doc.add_table(rows=len(data_rows) + 1, cols=cols_count)
                    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                    set_table_borders(tbl)

                    # Populate Header
                    hdr_cells = tbl.rows[0].cells
                    for c_idx, h_text in enumerate(headers):
                        if c_idx < len(hdr_cells):
                            cell = hdr_cells[c_idx]
                            set_cell_background(cell, HEX_HEADER_BG)
                            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
                            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                            p = cell.paragraphs[0]
                            p.paragraph_format.space_after = Pt(0)
                            format_inline_runs(p, h_text, base_font_size=Pt(9.5), base_color=RGBColor(255, 255, 255))
                            for r in p.runs:
                                r.bold = True

                    # Populate Data Rows
                    for r_idx, row_data in enumerate(data_rows):
                        row_cells = tbl.rows[r_idx + 1].cells
                        is_even = (r_idx % 2 == 1)
                        for c_idx, cell_value in enumerate(row_data):
                            if c_idx < len(row_cells):
                                cell = row_cells[c_idx]
                                if is_even:
                                    set_cell_background(cell, HEX_ZEBRA_BG)
                                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                                cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                                p = cell.paragraphs[0]
                                p.paragraph_format.space_after = Pt(0)
                                format_inline_runs(p, cell_value, base_font_size=Pt(9.0))

                    doc.add_paragraph()  # Spacing after table
                table_rows = []
                continue

        # Handle Alert / Callout blocks (> [!NOTE], > [!WARNING], > [!IMPORTANT], > [!CAUTION])
        if line.strip().startswith('>'):
            callout_lines = []
            while i < total_lines and lines[i].strip().startswith('>'):
                callout_lines.append(re.sub(r'^>\s?', '', lines[i].strip()))
                i += 1
            callout_text = '\n'.join(callout_lines)

            # Detect callout kind
            kind = "NOTE"
            bg_hex = HEX_CALLOUT_NOTE
            border_hex = "2B6CB0"
            if "[!WARNING]" in callout_text:
                kind = "WARNING"
                bg_hex = HEX_CALLOUT_WARN
                border_hex = "D69E2E"
                callout_text = callout_text.replace("[!WARNING]", "").strip()
            elif "[!IMPORTANT]" in callout_text:
                kind = "IMPORTANT"
                bg_hex = HEX_CALLOUT_NOTE
                border_hex = "3182CE"
                callout_text = callout_text.replace("[!IMPORTANT]", "").strip()
            elif "[!CAUTION]" in callout_text:
                kind = "CAUTION"
                bg_hex = HEX_CALLOUT_CAUTION
                border_hex = "E53E3E"
                callout_text = callout_text.replace("[!CAUTION]", "").strip()
            elif "[!NOTE]" in callout_text:
                kind = "NOTE"
                callout_text = callout_text.replace("[!NOTE]", "").strip()

            tbl = doc.add_table(rows=1, cols=1)
            tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            cell = tbl.cell(0, 0)
            set_cell_background(cell, bg_hex)
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            set_callout_border(cell, border_hex)

            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(0)
            tag_run = p.add_run(f"[{kind}] ")
            tag_run.bold = True
            tag_run.font.size = Pt(10.0)
            tag_run.font.color.rgb = RGBColor.from_string(border_hex)

            format_inline_runs(p, callout_text, base_font_size=Pt(10.0))
            doc.add_paragraph()  # Spacing
            continue

        # Handle Headings
        if line.startswith('# '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(8)
            format_inline_runs(h, line[2:].strip(), base_font_size=Pt(20), base_color=COLOR_PRIMARY)
            for r in h.runs:
                r.bold = True
            i += 1
            continue
        elif line.startswith('## '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(6)
            format_inline_runs(h, line[3:].strip(), base_font_size=Pt(14), base_color=COLOR_PRIMARY)
            for r in h.runs:
                r.bold = True
            i += 1
            continue
        elif line.startswith('### '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(8)
            h.paragraph_format.space_after = Pt(4)
            format_inline_runs(h, line[4:].strip(), base_font_size=Pt(12), base_color=COLOR_SECONDARY)
            for r in h.runs:
                r.bold = True
            i += 1
            continue
        elif line.startswith('#### '):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(6)
            h.paragraph_format.space_after = Pt(2)
            format_inline_runs(h, line[5:].strip(), base_font_size=Pt(11), base_color=COLOR_DARK)
            for r in h.runs:
                r.bold = True
            i += 1
            continue

        # Handle Horizontal Rules (---)
        if line.strip() in ['---', '***', '___']:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p_border = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="6" w:space="1" w:color="E2E8F0"/></w:pBdr>')
            p._element.get_or_add_pPr().append(p_border)
            i += 1
            continue

        # Handle Bulleted Lists
        if re.match(r'^\s*[-*]\s+', line):
            indent_level = (len(line) - len(line.lstrip())) // 2
            bullet_text = re.sub(r'^\s*[-*]\s+', '', line)
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            p.paragraph_format.space_after = Pt(2)
            format_inline_runs(p, bullet_text)
            i += 1
            continue

        # Handle Numbered Lists
        if re.match(r'^\s*\d+\.\s+', line):
            indent_level = (len(line) - len(line.lstrip())) // 2
            num_text = re.sub(r'^\s*\d+\.\s+', '', line)
            p = doc.add_paragraph(style='List Number')
            p.paragraph_format.left_indent = Inches(0.25 * (indent_level + 1))
            p.paragraph_format.space_after = Pt(2)
            format_inline_runs(p, num_text)
            i += 1
            continue

        # Handle Empty Lines
        if not line.strip():
            i += 1
            continue

        # Normal Paragraph
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(4)
        format_inline_runs(p, line.strip())
        i += 1

    doc.save(str(docx_path))
    return docx_path


def main():
    base_dir = Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1 and sys.argv[1] != '--all':
        target = Path(sys.argv[1]).resolve()
        if target.is_file() and target.suffix == '.md':
            out = convert_md_to_docx(target)
            print(f"✓ Converted: {target} -> {out}")
            return
        elif target.is_dir():
            md_files = list(target.rglob("*.md"))
        else:
            print(f"Invalid target: {target}")
            return
    else:
        # Default: scan standards/, protocols/, and evse/
        scan_dirs = ["standards", "protocols", "evse"]
        md_files = []
        for d in scan_dirs:
            p = base_dir / d
            if p.exists():
                md_files.extend(p.rglob("*.md"))
        md_files = sorted(md_files)

    print(f"Found {len(md_files)} Markdown files to process.")
    for md_file in md_files:
        try:
            out = convert_md_to_docx(md_file)
            try:
                rel = md_file.relative_to(base_dir)
            except ValueError:
                rel = md_file.name
            print(f"✓ Converted: {rel} -> {out.name}")
        except Exception as e:
            print(f"✗ Failed {md_file}: {e}")


if __name__ == '__main__':
    main()
