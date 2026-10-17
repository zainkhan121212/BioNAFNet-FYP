"""
Apply LGU FYP Guidelines to BioNAFNet_FYP_Final_Report.docx

Guidelines from 'guidlibnes of fyp.docx':
- Heading1: Times New Roman, Bold, 20pt, RIGHT alignment (chapter names)
- Heading2: Arial, Bold, Italic, 14pt, LEFT alignment (topic headings)
- Heading3: Arial, Bold, 13pt, LEFT alignment (sub headings)
- Paragraph: Times New Roman, 12pt, JUSTIFY alignment
- Paragraph spacing: 6pt after, 12pt before
- Line spacing: 1.5
- Table caption: ON TOP of table
- Figure caption: ON BOTTOM of figure (already done)
- References: Alphabetically ordered
- Copyrights/Declaration: match template wording
"""
import copy
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml

DOC_PATH = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_FYP_Final_Report.docx"
OUT_PATH = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_FYP_Final_Report_v2.docx"

doc = Document(DOC_PATH)

# ── 1. Fix Heading Styles ──
print("[1] Fixing heading styles...")

# Modify Heading 1 style
h1_style = doc.styles['Heading 1']
h1_style.font.name = 'Times New Roman'
h1_style.font.size = Pt(20)
h1_style.font.bold = True
h1_style.font.italic = False
h1_style.font.color.rgb = RGBColor(0, 0, 0)
h1_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
h1_style.paragraph_format.space_before = Pt(24)
h1_style.paragraph_format.space_after = Pt(12)
h1_style.paragraph_format.line_spacing = 1.5

# Modify Heading 2 style
h2_style = doc.styles['Heading 2']
h2_style.font.name = 'Arial'
h2_style.font.size = Pt(14)
h2_style.font.bold = True
h2_style.font.italic = True
h2_style.font.color.rgb = RGBColor(0, 0, 0)
h2_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
h2_style.paragraph_format.space_before = Pt(18)
h2_style.paragraph_format.space_after = Pt(6)
h2_style.paragraph_format.line_spacing = 1.5

# Modify Heading 3 style
h3_style = doc.styles['Heading 3']
h3_style.font.name = 'Arial'
h3_style.font.size = Pt(13)
h3_style.font.bold = True
h3_style.font.italic = False
h3_style.font.color.rgb = RGBColor(0, 0, 0)
h3_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
h3_style.paragraph_format.space_before = Pt(12)
h3_style.paragraph_format.space_after = Pt(6)
h3_style.paragraph_format.line_spacing = 1.5

print("  OK: H1=TNR/Bold/20pt/Right, H2=Arial/Bold/Italic/14pt/Left, H3=Arial/Bold/13pt/Left")

# ── 2. Fix Normal (paragraph) style ──
print("[2] Fixing paragraph style...")
normal_style = doc.styles['Normal']
normal_style.font.name = 'Times New Roman'
normal_style.font.size = Pt(12)
normal_style.font.bold = False
normal_style.font.italic = False
normal_style.font.color.rgb = RGBColor(0, 0, 0)
normal_style.paragraph_format.space_before = Pt(12)
normal_style.paragraph_format.space_after = Pt(6)
normal_style.paragraph_format.line_spacing = 1.5
print("  OK: TNR/12pt, 12pt before, 6pt after, 1.5 line spacing")

# ── 3. Apply justify alignment to all normal paragraphs ──
print("[3] Applying justify alignment to body paragraphs...")
justify_count = 0
for para in doc.paragraphs:
    style_name = para.style.name if para.style else ''
    # Don't change headings, centered items (title pages, captions, image placeholders)
    if 'Heading' in style_name:
        continue
    if para.alignment == WD_ALIGN_PARAGRAPH.CENTER:
        continue
    # Set justify for body text
    para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    para.paragraph_format.space_before = Pt(12)
    para.paragraph_format.space_after = Pt(6)
    para.paragraph_format.line_spacing = 1.5
    justify_count += 1
print(f"  OK: {justify_count} paragraphs set to justified")

# ── 4. Fix all runs in non-heading paragraphs to TNR 12pt ──
print("[4] Fixing font in all body text runs...")
run_count = 0
for para in doc.paragraphs:
    style_name = para.style.name if para.style else ''
    if 'Heading' in style_name:
        continue
    for run in para.runs:
        # Don't override existing italic captions (Figure/Table captions)
        if run.italic and run.font.size == Pt(10):
            continue  # keep caption formatting
        # Don't override red INSERT markers
        if run.font.color and run.font.color.rgb == RGBColor(0xCC, 0x00, 0x00):
            continue
        run.font.name = 'Times New Roman'
        if run.font.size is None or run.font.size != Pt(10):
            run.font.size = Pt(12)
        run_count += 1
print(f"  OK: {run_count} runs updated")

# ── 5. Fix heading runs (in case they inherited wrong formatting) ──
print("[5] Fixing heading run fonts...")
for para in doc.paragraphs:
    style_name = para.style.name if para.style else ''
    if style_name == 'Heading 1':
        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for run in para.runs:
            run.font.name = 'Times New Roman'
            run.font.size = Pt(20)
            run.font.bold = True
            run.font.italic = False
            run.font.color.rgb = RGBColor(0, 0, 0)
    elif style_name == 'Heading 2':
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in para.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.italic = True
            run.font.color.rgb = RGBColor(0, 0, 0)
    elif style_name == 'Heading 3':
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in para.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(13)
            run.font.bold = True
            run.font.italic = False
            run.font.color.rgb = RGBColor(0, 0, 0)
