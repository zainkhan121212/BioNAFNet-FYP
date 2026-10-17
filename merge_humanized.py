"""
merge_humanized_v2.py  (FIXED)
────────────────────────────────
Safely merges REWRITE_GUIDE.md into BioNAFNet_Master_Report.docx.

KEY FIX:  Process sections in REVERSE paragraph-index order so that
any paragraph manipulation never shifts the indices of sections we
haven't processed yet.  Also: NO insertions; extra text is concatenated
into the last available slot to avoid corrupting the XML tree.

RULES
  ✓  Heading styles are NEVER changed.
  ✓  Images (inline drawings) are NEVER touched.
  ✓  Tables are NEVER touched.
  ✓  Figure / Table captions are NEVER touched.
  ✓  [INSERT FIGURE ...] placeholders NEVER touched.
  ✓  Only 'Normal'-style prose paragraphs get new text.
"""

import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH

SRC   = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Master_Report.docx"
GUIDE = r"F:\low_light_enhancement\eye adaption\BioNAFNet\REWRITE_GUIDE.md"
OUT   = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Master_Report_Humanized.docx"

WP_NS = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'


# ════════════════════════════════════════════════════════════════
# 1) Parse REWRITE_GUIDE.md
# ════════════════════════════════════════════════════════════════
def parse_guide(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sections = {}
    current_key = None
    current_paras = []
    buf = []

    def flush():
        nonlocal buf
        text = ' '.join(buf).strip()
        if text:
            text = text.replace('**', '')
            current_paras.append(text)
        buf = []

    for line in lines:
        stripped = line.strip()

        # ── detect section headers ──
        new_key = None
        if re.match(r'^###\s+ABSTRACT', stripped, re.I):
            new_key = 'abstract'
        elif m := re.match(r'^#{2,4}\s+(\d+\.\d+\.?\d*)\b', stripped):
            new_key = m.group(1)
        elif m := re.match(r'^###\s+CHAPTER\s+(\d+)', stripped, re.I):
            new_key = f'chapter_{m.group(1)}'

        if new_key:
            flush()
            if current_key is not None:
                sections[current_key] = current_paras
            current_key = new_key
            current_paras = []
            buf = []
            continue

        # ── stop at meta sections ──
        if stripped.startswith('## STEP') or stripped.startswith('## HOW TO USE'):
            flush()
            if current_key is not None:
                sections[current_key] = current_paras
            current_key = None
            current_paras = []
            buf = []
            continue

        if current_key is None:
            continue

        # ── skip no-rewrite markers ──
        if stripped.startswith('(Table') or stripped.startswith('(Figures') or stripped.startswith('(Pseudocode'):
            flush()
            continue

        if stripped == '---':
            flush()
            continue

        # ── paragraph break on blank line ──
        if stripped == '':
            flush()
            continue

        buf.append(stripped)

    flush()
    if current_key is not None:
        sections[current_key] = current_paras

    # Drop empty sections (chapter headers with no text)
    return {k: v for k, v in sections.items() if v}


# ════════════════════════════════════════════════════════════════
# 2) Paragraph inspection helpers
# ════════════════════════════════════════════════════════════════
def has_image(para):
    el = para._element
    return bool(el.findall(f'.//{{{WP_NS}}}inline') or
                el.findall(f'.//{{{WP_NS}}}anchor'))

def is_protected(para):
    """Return True for any paragraph we must NOT touch."""
    t = para.text.strip()
    sn = para.style.name

    if sn.startswith('Heading'):
        return True
    if has_image(para):
        return True
    if not t:
        return True
    # Figure / Table captions
    if re.match(r'^(Figure|Table)\s+\d+', t):
        return True
    # Figure placeholders
    if t.startswith('[INSERT FIGURE'):
        return True
    return False


# ════════════════════════════════════════════════════════════════
# 3) Build heading index + ALL heading boundaries
# ════════════════════════════════════════════════════════════════
def build_heading_index(doc):
    """
    Returns:
      idx:             dict mapping section keys -> paragraph index
      all_heading_pos: sorted list of ALL heading paragraph indices
                       (used for boundary detection, includes References,
                        Appendices, etc. even if they have no section number)
    """
    idx = {}
    all_heading_pos = []
    for i, p in enumerate(doc.paragraphs):
        t = p.text.strip()
        if p.style.name.startswith('Heading'):
            all_heading_pos.append(i)
            if m := re.match(r'^(\d+\.\d+\.?\d*)\b', t):
                idx[m.group(1)] = i
            elif m2 := re.match(r'^Chapter\s+(\d+)', t, re.I):
                idx[f'chapter_{m2.group(1)}'] = i
        if t.lower() == 'abstract' and (p.style.name.startswith('Heading') or
                                         p.alignment == WD_ALIGN_PARAGRAPH.CENTER):
            idx['abstract'] = i
            if i not in all_heading_pos:
                all_heading_pos.append(i)
    all_heading_pos.sort()
    return idx, all_heading_pos


# ════════════════════════════════════════════════════════════════
# 4) Replace paragraph text (preserve formatting)
# ════════════════════════════════════════════════════════════════
def replace_text(para, new_text):
    """Set paragraph text to new_text, keeping original font/style."""
    # Grab formatting from the first run
    fmt = {}
    if para.runs:
        r0 = para.runs[0]
        fmt['name']   = r0.font.name
        fmt['size']   = r0.font.size
        fmt['bold']   = r0.font.bold
        fmt['italic'] = r0.font.italic
        fmt['color']  = r0.font.color.rgb if r0.font.color and r0.font.color.rgb else None

    # Remove all existing runs
    for child in list(para._element):
        if child.tag.endswith('}r'):
            para._element.remove(child)

    # Add new run
    run = para.add_run(new_text)
    if fmt.get('name'):   run.font.name  = fmt['name']
    if fmt.get('size'):   run.font.size  = fmt['size']
    if fmt.get('bold') is not None:  run.font.bold   = fmt['bold']
    if fmt.get('italic') is not None: run.font.italic = fmt['italic']
    if fmt.get('color'):  run.font.color.rgb = fmt['color']


# ════════════════════════════════════════════════════════════════
# 5) MAIN
# ════════════════════════════════════════════════════════════════
def main():
    print("=" * 60)
    print("MERGE HUMANIZED TEXT INTO MASTER REPORT  (v2 - fixed)")
    print("=" * 60)

    # ── Parse guide ──
    sections = parse_guide(GUIDE)
    print(f"\nParsed {len(sections)} non-empty sections from REWRITE_GUIDE.md:")
    for k, v in sections.items():
        print(f"  {k:20s} -> {len(v)} paragraphs")

    # ── Load docx ──
    doc = Document(SRC)
    N = len(doc.paragraphs)
    print(f"\nLoaded docx: {N} paragraphs, {len(doc.tables)} tables")

    # ── Build heading index ──
    h_idx, all_hpos = build_heading_index(doc)
    print(f"Found {len(h_idx)} section keys, {len(all_hpos)} total headings (for boundaries)")

    def section_end(start_pos):
        """The paragraph index of the NEXT heading after start_pos."""
        for hp in all_hpos:
            if hp > start_pos:
                return hp
        return N

    # ── Process sections in REVERSE order ──
    # Sort by paragraph index descending so edits never shift later sections
    ordered = []
    for key, paras in sections.items():
        if key in h_idx:
            ordered.append((h_idx[key], key, paras))
    ordered.sort(key=lambda x: x[0], reverse=True)

    total_replaced = 0
    summary = []

    for start_idx, key, new_paras in ordered:
        end_idx = section_end(start_idx)

        # Collect replaceable slots
        slots = []
        for i in range(start_idx + 1, end_idx):
            p = doc.paragraphs[i]
            if not is_protected(p):
                slots.append(i)

        if not slots:
            summary.append(f"  {key:15s} SKIPPED (no replaceable paragraphs)")
            continue

        n_slots = len(slots)
        n_new   = len(new_paras)

        # ── Case A: perfect or fewer new paragraphs ──
        if n_new <= n_slots:
            for j in range(n_new):
                replace_text(doc.paragraphs[slots[j]], new_paras[j])
            # Blank excess slots
            for j in range(n_new, n_slots):
                replace_text(doc.paragraphs[slots[j]], '')
            total_replaced += n_new
            if n_new < n_slots:
                summary.append(f"  {key:15s} replaced {n_new}, blanked {n_slots - n_new}")
            else:
                summary.append(f"  {key:15s} replaced {n_new} (exact match)")

        # ── Case B: more new paragraphs than slots ──
        else:
            # Fill all slots except the last one normally
            for j in range(n_slots - 1):
                replace_text(doc.paragraphs[slots[j]], new_paras[j])
            # Concatenate remaining guide paras into the last slot
            overflow = '\n\n'.join(new_paras[n_slots - 1:])
            replace_text(doc.paragraphs[slots[-1]], overflow)
            total_replaced += n_slots
            summary.append(f"  {key:15s} replaced {n_slots} slots ({n_new - n_slots} merged into last)")

    # ── Report ──
    print(f"\n{'─' * 60}")
    print("REPLACEMENT SUMMARY (processed bottom-to-top):")
    for s in reversed(summary):
        print(s)
    print(f"{'─' * 60}")
    print(f"TOTAL PARAGRAPHS TOUCHED: {total_replaced}")

    # ── Save ──
    doc.save(OUT)
    print(f"\nSaved: {OUT}")

    # ── Verify ──
    doc2 = Document(OUT)
    print(f"\nVerification:")
    print(f"  Paragraphs: {len(doc2.paragraphs)}  (was {N})")
    print(f"  Tables:     {len(doc2.tables)}  (should be {len(doc.tables)})")

    # Count images in both
    def count_images(d):
        n = 0
        for p in d.paragraphs:
            if has_image(p):
                n += 1
        return n

    img_before = count_images(Document(SRC))
    img_after  = count_images(doc2)
    print(f"  Images:     {img_after}  (was {img_before})")

    if len(doc2.tables) != len(doc.tables):
        print("  ⚠️  TABLE COUNT MISMATCH!")
    if img_after != img_before:
        print("  ⚠️  IMAGE COUNT MISMATCH!")
    if len(doc2.tables) == len(doc.tables) and img_after == img_before:
        print("  ✅  All tables and images preserved!")

    print("=" * 60)
    print("DONE!")


if __name__ == '__main__':
    main()
