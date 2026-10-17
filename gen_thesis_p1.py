"""
BioNAFNet FYP Thesis Generator - Part 1: Setup + Chapters 1-3
Generates the complete FYP thesis document with all content, tables, and figures.
"""
import os, sys
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

FIGURES = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
OUTPUT = r"F:\low_light_enhancement\eye adaption\BioNAFNet\FYP_Thesis_BioNAFNet_COMPLETE.docx"

doc = Document()

# Page setup
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.18)
    section.right_margin = Cm(2.54)

style = doc.styles['Normal']
style.font.name = 'Times New Roman'
style.font.size = Pt(12)
style.paragraph_format.line_spacing = 1.5
style.paragraph_format.space_after = Pt(6)

fig_num = [0]
tbl_num = [0]

def h1(text):
    p = doc.add_heading(text, level=1)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p

def h2(text):
    return doc.add_heading(text, level=2)

def h3(text):
    return doc.add_heading(text, level=3)

def para(text):
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Cm(1.27)
    return p

def para_no_indent(text):
    return doc.add_paragraph(text)

def bullet(text):
    return doc.add_paragraph(text, style='List Bullet')

def numbered(text):
    return doc.add_paragraph(text, style='List Number')

def add_figure(filename, caption, width=5.5):
    fig_num[0] += 1
    path = os.path.join(FIGURES, filename)
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width))
        last = doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = doc.add_paragraph(f'Figure {fig_num[0]}: {caption}')
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.runs[0].italic = True
    cap.runs[0].font.size = Pt(10)
    return fig_num[0]

def add_table(headers, rows, caption=None):
    tbl_num[0] += 1
    if caption:
        cap = doc.add_paragraph(f'Table {tbl_num[0]}: {caption}')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].italic = True
        cap.runs[0].font.size = Pt(10)
    table = doc.add_table(rows=1+len(rows), cols=len(headers))
    try:
        table.style = 'Table Grid'
    except:
        pass
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(headers):
        cell = table.rows[0].cells[j]
        cell.text = h
        for r in cell.paragraphs[0].runs:
            r.bold = True
            r.font.size = Pt(10)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = table.rows[i+1].cells[j]
            cell.text = str(val)
            for r in cell.paragraphs[0].runs:
                r.font.size = Pt(10)
    doc.add_paragraph('')
    return tbl_num[0]

# ═══════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════

for _ in range(4):
    doc.add_paragraph('')

title = doc.add_paragraph('BioNAFNet: Biologically-Inspired Low-Light Image Enhancement Using Deep Learning with Knowledge Distillation')
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in title.runs:
    r.bold = True
    r.font.size = Pt(22)

doc.add_paragraph('')
sub = doc.add_paragraph('Final Year Project Thesis')
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
for r in sub.runs:
    r.font.size = Pt(16)

doc.add_paragraph('')
doc.add_paragraph('')
author = doc.add_paragraph('Department of Computer Science\nUniversity Name\n2026')
author.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# ABSTRACT
# ═══════════════════════════════════════════════════════════════════════════