print("  OK: All heading runs corrected")

# ── 6. Fix List Bullet and List Number styles ──
print("[6] Fixing list styles...")
for style_name in ['List Bullet', 'List Number']:
    try:
        ls = doc.styles[style_name]
        ls.font.name = 'Times New Roman'
        ls.font.size = Pt(12)
        ls.paragraph_format.space_before = Pt(6)
        ls.paragraph_format.space_after = Pt(3)
        ls.paragraph_format.line_spacing = 1.5
    except:
        pass
print("  OK: List styles updated")

# ── 7. Fix Copyrights text ──
print("[7] Updating Copyrights text...")
for para in doc.paragraphs:
    if 'All rights reserved' in para.text:
        para.clear()
        run = para.add_run(
            'This is to certify that the project titled "BioNAFNet: Biologically-Inspired Low-Light Image '
            'Enhancement Using Deep Learning with Knowledge Distillation" is the genuine work carried out by '
            '[Student Names], student of BSSE of Software Engineering Department, Lahore Garrison University, '
            'Lahore. During the academic year [Year], in partial fulfilment of the requirements for the award '
            'of the degree of Bachelor of Science in Software Engineering and that the project has not formed '
            'the basis for the award previously of any other degree, diploma, fellowship or any other similar title.'
        )
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        break
print("  OK: Copyrights updated to LGU template wording")

# ── 8. Fix Declaration text ──
print("[8] Updating Declaration text...")
for para in doc.paragraphs:
    if 'We hereby declare' in para.text:
        para.clear()
        run = para.add_run(
            'This is to declare that the project entitled "BioNAFNet: Biologically-Inspired Low-Light Image '
            'Enhancement Using Deep Learning with Knowledge Distillation" is an original work done by '
            'undersigned, in partial fulfilment of the requirements for the degree "Bachelor of Science in '
            'Software Engineering" at Software Engineering Department, Lahore Garrison University, Lahore.\n\n'
            'All the analysis, design and system development have been accomplished by the undersigned. '
            'Moreover, this project has not been submitted to any other college or university.'
        )
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        para.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        break
print("  OK: Declaration updated to LGU template wording")

# ── 9. Sort references alphabetically ──
print("[9] Sorting references alphabetically...")
ref_start = None
ref_end = None
ref_paras = []
in_refs = False
for i, para in enumerate(doc.paragraphs):
    text = para.text.strip()
    if para.style and para.style.name == 'Heading 2' and 'References' in text:
        in_refs = True
        ref_start = i + 1
        continue
    if in_refs:
        if text.startswith('[') and ']' in text:
            ref_paras.append((i, text))
        elif para.style and 'Heading' in (para.style.name or ''):
            in_refs = False
            ref_end = i
            break

if ref_paras:
    # Sort by author name (after the [N] prefix)
    def get_sort_key(item):
        idx, text = item
        # Remove [N] prefix
        if ']' in text:
            return text[text.index(']')+1:].strip().upper()
        return text.upper()
    
    sorted_refs = sorted(ref_paras, key=get_sort_key)
    
    # Re-number and update text in place
    for new_num, (orig_idx, orig_text) in enumerate(sorted_refs, 1):
        # Find the ] to get the content after the number
        bracket_end = orig_text.index(']')
        content = orig_text[bracket_end+1:].strip()
        new_text = f'[{new_num}] {content}'
        
        para = doc.paragraphs[orig_idx]
        para.clear()
        run = para.add_run(new_text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
    
    print(f"  OK: {len(sorted_refs)} references sorted alphabetically and re-numbered")
else:
    print("  SKIP: No references found to sort")

# ── 10. Fix page margins ──
print("[10] Setting page margins...")
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)  # 1.25 inches
    section.right_margin = Cm(2.54)  # 1 inch
print("  OK: Margins set (1.25in left, 1in top/bottom/right)")

# ── 11. Fix table formatting ──
print("[11] Fixing table cell formatting...")
table_count = 0
for table in doc.tables:
    table_count += 1
    for row in table.rows:
        for cell in row.cells:
            for para in cell.paragraphs:
                para.paragraph_format.space_before = Pt(2)
                para.paragraph_format.space_after = Pt(2)
                para.paragraph_format.line_spacing = 1.0
                for run in para.runs:
                    run.font.name = 'Times New Roman'
                    if not run.bold:
                        run.font.size = Pt(10)
print(f"  OK: {table_count} tables formatted (TNR, 10pt, tight spacing)")

# ── 12. Fix caption formatting ── 
print("[12] Fixing caption styles...")
cap_count = 0
for para in doc.paragraphs:
    text = para.text.strip()
    if (text.startswith('Figure ') or text.startswith('Table ')) and ':' in text[:20]:
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in para.runs:
            run.italic = True
            run.font.size = Pt(10)
            run.font.name = 'Times New Roman'
        cap_count += 1
print(f"  OK: {cap_count} captions formatted")

# ── Save ──
doc.save(OUT_PATH)
print(f"\n{'='*60}")
print(f"DONE! Guidelines applied and saved to:")
print(f"  {OUT_PATH}")
print(f"{'='*60}")

# Count
para_count = len(doc.paragraphs)
print(f"Total paragraphs: {para_count}")
print(f"Total tables: {table_count}")
