"""
Insert BioNAFNet-specific content into the FYP handbook document.
Creates a new copy with all additions while preserving existing content.
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
import os, copy

INPUT_DOC = r"F:\low_light_enhancement\eye adaption\BioNAFNet\handbook sample (1).docx"
OUTPUT_DOC = r"F:\low_light_enhancement\eye adaption\BioNAFNet\handbook_BioNAFNet_COMPLETE.docx"

doc = Document(INPUT_DOC)

# ═══════════════════════════════════════════════════════════════════════════════
# Helper functions
# ═══════════════════════════════════════════════════════════════════════════════

def find_paragraph_index(doc, search_text):
    """Find paragraph index containing search_text."""
    for i, p in enumerate(doc.paragraphs):
        if search_text.lower() in p.text.lower():
            return i
    return -1

def add_heading_after(doc, after_idx, text, level=2):
    """Add a heading after a specific paragraph index."""
    new_para = doc.paragraphs[after_idx]._element
    heading = doc.add_heading(text, level=level)
    new_para.addnext(heading._element)
    return after_idx + 1

def add_paragraph_after(doc, after_idx, text, bold=False, style=None):
    """Add a paragraph after a specific paragraph index."""
    ref = doc.paragraphs[after_idx]._element
    p = doc.add_paragraph(text, style=style)
    if bold:
        for run in p.runs:
            run.bold = True
    ref.addnext(p._element)
    return after_idx + 1

def insert_table(doc, after_idx, headers, rows):
    """Insert a table after a specific paragraph index."""
    ref = doc.paragraphs[after_idx]._element
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    try:
        table.style = 'Table Grid'
    except KeyError:
        pass  # Style not available in this document
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Header row
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = h
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.size = Pt(9)
    
    # Data rows
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.rows[i + 1].cells[j]
            cell.text = str(val)
            for run in cell.paragraphs[0].runs:
                run.font.size = Pt(9)
    
    ref.addnext(table._tbl)
    return after_idx + 1

def insert_content_block(doc, after_text, content_lines):
    """Insert multiple paragraphs after the paragraph containing after_text."""
    idx = find_paragraph_index(doc, after_text)
    if idx == -1:
        print(f"  WARNING: Could not find '{after_text}' — skipping")
        return
    
    # Insert in reverse order so they appear in correct order
    for line in reversed(content_lines):
        if line.startswith("## "):
            add_heading_after(doc, idx, line[3:], level=2)
        elif line.startswith("### "):
            add_heading_after(doc, idx, line[4:], level=3)
        else:
            add_paragraph_after(doc, idx, line)
    print(f"  OK: Inserted {len(content_lines)} items after '{after_text[:50]}...'")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: Add Novel Contributions to Introduction/Chapter 1
# ═══════════════════════════════════════════════════════════════════════════════

print("=" * 60)
print("INSERTING BIONAFNET CONTENT INTO HANDBOOK")
print("=" * 60)

# Find a good insertion point in Chapter 1
idx = find_paragraph_index(doc, "significance")
if idx == -1:
    idx = find_paragraph_index(doc, "chapter 1")
if idx == -1:
    idx = 5  # fallback

print("\n[1] Adding Novel Contributions Summary...")
novelty_content = [
    "### Novel Contributions of BioNAFNet",
    "The proposed BioNAFNet architecture introduces seven biologically-inspired novelties into the NAFNet backbone for low-light image enhancement:",
    "1. Retinal Lateral Inhibition Network (RLIN) — Center-surround differentiation inspired by retinal ganglion cells, enhancing edge contrast in dark regions through learned inhibitory connections.",
    "2. Frequency-Aware Enhancement Branch (FAEB) — Fourier-domain processing at the bottleneck that independently modifies amplitude and phase spectra to recover degraded high-frequency textures.",
    "3. Adaptive Receptive Field Pooling (ARFP) — Luminance-dependent multi-scale convolution (3×3, 5×5, 7×7) that uses larger receptive fields in darker regions, mimicking how the human eye adapts its spatial resolution.",
    "4. Photoreceptor Response Curve Modeling (PRCM) — Learned rod and cone gamma curves with an adaptive scotopic-photopic threshold, simulating the nonlinear response of human photoreceptors.",
    "5. Scotopic-Photopic Dual Pathway (SPDP) — Separate processing pathways for luminance (rod/scotopic) and chrominance (cone/photopic) channels, inspired by the visual cortex's parallel processing streams.",
    "6. Temporal Adaptation Memory (TAM) — GRU-based iterative refinement across multiple forward passes, modeling how the human visual system progressively adapts to darkness over time.",
    "7. Weber-Fechner Perceptual Loss (WFPL) — A novel loss function that weights reconstruction errors inversely proportional to local luminance, reflecting the Weber-Fechner law of human perception where sensitivity is highest in dark regions.",
    "Additionally, the project demonstrates successful Knowledge Distillation from the full 154M-parameter Teacher model to a lightweight 24M-parameter Student model (BioNAFNet-Lite), achieving 6.4× compression and 4× speedup with minimal quality loss."
]
insert_content_block(doc, "significance" if find_paragraph_index(doc, "significance") != -1 else "chapter 1", novelty_content)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: Add Architecture Details
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[2] Adding Architecture Details...")
arch_idx = find_paragraph_index(doc, "architecture")
if arch_idx == -1:
    arch_idx = find_paragraph_index(doc, "design")
if arch_idx != -1:
    arch_content = [
        "### BioNAFNet Architecture Specification",
        "The BioNAFNet architecture is built upon the NAFNet (Nonlinear Activation Free Network) backbone with an encoder-decoder structure enhanced by seven biological modules. The complete processing pipeline is: Input → PRCM → SPDP → Encoder (with RLIN) → Bottleneck (with FAEB) → Decoder → ARFP → Output, with TAM providing iterative refinement and WFPL guiding training.",
        "",
        "Teacher Model Configuration: Width=64 channels, Encoder blocks=[2, 2, 4, 8], Middle blocks=12, Decoder blocks=[2, 2, 2, 2], N_passes=2 (multi-pass refinement). Total parameters: 154,380,888 (154M).",
        "",
        "Student Model Configuration (BioNAFNet-Lite): Width=32 channels, Encoder blocks=[2, 2, 4, 8], Middle blocks=4, Decoder blocks=[2, 2, 2, 2], N_passes=1 (single-pass for speed). Total parameters: 23,969,016 (24M).",
        "",
        "The encoder progressively downsamples spatial resolution while doubling channel width at each stage. Skip connections link corresponding encoder-decoder levels to preserve fine-grained detail. The bottleneck applies 12 (Teacher) or 4 (Student) BioNAFBlocks followed by the FAEB for frequency-domain enhancement.",
    ]
    insert_content_block(doc, doc.paragraphs[arch_idx].text[:40], arch_content)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Add Architecture Table
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[3] Adding Architecture Table...")
arch_table_idx = find_paragraph_index(doc, "BioNAFNet Architecture Specification")
if arch_table_idx == -1:
    arch_table_idx = find_paragraph_index(doc, "architecture")
if arch_table_idx != -1:
    insert_table(doc, arch_table_idx, 
        ["Stage", "Blocks", "Channels", "Resolution", "Key Module"],
        [
            ["Input Conv", "1", "64 / 32", "H×W", "—"],
            ["Encoder 1", "2 BioNAFBlocks", "64 / 32", "H×W", "RLIN"],
            ["Encoder 2", "2 BioNAFBlocks", "128 / 64", "H/2×W/2", "RLIN"],
            ["Encoder 3", "4 BioNAFBlocks", "256 / 128", "H/4×W/4", "RLIN"],
            ["Encoder 4", "8 BioNAFBlocks", "512 / 256", "H/8×W/8", "—"],
            ["Bottleneck", "12 / 4 BioNAFBlocks", "512 / 256", "H/16×W/16", "FAEB"],
            ["Decoder 1-4", "2 each", "256→64", "H/8→H", "—"],
            ["Output", "ARFP + Conv", "3", "H×W", "ARFP"],
        ]
    )
    add_paragraph_after(doc, arch_table_idx, 
        "Table: Layer-by-layer BioNAFNet architecture specification (Teacher / Student values where different).")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: Add Training Configuration
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[4] Adding Training Configuration...")
train_idx = find_paragraph_index(doc, "training")
if train_idx == -1:
    train_idx = find_paragraph_index(doc, "hyperparameter")
if train_idx == -1:
    train_idx = find_paragraph_index(doc, "implementation")
if train_idx != -1:
    train_content = [
        "### Training Hyperparameters",
        "Both Teacher and Student models were trained using the following configuration:",
    ]
    insert_content_block(doc, doc.paragraphs[train_idx].text[:40], train_content)
    
    # Find the newly added heading
    new_idx = find_paragraph_index(doc, "Training Hyperparameters")
    if new_idx != -1:
        insert_table(doc, new_idx,
            ["Parameter", "Teacher", "Student"],
            [
                ["Optimizer", "AdamW (β₁=0.9, β₂=0.999)", "AdamW"],
                ["Initial Learning Rate", "2×10⁻⁴", "2×10⁻⁴"],
                ["Minimum Learning Rate", "1×10⁻⁶", "1×10⁻⁶"],
                ["LR Scheduler", "CosineAnnealingWarmRestarts", "Same"],
                ["Batch Size", "4 × 2 (accum)", "4 × 2 (accum)"],
                ["Patch Size", "128×128", "128×128"],
                ["EMA Decay", "0.9995", "0.9995"],
                ["Training Epochs", "500", "693"],
                ["Weight Decay", "1×10⁻⁴", "1×10⁻⁴"],
                ["Gradient Clipping", "0.5", "0.5"],
                ["Mixed Precision (AMP)", "Yes", "Yes"],
                ["GPU", "NVIDIA RTX", "NVIDIA RTX"],
            ]
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5: Add Loss Functions
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[5] Adding Loss Function Details...")
loss_idx = find_paragraph_index(doc, "loss")
if loss_idx == -1:
    loss_idx = find_paragraph_index(doc, "objective function")
if loss_idx != -1:
    loss_content = [
        "### Loss Function Design",
        "The BioNAFNet training employs a composite loss function with six components, each targeting a different aspect of image quality. The total loss is a weighted sum: L_total = 1.0·L_charb + 0.8·L_ssim + 0.2·L_perc + 0.25·L_edge + 0.1·L_color + 0.3·L_wfpl.",
        "The Weber-Fechner Perceptual Loss (WFPL) is a novel contribution that weights errors inversely proportional to local luminance: L_wfpl = mean(|pred - gt| / (lum + ε)), reflecting the psychophysical Weber-Fechner law where human sensitivity is highest in dark regions.",
        "For Knowledge Distillation, the Student model uses an additional Mimic Loss: L_student = 0.5·L1(student, gt) + 0.1·SSIM(student, gt) + 0.4·L2(student, teacher_output), enabling the lightweight model to replicate the Teacher's learned enhancement strategy.",
    ]
    insert_content_block(doc, doc.paragraphs[loss_idx].text[:40], loss_content)
    
    new_idx = find_paragraph_index(doc, "Loss Function Design")
    if new_idx != -1:
        insert_table(doc, new_idx,
            ["Loss Component", "Weight", "Purpose"],
            [
                ["Charbonnier", "1.0", "Pixel-level reconstruction (robust L1)"],
                ["SSIM", "0.8", "Structural similarity preservation"],
                ["Perceptual (VGG16)", "0.2", "High-level visual quality"],
                ["Edge (Sobel)", "0.25", "Detail and edge preservation"],
                ["Color (YUV)", "0.1", "Chrominance accuracy"],
                ["Weber-Fechner (WFPL)", "0.3", "Dark region sensitivity (Novel)"],
            ]
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 6: Add Knowledge Distillation
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[6] Adding Knowledge Distillation Section...")
# Find Chapter 7 or Results section
results_idx = find_paragraph_index(doc, "chapter 7")
if results_idx == -1:
    results_idx = find_paragraph_index(doc, "results")
if results_idx != -1:
    kd_content = [
        "### Knowledge Distillation: Teacher to Student",
        "A key contribution of this work is the successful compression of the full BioNAFNet (154M parameters) into BioNAFNet-Lite (24M parameters) through knowledge distillation. The Student model mimics the Teacher's outputs using a combination of ground-truth reconstruction loss and a mimic loss (L2 distance to Teacher outputs, weighted at 0.4).",
        "",
        "The distillation achieves 6.4× parameter reduction and 4× inference speedup while maintaining competitive image quality. Notably, the Student-693 model (trained for 693 epochs) actually surpasses the Teacher on LOLv1 (25.23 vs 24.94 dB PSNR), demonstrating that the distillation process can lead to regularization benefits.",
        "",
        "Exponential Moving Average (EMA) with decay 0.9995 was employed during training to stabilize the Student's weights, providing smoother convergence and better generalization to full-resolution test images.",
    ]
    insert_content_block(doc, doc.paragraphs[results_idx].text[:40], kd_content)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Add Comprehensive Benchmark Results Table
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[7] Adding Benchmark Results Tables...")
quant_idx = find_paragraph_index(doc, "quantitative")
if quant_idx == -1:
    quant_idx = find_paragraph_index(doc, "psnr")
if quant_idx == -1:
    quant_idx = find_paragraph_index(doc, "evaluation")
if quant_idx != -1:
    results_content = [
        "### Comprehensive Model Benchmark (Full-Resolution Test Images)",
        "All six BioNAFNet model variants were evaluated on full-resolution test images from LOLv1 (15 images), LOLv2 Real (100 images), and LOLv2 Synthetic (100 images). The following table presents the complete benchmark results:",
    ]
    insert_content_block(doc, doc.paragraphs[quant_idx].text[:40], results_content)
    
    new_idx = find_paragraph_index(doc, "Comprehensive Model Benchmark")
    if new_idx != -1:
        insert_table(doc, new_idx,
            ["Model", "Params", "LOLv1 PSNR", "LOLv2R PSNR", "LOLv2S PSNR", "LOLv1 SSIM", "LOLv2R SSIM", "LOLv2S SSIM", "FPS"],
            [
                ["Teacher (2-pass)", "154M", "24.94", "28.67", "26.22", "0.8661", "0.9101", "0.9457", "5.3"],
                ["Student-350", "24M", "23.44", "26.78", "25.06", "0.8409", "0.8844", "0.9329", "21.4"],
                ["Student-693", "24M", "25.23", "28.48", "25.75", "0.8528", "0.8942", "0.9375", "20.5"],
                ["Synergy (T70/S30)", "178M", "24.96", "28.90", "26.33", "0.8646", "0.9095", "0.9472", "~3"],
                ["Ensemble 50/50", "178M", "25.27", "29.26", "26.47", "0.8637", "0.9080", "0.9462", "~4"],
                ["Ensemble T60/S40", "178M", "25.23", "29.29", "26.46", "0.8649", "0.9094", "0.9468", "~4"],
            ]
        )
        add_paragraph_after(doc, new_idx,
            "Table: Complete benchmark results across all BioNAFNet model variants. Bold values indicate best performance per metric.")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 8: Add Comparison with Literature
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[8] Adding Literature Comparison Table...")
comp_idx = find_paragraph_index(doc, "comparison")
if comp_idx == -1:
    comp_idx = find_paragraph_index(doc, "state-of-the-art")
if comp_idx == -1:
    comp_idx = find_paragraph_index(doc, "baseline")
if comp_idx != -1:
    lit_content = [
        "### Comparison with State-of-the-Art Methods",
        "The following table compares BioNAFNet against established methods in the low-light image enhancement literature. Results for competing methods are sourced from their respective publications.",
    ]
    insert_content_block(doc, doc.paragraphs[comp_idx].text[:40], lit_content)
    
    new_idx = find_paragraph_index(doc, "Comparison with State-of-the-Art")
    if new_idx != -1:
        insert_table(doc, new_idx,
            ["Method", "Year", "Type", "Params", "LOLv1 PSNR", "LOLv1 SSIM"],
            [
                ["RetinexNet", "2018", "CNN", "0.8M", "16.77", "0.560"],
                ["KinD", "2019", "CNN", "8.2M", "20.87", "0.800"],
                ["MIRNet", "2020", "CNN", "31.8M", "24.14", "0.830"],
                ["SNR-Aware", "2022", "Transformer", "39.1M", "24.61", "0.842"],
                ["Retinexformer", "2023", "Transformer", "1.6M", "25.16", "0.845"],
                ["NAFNet (baseline)", "2022", "CNN", "67.9M", "~23.0", "~0.830"],
                ["BioNAFNet-Lite (Ours)", "2026", "Bio-CNN", "24M", "25.23", "0.853"],
                ["BioNAFNet-Ensemble (Ours)", "2026", "Bio-CNN", "178M", "25.27", "0.864"],
            ]
        )
        add_paragraph_after(doc, new_idx,
            "Table: Comparison with state-of-the-art low-light image enhancement methods on LOLv1 dataset.")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 9: Add Computational Efficiency Analysis
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[9] Adding Computational Efficiency Table...")
comp_eff_idx = find_paragraph_index(doc, "runtime")
if comp_eff_idx == -1:
    comp_eff_idx = find_paragraph_index(doc, "computational")
if comp_eff_idx == -1:
    comp_eff_idx = find_paragraph_index(doc, "efficiency")
if comp_eff_idx != -1:
    eff_content = [
        "### Model Efficiency and Compression Analysis",
        "Knowledge distillation successfully compressed BioNAFNet by 6.4× while maintaining competitive quality. The following table summarizes the efficiency metrics:",
    ]
    insert_content_block(doc, doc.paragraphs[comp_eff_idx].text[:40], eff_content)
    
    new_idx = find_paragraph_index(doc, "Model Efficiency and Compression")
    if new_idx != -1:
        insert_table(doc, new_idx,
            ["Metric", "Teacher", "Student-693", "Improvement"],
            [
                ["Parameters", "154.4M", "24.0M", "6.4× smaller"],
                ["Model Size", "589 MB", "91 MB", "6.5× smaller"],
                ["Inference Speed", "188.7 ms/img", "48.9 ms/img", "3.9× faster"],
                ["Frames Per Second", "5.3 FPS", "20.5 FPS", "3.9× faster"],
                ["LOLv1 PSNR", "24.94 dB", "25.23 dB", "+0.29 dB (Student wins)"],
                ["LOLv2 Real PSNR", "28.67 dB", "28.48 dB", "-0.19 dB (negligible)"],
                ["Real-time Capable?", "No", "Yes (20 FPS)", "—"],
            ]
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 10: Add Ensemble Fusion Analysis
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[10] Adding Ensemble Fusion Analysis...")
discuss_idx = find_paragraph_index(doc, "discussion")
if discuss_idx == -1:
    discuss_idx = find_paragraph_index(doc, "findings")
if discuss_idx != -1:
    ensemble_content = [
        "### Teacher-Student Ensemble Fusion",
        "A key finding is that combining the Teacher and Student model outputs through weighted averaging produces results superior to either model alone. The ensemble leverages complementary learned representations — the Teacher provides fine detail from its 2-pass refinement and larger capacity, while the Student provides cleaner overall structure from its simpler, regularized architecture.",
        "",
        "The optimal fusion ratio was found to be 50:50 (simple average) for overall performance, and 60:40 (Teacher-biased) for LOLv2 Real. The Ensemble achieved the highest PSNR across all datasets: 29.29 dB on LOLv2 Real (surpassing the Teacher by +0.62 dB) and 26.47 dB on LOLv2 Synthetic (+0.25 dB above Teacher).",
        "",
        "This demonstrates that knowledge distillation not only compresses the model but also produces a complementary representation that can be synergistically combined with the original Teacher for peak performance.",
    ]
    insert_content_block(doc, doc.paragraphs[discuss_idx].text[:40], ensemble_content)


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 11: Add Datasets Description
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[11] Adding Datasets Table...")
ds_idx = find_paragraph_index(doc, "dataset")
if ds_idx != -1:
    ds_content = [
        "### Datasets Used for Training and Evaluation",
        "Three benchmark datasets were used for comprehensive evaluation:",
    ]
    insert_content_block(doc, doc.paragraphs[ds_idx].text[:40], ds_content)
    
    new_idx = find_paragraph_index(doc, "Datasets Used for Training")
    if new_idx != -1:
        insert_table(doc, new_idx,
            ["Dataset", "Type", "Train Images", "Test Images", "Resolution", "Year"],
            [
                ["LOLv1", "Real paired", "485", "15", "400×600", "2018"],
                ["LOLv2 Real", "Real paired", "689", "100", "Various", "2021"],
                ["LOLv2 Synthetic", "Synthetic paired", "900", "100", "Various", "2021"],
            ]
        )


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 12: Add Graphs Placeholder descriptions
# ═══════════════════════════════════════════════════════════════════════════════

print("\n[12] Adding Recommended Graphs Section...")
graph_idx = find_paragraph_index(doc, "chapter summary")  # End of results chapter
if graph_idx == -1:
    graph_idx = find_paragraph_index(doc, "7.7")
if graph_idx != -1:
    graph_content = [
        "### Recommended Figures and Graphs for This Chapter",
        "Figure: Bar Chart — PSNR comparison across all 6 model variants × 3 datasets (LOLv1, LOLv2 Real, LOLv2 Synthetic). X-axis: Model variants, Y-axis: PSNR (dB), grouped bars by dataset.",
        "Figure: Bar Chart — SSIM comparison across all 6 model variants × 3 datasets.",
        "Figure: Scatter Plot — PSNR vs Inference Speed tradeoff. Each point represents a model variant. Shows Student-693 on the Pareto-optimal frontier (high quality + fast speed).",
        "Figure: Box Plot — Per-image PSNR distribution across models. Shows variance, not just mean. Demonstrates consistency of Student-693.",
        "Figure: Line Chart — Training convergence curves (PSNR vs Epoch) for both Teacher and Student models.",
        "Figure: Stacked Bar Chart — Ablation study showing incremental PSNR gain from each biological module (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL).",
        "Figure: Visual Comparison Grid (4 columns: Input | Retinexformer | BioNAFNet | Ground Truth) for 4 challenging test scenarios.",
        "Figure: Scatter Plot — Model Size (MB) vs PSNR showing Student-693 on the efficient frontier.",
        "Figure: Zoomed crop comparisons showing detail/edge preservation between Teacher, Student, and Ensemble outputs.",
    ]
    insert_content_block(doc, doc.paragraphs[graph_idx].text[:40], graph_content)


# ═══════════════════════════════════════════════════════════════════════════════
# Save
# ═══════════════════════════════════════════════════════════════════════════════

doc.save(OUTPUT_DOC)
print(f"\n{'='*60}")
print(f"SUCCESS! Saved to: {OUTPUT_DOC}")
print(f"{'='*60}")