h1('Abstract')
para('Low-light image enhancement is a challenging problem in computer vision. Images taken in dark or poorly lit conditions suffer from noise, color distortion, and loss of detail. Traditional methods like histogram equalization and gamma correction can improve brightness but they often amplify noise and produce unnatural colors. Deep learning based approaches have shown much better results but most of them do not consider how the human visual system actually processes light and darkness.')
para('In this thesis, we present BioNAFNet, a biologically-inspired deep learning architecture for low-light image enhancement. Our model is built on the NAFNet backbone and introduces seven novel biological modules inspired by the human visual system: Retinal Lateral Inhibition Network (RLIN), Frequency-Aware Enhancement Branch (FAEB), Adaptive Receptive Field Pooling (ARFP), Photoreceptor Response Curve Modeling (PRCM), Scotopic-Photopic Dual Pathway (SPDP), Temporal Adaptation Memory (TAM), and Weber-Fechner Perceptual Loss (WFPL).')
para('We also demonstrate knowledge distillation from the full Teacher model (154M parameters) to a lightweight Student model called BioNAFNet-Lite (24M parameters), achieving 6.4x compression and 4x speedup with minimal quality loss. The Student model achieves 25.23 dB PSNR on LOLv1 which actually beats the Teacher model (24.94 dB). An ensemble fusion of Teacher and Student achieves 29.29 dB on LOLv2 Real, the highest result across all configurations.')
para('We evaluate on three benchmark datasets: LOLv1, LOLv2 Real, and LOLv2 Synthetic, and provide comprehensive comparisons with state-of-the-art methods. The results show that BioNAFNet achieves competitive performance while offering real-time inference at 20+ FPS for practical deployment.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS (placeholder)
# ═══════════════════════════════════════════════════════════════════════════

h1('Table of Contents')
para_no_indent('[Insert Table of Contents from Word: References > Table of Contents > Automatic Table]')
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# LIST OF FIGURES / TABLES
# ═══════════════════════════════════════════════════════════════════════════

h1('List of Figures')
para_no_indent('[Insert from Word: References > Insert Table of Figures]')
doc.add_paragraph('')
h1('List of Tables')
para_no_indent('[Insert from Word: References > Insert Table of Figures > select Table label]')
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 1: INTRODUCTION
# ═══════════════════════════════════════════════════════════════════════════

h1('Chapter 1: Introduction')

h2('1.1 Background and Motivation')

h3('1.1.1 Overview of Image Enhancement')
para('Image enhancement is one of the most fundamental tasks in computer vision and image processing. The goal is simple: take a degraded image and make it look better. This includes fixing issues like low contrast, poor brightness, noise, and color problems. Over the years, many techniques have been developed for this purpose, starting from basic histogram equalization all the way to modern deep learning approaches.')
para('The field has grown rapidly in the last decade especially with the rise of convolutional neural networks (CNNs). These networks can learn complex image-to-image mapping functions directly from data, which makes them much more powerful than hand-crafted algorithms that rely on fixed mathematical rules.')

h3('1.1.2 Importance of Low Light Image Enhancement')
para('Low-light image enhancement (LLIE) is a specific and very important subset of image enhancement. When we take photos in dark conditions like at night, in a dimly lit room, or under heavy shadows, the resulting images look terrible. They have very low contrast, lots of noise (those grainy dots), washed out or wrong colors, and you can barely see any details.')
para('This is not just an aesthetic problem. Low-light degradation directly affects the performance of downstream computer vision tasks like object detection, face recognition, autonomous driving, and surveillance. If the input image is dark and noisy, any AI system processing it will perform poorly. So fixing low-light images is critical for many real world applications.')
para('Some key application areas where LLIE matters:')
bullet('Surveillance and Security: CCTV cameras often operate in low-light conditions. Enhancing their footage helps identify people and events.')
bullet('Mobile Photography: Phone cameras struggle in low light. Good enhancement algorithms can dramatically improve the user experience.')
bullet('Medical Imaging: Some medical imaging modalities produce low-contrast images that need enhancement for accurate diagnosis.')
bullet('Autonomous Driving: Self-driving cars need to work at night and in tunnels. Enhancement helps their perception systems work better.')
bullet('Remote Sensing: Satellite images taken in low-light or shadowed areas need enhancement for analysis.')

h3('1.1.3 Real-world Applications')
para('The demand for low-light image enhancement has grown significantly in recent years. Smartphones now have dedicated night mode features, security systems need 24/7 operation, and autonomous vehicles must handle all lighting conditions. Our work on BioNAFNet targets these real-world needs by providing both a high-quality enhancement model (Teacher) and a real-time capable lightweight model (Student) that can run at 20+ FPS on a standard GPU.')

h2('1.2 Problem Statement')

h3('1.2.1 Challenges in Low Light Conditions')
para('Low-light image degradation is a complex problem because multiple types of degradation happen simultaneously:')
bullet('Noise Amplification: When there is less light, the camera sensor receives fewer photons. This means the signal-to-noise ratio drops dramatically, resulting in visible noise (grain) throughout the image.')
bullet('Color Distortion: Low light causes the camera white balance and color processing to fail, leading to unnatural color shifts, typically towards yellow or green tones.')
bullet('Loss of Detail: Fine textures and edges become invisible in dark regions. Information is literally lost when pixel values are very close to zero.')
bullet('Low Dynamic Range: The contrast between the brightest and darkest regions is compressed, making the image look flat and lifeless.')
bullet('Motion Blur: To compensate for low light, cameras use longer exposure times which introduces motion blur if there is any movement.')
para('The challenge is that any enhancement method must address all these problems simultaneously. Simply increasing brightness will also amplify noise. Removing noise will blur fine details. Fixing colors might introduce artifacts. This is why traditional methods often fail and why deep learning approaches are needed.')

h3('1.2.2 Limitations of Traditional Methods')
para('Traditional image enhancement methods like Histogram Equalization (HE), Contrast Limited Adaptive Histogram Equalization (CLAHE), and gamma correction have been around for decades. They work by mathematically transforming pixel values to improve brightness and contrast. However they have significant limitations:')
bullet('They do not understand image content. They apply the same transformation everywhere regardless of whether a region is sky, face, or texture.')
bullet('They amplify noise along with the signal because they cannot distinguish between information and noise.')
bullet('They often produce over-saturated or unnatural looking results, especially CLAHE which can create a "halo" effect around edges.')
bullet('They cannot recover information that is completely lost in very dark regions.')
para('Retinex-based methods like Single Scale Retinex (SSR) and Multi-Scale Retinex (MSR) are more sophisticated. They decompose the image into illumination and reflectance components based on the Retinex theory. However they still rely on hand-crafted priors and often produce artifacts at edges.')

h3('1.2.3 Need for Deep Learning Approaches')
para('Deep learning has changed the game for low-light image enhancement. Instead of designing hand-crafted rules, we can train neural networks on pairs of low-light and well-lit images. The network learns the mapping from dark to bright automatically from the data. This has several advantages:')
bullet('The network can learn context-aware processing. It can treat different image regions differently based on their content.')
bullet('It can jointly handle noise reduction, brightness enhancement, and color correction in a single forward pass.')
bullet('It can learn from large datasets and generalize to new images it has never seen before.')
bullet('Modern architectures can run in real-time on GPUs, making them practical for deployment.')
para('However most existing deep learning methods do not consider how the human visual system processes light. The human eye has evolved over millions of years to handle extreme lighting variations through specialized biological mechanisms. Our work, BioNAFNet, bridges this gap by incorporating seven biologically-inspired modules into a modern deep learning architecture.')

h2('1.3 Research Objectives')

h3('1.3.1 Primary Objectives')
para('The primary objectives of this research are:')
numbered('To design and implement BioNAFNet, a novel deep learning architecture that incorporates biological principles from the human visual system for low-light image enhancement.')
numbered('To integrate seven novel biologically-inspired modules (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL) into the NAFNet backbone.')
numbered('To achieve state-of-the-art or competitive performance on standard benchmark datasets (LOLv1, LOLv2).')
numbered('To demonstrate successful knowledge distillation from a large Teacher model (154M params) to a lightweight Student model (24M params) for real-time deployment.')

h3('1.3.2 Secondary Objectives')
numbered('To analyze the contribution of each biological module through ablation studies.')
numbered('To build a real-time desktop application for live webcam enhancement using the Student model.')
numbered('To demonstrate ensemble fusion of Teacher and Student models for maximum quality.')
numbered('To provide comprehensive evaluation using both quantitative metrics (PSNR, SSIM) and qualitative visual comparisons.')

h2('1.4 Research Questions')
para('This research aims to answer the following questions:')
numbered('RQ1: Can biologically-inspired modules improve the performance of deep learning models for low-light image enhancement compared to standard architectures?')
numbered('RQ2: How does each biological module (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL) individually contribute to the overall enhancement quality?')
numbered('RQ3: Can knowledge distillation effectively compress a large Teacher model into a lightweight Student model while maintaining competitive image quality?')
numbered('RQ4: Does ensemble fusion of Teacher and Student models produce superior results compared to either model alone?')

h2('1.5 Significance of the Study')

h3('1.5.1 Theoretical Contributions')
para('This work makes several theoretical contributions to the field:')
bullet('We propose the first deep learning architecture that systematically integrates seven different biological visual processing mechanisms into a single network.')
bullet('We introduce the Weber-Fechner Perceptual Loss (WFPL) which models the psychophysical relationship between stimulus intensity and perceived brightness.')
bullet('We demonstrate that biologically-inspired preprocessing (PRCM, SPDP) can improve feature extraction for low-light enhancement.')
bullet('We show that multi-scale adaptive processing (ARFP) inspired by retinal adaptation can handle varying brightness levels within a single image.')

h3('1.5.2 Practical Implications')
para('From a practical standpoint, our work provides:')
bullet('A real-time capable model (BioNAFNet-Lite at 20+ FPS) suitable for desktop and mobile deployment.')
bullet('A knowledge distillation pipeline that achieves 6.4x compression with minimal quality loss.')
bullet('An ensemble strategy that achieves the highest enhancement quality for offline processing applications.')
bullet('Open-source implementation that can be used by other researchers and practitioners.')

h3('1.5.3 Novel Contributions Summary')
para('We summarize our seven novel contributions:')
numbered('RLIN (Retinal Lateral Inhibition Network): Center-surround edge enhancement inspired by retinal ganglion cells.')
numbered('FAEB (Frequency-Aware Enhancement Branch): Fourier-domain amplitude and phase correction at the bottleneck.')
numbered('ARFP (Adaptive Receptive Field Pooling): Luminance-dependent multi-scale convolution (3x3, 5x5, 7x7).')
numbered('PRCM (Photoreceptor Response Curve Modeling): Learned rod and cone gamma curves with adaptive threshold.')
numbered('SPDP (Scotopic-Photopic Dual Pathway): Separate luminance and chrominance processing streams.')
numbered('TAM (Temporal Adaptation Memory): GRU-based iterative refinement across multiple passes.')
numbered('WFPL (Weber-Fechner Perceptual Loss): Perception-weighted loss emphasizing dark region accuracy.')

h2('1.6 Scope and Limitations')

h3('1.6.1 Scope of the Research')
para('This research focuses on:')
bullet('Single image low-light enhancement (not video, though TAM provides a foundation for video extension).')
bullet('Supervised learning with paired low-light and normal-light training data.')
bullet('Evaluation on three standard benchmark datasets: LOLv1, LOLv2 Real, and LOLv2 Synthetic.')
bullet('Desktop GPU deployment using NVIDIA RTX series graphics cards.')

h3('1.6.2 Limitations and Constraints')
para('We acknowledge the following limitations:')
bullet('Training was done on 128x128 patches due to GPU memory constraints. Progressive patch training could further improve results.')
bullet('The Teacher model (154M params) is too large for mobile deployment without further optimization.')
bullet('We did not train on extremely challenging datasets like SID (See-in-the-Dark) which uses RAW sensor data.')
bullet('The current evaluation is limited to PSNR and SSIM metrics. Perceptual metrics like LPIPS and FID could provide additional insights.')

h2('1.7 Project Timeline')
para('The project was completed over approximately 8 months following this timeline:')
add_table(
    ['Phase', 'Duration', 'Activities'],
    [
        ['Literature Review', 'Month 1-2', 'Studying existing LLIE methods, NAFNet architecture, biological vision systems'],
        ['Architecture Design', 'Month 2-3', 'Designing 7 biological modules, integrating into NAFNet backbone'],
        ['Teacher Training', 'Month 3-4', 'Training full BioNAFNet (154M) on LOLv1+LOLv2, 504 epochs'],
        ['Knowledge Distillation', 'Month 4-5', 'Training Student model (24M), 693 epochs with mimic loss'],
        ['Testing & Evaluation', 'Month 5-6', 'Benchmarking all model variants, ensemble experiments'],
        ['Application Development', 'Month 6-7', 'Building desktop demo with webcam support'],
        ['Documentation', 'Month 7-8', 'Writing thesis, preparing figures and tables'],
    ],
    'Project Timeline'
)

h2('1.8 Thesis Organization')
para('The rest of this thesis is organized as follows:')
bullet('Chapter 2: Literature Review — Reviews traditional and deep learning methods for LLIE, discusses biological vision concepts, and identifies research gaps.')
bullet('Chapter 3: Research Methodology — Describes the BioNAFNet architecture, all seven biological modules, loss functions, and training strategy.')
bullet('Chapter 4: System Design and Implementation — Covers system architecture, code structure, training/distillation pipeline, and deployment.')
bullet('Chapter 5: Experiments and Results — Presents quantitative and qualitative results, ablation studies, computational analysis, and SOTA comparison.')
bullet('Chapter 6: Conclusion and Future Work — Summarizes contributions and discusses future research directions.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 2: LITERATURE REVIEW
# ═══════════════════════════════════════════════════════════════════════════

h1('Chapter 2: Literature Review')

h2('2.1 Fundamentals of Image Enhancement')

h3('2.1.1 Image Formation and Degradation Models')
para('To understand low-light image enhancement, we first need to understand how images are formed. A digital camera captures light through its lens and projects it onto a sensor array. Each sensor element (pixel) converts photons into an electrical signal which is then digitized. The number of photons captured determines the pixel brightness value.')
para('In low-light conditions, fewer photons reach the sensor. This leads to a lower signal-to-noise ratio (SNR) because the electronic noise from the sensor circuitry becomes significant relative to the actual signal. Mathematically, the observed low-light image I_low can be modeled as:')
para_no_indent('I_low = I_clean × α + n')
para('where I_clean is the ideal clean image, α is the illumination attenuation factor (0 < α < 1), and n represents additive noise. The goal of LLIE is to recover I_clean from I_low.')

h3('2.1.2 Low Light Image Characteristics')
para('Low-light images exhibit several characteristic degradation patterns:')
bullet('Reduced Brightness: Overall pixel intensity values are concentrated in the lower range (0-50 out of 255).')
bullet('Compressed Dynamic Range: The difference between the brightest and darkest regions is very small.')
bullet('Signal-Dependent Noise: Noise follows a Poisson distribution in raw sensor data, becoming more severe in darker regions.')
bullet('Color Cast: Auto white balance algorithms fail in low light, producing yellowish or greenish tints.')
bullet('Detail Loss: Fine textures and small features become invisible when pixel values approach zero.')

h3('2.1.3 Quality Metrics')
para('Two primary metrics are used to evaluate LLIE methods:')
para('Peak Signal-to-Noise Ratio (PSNR): Measured in decibels (dB), PSNR quantifies the pixel-level difference between the enhanced image and the ground truth. Higher is better. PSNR = 10 × log10(MAX² / MSE), where MAX is the maximum pixel value and MSE is the mean squared error. Typical good results range from 20-30 dB.')
para('Structural Similarity Index (SSIM): Ranges from 0 to 1, with 1 being perfect. SSIM considers luminance, contrast, and structural information, making it more aligned with human perception than PSNR. Values above 0.85 generally indicate good structural preservation.')

h2('2.2 Traditional Image Enhancement Methods')

h3('2.2.1 Histogram Equalization Techniques')
para('Histogram Equalization (HE) is one of the oldest and simplest enhancement methods. It works by redistributing the pixel intensity values so that they span the full 0-255 range uniformly. While this improves contrast, it often over-enhances certain regions and produces unnatural results.')
para('Contrast Limited Adaptive Histogram Equalization (CLAHE) improves on HE by dividing the image into small tiles and applying HE locally to each tile. A clip limit parameter prevents over-amplification of noise. CLAHE produces better results than global HE but can still create blocky artifacts at tile boundaries.')

h3('2.2.2 Gamma Correction Methods')
para('Gamma correction applies a power-law transformation to pixel values: I_out = I_in^γ, where γ < 1 brightens the image and γ > 1 darkens it. Adaptive gamma correction methods estimate γ locally based on image statistics. While simple and fast, gamma correction cannot distinguish between signal and noise, so it amplifies both equally.')

h3('2.2.3 Retinex Theory and Variants')
para('The Retinex theory, proposed by Edwin Land in 1977, states that the perceived color and brightness of an object depend on the relative reflectance rather than the absolute light intensity. Based on this theory, an image can be decomposed as: I = R × L, where R is the reflectance (intrinsic scene property) and L is the illumination map.')
para('Single Scale Retinex (SSR) estimates the illumination using a Gaussian filter and recovers the reflectance through division. Multi-Scale Retinex (MSR) uses multiple Gaussian scales and combines the results. While theoretically sound, Retinex methods often produce halo artifacts around high-contrast edges and struggle with strong noise.')

h3('2.2.4 Limitations of Traditional Approaches')
para('Traditional methods share several fundamental limitations:')
bullet('They use fixed or simple adaptive rules that cannot capture the complex relationships in real images.')
bullet('They treat all image regions equally without understanding content or context.')
bullet('They amplify noise while enhancing brightness because they cannot separate signal from noise.')
bullet('They cannot recover information that is completely lost in extremely dark regions.')
bullet('They often produce artifacts: halos (Retinex), blocking (CLAHE), or over-saturation (HE).')
para('These limitations motivate the use of deep learning, which can learn complex, content-aware enhancement strategies from data.')

h2('2.3 Deep Learning Fundamentals')

h3('2.3.1 Convolutional Neural Networks (CNNs)')
para('CNNs are the backbone of modern image processing. They use learnable convolution filters to extract hierarchical features from images. Lower layers capture edges and textures while deeper layers capture semantic information like objects and scenes. Key components include: convolutional layers for feature extraction, pooling layers for spatial reduction, activation functions for non-linearity, and batch/layer normalization for stable training.')
para('For image-to-image tasks like LLIE, encoder-decoder architectures (U-Net style) are widely used. The encoder progressively reduces spatial resolution while increasing channel depth, capturing multi-scale features. The decoder upsamples back to full resolution using skip connections to preserve fine details from the encoder.')

h3('2.3.2 Generative Adversarial Networks (GANs)')
para('GANs consist of a Generator that produces enhanced images and a Discriminator that distinguishes between real and generated images. The adversarial training pushes the generator to produce increasingly realistic outputs. EnlightenGAN is a notable GAN-based LLIE method that works without paired training data.')

h3('2.3.3 Autoencoders and Variants')
para('Autoencoders learn to compress images into a latent representation and then reconstruct them. For LLIE, the decoder learns to reconstruct the well-lit version from the compressed low-light representation. Variational Autoencoders (VAEs) add probabilistic modeling which can help handle the inherent ambiguity in enhancement.')

h3('2.3.4 Transfer Learning Concepts')
para('Transfer learning uses features learned on large datasets (like ImageNet) to improve performance on smaller datasets. In LLIE, pre-trained VGG features are commonly used for perceptual loss computation, and pre-trained backbones can be fine-tuned for enhancement tasks.')

h2('2.4 Deep Learning-Based Low Light Enhancement')

h3('2.4.1 CNN-based Methods')
para('Several landmark CNN methods have been proposed for LLIE:')
bullet('LLNet (Lore et al., 2017): Used stacked sparse denoising autoencoders. One of the first deep learning approaches for LLIE.')
bullet('MBLLEN (Lv et al., 2018): Multi-Branch Low-Light Enhancement Network that processes features at multiple scales.')
bullet('KinD (Zhang et al., 2019): Kindling the Darkness. Decomposed images into reflectance and illumination using a two-branch CNN.')
bullet('MIRNet (Zamir et al., 2020): Multi-scale image restoration using feature extraction at multiple resolutions with selective kernel features.')
bullet('NAFNet (Chen et al., 2022): Nonlinear Activation Free Network. Achieved strong results using simple gate mechanisms instead of traditional activations. This is our backbone architecture.')

h3('2.4.2 GAN-based Methods')
para('GAN approaches offer the advantage of perceptually realistic outputs:')
bullet('EnlightenGAN (Jiang et al., 2021): Unsupervised enhancement using unpaired data with global-local discriminators.')
bullet('DRBN (Yang et al., 2020): Deep Recursive Band Network with progressive enhancement through recursive processing.')

h3('2.4.3 Transformer-based Methods')
para('Transformers have recently been applied to LLIE with strong results:')
bullet('Restormer (Zamir et al., 2022): Efficient transformer for image restoration using multi-DConv head transposed attention.')
bullet('Retinexformer (Cai et al., 2023): Combines Retinex theory with transformer architecture. Achieves 25.16 dB on LOLv1.')
bullet('SNR-Aware Transformer (Xu et al., 2022): Uses signal-to-noise ratio aware attention for spatially-varying enhancement.')

h3('2.4.4 Attention Mechanisms in LLIE')
para('Attention mechanisms help networks focus on important regions:')
bullet('Channel Attention: Re-weights feature channels based on their importance (used in NAFNet as Simplified Channel Attention).')
bullet('Spatial Attention: Highlights important spatial locations in the feature map.')
bullet('Self-Attention: Captures long-range dependencies between different image regions (used in transformers).')
para('Our BioNAFNet uses channel attention (SCA in NAFNet blocks) combined with our novel ARFP which provides luminance-dependent spatial attention through adaptive receptive fields.')

h2('2.5 Datasets for Low Light Enhancement')

h3('2.5.1 Synthetic Datasets')
para('Synthetic low-light datasets are created by artificially darkening well-lit images. The LOLv2 Synthetic subset uses programmatic brightness reduction to create paired data. The advantage is that ground truth is available and noise characteristics are controlled. The disadvantage is that synthetic degradation may not fully represent real-world low-light conditions.')

h3('2.5.2 Real-world Datasets')
para('Real-world datasets capture actual low-light and normal-light image pairs. The LOLv1 and LOLv2 Real subsets were captured by adjusting camera exposure times. These datasets are more realistic but harder to collect because they require carefully aligned image pairs taken at different exposures.')

h3('2.5.3 Dataset Characteristics and Challenges')
add_table(
    ['Dataset', 'Type', 'Train', 'Test', 'Resolution', 'Year'],
    [
        ['LOLv1', 'Real paired', '485', '15', '400×600', '2018'],
        ['LOLv2 Real', 'Real paired', '689', '100', 'Various', '2021'],
        ['LOLv2 Synthetic', 'Synthetic paired', '900', '100', 'Various', '2021'],
        ['SID', 'Raw sensor data', '5094', '598', 'Various', '2018'],
        ['MIT-Adobe FiveK', 'Expert retouched', '5000', '—', 'Various', '2011'],
    ],
    'Benchmark Datasets for Low-Light Image Enhancement'
)
para('We use LOLv1, LOLv2 Real, and LOLv2 Synthetic for our evaluation, providing 2074 training images and 215 test images in total. This combination covers both real-world and synthetic degradation scenarios.')

h2('2.6 Comparative Analysis of Existing Methods')

h3('2.6.1 Performance Comparison Table')
add_table(
    ['Method', 'Year', 'Type', 'Params', 'LOLv1 PSNR', 'LOLv1 SSIM'],
    [
        ['RetinexNet', '2018', 'CNN', '0.8M', '16.77', '0.560'],
        ['KinD', '2019', 'CNN', '8.2M', '20.87', '0.800'],
        ['MIRNet', '2020', 'CNN', '31.8M', '24.14', '0.830'],
        ['EnlightenGAN', '2021', 'GAN', '8.6M', '17.48', '0.650'],
        ['SNR-Aware', '2022', 'Transformer', '39.1M', '24.61', '0.842'],
        ['NAFNet', '2022', 'CNN', '67.9M', '~23.0', '~0.830'],
        ['Retinexformer', '2023', 'Transformer', '1.6M', '25.16', '0.845'],
        ['BioNAFNet-Lite (Ours)', '2026', 'Bio-CNN', '24M', '25.23', '0.853'],
        ['BioNAFNet-Ensemble (Ours)', '2026', 'Bio-CNN', '178M', '25.27', '0.864'],
    ],
    'Performance Comparison with State-of-the-Art Methods on LOLv1'
)

h3('2.6.2 Identified Research Gaps')
para('From the literature review, we identify the following research gaps:')
numbered('No existing LLIE method systematically incorporates biological visual processing mechanisms. While methods like Retinex use the theory of illumination decomposition, they do not model actual photoreceptor behavior, lateral inhibition, or temporal adaptation.')
numbered('Frequency-domain enhancement is underexplored. Most methods operate entirely in the spatial domain, missing the opportunity to correct degraded frequency components directly.')
numbered('Fixed receptive fields are used regardless of local brightness. The human eye adapts its spatial resolution based on lighting, using larger receptive fields in darkness for better signal integration.')
numbered('Loss functions do not account for the psychophysical relationship between brightness and perception sensitivity. The Weber-Fechner law states that sensitivity is highest in dark regions, but no existing loss function models this.')
numbered('There is a quality-speed tradeoff gap. Large models (50+ M params) achieve good quality but are too slow for real-time use. Lightweight models are fast but sacrifice quality. Knowledge distillation can bridge this gap.')

h3('2.6.3 Motivation for Proposed Work')
para('Our proposed BioNAFNet directly addresses each of the identified gaps. We integrate seven biological modules into the NAFNet backbone: RLIN addresses gap 1 (lateral inhibition), FAEB addresses gap 2 (frequency enhancement), ARFP addresses gap 3 (adaptive receptive fields), PRCM and SPDP address gap 1 (photoreceptor modeling), TAM addresses gap 1 (temporal adaptation), and WFPL addresses gap 4 (perception-weighted loss). Knowledge distillation addresses gap 5 (quality-speed tradeoff).')

h2('2.7 Summary')
para('This chapter reviewed the fundamentals of image enhancement, traditional methods and their limitations, deep learning approaches for LLIE, available datasets, and existing state-of-the-art methods. We identified five key research gaps that our proposed BioNAFNet architecture addresses through seven novel biologically-inspired modules and a knowledge distillation pipeline. The next chapter presents our detailed methodology.')

doc.add_page_break()

# Save progress
doc.save(OUTPUT)
print('Chapters 1-2 written. Saving progress...')
print(f'Output: {OUTPUT}')
