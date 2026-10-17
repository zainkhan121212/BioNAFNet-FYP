"""
BioNAFNet FYP Final Report — Part 1: Front Matter + Chapters 1-3
Using LGU SE Department 'Final Report Template (6) (1)' format.
"""
import os
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

FIGS = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
OUT = r"F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_FYP_Final_Report.docx"

doc = Document()
for s in doc.sections:
    s.top_margin=Cm(2.54); s.bottom_margin=Cm(2.54)
    s.left_margin=Cm(3.18); s.right_margin=Cm(2.54)

style=doc.styles['Normal']
style.font.name='Times New Roman'; style.font.size=Pt(12)
style.paragraph_format.line_spacing=1.5; style.paragraph_format.space_after=Pt(6)

FN=[0]; TN=[0]

def h1(t): p=doc.add_heading(t,1); p.alignment=WD_ALIGN_PARAGRAPH.LEFT
def h2(t): doc.add_heading(t,2)
def h3(t): doc.add_heading(t,3)
def para(t): p=doc.add_paragraph(t); p.paragraph_format.first_line_indent=Cm(1.27); return p
def pn(t): return doc.add_paragraph(t)
def bl(t): doc.add_paragraph(t, style='List Bullet')
def nl(t): doc.add_paragraph(t, style='List Number')
def center(t,sz=12,bold=False):
    p=doc.add_paragraph(); r=p.add_run(t); r.font.size=Pt(sz); r.bold=bold
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER; return p
def fig(fn,cap,w=5.5):
    FN[0]+=1; path=os.path.join(FIGS,fn)
    if os.path.exists(path):
        doc.add_picture(path,width=Inches(w)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
    c=doc.add_paragraph(f'Figure {FN[0]}: {cap}')
    c.alignment=WD_ALIGN_PARAGRAPH.CENTER; c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
def tbl(headers,rows,cap=None):
    TN[0]+=1
    if cap:
        c=doc.add_paragraph(f'Table {TN[0]}: {cap}'); c.alignment=WD_ALIGN_PARAGRAPH.CENTER
        c.runs[0].italic=True; c.runs[0].font.size=Pt(10)
    t=doc.add_table(rows=1+len(rows),cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    try: t.style='Table Grid'
    except: pass
    for j,h in enumerate(headers):
        cell=t.rows[0].cells[j]; cell.text=h
        for r in cell.paragraphs[0].runs: r.bold=True; r.font.size=Pt(10)
    for i,row in enumerate(rows):
        for j,val in enumerate(row):
            cell=t.rows[i+1].cells[j]; cell.text=str(val)
            for r in cell.paragraphs[0].runs: r.font.size=Pt(10)
    doc.add_paragraph('')

def photo_note(desc):
    """Mark where user should insert a picture"""
    p=doc.add_paragraph()
    r=p.add_run(f'[INSERT IMAGE HERE: {desc}]')
    r.bold=True; r.font.color.rgb=RGBColor(0xCC,0x00,0x00); r.font.size=Pt(11)
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER

# ═══════════════════════════════════════════════════════════════════════════
# TITLE PAGE
# ═══════════════════════════════════════════════════════════════════════════
for _ in range(3): doc.add_paragraph('')
center('Project Report', 14, True)
doc.add_paragraph('')
center('BioNAFNet: Biologically-Inspired Low-Light Image Enhancement\nUsing Deep Learning with Knowledge Distillation', 18, True)
doc.add_paragraph('')
center('_______________________________', 12)
doc.add_paragraph('')
center('Submitted by', 12)
center('[Student Name 1] (BSSE-[Roll#]-[Section])', 12)
center('[Student Name 2] (BSSE-[Roll#]-[Section])', 12)
doc.add_paragraph('')
center('Session', 12); center('[Write Session here]', 12)
doc.add_paragraph('')
center('Supervised by', 12); center('[Teacher Name]', 12)
doc.add_paragraph('')
center('Department of Software Engineering', 12)
center('Lahore Garrison University', 12)
center('Lahore', 12)
doc.add_page_break()

# Approval page
center('BioNAFNet: Biologically-Inspired Low-Light Image Enhancement\nUsing Deep Learning with Knowledge Distillation', 14, True)
doc.add_paragraph('')
center('A project submitted to the', 12)
center('Department of Software Engineering', 12)
center('In', 12)
center("Partial Fulfillment of the Requirements for the", 12)
center("Bachelor's Degree in Software Engineering", 12)
doc.add_paragraph('')
center('By', 12)
center('[Student Name 1]', 12); center('[Student Name 2]', 12)
doc.add_paragraph('')
center('Supervisor', 12)
center('[Teacher Name]', 12)
center('_______________________', 12)
center('Designation', 10)
center('Department of Software Engineering', 12)
doc.add_paragraph('')
center('Chairperson', 12)
center('Dr. Omer Irshad', 12)
center('_______________________', 12)
center('Head of Department', 10)
center('Department of Software Engineering', 12)
doc.add_page_break()

# Copyrights
center('COPYRIGHTS', 14, True)
doc.add_paragraph('')
para('All rights reserved. No part of this project report may be reproduced, stored in a retrieval system, or transmitted in any form or by any means, electronic, mechanical, photocopying, recording, or otherwise, without the prior written permission of the authors.')
doc.add_paragraph('')
pn('[Student Name 1] ____________')
pn('[Student Name 2] ____________')
doc.add_page_break()

# Declaration
center('DECLARATION', 14, True)
doc.add_paragraph('')
para('We hereby declare that this project report titled "BioNAFNet: Biologically-Inspired Low-Light Image Enhancement Using Deep Learning with Knowledge Distillation" is our original work and has not been submitted for any other degree or professional qualification. All sources of information used in this work have been properly cited and acknowledged.')
doc.add_paragraph('')
pn('[Student Name 1] ________________')
pn('[Student Name 2] ________________')
doc.add_page_break()

# Acknowledgements
center('ACKNOWLEDGEMENTS', 14, True)
doc.add_paragraph('')
para('We would like to express our sincere gratitude to our supervisor [Teacher Name] for their continuous guidance, support, and encouragement throughout this project. Their expertise in deep learning and computer vision helped us navigate the challenges of designing and implementing BioNAFNet.')
para('We are also grateful to Dr. Omer Irshad, Head of Department of Software Engineering, Lahore Garrison University, for providing the academic environment and resources that made this work possible.')
para('We thank the creators of the LOL datasets (Wei et al., 2018; Yang et al., 2021) for making their data publicly available for research purposes. We also acknowledge the authors of NAFNet (Chen et al., 2022) whose architecture served as our backbone.')
para('Finally, we thank our families and friends for their patience and moral support during the long hours of training and experimentation.')
doc.add_page_break()

# Dedication
center('DEDICATION', 14, True)
doc.add_paragraph('')
center('Dedicated to our families,\nwho supported us throughout this journey,\nand to the pursuit of making machines see in the dark\nas well as the human eye.', 14)
doc.add_page_break()

# TOC
center('Table of Contents', 16, True)
doc.add_paragraph('')
para('[Generate automatically in Word: References tab → Table of Contents → Automatic Table 1]')
para('Right-click the table of contents after generating and select "Update Field" → "Update entire table" to refresh page numbers.')
doc.add_page_break()

# List of Tables
center('List of Tables', 16, True)
doc.add_paragraph('')
para('[Generate in Word: References tab → Insert Table of Figures → Select "Table" from the label dropdown]')
doc.add_page_break()

# List of Figures
center('List of Figures', 16, True)
doc.add_paragraph('')
para('[Generate in Word: References tab → Insert Table of Figures → Select "Figure" from the label dropdown]')
doc.add_page_break()

# List of Abbreviations
center('List of Abbreviations', 16, True)
doc.add_paragraph('')
tbl(['Abbreviation', 'Full Form'],
    [['LLIE', 'Low-Light Image Enhancement'],
     ['CNN', 'Convolutional Neural Network'],
     ['GAN', 'Generative Adversarial Network'],
     ['NAFNet', 'Nonlinear Activation Free Network'],
     ['BioNAFNet', 'Biologically-Inspired NAFNet'],
     ['RLIN', 'Retinal Lateral Inhibition Network'],
     ['FAEB', 'Frequency-Aware Enhancement Branch'],
     ['ARFP', 'Adaptive Receptive Field Pooling'],
     ['PRCM', 'Photoreceptor Response Curve Modeling'],
     ['SPDP', 'Scotopic-Photopic Dual Pathway'],
     ['TAM', 'Temporal Adaptation Memory'],
     ['WFPL', 'Weber-Fechner Perceptual Loss'],
     ['PSNR', 'Peak Signal-to-Noise Ratio'],
     ['SSIM', 'Structural Similarity Index Measure'],
     ['EMA', 'Exponential Moving Average'],
     ['AMP', 'Automatic Mixed Precision'],
     ['GPU', 'Graphics Processing Unit'],
     ['FPS', 'Frames Per Second'],
     ['FFT', 'Fast Fourier Transform'],
     ['GRU', 'Gated Recurrent Unit'],
     ['SCA', 'Simplified Channel Attention'],
     ['VGG', 'Visual Geometry Group (Network)'],
     ['LOL', 'Low-Light (Dataset)'],
     ['UNet', 'U-shaped Network Architecture'],
     ['RGB', 'Red Green Blue (Color Space)'],
     ['YUV', 'Luminance-Chrominance Color Space'],
     ['DL', 'Deep Learning'],
     ['CLAHE', 'Contrast Limited Adaptive Histogram Equalization'],
     ['KD', 'Knowledge Distillation'],
     ['LR', 'Learning Rate']],
    'List of Abbreviations')
doc.add_page_break()

# Abstract
center('Abstract', 16, True)
doc.add_paragraph('')
para('Low-light image enhancement is a critical challenge in computer vision that affects applications ranging from surveillance systems to mobile photography. Images captured in poor lighting conditions suffer from noise, color distortion, low contrast, and loss of fine details. While deep learning methods have shown impressive results, none of them systematically incorporate the biological mechanisms that allow the human visual system to adapt to darkness.')
para('This project presents BioNAFNet, a novel deep learning architecture that integrates seven biologically-inspired modules into the NAFNet backbone for low-light image enhancement. These modules are: Retinal Lateral Inhibition Network (RLIN) for edge enhancement, Frequency-Aware Enhancement Branch (FAEB) for spectral recovery, Adaptive Receptive Field Pooling (ARFP) for luminance-dependent spatial processing, Photoreceptor Response Curve Modeling (PRCM) for simulating rod and cone responses, Scotopic-Photopic Dual Pathway (SPDP) for separate luminance and color processing, Temporal Adaptation Memory (TAM) for iterative refinement, and Weber-Fechner Perceptual Loss (WFPL) for perception-weighted training.')
para('We train a full Teacher model (154M parameters) and successfully compress it to a lightweight Student model called BioNAFNet-Lite (24M parameters) through knowledge distillation, achieving 6.4x compression and 4x speedup. The Student model achieves 25.23 dB PSNR on LOLv1, actually surpassing the Teacher (24.94 dB). An ensemble fusion of both models achieves the highest results: 29.29 dB on LOLv2 Real. The Student model runs at 20+ FPS, enabling real-time deployment for desktop and webcam applications.')
para('Keywords: Low-light image enhancement, deep learning, biologically-inspired, NAFNet, knowledge distillation, ensemble fusion, PSNR, SSIM')
doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 1: INTRODUCTION
# ═══════════════════════════════════════════════════════════════════════════
h1('Chapter 1')
h2('Introduction')

h3('1.1 Background')
para('Image enhancement is one of the oldest and most fundamental tasks in computer vision. The idea is straightforward: take a bad image and make it look better. But when it comes to low-light images specifically, things get much more complicated than just "making it brighter." Low-light images have multiple problems happening at the same time: they are dark, noisy, color-shifted, and lacking in detail. Fixing one problem often makes another worse.')
para('Traditional methods like Histogram Equalization and gamma correction have been used for decades but they have serious limitations. They apply the same mathematical transformation everywhere in the image without understanding what is actually in the scene. So when they boost brightness, they also boost noise. When they fix contrast, they sometimes create unnatural artifacts. These methods simply cannot handle the complexity of real low-light degradation.')
para('Deep learning changed everything. Instead of hand-coding rules, we can now train neural networks on thousands of paired examples (dark image → well-lit image) and the network learns the mapping automatically. Networks like RetinexNet, KinD, MIRNet, and Retinexformer have pushed the boundaries of what is possible. But here is the interesting thing: none of them look at how the human eye actually handles the same problem.')

h3('1.2 Motivation')
para('The human visual system is remarkable. Our eyes can adapt to lighting conditions spanning over 10 orders of magnitude, from starlight to bright sunshine. This adaptation happens through specific biological mechanisms: rod and cone photoreceptors with different sensitivity curves, lateral inhibition between retinal neurons that enhances edges, separate processing pathways for brightness and color, and temporal adaptation that gradually adjusts sensitivity over time.')
para('These mechanisms have been refined by millions of years of evolution. It makes sense to ask: can we incorporate these biological principles into our deep learning models to make them better at low-light enhancement? That is exactly what BioNAFNet does. We take the NAFNet architecture, which is already a strong backbone for image restoration, and we enhance it with seven modules that are each inspired by a specific biological mechanism of the human visual system.')

h3('1.3 Research Objectives')
para('The primary objectives of this project are:')
nl('To design BioNAFNet, a novel architecture with seven biologically-inspired modules (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL) integrated into the NAFNet backbone.')
nl('To train the full Teacher model (154M parameters) on LOLv1 and LOLv2 datasets and achieve competitive performance with state-of-the-art methods.')
nl('To compress the Teacher to a lightweight Student model (24M parameters) via knowledge distillation for real-time deployment at 20+ FPS.')
nl('To demonstrate ensemble fusion of Teacher and Student for maximum enhancement quality.')
nl('To evaluate all model variants on LOLv1, LOLv2 Real, and LOLv2 Synthetic test sets using PSNR and SSIM metrics.')
nl('To build a practical desktop application supporting real-time webcam enhancement.')

h3('1.4 Scope of the Project')
para('This project covers single-image low-light enhancement using supervised learning with paired data. We use three benchmark datasets: LOLv1 (485 training / 15 test pairs), LOLv2 Real (689/100), and LOLv2 Synthetic (900/100). Training and testing are done on a desktop GPU. The project includes model design, training, distillation, ensemble fusion, benchmarking, and application development.')

h3('1.5 Novel Contributions')
para('We make the following novel contributions:')
nl('RLIN (Retinal Lateral Inhibition Network): Center-surround edge enhancement inspired by retinal ganglion cell receptive fields.')
nl('FAEB (Frequency-Aware Enhancement Branch): Fourier-domain amplitude and phase correction at the network bottleneck.')
nl('ARFP (Adaptive Receptive Field Pooling): Multi-scale convolution (3x3, 5x5, 7x7) with luminance-dependent gating.')
nl('PRCM (Photoreceptor Response Curve Modeling): Learned rod and cone gamma curves with adaptive scotopic-photopic threshold.')
nl('SPDP (Scotopic-Photopic Dual Pathway): Separate luminance and chrominance processing streams inspired by magnocellular and parvocellular pathways.')
nl('TAM (Temporal Adaptation Memory): GRU-based iterative refinement across multiple forward passes, modeling dark adaptation.')
nl('WFPL (Weber-Fechner Perceptual Loss): Perception-weighted loss emphasizing dark region accuracy based on psychophysical principles.')
nl('Knowledge distillation pipeline achieving 6.4x compression with minimal quality loss.')

h3('1.6 Significance')
para('From a theoretical perspective, BioNAFNet is the first architecture to systematically integrate multiple biological visual processing mechanisms into a single deep learning model for LLIE. Each module has a clear biological analog, making the architecture interpretable and scientifically grounded.')
para('From a practical perspective, the Student model (BioNAFNet-Lite) at 24M parameters and 20+ FPS enables real-time low-light enhancement on standard desktop GPUs. The ensemble fusion strategy provides the highest quality for offline processing. This makes BioNAFNet suitable for both interactive demo applications and batch processing of large image collections.')

h3('1.7 Report Organization')
para('This report is organized as follows:')
bl('Chapter 2 defines the problem of low-light image enhancement and explains the challenges.')
bl('Chapter 3 covers the software requirements, literature survey, and research gaps.')
bl('Chapter 4 describes our methodology including all seven biological modules, loss functions, and training strategy.')
bl('Chapter 5 presents the system architecture, detailed design, and UML diagrams.')
bl('Chapter 6 covers implementation details and testing procedures.')
bl('Chapter 7 presents all experimental results, benchmark comparisons, and discussion.')
bl('Chapter 8 provides conclusions and future work directions.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 2: PROBLEM DEFINITION
# ═══════════════════════════════════════════════════════════════════════════
h1('Chapter 2')
h2('Problem Definition')

h3('2.1 Problem Overview')
para('Low-light image enhancement is the task of recovering a high-quality, well-lit image from a degraded input captured in poor lighting conditions. The degradation is complex because multiple problems occur simultaneously and interact with each other.')

h3('2.2 Types of Low-Light Degradation')
para('Images captured in low-light conditions suffer from the following degradations:')

pn('2.2.1 Noise Amplification')
para('When the camera sensor receives very few photons in dark conditions, the electronic noise from the sensor circuitry becomes significant relative to the actual signal. This noise appears as random grain throughout the image and is especially severe in the darkest regions. Any attempt to brighten the image also amplifies this noise.')

pn('2.2.2 Color Distortion')
para('Camera auto white balance algorithms are designed for normal lighting. In low light, they often fail and produce images with unnatural color casts, typically yellowish or greenish tints. The chrominance information becomes unreliable when the luminance signal is too weak.')

pn('2.2.3 Loss of Detail')
para('Fine textures, edges, and small features become invisible when pixel intensity values are very close to zero. This is not just a display problem. The information is genuinely lost because the sensor could not capture enough photons to differentiate between adjacent structures.')

pn('2.2.4 Low Dynamic Range')
para('The contrast between bright and dark regions is compressed. An image that should show a wide range of brightness levels instead looks flat and lifeless, with everything clustered in the low-intensity range.')

h3('2.3 Limitations of Existing Solutions')

pn('2.3.1 Traditional Methods')
para('Histogram Equalization (HE) redistributes pixel intensities across the full range. It improves contrast but amplifies noise and often produces over-saturated results. CLAHE applies HE locally but creates blocky artifacts. Gamma correction uses a power-law transformation but cannot distinguish signal from noise. Retinex methods decompose images into reflectance and illumination but produce halo artifacts around edges.')

pn('2.3.2 Deep Learning Methods')
para('Existing deep learning approaches like RetinexNet, KinD, MIRNet, and Retinexformer achieve much better results. However they share a common limitation: none of them incorporate the biological mechanisms that allow the human eye to handle extreme lighting variations. They treat low-light enhancement as a pure signal processing problem rather than drawing on the principles of biological vision.')

pn('2.3.3 The Quality-Speed Gap')
para('Large models with many parameters (50M+) achieve good quality but are too slow for real-time applications. Lightweight models are fast but sacrifice quality. There is a gap between what is achievable in terms of quality and what is practical for deployment. Knowledge distillation can help bridge this gap but has not been widely applied to LLIE methods.')

h3('2.4 Problem Statement')
para('Given the limitations described above, the problem can be formally stated as:')
para('"How can we design a deep learning architecture for low-light image enhancement that (a) incorporates biological visual processing principles to improve enhancement quality, (b) achieves competitive performance with state-of-the-art methods, and (c) can be compressed into a lightweight model suitable for real-time deployment?"')

h3('2.5 Research Questions')
nl('RQ1: Can biologically-inspired modules improve the performance of deep learning models for low-light image enhancement?')
nl('RQ2: What is the individual contribution of each biological module to the overall enhancement quality?')
nl('RQ3: Can knowledge distillation effectively compress a large Teacher model into a real-time capable Student model?')
nl('RQ4: Does ensemble fusion of Teacher and Student produce results superior to either model alone?')

photo_note('Figure showing side-by-side comparison: (a) Low-light input with arrows pointing to noise, color distortion, detail loss. (b) BioNAFNet enhanced output. (c) Ground truth. Use one LOLv1 test image. Screenshot from results_ensemble/ensemble_avg/LOLv1/ folder.')

doc.add_page_break()

# ═══════════════════════════════════════════════════════════════════════════
# CHAPTER 3: SRS + LITERATURE SURVEY
# ═══════════════════════════════════════════════════════════════════════════
h1('Chapter 3')
h2('Software Requirement Specification')

h3('3.1 Literature Survey')

pn('3.1.1 Traditional Image Enhancement Methods')
para('Histogram Equalization (HE) was one of the earliest enhancement techniques, proposed in the 1970s. It maps the cumulative distribution function of pixel intensities to a uniform distribution, effectively spreading intensity values across the full range [Gonzalez and Woods, 2002]. While effective for simple contrast enhancement, HE tends to wash out regions and amplify noise in low-light scenarios.')
para('Contrast Limited Adaptive Histogram Equalization (CLAHE), introduced by Zuiderveld in 1994, improved upon HE by dividing the image into small tiles and applying local histogram equalization with a clip limit to prevent over-amplification. CLAHE is widely used in medical imaging but still produces blocking artifacts at tile boundaries and cannot handle severe low-light conditions effectively.')
para('Gamma correction applies the transformation I_out = I_in^gamma where gamma < 1 brightens the image. Adaptive gamma methods estimate gamma locally but still cannot separate signal from noise [Huang et al., 2013].')
para('The Retinex theory, proposed by Edwin Land in 1977, states that perceived color depends on relative reflectance rather than absolute light intensity. Image formation is modeled as I = R x L where R is reflectance and L is illumination. Single Scale Retinex (SSR) and Multi-Scale Retinex (MSR) estimate illumination using Gaussian filters and recover reflectance through division [Jobson et al., 1997]. While theoretically sound, Retinex methods produce halo artifacts and struggle with strong noise.')

tbl(['Method', 'Year', 'Approach', 'Pros', 'Cons'],
    [['HE', '1970s', 'Global histogram redistribution', 'Simple, fast', 'Over-enhancement, noise amplification'],
     ['CLAHE', '1994', 'Local adaptive HE', 'Better local contrast', 'Blocking artifacts, limited in dark'],
     ['Gamma Correction', 'Various', 'Power-law transform', 'Simple, adjustable', 'Cannot denoise, fixed rule'],
     ['SSR/MSR', '1997', 'Retinex decomposition', 'Theoretically grounded', 'Halo artifacts, noise sensitive'],
     ['LIME', '2017', 'Illumination estimation', 'Structure preserving', 'Over-smoothing, slow']],
    'Summary of Traditional Enhancement Methods')

pn('3.1.2 CNN-Based Enhancement Methods')
para('LLNet (Lore et al., 2017) was one of the first deep learning approaches for LLIE, using stacked sparse denoising autoencoders. It showed that neural networks can learn enhancement from data, but its quality was limited by the simple architecture.')
para('MBLLEN (Lv et al., 2018) used a Multi-Branch architecture that processes features at multiple scales through separate branches. This multi-scale approach helped capture both local and global features but increased computational cost.')
para('KinD (Zhang et al., 2019) decomposed images into reflectance and illumination using a two-branch CNN inspired by Retinex theory. It achieved significant improvements over earlier methods with 20.87 dB PSNR on LOLv1.')
para('MIRNet (Zamir et al., 2020) introduced multi-scale residual blocks with selective kernel features for image restoration. It achieved 24.14 dB on LOLv1 and set a new standard for CNN-based methods.')
para('NAFNet (Chen et al., 2022) simplified image restoration architectures by replacing activation functions with a SimpleGate mechanism (splitting features and multiplying). This Nonlinear Activation Free approach achieved strong results with clean, efficient design. NAFNet is our backbone architecture.')

pn('3.1.3 Transformer-Based Enhancement Methods')
para('Restormer (Zamir et al., 2022) applied efficient transformers to image restoration using multi-DConv head transposed attention, achieving state-of-the-art results across multiple restoration tasks.')
para('SNR-Aware Transformer (Xu et al., 2022) introduced signal-to-noise ratio aware attention that adapts processing based on local noise levels. It achieved 24.61 dB on LOLv1.')
para('Retinexformer (Cai et al., 2023) combined Retinex decomposition with transformer architecture, achieving 25.16 dB on LOLv1. It is currently one of the top-performing methods on LOL benchmarks.')

pn('3.1.4 GAN-Based Enhancement Methods')
para('EnlightenGAN (Jiang et al., 2021) was notable for using unpaired training data through adversarial learning. While it eliminated the need for paired data, its results (17.48 dB) were lower than supervised methods.')

pn('3.1.5 Knowledge Distillation in Image Processing')
para('Knowledge Distillation (KD), introduced by Hinton et al. (2015), compresses a large Teacher model into a smaller Student by training the Student to mimic the Teacher outputs. KD has been successfully applied in classification and detection tasks but is underexplored in LLIE. Our work demonstrates that KD can effectively compress a LLIE model by 6.4x while maintaining competitive quality.')

tbl(['Method', 'Year', 'Type', 'Params', 'LOLv1 PSNR', 'LOLv1 SSIM'],
    [['LLNet', '2017', 'Autoencoder', '~1M', '~17.0', '~0.600'],
     ['RetinexNet', '2018', 'CNN', '0.8M', '16.77', '0.560'],
     ['MBLLEN', '2018', 'Multi-Branch', '~0.5M', '17.90', '0.715'],
     ['KinD', '2019', 'Retinex-CNN', '8.2M', '20.87', '0.800'],
     ['MIRNet', '2020', 'Multi-Scale', '31.8M', '24.14', '0.830'],
     ['EnlightenGAN', '2021', 'GAN', '8.6M', '17.48', '0.650'],
     ['SNR-Aware', '2022', 'Transformer', '39.1M', '24.61', '0.842'],
     ['NAFNet', '2022', 'CNN (SG)', '67.9M', '~23.0', '~0.830'],
     ['Retinexformer', '2023', 'Retinex-Trans', '1.6M', '25.16', '0.845'],
     ['BioNAFNet-Lite (Ours)', '2026', 'Bio-CNN', '24M', '25.23', '0.853'],
     ['BioNAFNet-Ens (Ours)', '2026', 'Bio-CNN', '178M', '25.27', '0.864']],
    'Performance Comparison with State-of-the-Art Methods on LOLv1 Dataset')

h3('3.2 Research Gaps')
para('From the literature survey, we identify the following gaps:')
nl('Gap 1 — No Biological Integration: No existing LLIE method systematically incorporates biological visual processing mechanisms like photoreceptor modeling, lateral inhibition, or temporal adaptation.')
nl('Gap 2 — Limited Frequency Processing: Most methods operate entirely in the spatial domain, missing the opportunity to correct degraded frequency components through FFT-based processing.')
nl('Gap 3 — Fixed Receptive Fields: All methods use the same receptive field size regardless of local brightness, whereas the human eye adapts spatial resolution based on light levels.')
nl('Gap 4 — Perception-Unaware Losses: Loss functions treat all pixel errors equally, ignoring the Weber-Fechner law that sensitivity is highest in dark regions.')
nl('Gap 5 — Quality-Speed Gap: No existing work applies knowledge distillation to bridge the gap between high-quality large models and real-time lightweight models in LLIE.')

h3('3.3 Datasets')
tbl(['Dataset', 'Type', 'Train Pairs', 'Test Pairs', 'Resolution', 'Year', 'Source'],
    [['LOLv1', 'Real captured', '485', '15', '400x600', '2018', 'Wei et al.'],
     ['LOLv2 Real', 'Real captured', '689', '100', 'Various', '2021', 'Yang et al.'],
     ['LOLv2 Synthetic', 'Synthetic', '900', '100', 'Various', '2021', 'Yang et al.'],
     ['SID', 'RAW sensor', '5094', '598', 'Various', '2018', 'Chen et al.'],
     ['LSRW', 'Real-world', '5650', '—', 'Various', '2022', 'Hai et al.']],
    'Benchmark Datasets for Low-Light Image Enhancement')
para('We use LOLv1, LOLv2 Real, and LOLv2 Synthetic for our experiments, providing 2074 training pairs and 215 test images in total. This combination covers both real-world and synthetic degradation scenarios, ensuring thorough evaluation.')

h3('3.4 Functional Requirements')
tbl(['ID', 'Requirement', 'Priority', 'Status'],
    [['FR-01', 'Load low-light images (JPEG, PNG)', 'High', 'Implemented'],
     ['FR-02', 'Enhance image using BioNAFNet model', 'High', 'Implemented'],
     ['FR-03', 'Support batch processing of datasets', 'High', 'Implemented'],
     ['FR-04', 'Calculate PSNR and SSIM metrics', 'High', 'Implemented'],
     ['FR-05', 'Save enhanced images to disk', 'High', 'Implemented'],
     ['FR-06', 'Support multiple model variants (Teacher, Student, Ensemble)', 'High', 'Implemented'],
     ['FR-07', 'Real-time webcam enhancement preview', 'Medium', 'Implemented'],
     ['FR-08', 'Side-by-side comparison display', 'Medium', 'Implemented'],
     ['FR-09', 'Model switching during inference', 'Medium', 'Implemented'],
     ['FR-10', 'Performance logging and reporting', 'Medium', 'Implemented']],
    'Functional Requirements')

h3('3.5 Non-Functional Requirements')
tbl(['ID', 'Requirement', 'Metric', 'Status'],
    [['NFR-01', 'Student model inference < 50ms per image', '48.9 ms', 'Met'],
     ['NFR-02', 'Student model FPS > 15 for webcam', '20.5 FPS', 'Met'],
     ['NFR-03', 'PSNR > 24.0 dB on LOLv1', '25.23 dB', 'Met'],
     ['NFR-04', 'SSIM > 0.84 on LOLv1', '0.853', 'Met'],
     ['NFR-05', 'Model size < 100 MB for Student', '91 MB', 'Met'],
     ['NFR-06', 'GPU VRAM < 4 GB for inference', '~1 GB', 'Met'],
     ['NFR-07', 'Reproducible results (seeded)', 'Seed=42', 'Met']],
    'Non-Functional Requirements')

h3('3.6 Hardware and Software Requirements')
tbl(['Component', 'Specification'],
    [['Operating System', 'Windows 10/11 with CUDA support'],
     ['GPU', 'NVIDIA RTX series (8+ GB VRAM recommended)'],
     ['RAM', '16 GB minimum'],
     ['Storage', '50 GB (for datasets + checkpoints)'],
     ['Python', '3.8 or higher'],
     ['PyTorch', '2.0+ with CUDA'],
     ['CUDA', '11.8 or 12.x'],
     ['Additional Libraries', 'torchvision, numpy, PIL, scikit-image, matplotlib']],
    'Hardware and Software Requirements')

h3('3.7 Evaluation Metrics')
para('We use two standard metrics for quantitative evaluation:')
para('Peak Signal-to-Noise Ratio (PSNR): Measured in decibels (dB). PSNR = 10 x log10(MAX^2 / MSE) where MAX is 1.0 for normalized images. Higher values indicate better pixel-level accuracy. Good LLIE results typically range from 20-30 dB.')
para('Structural Similarity Index (SSIM): Ranges from 0 to 1. Compares luminance, contrast, and structure between predicted and ground truth images. More aligned with human perception than PSNR. Values above 0.85 indicate good structural preservation.')

doc.add_page_break()
doc.save(OUT)
print('Part 1 done: Front matter + Chapters 1-3')
print('Tables:', TN[0], '| Figures:', FN[0])
