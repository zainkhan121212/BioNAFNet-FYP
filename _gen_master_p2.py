"""
Master FYP Report Generator — Part 2: Chapters 3-4
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _merge_helpers import *

DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams_only")


def build_chapter3(doc):
    """Chapter 3: Software Requirement Specification"""
    add_heading1(doc, "Chapter 3")
    add_heading2(doc, "Software Requirement Specification")

    # 3.1 Literature Survey
    add_heading3(doc, "3.1 Literature Survey")

    add_para(doc, "3.1.1 Traditional Image Enhancement Methods", bold=True)
    add_para(doc, "Histogram Equalization (HE) was one of the earliest enhancement techniques, proposed in the 1970s. It maps pixel intensities to a uniform distribution, spreading values across the full 0-255 range [Gonzalez and Woods, 2002]. While it improves contrast, it also boosts noise and washes out regions in low-light images.")
    add_para(doc, "Contrast Limited Adaptive Histogram Equalization (CLAHE), introduced by Zuiderveld in 1994, improved upon HE by dividing the image into small tiles and applying local histogram equalization with a clip limit to prevent over-amplification. CLAHE is widely used in medical imaging but still creates blocking artifacts at tile boundaries and cannot handle really dark images well.")
    add_para(doc, "Gamma correction applies a power-law transformation (I_out = I_in^gamma) where gamma < 1 brightens the image. Adaptive gamma methods estimate gamma locally but still cannot tell the difference between signal and noise [Huang et al., 2013].")
    add_para(doc, "The Retinex theory, proposed by Edwin Land in 1977, says that perceived color depends on relative reflectance rather than absolute light intensity. Image formation is modeled as I = R \u00d7 L where R is reflectance and L is illumination. Single Scale Retinex (SSR) and Multi-Scale Retinex (MSR) estimate illumination using Gaussian filters [Jobson et al., 1997]. While theoretically sound, Retinex methods produce halo artifacts and struggle with strong noise.")

    # Traditional Methods Summary Table (from Doc2)
    add_table_caption(doc, 3, "Summary of Traditional Enhancement Methods")
    trad_methods = [
        ("HE", "1970s", "Global histogram redistribution", "Simple, fast", "Over-enhancement, noise amplification"),
        ("CLAHE", "1994", "Local adaptive HE", "Better local contrast", "Blocking artifacts, limited in dark"),
        ("Gamma Correction", "Various", "Power-law transform", "Simple, adjustable", "Cannot denoise, fixed rule"),
        ("SSR/MSR", "1997", "Retinex decomposition", "Theoretically grounded", "Halo artifacts, noise sensitive"),
        ("LIME", "2017", "Illumination estimation", "Structure preserving", "Over-smoothing, slow"),
    ]
    make_table(doc, ["Method", "Year", "Approach", "Pros", "Cons"], trad_methods)

    add_para(doc, "3.1.2 CNN-Based Enhancement Methods", bold=True)
    add_para(doc, "LLNet (Lore et al., 2017) was one of the first deep learning approaches for LLIE, using stacked sparse denoising autoencoders. It showed that neural networks can learn enhancement from data, but its quality was limited by the simple architecture.")
    add_para(doc, "MBLLEN (Lv et al., 2018) used a Multi-Branch architecture that processes features at multiple scales through separate branches. This multi-scale approach helped capture both local and global features but increased computational cost.")
    add_para(doc, "RetinexNet (Wei et al., 2018) was one of the first to apply deep learning to LLIE using a Retinex decomposition network. KinD (Zhang et al., 2019) improved on this with a two-branch architecture achieving 20.87 dB on LOLv1.")
    add_para(doc, "MIRNet (Zamir et al., 2020) introduced multi-scale residual blocks with selective kernel features, reaching 24.14 dB. NAFNet (Chen et al., 2022) simplified things by removing activation functions entirely, using a SimpleGate mechanism instead. NAFNet is our backbone architecture because of its clean, efficient design.")

    add_para(doc, "3.1.3 Transformer-Based Enhancement Methods", bold=True)
    add_para(doc, "Restormer (Zamir et al., 2022) applied efficient transformers to image restoration using multi-DConv head transposed attention, achieving state-of-the-art results across multiple restoration tasks.")
    add_para(doc, "SNR-Aware Transformer (Xu et al., 2022) introduced signal-to-noise ratio aware attention that adapts processing based on local noise levels. It achieved 24.61 dB on LOLv1.")
    add_para(doc, "Retinexformer (Cai et al., 2023) combined Retinex decomposition with transformer architecture, achieving 25.16 dB on LOLv1. It is currently one of the top-performing methods on LOL benchmarks.")

    add_para(doc, "3.1.4 GAN-Based Enhancement Methods", bold=True)
    add_para(doc, "EnlightenGAN (Jiang et al., 2021) was notable for using unpaired training data through adversarial learning. While it removed the need for paired data, its results (17.48 dB) were lower than supervised methods.")

    add_para(doc, "3.1.5 Knowledge Distillation in Image Processing", bold=True)
    add_para(doc, "Knowledge Distillation (KD), introduced by Hinton et al. (2015), compresses a large Teacher model into a smaller Student by training the Student to copy the Teacher outputs. KD has been successfully applied in classification and detection tasks but it is not common in LLIE. Our work shows that KD can effectively compress a LLIE model by 6.4x while the Student actually beats the Teacher on some datasets.")

    # SOTA Comparison Table
    add_table_caption(doc, 4, "Performance Comparison with State-of-the-Art Methods on LOLv1 Dataset")
    sota = [
        ("LLNet", "2017", "Autoencoder", "~1M", "~17.0", "~0.600"),
        ("RetinexNet", "2018", "CNN", "0.8M", "16.77", "0.560"),
        ("MBLLEN", "2018", "Multi-Branch", "~0.5M", "17.90", "0.715"),
        ("KinD", "2019", "Retinex-CNN", "8.2M", "20.87", "0.800"),
        ("DRBN", "2020", "Recursive", "5.3M", "20.13", "0.830"),
        ("MIRNet", "2020", "Multi-Scale", "31.8M", "24.14", "0.830"),
        ("EnlightenGAN", "2021", "GAN", "8.6M", "17.48", "0.650"),
        ("SNR-Aware", "2022", "Transformer", "39.1M", "24.61", "0.842"),
        ("NAFNet", "2022", "CNN (SimpleGate)", "67.9M", "~23.0", "~0.830"),
        ("Restormer", "2022", "Transformer", "26.1M", "22.43", "0.823"),
        ("Retinexformer", "2023", "Retinex-Trans", "1.6M", "25.16", "0.845"),
        ("BioNAFNet-Lite (Ours)", "2026", "Bio-CNN", "24M", "25.23", "0.853"),
        ("BioNAFNet-Ens (Ours)", "2026", "Bio-CNN", "178M", "25.27", "0.864"),
    ]
    make_table(doc, ["Method", "Year", "Type", "Params", "PSNR (dB)", "SSIM"], sota)

    # 3.2 Research Gaps
    add_heading3(doc, "3.2 Research Gaps")
    add_para(doc, "From the literature survey, we found the following gaps:")
    gaps = [
        "Gap 1 \u2014 No Biological Integration: No existing LLIE method uses biological visual system mechanisms like photoreceptor modeling, lateral inhibition, or temporal adaptation.",
        "Gap 2 \u2014 Limited Frequency Processing: Most methods work only in the spatial domain. None use FFT-based frequency processing for low-light enhancement.",
        "Gap 3 \u2014 Fixed Receptive Fields: All methods use the same receptive field size everywhere. The human eye adapts receptive field size based on brightness.",
        "Gap 4 \u2014 Perception-Unaware Losses: Loss functions treat all pixel errors the same, ignoring the Weber-Fechner law that says human sensitivity is highest in dark areas.",
        "Gap 5 \u2014 Quality-Speed Gap: No existing work applies knowledge distillation to bridge the gap between high-quality large models and real-time lightweight models in LLIE.",
        "Gap 6 \u2014 No Desktop Application: No existing desktop application combines multiple AI models with image processing tools (augmentation, cropping, resizing, live preview) in one package.",
    ]
    for i, g in enumerate(gaps, 1):
        add_list_numbered(doc, f"{i}. {g}")

    # 3.3 Datasets
    add_heading3(doc, "3.3 Benchmark Datasets")
    add_table_caption(doc, 5, "Benchmark Datasets for Low-Light Image Enhancement")
    datasets = [
        ("LOLv1", "Real captured", "485", "15", "400\u00d7600", "2018", "Wei et al."),
        ("LOLv2 Real", "Real captured", "689", "100", "Various", "2021", "Yang et al."),
        ("LOLv2 Synthetic", "Synthetic", "900", "100", "Various", "2021", "Yang et al."),
        ("SID", "RAW sensor", "5094", "598", "Various", "2018", "Chen et al."),
        ("LSRW", "Real-world", "5650", "\u2014", "Various", "2022", "Hai et al."),
    ]
    make_table(doc, ["Dataset", "Type", "Train", "Test", "Resolution", "Year", "Source"], datasets)
    add_para(doc, "We use LOLv1, LOLv2 Real, and LOLv2 Synthetic for our experiments, providing 2074 training pairs and 215 test images in total. This combination covers both real-world and synthetic degradation scenarios which gives us a thorough evaluation.")

    # 3.4 Functional Requirements
    add_heading3(doc, "3.4 Functional Requirements")
    add_table_caption(doc, 6, "Functional Requirements")
    func_reqs = [
        ("FR-01", "Load low-light images (JPEG, PNG, BMP)", "High", "Done"),
        ("FR-02", "Enhance image using 12 different AI models", "High", "Done"),
        ("FR-03", "Switch between CPU and GPU processing", "High", "Done"),
        ("FR-04", "Batch process entire image folders", "High", "Done"),
        ("FR-05", "Show before/after comparison in gallery view", "High", "Done"),
        ("FR-06", "Save enhanced images to selected directory", "High", "Done"),
        ("FR-07", "Augment images with rotation, flip, brightness, contrast", "High", "Done"),
        ("FR-08", "Crop images with custom aspect ratio presets", "High", "Done"),
        ("FR-09", "Resize images with width/height controls and aspect ratio lock", "High", "Done"),
        ("FR-10", "Live webcam enhancement preview", "Medium", "Done"),
        ("FR-11", "Calculate PSNR and SSIM when ground truth is available", "Medium", "Done"),
        ("FR-12", "Display model descriptions and information", "Low", "Done"),
    ]
    make_table(doc, ["ID", "Requirement", "Priority", "Status"], func_reqs)

    # 3.5 Non-Functional Requirements
    add_heading3(doc, "3.5 Non-Functional Requirements")
    add_table_caption(doc, 7, "Non-Functional Requirements")
    nfr = [
        ("NFR-01", "Student model inference time < 50ms per image", "48.9 ms", "Met"),
        ("NFR-02", "Student model FPS > 15 for webcam", "20.5 FPS", "Met"),
        ("NFR-03", "PSNR > 24.0 dB on LOLv1", "25.23 dB", "Met"),
        ("NFR-04", "SSIM > 0.84 on LOLv1", "0.853", "Met"),
        ("NFR-05", "Student model file size < 100 MB", "91 MB", "Met"),
        ("NFR-06", "Application startup time < 5 seconds", "~3 seconds", "Met"),
        ("NFR-07", "GPU VRAM for inference < 4 GB", "~1 GB", "Met"),
        ("NFR-08", "Reproducible results (seeded)", "Seed=42", "Met"),
    ]
    make_table(doc, ["ID", "Requirement", "Achieved", "Status"], nfr)

    # 3.6 Hardware/Software Requirements
    add_heading3(doc, "3.6 Hardware and Software Requirements")
    add_table_caption(doc, 8, "Hardware and Software Requirements")
    hw = [
        ("Operating System", "Windows 10/11 with CUDA support"),
        ("GPU", "NVIDIA RTX series (8+ GB VRAM recommended)"),
        ("RAM", "16 GB minimum"),
        ("Storage", "50 GB (datasets + checkpoints)"),
        ("Python", "3.8 or higher"),
        ("PyTorch", "2.0+ with CUDA 11.8 or 12.x"),
        ("CustomTkinter", "5.2+ (UI framework)"),
        ("PIL/Pillow", "10.0+ (image processing)"),
        ("Additional", "torchvision, numpy, scikit-image, matplotlib"),
    ]
    make_table(doc, ["Component", "Specification"], hw)

    # 3.7 Evaluation Metrics
    add_heading3(doc, "3.7 Evaluation Metrics")
    add_para(doc, "We use two standard metrics for quantitative evaluation:")
    add_para(doc, "Peak Signal-to-Noise Ratio (PSNR): Measured in decibels (dB). PSNR = 10 \u00d7 log10(MAX\u00b2 / MSE) where MAX is 1.0 for normalized images. Higher values mean better pixel-level accuracy. Good LLIE results are typically between 20-30 dB. Our best result is 29.29 dB.")
    add_para(doc, "Structural Similarity Index (SSIM): Ranges from 0 to 1. Compares the structure, luminance, and contrast between the predicted and ground truth images. It is more aligned with how humans see image quality than PSNR. Values above 0.85 are considered good.")
    add_page_break(doc)


def build_chapter4(doc):
    """Chapter 4: Methodology"""
    add_heading1(doc, "Chapter 4")
    add_heading2(doc, "Methodology")

    # 4.1 Research Approach
    add_heading3(doc, "4.1 Research Approach")
    add_para(doc, "Our research follows an experimental quantitative approach. We design a novel architecture, implement it in PyTorch, train it on benchmark datasets, and evaluate performance using objective metrics. The methodology has four main phases:")
    phases = [
        "Phase 1 \u2014 Architecture Design: Build seven biological modules and integrate them into the NAFNet backbone.",
        "Phase 2 \u2014 Teacher Training: Train the full BioNAFNet model (154M parameters) on combined LOLv1+LOLv2 datasets for 504 epochs.",
        "Phase 3 \u2014 Knowledge Distillation: Train a 24M parameter Student model for 693 epochs using Teacher outputs as guidance.",
        "Phase 4 \u2014 Application Development: Build the NeonEnhancer Pro desktop application with CustomTkinter and evaluate all model variants including ensemble fusion.",
    ]
    for i, ph in enumerate(phases, 1):
        add_list_numbered(doc, f"{i}. {ph}")

    # 4.2 NAFNet Backbone
    add_heading3(doc, "4.2 NAFNet Backbone")
    add_para(doc, "We build our model on top of NAFNet (Nonlinear Activation Free Network) by Chen et al. (2022). The key idea of NAFNet is that it replaces activation functions like ReLU with a SimpleGate mechanism. This works by splitting the features into two halves along the channel dimension and multiplying them together. Unlike ReLU which throws away negative values (losing information), SimpleGate keeps all the information.")
    add_para(doc, "The NAFNet block works like this: LayerNorm normalizes the input, then a 1\u00d71 convolution expands the channels, a 3\u00d73 depthwise convolution processes spatial features, SimpleGate provides non-linearity, Simplified Channel Attention (SCA) reweights channels, and a final 1\u00d71 convolution reduces channels back. We call our modified version BioNAFBlock because we add our RLIN module after the channel attention step.")

    # 4.3 - 4.9 Biological Modules
    add_heading3(doc, "4.3 Module 1: RLIN (Retinal Lateral Inhibition Network)")
    add_para(doc, "How the eye does it: In the retina, ganglion cells have a special receptive field shape called center-surround. The center of the field gets excited by light but the surrounding area gets inhibited. This means when there is an edge (bright on one side, dark on the other), the response is very strong. This is how we can see edges even in very dim light.")
    add_para(doc, "How we implement it: RLIN has two pathways. The center pathway uses a 1\u00d71 convolution to capture the direct response at each pixel. The surround pathway uses 5\u00d75 average pooling followed by a 1\u00d71 convolution to capture the surrounding area. The difference between center and surround is scaled by a learnable parameter alpha (starts at 0.3). The formula is: Output = x + alpha \u00d7 (Center(x) - Surround(x)). RLIN is added to every BioNAFBlock in the first three encoder stages.")
    add_figure_placeholder(doc, 4, "RLIN Module Architecture \u2014 Center-Surround Pathways with Subtraction and Scaling",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig04_RLIN_Module_Architecture", "diagram.png"))

    add_heading3(doc, "4.4 Module 2: FAEB (Frequency-Aware Enhancement Branch)")
    add_para(doc, "How the eye does it: The visual cortex has neurons that respond to specific spatial frequencies. Some neurons see fine details (high frequency) while others see overall brightness patterns (low frequency). In dark images, high-frequency components are damaged more by noise.")
    add_para(doc, "How we implement it: FAEB sits at the bottleneck (deepest level) of the network. It takes the feature maps and converts them to the frequency domain using 2D Fast Fourier Transform (FFT). Then it processes the amplitude spectrum (how much of each frequency) and phase spectrum (where things are located) through separate small convolutional networks. After processing, it converts back using inverse FFT and blends the result with the original features using a learnable blend factor (starts at 0.15). All FFT operations use float32 precision to avoid numerical problems with half-precision training.")
    add_figure_placeholder(doc, 5, "FAEB Module \u2014 FFT \u2192 Amplitude/Phase Processing \u2192 iFFT \u2192 Blend",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig05_FAEB_Module", "diagram.png"))

    add_heading3(doc, "4.5 Module 3: ARFP (Adaptive Receptive Field Pooling)")
    add_para(doc, "How the eye does it: In bright light, cone cells give us sharp, detailed vision through small receptive fields. In dark conditions, rod cells pool signals over larger areas to collect more light. This is why we cannot read fine print in dim light but can see large objects.")
    add_para(doc, "How we implement it: ARFP uses three parallel depthwise convolutions with kernel sizes 3\u00d73, 5\u00d75, and 7\u00d77. A gating network takes the luminance map and produces three softmax-normalized weights. In dark regions, the larger kernels get higher weights (like rod cells). In bright regions, the 3\u00d73 kernel dominates (like cone cells). ARFP is placed at the decoder output right before the final reconstruction.")

    add_heading3(doc, "4.6 Module 4: PRCM (Photoreceptor Response Curve Modeling)")
    add_para(doc, "How the eye does it: Rod cells (active in dark) have a response curve with gamma around 0.45 which makes them very sensitive to small brightness changes. Cone cells (active in bright light) have gamma around 0.95 for more linear response. The brain blends between the two based on brightness level.")
    add_para(doc, "How we implement it: PRCM applies two learned gamma transformations. Rod response: x^gamma_rod (starts at 0.45). Cone response: x^gamma_cone (starts at 0.95). A sigmoid function blends between the two based on luminance with a learnable threshold (starts at 0.25). All three parameters are learnable. PRCM is the very first module applied to the input image.")

    add_heading3(doc, "4.7 Module 5: SPDP (Scotopic-Photopic Dual Pathway)")
    add_para(doc, "How the eye does it: The brain processes brightness and color through separate parallel pathways. The magnocellular pathway handles luminance and motion. The parvocellular pathway handles color and fine detail. This separation lets each pathway be optimized independently.")
    add_para(doc, "How we implement it: SPDP converts RGB input to YUV color space. The scotopic pathway processes Y (luminance) through a dedicated convolutional network. The photopic pathway processes U and V (color) through a separate network. Results are fused and added as a residual with 0.2 scaling. SPDP is applied after PRCM as the second preprocessing step.")

    add_heading3(doc, "4.8 Module 6: TAM (Temporal Adaptation Memory)")
    add_para(doc, "How the eye does it: When you walk from a bright room into a dark one, your eyes do not adapt instantly. Dark adaptation takes several minutes as the photoreceptor chemicals slowly regenerate. During this time, your vision gets progressively better. No existing LLIE method models this time-based adaptation.")
    add_para(doc, "How we implement it: TAM uses a GRU (Gated Recurrent Unit) cell to maintain a memory state across multiple forward passes. In the Teacher model (n_passes=2), the image is processed twice. Each pass refines the previous output, mimicking the progressive nature of dark adaptation. The GRU accumulates information from both passes to provide additional refinement. In the Student model (n_passes=1), TAM is effectively bypassed for speed.")

    add_heading3(doc, "4.9 Module 7: WFPL (Weber-Fechner Perceptual Loss)")
    add_para(doc, "How the eye does it: The Weber-Fechner law is a fundamental principle of psychophysics discovered in the 1800s. It says that the perceived change in a stimulus is proportional to the logarithm of the stimulus intensity. In simple terms: humans are much more sensitive to brightness changes in dark regions than in bright regions. A 5-unit change from 0 to 5 is very noticeable, while the same 5-unit change from 200 to 205 is barely perceptible.")
    add_para(doc, "How we implement it: WFPL creates a weight map that assigns higher penalty to errors in dark regions: weight_map = 1 / (luminance(target) + epsilon). The epsilon value (0.02) prevents division by zero. Normalization ensures the loss magnitude is comparable to other components. WFPL forces the network to prioritize accuracy in dark regions, which is exactly where enhancement quality matters most to human observers.")

    # 4.10 Loss Function Design
    add_heading3(doc, "4.10 Loss Function Design")
    add_table_caption(doc, 9, "Composite Loss Function \u2014 Teacher Training")
    loss_teacher = [
        ("Charbonnier", "1.0", "sqrt((pred-gt)\u00b2 + 0.001\u00b2)", "Robust pixel reconstruction"),
        ("SSIM", "0.8", "1 - SSIM(pred, gt)", "Structural preservation"),
        ("Perceptual (VGG16)", "0.2", "L1(VGG16(pred), VGG16(gt))", "Feature-level quality"),
        ("Edge (Sobel)", "0.25", "L1(Sobel(pred), Sobel(gt))", "Edge and detail sharpness"),
        ("Color (UV)", "0.1", "L1(UV(pred), UV(gt))", "Chrominance accuracy"),
        ("Weber-Fechner", "0.3", "mean(|pred-gt| / (lum+eps))", "Dark region emphasis"),
    ]
    make_table(doc, ["Component", "Weight", "Formula", "Purpose"], loss_teacher)
    add_para(doc, "L_total = 1.0\u00d7L_charb + 0.8\u00d7L_ssim + 0.2\u00d7L_perc + 0.25\u00d7L_edge + 0.1\u00d7L_color + 0.3\u00d7L_wfpl")

    add_table_caption(doc, 10, "Distillation Loss Function \u2014 Student Training")
    loss_student = [
        ("L1 (vs ground truth)", "0.5", "L1(student, gt)", "Pixel accuracy"),
        ("SSIM (vs ground truth)", "0.1", "SSIM(student, gt)", "Structure preservation"),
        ("Mimic L2 (vs teacher)", "0.4", "L2(student, teacher_out)", "Knowledge transfer"),
    ]
    make_table(doc, ["Component", "Weight", "Formula", "Purpose"], loss_student)

    # 4.11 Training Strategy
    add_heading3(doc, "4.11 Training Strategy")
    add_table_caption(doc, 11, "Complete Training Configuration")
    train_config = [
        ("Architecture", "width=64, mid=12, 2-pass", "width=32, mid=4, 1-pass"),
        ("Parameters", "154,380,888 (154M)", "23,969,016 (24M)"),
        ("Optimizer", "AdamW (beta1=0.9, beta2=0.999)", "AdamW"),
        ("Initial Learning Rate", "2e-4", "2e-4"),
        ("Minimum Learning Rate", "1e-6", "1e-6"),
        ("LR Scheduler", "CosineAnnealingWarmRestarts", "Same"),
        ("T_0 / T_mult", "50 / 2", "50 / 2"),
        ("Weight Decay", "1e-4", "1e-4"),
        ("Batch Size", "4 (effective 8 with accum)", "4 (effective 8)"),
        ("Gradient Accumulation", "2 steps", "2 steps"),
        ("Gradient Clipping", "0.5 (max_norm)", "0.5"),
        ("Patch Size", "128\u00d7128", "128\u00d7128"),
        ("EMA Decay", "0.9995", "0.9995"),
        ("Mixed Precision (AMP)", "Yes", "Yes"),
        ("Training Epochs", "504", "693"),
        ("Best Validation PSNR", "25.05 dB (epoch 476)", "25.09 dB (epoch 693)"),
        ("Training Time", "~34 hours", "~40 hours"),
        ("Training Data", "2074 pairs combined", "Same + Teacher outputs"),
        ("Augmentation", "H-flip, V-flip, 90-rot, MixUp(0.2)", "Same"),
    ]
    make_table(doc, ["Parameter", "Teacher Model", "Student Model"], train_config)

    # 4.12 Knowledge Distillation
    add_heading3(doc, "4.12 Knowledge Distillation Pipeline")
    add_para(doc, "Knowledge distillation compresses the 154M Teacher into a 24M Student. The Student has the same architecture family but with reduced width (32 vs 64 channels), fewer middle blocks (4 vs 12), and single-pass inference (n_passes=1). During distillation training, the Teacher is frozen and generates outputs for each training batch. The Student learns from both ground truth images (L1+SSIM) and Teacher outputs (L2 mimic loss with weight 0.4).")
    add_para(doc, "The distillation achieves remarkable compression: 6.4x fewer parameters, 6.5x smaller model file (91 MB vs 589 MB), and 3.9x faster inference (48.9 ms vs 188.7 ms per image). Surprisingly the Student-693 achieves higher PSNR than the Teacher on LOLv1 (25.23 vs 24.94 dB). This suggests that the reduced capacity provides beneficial regularization that helps the Student generalize better to full-resolution test images.")
    add_figure_placeholder(doc, 6, "Knowledge Distillation Pipeline \u2014 Teacher (154M) to Student (24M)",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig06_Knowledge_Distillation_Pipeline", "diagram.png"))

    # 4.13 Ensemble Fusion
    add_heading3(doc, "4.13 Ensemble Fusion Strategy")
    add_para(doc, "We explore combining Teacher and Student outputs through weighted averaging to use their complementary learned representations. The ensemble output is: enhanced = alpha \u00d7 teacher_out + (1-alpha) \u00d7 student_out, then clamped to [0,1]. Three main fusion strategies are tested:")
    add_table_caption(doc, 12, "Ensemble Fusion Strategies")
    ensemble = [
        ("Ensemble 50/50", "50%", "50%", "Equal contribution, balanced quality"),
        ("Ensemble T60/S40", "60%", "40%", "Teacher-biased for detail richness"),
        ("Ensemble T40/S60", "40%", "60%", "Student-biased for cleaner structure"),
        ("Synergy T70/S30", "70%", "30%", "Heavy teacher reliance"),
    ]
    make_table(doc, ["Strategy", "Teacher %", "Student %", "Rationale"], ensemble)
    add_para(doc, "The ensemble requires running both models during inference, so it is 3-4x slower than individual models. This makes it suitable for offline processing only, not real-time use.")
    add_page_break(doc)


if __name__ == "__main__":
    from docx import Document
    doc = Document()
    setup_styles(doc)
    build_chapter3(doc)
    build_chapter4(doc)
    doc.save("_test_p2.docx")
    print("Part 2 done.")
