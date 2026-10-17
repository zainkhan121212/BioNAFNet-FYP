"""
BioNAFNet FYP Thesis Generator - Part 2: Chapter 3 (Research Methodology)
Appends to the existing document from Part 1.
"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

FIGURES = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
DOC_PATH = r"F:\low_light_enhancement\eye adaption\BioNAFNet\FYP_Thesis_BioNAFNet_COMPLETE.docx"
doc = Document(DOC_PATH)

fig_num = [10]  # continue from part 1
tbl_num = [3]

def h1(t): p=doc.add_heading(t,1); p.alignment=WD_ALIGN_PARAGRAPH.LEFT
def h2(t): doc.add_heading(t,2)
def h3(t): doc.add_heading(t,3)
def para(t):
    p=doc.add_paragraph(t); p.paragraph_format.first_line_indent=Cm(1.27); return p
def pn(t): return doc.add_paragraph(t)
def bullet(t): doc.add_paragraph(t, style='List Bullet')
def numbered(t): doc.add_paragraph(t, style='List Number')
def fig(fn, cap, w=5.5):
    fig_num[0]+=1
    path=os.path.join(FIGURES,fn)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(w))
        doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    c=doc.add_paragraph(f'Figure {fig_num[0]}: {cap}')
    c.alignment=WD_ALIGN_PARAGRAPH.CENTER; c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
def tbl(headers, rows, cap=None):
    tbl_num[0]+=1
    if cap:
        c=doc.add_paragraph(f'Table {tbl_num[0]}: {cap}')
        c.alignment=WD_ALIGN_PARAGRAPH.CENTER; c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
    table=doc.add_table(rows=1+len(rows), cols=len(headers))
    try: table.style='Table Grid'
    except: pass
    table.alignment=WD_TABLE_ALIGNMENT.CENTER
    for j,h in enumerate(headers):
        cell=table.rows[0].cells[j]; cell.text=h
        for r in cell.paragraphs[0].runs: r.bold=True; r.font.size=Pt(10)
    for i,row in enumerate(rows):
        for j,val in enumerate(row):
            cell=table.rows[i+1].cells[j]; cell.text=str(val)
            for r in cell.paragraphs[0].runs: r.font.size=Pt(10)
    doc.add_paragraph('')

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 3: RESEARCH METHODOLOGY
# ═══════════════════════════════════════════════════════════════════════════

h1('Chapter 3: Research Methodology')

h2('3.1 Research Design')
h3('3.1.1 Research Approach')
para('This research follows an experimental and quantitative approach. We design a novel neural network architecture, train it on benchmark datasets, and evaluate its performance using objective metrics. The research involves iterative design where each biological module is integrated and tested to measure its individual contribution through ablation studies.')

h3('3.1.2 Research Framework Overview')
para('Our research framework consists of four main stages: (1) Architecture design incorporating biological modules into NAFNet, (2) Teacher model training on combined LOLv1+LOLv2 datasets, (3) Knowledge distillation to create the lightweight Student model, and (4) Comprehensive evaluation including ensemble fusion experiments. Each stage builds upon the previous one to create a complete low-light enhancement pipeline.')

h2('3.2 Proposed Methodology')
h3('3.2.1 Overall Architecture Design')
para('BioNAFNet is built on the NAFNet backbone which uses a U-Net style encoder-decoder architecture. The key insight of NAFNet is replacing traditional activation functions (ReLU, GELU) with a Simple Gate mechanism that splits features into two halves and multiplies them element-wise. This avoids the information loss caused by activation functions while maintaining non-linearity.')
para('We enhance the NAFNet backbone with seven biologically-inspired modules integrated at strategic positions in the network. The complete processing pipeline is:')
pn('Input Image → PRCM (Photoreceptor Curve) → SPDP (Dual Pathway) → NAFNet Encoder (with RLIN) → Bottleneck (with FAEB) → NAFNet Decoder → ARFP (Adaptive Receptive Field) → Output Image')
para('For the Teacher model, TAM (Temporal Adaptation Memory) provides multi-pass refinement where the output of one pass is fed back as input for the next pass, similar to how the human eye gradually adapts to darkness. The WFPL (Weber-Fechner Perceptual Loss) guides training by emphasizing accuracy in dark regions.')

h3('3.2.2 Problem Formulation')
para('Given a low-light input image I_low with dimensions H x W x 3, our goal is to learn a mapping function F_θ such that F_θ(I_low) = I_enhanced, where I_enhanced approximates the well-lit ground truth image I_gt. The model parameters θ are optimized by minimizing a composite loss function L(I_enhanced, I_gt) that combines pixel-level, perceptual, structural, and our novel Weber-Fechner components.')

h3('3.2.3 Mathematical Modeling')
para('The forward pass of BioNAFNet can be formalized as:')
pn('x₁ = PRCM(I_low)    — Photoreceptor response simulation')
pn('x₂ = SPDP(x₁)       — Scotopic-photopic dual pathway processing')
pn('x₃ = Encoder(x₂)    — Multi-scale feature extraction with RLIN')
pn('x₄ = FAEB(Bottleneck(x₃))  — Frequency-aware bottleneck processing')
pn('x₅ = Decoder(x₄)    — Multi-scale feature reconstruction')
pn('x₆ = ARFP(x₅, lum)  — Luminance-adaptive output refinement')
pn('I_enhanced = x₆ + I_low  — Residual connection')

h2('3.3 Network Architecture')
h3('3.3.1 Encoder-Decoder Structure')
para('The encoder consists of four stages, each containing BioNAFBlocks followed by a downsampling convolution (stride-2 conv that doubles channels). The decoder mirrors this with four upsampling stages using PixelShuffle. Skip connections between corresponding encoder and decoder stages preserve fine-grained spatial information.')

tbl(['Stage', 'Blocks', 'Channels (T/S)', 'Resolution', 'Key Module'],
    [['Input Conv', '1 Conv3x3', '64 / 32', 'H×W', '—'],
     ['Encoder 1', '2 BioNAFBlocks', '64 / 32', 'H×W', 'RLIN'],
     ['Encoder 2', '2 BioNAFBlocks', '128 / 64', 'H/2×W/2', 'RLIN'],
     ['Encoder 3', '4 BioNAFBlocks', '256 / 128', 'H/4×W/4', 'RLIN'],
     ['Encoder 4', '8 BioNAFBlocks', '512 / 256', 'H/8×W/8', '—'],
     ['Bottleneck', '12 / 4 Blocks', '512 / 256', 'H/16×W/16', 'FAEB'],
     ['Decoder 1-4', '2 each', '256→64 / 128→32', 'H/8→H', '—'],
     ['Output', 'ARFP + Conv3x3', '3', 'H×W', 'ARFP']],
    'Layer-by-layer Architecture (T=Teacher, S=Student)')

h3('3.3.2 Feature Extraction Modules')
para('Each BioNAFBlock processes features through: LayerNorm → 1x1 Conv (channel expansion) → 3x3 Depthwise Conv → SimpleGate → Simplified Channel Attention (SCA) → 1x1 Conv (channel reduction) → RLIN → Residual connection. A second branch applies LayerNorm → 1x1 Conv → SimpleGate → 1x1 Conv for the feed-forward network (FFN). Learnable scaling parameters beta and gamma control the residual contributions.')

h3('3.3.3 Enhancement Modules')
para('The enhancement modules are the biological components that distinguish BioNAFNet from standard NAFNet. They are placed at specific positions in the network where they can have the most impact: PRCM and SPDP at the input for preprocessing, RLIN in encoder blocks for edge enhancement, FAEB at the bottleneck for frequency processing, and ARFP at the output for adaptive final refinement.')

h3('3.3.4 Skip Connections and Residual Learning')
para('Skip connections are critical for image restoration tasks. They allow the decoder to access high-resolution features from the encoder, preventing the loss of fine details during downsampling. Additionally, a global residual connection adds the input image to the network output, meaning the network only needs to learn the residual (difference) between the low-light and well-lit images. This makes training easier and more stable.')

h2('3.4 Key Components Design')

h3('3.4.1 RLIN — Retinal Lateral Inhibition Network')
para('Biological Inspiration: In the human retina, ganglion cells exhibit center-surround antagonism. The center of the receptive field responds to light stimulation while the surrounding area inhibits the response. This creates edge enhancement and helps the visual system detect boundaries even in low contrast conditions.')
para('Implementation: RLIN uses a center pathway (1x1 convolution capturing the direct response) and a surround pathway (5x5 average pooling followed by 1x1 convolution capturing the inhibitory surround). The difference between center and surround responses is scaled by a learnable parameter alpha (initialized to 0.3) and added to the input:')
pn('Output = x + α × (Center(x) - Surround(x))')
para('RLIN is integrated into every BioNAFBlock in the first three encoder stages (excluding the deepest stage to save memory). This provides edge enhancement at multiple scales throughout the encoding process.')

h3('3.4.2 FAEB — Frequency-Aware Enhancement Branch')
para('Biological Inspiration: The human visual cortex contains neurons tuned to specific spatial frequencies. Low spatial frequencies carry overall brightness and structure while high frequencies carry textures and edges. In low-light images, high-frequency components are disproportionately degraded by noise.')
para('Implementation: FAEB operates at the bottleneck level. It converts features to the frequency domain using 2D FFT, then processes the amplitude and phase spectra separately through dedicated convolutional networks. The modified spectra are recombined and converted back to the spatial domain via inverse FFT:')
pn('FFT(x) → Amplitude, Phase')
pn('Amp_out = ConvNet_amp(Amplitude)')
pn('Phase_out = ConvNet_phase(Phase)')
pn('Output = x + blend × iFFT(Amp_out, Phase_out)')
para('The blend parameter is initialized to 0.15 to ensure gradual frequency-domain contribution. All FFT operations are performed in float32 precision to avoid numerical issues with half-precision training.')

h3('3.4.3 ARFP — Adaptive Receptive Field Pooling')
para('Biological Inspiration: The human visual system adapts its spatial resolution based on ambient light levels. In bright conditions (photopic vision), the eye uses small, densely packed cone cells for high-resolution vision. In dark conditions (scotopic vision), rod cells pool signals over larger areas to increase sensitivity at the cost of spatial resolution.')
para('Implementation: ARFP uses three parallel depthwise convolution branches with kernel sizes 3x3, 5x5, and 7x7 (small, medium, large receptive fields). A gating network takes the luminance map as input and produces softmax weights that blend the three branches:')
pn('weights = Softmax(GateNet(luminance_map))')
pn('Output = w₁×Small(x) + w₂×Medium(x) + w₃×Large(x)')
para('In dark regions, the gating network learns to assign higher weight to the large receptive field branch, effectively pooling information from a wider area just like rod cells do. In bright regions, the small receptive field branch dominates for sharp detail preservation.')

h3('3.4.4 PRCM — Photoreceptor Response Curve Modeling')
para('Biological Inspiration: Human photoreceptors (rods and cones) have different sensitivity curves. Rods are sensitive in low light (scotopic vision) with a gamma response around 0.45. Cones require more light (photopic vision) with a gamma around 0.95. The transition between rod and cone dominance happens around a luminance threshold.')
para('Implementation: PRCM applies learned gamma curves to simulate rod and cone responses:')
pn('Rod response: x_rod = x^γ_rod (γ_rod initialized to 0.45)')
pn('Cone response: x_cone = x^γ_cone (γ_cone initialized to 0.95)')
pn('Blend weight: w = sigmoid((luminance - threshold) × 12)')
pn('Output = x_rod × (1 - w) + x_cone × w')
para('The threshold parameter (initialized to 0.25) and both gamma values are learnable, allowing the network to discover optimal response curves during training. This happens before the NAFNet backbone, providing biologically-plausible input preprocessing.')

h3('3.4.5 SPDP — Scotopic-Photopic Dual Pathway')
para('Biological Inspiration: The human visual cortex processes luminance and color information through separate parallel pathways. The magnocellular (M) pathway handles luminance and motion while the parvocellular (P) pathway handles color and fine detail. This parallel processing allows efficient handling of different visual attributes.')
para('Implementation: SPDP converts the RGB input to YUV color space, where Y represents luminance and U/V represent chrominance. The scotopic pathway processes Y (luminance) through a dedicated CNN, simulating rod-based processing. The photopic pathway processes U and V (color) through a separate CNN, simulating cone-based processing:')
pn('Y, U, V = RGB_to_YUV(x)')
pn('Luminance features = ScotopicNet(Y)')
pn('Color features = PhotopicNet(concat(U, V))')
pn('Residual = FuseNet(concat(lum_feat, col_feat)) × 0.2')
pn('Output = x + Residual')
para('The 0.2 scaling factor ensures the dual pathway provides a gentle refinement rather than dominating the input signal.')

h3('3.4.6 TAM — Temporal Adaptation Memory')
para('Biological Inspiration: When you walk from a bright room into a dark one, your eyes do not adapt instantly. Instead, the visual system gradually adjusts over several seconds through a process called dark adaptation. Similarly, when moving from dark to bright, light adaptation occurs more quickly. This temporal aspect of vision is not modeled by any existing LLIE method.')
para('Implementation: TAM uses a GRU (Gated Recurrent Unit) cell to aggregate information across multiple forward passes of the network. In the Teacher model (n_passes=2), the image is processed twice through the NAFNet backbone. The GRU maintains a hidden state that accumulates information from each pass:')
pn('For each pass p = 1, ..., N:')
pn('  output_p = NAFNet(current_input)')
pn('  hidden = GRU(proj_in(output_p), hidden)')
pn('  current_input = output_p')
pn('Final = output_N + proj_out(hidden) × 0.15')
para('In the Student model (n_passes=1), TAM is effectively bypassed since there is only one pass. The TAM weights were found to be identical between checkpoints, confirming they are not updated during single-pass training.')

h3('3.4.7 WFPL — Weber-Fechner Perceptual Loss')
para('Biological Inspiration: The Weber-Fechner law is a fundamental principle of psychophysics. It states that the perceived change in a stimulus is proportional to the logarithm of the stimulus intensity. In practical terms, humans are much more sensitive to brightness changes in dark regions than in bright regions. A small change from 0 to 5 (out of 255) is much more noticeable than a change from 200 to 205.')
para('Implementation: WFPL weights the pixel-level errors inversely proportional to the local luminance of the ground truth image:')
pn('weight_map = 1 / (luminance(target) + ε)')
pn('weight_map = weight_map / mean(weight_map)  — normalization')
pn('L_wfpl = mean(|pred - target| × weight_map)')
para('The epsilon value (0.02) prevents division by zero in completely black regions. The normalization ensures the loss magnitude is comparable to other loss components. This loss forces the network to pay extra attention to dark region accuracy, which is exactly where enhancement matters most.')

h2('3.5 Loss Functions')
h3('3.5.1 Pixel-level Losses')
para('We use Charbonnier loss instead of L1 or L2. Charbonnier loss is defined as L = sqrt((pred - target)² + ε²), where ε = 0.001. It is differentiable at zero (unlike L1) and more robust to outliers than L2. This provides stable gradients during training.')

h3('3.5.2 Perceptual Loss')
para('VGG16 perceptual loss computes the L1 distance between feature representations of the predicted and target images extracted from the first 16 layers of a pre-trained VGG16 network. This encourages the enhanced image to have similar high-level features (textures, structures) to the ground truth even if pixel values differ slightly.')

h3('3.5.3 SSIM Loss')
para('SSIM loss = 1 - SSIM(pred, target). This directly optimizes for structural similarity by comparing local luminance, contrast, and structure between patches of the predicted and target images.')

h3('3.5.4 Edge and Color Losses')
para('Edge loss uses Sobel filters to extract edge maps from both predicted and target images, then computes L1 distance between them. This preserves sharp edges and fine details. Color loss converts both images to YUV space and computes L1 distance on the chrominance channels (U and V), ensuring accurate color reproduction.')

h3('3.5.5 Combined Loss Function')
tbl(['Component', 'Weight', 'Purpose'],
    [['Charbonnier', '1.0', 'Pixel-level reconstruction'],
     ['SSIM', '0.8', 'Structural similarity'],
     ['Perceptual (VGG16)', '0.2', 'Feature-level quality'],
     ['Edge (Sobel)', '0.25', 'Detail preservation'],
     ['Color (YUV)', '0.1', 'Chrominance accuracy'],
     ['Weber-Fechner', '0.3', 'Dark region emphasis (Novel)']],
    'Loss Function Components and Weights')
pn('L_total = 1.0×L_charb + 0.8×L_ssim + 0.2×L_perc + 0.25×L_edge + 0.1×L_color + 0.3×L_wfpl')

h2('3.6 Training Strategy')
h3('3.6.1 Dataset Preparation and Preprocessing')
para('Training data consists of LOLv1 (485 pairs), LOLv2 Real (689 pairs), and LOLv2 Synthetic (900 pairs), totaling 2074 training image pairs. All three datasets are concatenated into a single training set. Images are normalized to [0, 1] range by dividing by 255. Random 128x128 patches are extracted during training to fit within GPU memory.')

h3('3.6.2 Data Augmentation Techniques')
para('We apply the following augmentations with 50 percent probability each:')
bullet('Random horizontal flip')
bullet('Random vertical flip')
bullet('Random 90-degree rotation (0, 90, 180, or 270 degrees)')
bullet('MixUp augmentation (20 percent probability): Two random patches are blended with a beta-distributed mixing ratio.')

h3('3.6.3 Training Hyperparameters')
tbl(['Parameter', 'Teacher', 'Student'],
    [['Optimizer', 'AdamW (β₁=0.9, β₂=0.999)', 'AdamW'],
     ['Initial LR', '2×10⁻⁴', '2×10⁻⁴'],
     ['Min LR', '1×10⁻⁶', '1×10⁻⁶'],
     ['Weight Decay', '1×10⁻⁴', '1×10⁻⁴'],
     ['Batch Size', '4 × 2 (gradient accum)', '4 × 2'],
     ['Patch Size', '128×128', '128×128'],
     ['EMA Decay', '0.9995', '0.9995'],
     ['Epochs', '504', '693'],
     ['Gradient Clipping', '0.5', '0.5'],
     ['Mixed Precision', 'Yes (AMP)', 'Yes (AMP)']],
    'Training Hyperparameters')

h3('3.6.4 Optimization Algorithm')
para('We use AdamW optimizer which decouples weight decay from the adaptive learning rate. Gradient accumulation over 2 steps gives an effective batch size of 8. Gradient clipping at 0.5 prevents training instability from large gradients, which can occur during frequency-domain operations in FAEB.')

h3('3.6.5 Learning Rate Scheduling')
para('We use CosineAnnealingWarmRestarts with T_0=50 epochs and T_mult=2. This creates a learning rate schedule that decays from 2e-4 to 1e-6 following a cosine curve, then restarts. Each restart period doubles in length (50, 100, 200, 400 epochs). This helps the optimizer escape local minima and explore the loss landscape more thoroughly.')
fig('fig_lr_schedule.png', 'Learning Rate Schedule for Teacher and Student Models')

h3('3.6.6 Knowledge Distillation Strategy')
para('Knowledge distillation compresses the 154M-parameter Teacher into a 24M-parameter Student (BioNAFNet-Lite). The Student has the same architecture but with reduced width (32 vs 64 channels) and fewer middle blocks (4 vs 12). It uses single-pass inference (n_passes=1) instead of the Teacher two-pass refinement.')
para('The Student is trained using a combination of ground truth supervision and Teacher mimicry:')
pn('L_student = 0.5×L1(student_out, ground_truth) + 0.1×SSIM(student_out, ground_truth) + 0.4×L2(student_out, teacher_out)')
para('The mimic loss weight of 0.4 forces the Student to replicate the Teacher enhancement patterns while still learning directly from ground truth. EMA with decay 0.9995 smooths the Student weights for better generalization.')

h2('3.7 Evaluation Methodology')
h3('3.7.1 Evaluation Metrics')
para('We evaluate using PSNR (dB) for pixel-level accuracy and SSIM for structural similarity. Both metrics are computed on full-resolution test images (not patches) to ensure the evaluation reflects real-world performance. Higher values indicate better quality for both metrics.')

h3('3.7.2 Comparison Baselines')
para('We compare against RetinexNet (2018), KinD (2019), MIRNet (2020), EnlightenGAN (2021), SNR-Aware Transformer (2022), NAFNet (2022), and Retinexformer (2023). These represent the progression of LLIE methods from early CNN approaches to modern transformers.')

h3('3.7.3 Testing Protocol')
para('All models are evaluated on full-resolution test images without any preprocessing or post-processing. The EMA model weights are used for inference (not the training weights) as EMA provides smoother and more generalized predictions. Inference is done with batch size 1 and images are padded to the nearest multiple of 16 to accommodate the 4-level encoder-decoder structure.')

h2('3.8 Development Environment')
h3('3.8.1 Hardware Specifications')
para('Training was conducted on a single NVIDIA RTX GPU with CUDA support. Mixed precision training (AMP) was used to reduce memory usage and speed up training. Each Teacher epoch took approximately 4 minutes and each Student epoch took approximately 3.5 minutes.')

h3('3.8.2 Software and Frameworks')
bullet('Python 3.8+')
bullet('PyTorch 2.0+ with CUDA')
bullet('torchvision (for VGG16 perceptual loss)')
bullet('NumPy, PIL, scikit-image')
bullet('matplotlib (for visualization)')

h3('3.8.3 Libraries and Tools')
para('The implementation is self-contained in a single Python file for both Teacher (train_bionafnet.py) and Student (train_distillation.py). No external model definitions or configuration files are needed. All architectural components including the seven biological modules are defined within the training scripts.')

h2('3.9 Summary')
para('This chapter presented the complete methodology of BioNAFNet. We described the NAFNet backbone enhanced with seven biological modules (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL), each inspired by specific mechanisms of the human visual system. We detailed the composite loss function, training strategy, knowledge distillation pipeline, and evaluation methodology. The next chapter covers the system design and implementation details.')

doc.add_page_break()
doc.save(DOC_PATH)
print('Chapter 3 complete. Saved.')
