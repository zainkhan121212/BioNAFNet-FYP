"""
BioNAFNet FYP Final Report — Part 2: Chapters 4-5 (Methodology + System Architecture)
"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

FIGS = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
DOC = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_FYP_Final_Report.docx"
doc = Document(DOC)
FN=[0]; TN=[7]  # continue from Part 1

def h1(t): doc.add_heading(t,1).alignment=WD_ALIGN_PARAGRAPH.LEFT
def h2(t): doc.add_heading(t,2)
def h3(t): doc.add_heading(t,3)
def para(t): p=doc.add_paragraph(t); p.paragraph_format.first_line_indent=Cm(1.27); return p
def pn(t): return doc.add_paragraph(t)
def bl(t): doc.add_paragraph(t, style='List Bullet')
def nl(t): doc.add_paragraph(t, style='List Number')
def fig(fn,cap,w=5.5):
    FN[0]+=1; path=os.path.join(FIGS,fn)
    if os.path.exists(path):
        doc.add_picture(path,width=Inches(w)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    c=doc.add_paragraph(f'Figure {FN[0]}: {cap}'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
    c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
def tbl(headers,rows,cap=None):
    TN[0]+=1
    if cap: c=doc.add_paragraph(f'Table {TN[0]}: {cap}'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER; c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
    t=doc.add_table(rows=1+len(rows),cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    try: t.style='Table Grid'
    except: pass
    for j,h in enumerate(headers):
        cell=t.rows[0].cells[j]; cell.text=h
        for r in cell.paragraphs[0].runs: r.bold=True; r.font.size=Pt(10)
    for i,row in enumerate(rows):
        for j,val in enumerate(row): cell=t.rows[i+1].cells[j]; cell.text=str(val)
    doc.add_paragraph('')
def photo_note(desc):
    p=doc.add_paragraph(); r=p.add_run(f'[INSERT IMAGE HERE: {desc}]')
    r.bold=True; r.font.color.rgb=RGBColor(0xCC,0x00,0x00); r.font.size=Pt(11)
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 4: METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════
h1('Chapter 4')
h2('Methodology')

h3('4.1 Research Approach')
para('Our research follows an experimental quantitative approach. We design a novel architecture, implement it in PyTorch, train it on benchmark datasets, and evaluate performance using objective metrics. The methodology consists of four main phases:')
nl('Phase 1 — Architecture Design: Integrate seven biological modules into the NAFNet backbone.')
nl('Phase 2 — Teacher Training: Train the full BioNAFNet model (154M parameters) on combined LOLv1+LOLv2 datasets.')
nl('Phase 3 — Knowledge Distillation: Train a lightweight Student model (24M parameters) to mimic the Teacher.')
nl('Phase 4 — Evaluation: Benchmark all model variants including ensemble fusion experiments.')

h3('4.2 NAFNet Backbone')
para('NAFNet (Nonlinear Activation Free Network) by Chen et al. (2022) serves as our backbone. Its key innovation is replacing traditional activation functions (ReLU, GELU) with a SimpleGate mechanism that splits feature channels into two halves and multiplies them element-wise. This avoids information loss from clipping negative values while maintaining non-linearity.')
para('The NAFNet block consists of: LayerNorm → 1x1 Conv (channel expansion) → 3x3 Depthwise Conv → SimpleGate → Simplified Channel Attention (SCA) → 1x1 Conv (channel reduction). This block is repeated multiple times in each encoder/decoder stage. We call our modified version the BioNAFBlock because we add RLIN (lateral inhibition) after the channel attention.')

h3('4.3 Biological Module 1: RLIN (Retinal Lateral Inhibition Network)')
para('Biological Inspiration: In the human retina, ganglion cells have center-surround receptive fields. The center responds excitatorily to light while the surrounding region responds inhibitorily. This creates edge enhancement and helps detect boundaries even when overall contrast is very low. This is how we can see edges of objects in dim moonlight.')
para('Our Implementation: RLIN computes center and surround responses using separate convolutions. The center pathway uses a 1x1 convolution capturing the direct response at each position. The surround pathway uses 5x5 average pooling followed by a 1x1 convolution, capturing the average response of the surrounding area. The difference is scaled by a learnable parameter alpha (initialized to 0.3):')
pn('Output = x + alpha * (Center(x) - Surround(x))')
para('RLIN is integrated into every BioNAFBlock in the first three encoder stages (2+2+4 = 8 blocks). This provides edge enhancement at multiple spatial scales throughout the encoding process.')
photo_note('Diagram of RLIN module: (a) Center-surround receptive field of retinal ganglion cell. (b) Block diagram showing Center pathway (1x1 conv), Surround pathway (5x5 AvgPool + 1x1 conv), subtraction, and scaling. Draw in PowerPoint.')

h3('4.4 Biological Module 2: FAEB (Frequency-Aware Enhancement Branch)')
para('Biological Inspiration: The human visual cortex contains neurons tuned to specific spatial frequencies. Some neurons respond to fine details (high frequency) while others respond to overall brightness patterns (low frequency). In low-light images, high-frequency components are disproportionately degraded by noise, while low-frequency components are compressed by reduced dynamic range.')
para('Our Implementation: FAEB operates at the bottleneck (deepest) level of the network. It converts features to the frequency domain using 2D Fast Fourier Transform (FFT), then processes the amplitude and phase spectra through separate convolutional networks:')
pn('FFT(x) → Amplitude spectrum, Phase spectrum')
pn('Amp_enhanced = Conv_amp(Amplitude)')
pn('Phase_enhanced = Conv_phase(Phase)')
pn('Freq_output = iFFT(Amp_enhanced, Phase_enhanced)')
pn('Output = x + blend * Freq_output  (blend initialized to 0.15)')
para('The amplitude spectrum controls how much of each frequency is present, while the phase spectrum controls where features are located spatially. By processing them separately, FAEB can independently boost degraded high-frequency textures and correct the overall brightness distribution. All FFT operations are done in float32 precision to avoid numerical issues with half-precision training.')
photo_note('Diagram of FAEB module: Input features → FFT → Amplitude/Phase split → Separate ConvNets → Combine → iFFT → Blend with input. Draw in PowerPoint.')

h3('4.5 Biological Module 3: ARFP (Adaptive Receptive Field Pooling)')
para('Biological Inspiration: The human eye adapts its effective spatial resolution based on ambient light. In bright conditions (photopic vision), cone cells provide high-resolution vision through small, densely packed receptive fields. In dark conditions (scotopic vision), rod cells pool signals over larger areas, sacrificing spatial resolution for better sensitivity. This is why you cannot read fine print in dim light but can still see large objects.')
para('Our Implementation: ARFP uses three parallel depthwise convolution branches with kernel sizes 3x3, 5x5, and 7x7 representing small, medium, and large receptive fields. A gating network takes the luminance map as input and produces three softmax-normalized weights:')
pn('weights = Softmax(GateNet(luminance_map))')
pn('Output = w1*Conv3x3(x) + w2*Conv5x5(x) + w3*Conv7x7(x)')
para('In dark regions (low luminance), the gating network learns to assign higher weights to the 5x5 and 7x7 branches, pooling information from wider areas just like rod cells. In bright regions (high luminance), the 3x3 branch dominates for sharp detail retention. ARFP is placed at the decoder output, right before the final reconstruction convolution.')

h3('4.6 Biological Module 4: PRCM (Photoreceptor Response Curve Modeling)')
para('Biological Inspiration: Human photoreceptors have nonlinear response curves. Rod cells, which dominate in low light (scotopic vision), have a response characterized by a gamma value around 0.45, providing high sensitivity to small changes in dark regions. Cone cells, active in bright light (photopic vision), have a gamma around 0.95, providing more linear response. The transition between rod and cone dominance happens at a specific luminance threshold.')
para('Our Implementation: PRCM applies learned gamma transformations:')
pn('Rod response: x_rod = x ^ gamma_rod  (gamma_rod init: 0.45)')
pn('Cone response: x_cone = x ^ gamma_cone  (gamma_cone init: 0.95)')
pn('Blend weight w = sigmoid((luminance - threshold) * 12)')
pn('Output = x_rod * (1 - w) + x_cone * w')
para('All three parameters (gamma_rod, gamma_cone, threshold) are learnable, allowing the network to discover optimal response curves during training. PRCM is the first module applied to the input, providing biologically-plausible preprocessing before the NAFNet backbone.')

h3('4.7 Biological Module 5: SPDP (Scotopic-Photopic Dual Pathway)')
para('Biological Inspiration: The visual cortex processes luminance and color through separate parallel pathways. The magnocellular (M) pathway handles luminance, motion, and coarse spatial information. The parvocellular (P) pathway handles color and fine detail. This parallel processing allows the brain to efficiently optimize different visual attributes independently.')
para('Our Implementation: SPDP converts the RGB input to YUV color space. The scotopic pathway processes Y (luminance) through a dedicated ConvNet simulating rod-based processing. The photopic pathway processes U and V (chrominance) through a separate ConvNet simulating cone-based processing:')
pn('Y, U, V = RGB_to_YUV(x)')
pn('Lum_features = ScotopicNet(Y)')
pn('Color_features = PhotopicNet(concat(U, V))')
pn('Residual = FuseNet(concat(Lum, Color)) * 0.2')
pn('Output = x + Residual')
para('The 0.2 scaling ensures subtle but effective dual-pathway refinement. SPDP is applied after PRCM, providing the second stage of biological preprocessing.')

h3('4.8 Biological Module 6: TAM (Temporal Adaptation Memory)')
para('Biological Inspiration: When you walk from a bright room into a dark one, your eyes do not adapt instantly. Dark adaptation takes several minutes as the photoreceptor chemicals slowly regenerate. During this time, your vision progressively improves. Similarly, light adaptation (dark to bright) takes only seconds. No existing LLIE method models this temporal aspect of visual adaptation.')
para('Our Implementation: TAM uses a GRU (Gated Recurrent Unit) cell to maintain a memory state across multiple forward passes of the network. In the Teacher model (n_passes=2), the image is processed twice:')
pn('Pass 1: output_1 = NAFNet(input)')
pn('Pass 2: output_2 = NAFNet(output_1)')
pn('GRU state: hidden = GRU(proj_in(output_2), hidden)')
pn('Final = output_2 + proj_out(hidden) * 0.15')
para('Each pass refines the previous output, mimicking the progressive nature of dark adaptation. The GRU accumulates information from both passes to provide additional refinement. In the Student model (n_passes=1), TAM is effectively bypassed for speed.')

h3('4.9 Biological Module 7: WFPL (Weber-Fechner Perceptual Loss)')
para('Biological Inspiration: The Weber-Fechner law is a fundamental principle of psychophysics discovered in the 1800s. It states that the perceived change in a stimulus is proportional to the logarithm of the stimulus intensity. In practical terms: humans are much more sensitive to brightness changes in dark regions than in bright regions. A 5-unit change from 0 to 5 is very noticeable, while the same 5-unit change from 200 to 205 is barely perceptible.')
para('Our Implementation: WFPL creates a weight map that assigns higher penalty to errors in dark regions:')
pn('weight_map = 1 / (luminance(target) + epsilon)')
pn('weight_map = weight_map / mean(weight_map)  — normalization')
pn('L_wfpl = mean(|predicted - target| * weight_map)')
para('The epsilon value (0.02) prevents division by zero. Normalization ensures the loss magnitude is comparable to other components. WFPL forces the network to prioritize accuracy in dark regions, which is exactly where enhancement quality matters most to human observers.')

h3('4.10 Loss Function Design')
tbl(['Component', 'Weight', 'Formula', 'Purpose'],
    [['Charbonnier', '1.0', 'sqrt((pred-gt)^2 + 0.001^2)', 'Robust pixel reconstruction'],
     ['SSIM', '0.8', '1 - SSIM(pred, gt)', 'Structural preservation'],
     ['Perceptual', '0.2', 'L1(VGG16(pred), VGG16(gt))', 'Feature-level quality'],
     ['Edge', '0.25', 'L1(Sobel(pred), Sobel(gt))', 'Edge and detail sharpness'],
     ['Color', '0.1', 'L1(UV(pred), UV(gt))', 'Chrominance accuracy'],
     ['Weber-Fechner', '0.3', 'mean(|pred-gt| / (lum+eps))', 'Dark region emphasis']],
    'Composite Loss Function — Teacher Training')
pn('L_total = 1.0*L_charb + 0.8*L_ssim + 0.2*L_perc + 0.25*L_edge + 0.1*L_color + 0.3*L_wfpl')

tbl(['Component', 'Weight', 'Formula', 'Purpose'],
    [['L1 (ground truth)', '0.5', 'L1(student, gt)', 'Pixel accuracy'],
     ['SSIM (ground truth)', '0.1', 'SSIM(student, gt)', 'Structure preservation'],
     ['Mimic (teacher)', '0.4', 'L2(student, teacher_out)', 'Knowledge transfer']],
    'Distillation Loss Function — Student Training')

h3('4.11 Training Strategy')
tbl(['Parameter', 'Teacher Model', 'Student Model'],
    [['Architecture', 'width=64, mid=12, 2-pass', 'width=32, mid=4, 1-pass'],
     ['Parameters', '154,380,888 (154M)', '23,969,016 (24M)'],
     ['Optimizer', 'AdamW (beta1=0.9, beta2=0.999)', 'AdamW'],
     ['Initial Learning Rate', '2e-4', '2e-4'],
     ['Minimum Learning Rate', '1e-6', '1e-6'],
     ['LR Scheduler', 'CosineAnnealingWarmRestarts', 'Same'],
     ['T_0 / T_mult', '50 / 2', '50 / 2'],
     ['Weight Decay', '1e-4', '1e-4'],
     ['Batch Size', '4 (eff. 8 with accum)', '4 (eff. 8)'],
     ['Gradient Accumulation', '2 steps', '2 steps'],
     ['Gradient Clipping', '0.5 (max_norm)', '0.5'],
     ['Patch Size', '128x128', '128x128'],
     ['EMA Decay', '0.9995', '0.9995'],
     ['Mixed Precision (AMP)', 'Yes', 'Yes'],
     ['Training Epochs', '504', '693'],
     ['Best Validation PSNR', '25.05 dB (epoch 476)', '25.09 dB (epoch 693)'],
     ['Training Time', '~34 hours', '~40 hours'],
     ['Training Data', '2074 pairs combined', 'Same + Teacher outputs'],
     ['Augmentation', 'H-flip, V-flip, 90-rot, MixUp(0.2)', 'Same']],
    'Complete Training Configuration')

h3('4.12 Knowledge Distillation Pipeline')
para('Knowledge distillation compresses the 154M Teacher into a 24M Student. The Student has the same architecture family but with reduced width (32 vs 64 channels), fewer middle blocks (4 vs 12), and single-pass inference (n_passes=1). During distillation training, the Teacher is frozen and generates outputs for each training batch. The Student learns from both ground truth images (L1+SSIM) and Teacher outputs (L2 mimic loss with weight 0.4).')
para('The distillation achieves remarkable compression: 6.4x fewer parameters, 6.5x smaller model file (91 MB vs 589 MB), and 3.9x faster inference (48.9 ms vs 188.7 ms per image). Surprisingly the Student-693 achieves higher PSNR than the Teacher on LOLv1 (25.23 vs 24.94 dB), suggesting that the reduced capacity provides beneficial regularization.')

fig('fig_distillation.png', 'Knowledge Distillation Compression: Teacher (154M) vs Student (24M)', 6)

h3('4.13 Ensemble Fusion Strategy')
para('We explore combining Teacher and Student outputs through weighted averaging to leverage complementary learned representations. Three fusion strategies are tested:')
tbl(['Strategy', 'Teacher Weight', 'Student Weight', 'Rationale'],
    [['Ensemble 50/50', '50%', '50%', 'Equal contribution, balanced quality'],
     ['Ensemble T60/S40', '60%', '40%', 'Teacher-biased for detail richness'],
     ['Ensemble T40/S60', '40%', '60%', 'Student-biased for cleaner structure'],
     ['Synergy T70/S30', '70%', '30%', 'Heavy teacher reliance']],
    'Ensemble Fusion Strategies')
para('The ensemble output is computed as: enhanced = alpha * teacher_out + (1-alpha) * student_out, then clamped to [0,1]. This requires running both models during inference, so it is 3-4x slower than individual models, making it suitable for offline processing only.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 5: SYSTEM ARCHITECTURE / INITIAL DESIGN
# ═══════════════════════════════════════════════════════════════════════════
h1('Chapter 5')
h2('System Architecture / Initial Design')

h3('5.1 System Architecture')
pn('5.1.1 Architecture Design Approach')
para('We follow a modular architecture where each biological component is implemented as an independent PyTorch nn.Module. This allows easy addition, removal, or modification of any module without affecting the rest of the system. The overall system follows a pipeline pattern: Input → Preprocessing → Enhancement Core → Postprocessing → Output.')

pn('5.1.2 Architecture Design')
para('The BioNAFNet system has four main layers:')
nl('Input Layer: Image loading (PIL), format conversion (to tensor), normalization to [0,1] range, and padding to multiples of 16.')
nl('Preprocessing Layer: PRCM (photoreceptor curves) → SPDP (dual pathway) applied to normalized input.')
nl('Enhancement Core: NAFNet encoder-decoder with RLIN in encoder blocks and FAEB at bottleneck. For Teacher: 2-pass with TAM.')
nl('Output Layer: ARFP (adaptive receptive field) → global residual connection → crop padding → clamp [0,1] → save.')

photo_note('System architecture block diagram showing: Input → PRCM → SPDP → NAFNet Encoder (4 stages with RLIN) → Bottleneck + FAEB → NAFNet Decoder (4 stages) → ARFP → Output, with TAM feedback loop and skip connections. Draw in PowerPoint or draw.io.')

tbl(['Stage', 'Teacher Config', 'Student Config', 'Resolution', 'Key Module'],
    [['Input Conv', '3→64', '3→32', 'H×W', '—'],
     ['Encoder 1', '2 BioNAFBlocks', '2 BioNAFBlocks', 'H×W', 'RLIN'],
     ['Encoder 2', '2 BioNAFBlocks', '2 BioNAFBlocks', 'H/2×W/2', 'RLIN'],
     ['Encoder 3', '4 BioNAFBlocks', '4 BioNAFBlocks', 'H/4×W/4', 'RLIN'],
     ['Encoder 4', '8 BioNAFBlocks', '8 BioNAFBlocks', 'H/8×W/8', '—'],
     ['Bottleneck', '12 BioNAFBlocks', '4 BioNAFBlocks', 'H/16×W/16', 'FAEB'],
     ['Decoder 1-4', '2 blocks each', '2 blocks each', 'H/8→H', '—'],
     ['Output', 'ARFP+Conv 64→3', 'ARFP+Conv 32→3', 'H×W', 'ARFP']],
    'BioNAFNet Layer-by-Layer Architecture')

pn('5.1.3 Subsystem Architecture')
para('The system consists of the following subsystems:')
bl('Training Subsystem: Handles data loading, augmentation, forward/backward pass, loss computation, EMA update, validation, and checkpoint saving.')
bl('Distillation Subsystem: Extends training with frozen Teacher inference and mimic loss computation.')
bl('Inference Subsystem: Loads trained checkpoint, processes single images or batches, computes metrics.')
bl('Ensemble Subsystem: Loads both Teacher and Student, computes weighted average of outputs.')
bl('Application Subsystem: Webcam capture, real-time enhancement, display, and user interface.')

h3('5.2 Detailed System Design')
pn('5.2.1 Classification')
para('BioNAFNet is a deep learning model implemented as a PyTorch nn.Module. The system is organized as a collection of Python modules with self-contained model definitions in each training/testing script.')

pn('5.2.2 Definition')
para('BioNAFNet is a biologically-inspired low-light image enhancement system that takes a degraded low-light image as input and produces an enhanced version with improved brightness, contrast, color accuracy, and detail visibility.')

pn('5.2.3 Responsibilities')
bl('Accept low-light images in standard formats (JPEG, PNG)')
bl('Apply biological preprocessing (PRCM, SPDP)')
bl('Enhance through NAFNet encoder-decoder with biological modules')
bl('Apply adaptive postprocessing (ARFP)')
bl('Compute quality metrics (PSNR, SSIM) against ground truth')
bl('Support real-time webcam enhancement at 20+ FPS')

pn('5.2.4 Constraints')
bl('Input images must be RGB format')
bl('Teacher model requires ~600 MB GPU VRAM')
bl('Training requires paired low-light/normal-light image data')
bl('Ensemble mode requires both models loaded simultaneously')
bl('128x128 patch training limits global context learning')

pn('5.2.5 Composition')
para('BioNAFNet is composed of the following primary components:')
tbl(['Component', 'Type', 'Parameters', 'Purpose'],
    [['BioNAFNet', 'nn.Module', '154M / 24M', 'Main model class'],
     ['BioNAFBlock', 'nn.Module', '~1.5M / ~0.4M each', 'Core processing block'],
     ['LateralInhibition', 'nn.Module', '~2K per block', 'RLIN edge enhancement'],
     ['FrequencyBranch', 'nn.Module', '~500K', 'FAEB spectral processing'],
     ['AdaptiveReceptiveField', 'nn.Module', '~100K', 'ARFP luminance-adaptive output'],
     ['PhotoreceptorCurve', 'nn.Module', '3 params', 'PRCM input preprocessing'],
     ['DualPathway', 'nn.Module', '~50K', 'SPDP Y/UV processing'],
     ['TemporalAdaptation', 'nn.Module', '~200K', 'TAM multi-pass memory'],
     ['TotalLoss', 'nn.Module', 'VGG16 features', 'Composite loss function'],
     ['LOLDataset', 'Dataset', '—', 'Data loading and augmentation'],
     ['EMA', 'Helper', '—', 'Exponential moving average']],
    'System Component Hierarchy')

pn('5.2.6 Uses/Interactions')
para('The main interactions are: LOLDataset provides batches to BioNAFNet → BioNAFNet processes through PRCM → SPDP → Encoder (with RLIN per block) → FAEB → Decoder → ARFP → Output. TotalLoss compares output with ground truth. During distillation, the frozen Teacher provides reference outputs for mimic loss. EMA smooths model weights after each optimization step.')

pn('5.2.10 Detailed Subsystem Design')
para('The following UML diagrams describe the system design in detail.')

photo_note('Use Case Diagram: Show User actor interacting with: "Load Image", "Enhance Image", "View Side-by-Side", "Switch Model", "Batch Process", "Export Results", "Real-time Webcam". Draw in draw.io or StarUML.')

photo_note('Class Diagram (UML): BioNAFNet → contains → BioNAFBlock, LateralInhibition, FrequencyBranch, AdaptiveReceptiveField, PhotoreceptorCurve, DualPathway, TemporalAdaptation. TotalLoss → uses → VGG16. LOLDataset → extends → torch.utils.data.Dataset. Draw in draw.io or StarUML.')

photo_note('Activity Diagram: Start → Load Image → Normalize → Pad → PRCM → SPDP → Encoder → Bottleneck+FAEB → Decoder → ARFP → Residual → Crop → Clamp → Save → End. Use diamond for "Multi-pass?" decision. Draw in draw.io.')

photo_note('Sequence Diagram: User → System: load_image(), System → BioNAFNet: forward(image), BioNAFNet → PRCM: apply(), BioNAFNet → SPDP: apply(), BioNAFNet → Encoder: encode(), BioNAFNet → FAEB: enhance_freq(), BioNAFNet → Decoder: decode(), BioNAFNet → ARFP: apply(), System → Metrics: compute_psnr(), System → User: display_result(). Draw in draw.io.')

photo_note('Data Flow Diagram (DFD Level 0): External Entity "User" → Process "BioNAFNet System" → Data Store "Enhanced Images". Data Store "LOL Dataset" → Process "BioNAFNet System". Draw in draw.io.')

pn('Training Algorithm (Pseudocode)')
pn('Algorithm 1: Teacher Model Training')
pn('INPUT: Dataset D, BioNAFNet model M, epochs N=504')
pn('INIT: AdamW optimizer, EMA (decay=0.9995), LR scheduler')
pn('FOR epoch = 1 TO N:')
pn('  FOR each batch (low, high) IN D:')
pn('    enhanced = M.forward(low)')
pn('    loss = TotalLoss(enhanced, high)')
pn('    loss.backward()')
pn('    IF step % 2 == 0: optimizer.step()  // grad accum')
pn('    EMA.update(M)')
pn('  END FOR')
pn('  val_psnr = validate(EMA_model, val_set)')
pn('  IF val_psnr > best: save_checkpoint("best.pth")')
pn('  scheduler.step()')
pn('END FOR')

pn('')
pn('Algorithm 2: Knowledge Distillation')
pn('INPUT: Frozen Teacher T, Student S, Dataset D, epochs N=693')
pn('FOR epoch = 1 TO N:')
pn('  FOR each batch (low, high) IN D:')
pn('    WITH no_grad: teacher_out = T(low)')
pn('    student_out = S(low)')
pn('    loss = 0.5*L1(student,high) + 0.1*SSIM(student,high)')
pn('           + 0.4*L2(student, teacher_out)')
pn('    loss.backward(); optimizer.step(); EMA.update(S)')
pn('  END FOR')
pn('END FOR')

pn('')
pn('Algorithm 3: Ensemble Inference')
pn('INPUT: Teacher T, Student S, image I, alpha')
pn('teacher_out = T(I)')
pn('student_out = S(I)')
pn('ensemble_out = alpha * teacher_out + (1-alpha) * student_out')
pn('RETURN clamp(ensemble_out, 0, 1)')

doc.add_page_break()
doc.save(DOC)
print('Part 2 done: Chapters 4-5')
print('Tables:', TN[0], '| Figures:', FN[0])
