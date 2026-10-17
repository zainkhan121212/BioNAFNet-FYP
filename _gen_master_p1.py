"""
Master FYP Report Generator — Part 1: Front Matter + Chapters 1-2
Merged from LLIE_FYP_Final_Report.docx and BioNAFNet_FYP_Final_Report_v2.docx
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _merge_helpers import *


def build_front_matter(doc):
    """Title page, copyrights, declaration, acknowledgements, dedication, ToC stubs."""

    # ── Title Page 1 ──
    add_center(doc, "Project Report", bold=True, size=Pt(16))
    add_center(doc, "")
    add_center(doc, "BioNAFNet: Biologically-Inspired Low-Light Image Enhancement", bold=True, size=Pt(18))
    add_center(doc, "with Knowledge Distillation and Desktop Application", bold=True, size=Pt(16))
    add_center(doc, "")
    add_center(doc, "_______________________________")
    add_center(doc, "")
    add_center(doc, "Submitted by")
    add_center(doc, "[Student Name 1] (BSSE-[Roll#]-[Section])")
    add_center(doc, "[Student Name 2] (BSSE-[Roll#]-[Section])")
    add_center(doc, "")
    add_center(doc, "Session")
    add_center(doc, "[Write Session here]")
    add_center(doc, "")
    add_center(doc, "Supervised by")
    add_center(doc, "[Teacher Name]")
    add_center(doc, "")
    add_center(doc, "Department of Software Engineering")
    add_center(doc, "Lahore Garrison University")
    add_center(doc, "Lahore")
    add_page_break(doc)

    # ── Title Page 2 (formal) ──
    add_center(doc, "BioNAFNet: Biologically-Inspired Low-Light Image Enhancement", bold=True, size=Pt(16))
    add_center(doc, "with Knowledge Distillation and Desktop Application", bold=True, size=Pt(14))
    add_center(doc, "")
    add_center(doc, "A project submitted to the")
    add_center(doc, "Department of Software Engineering")
    add_center(doc, "In")
    add_center(doc, "Partial Fulfillment of the Requirements for the")
    add_center(doc, "Bachelor\u2019s Degree in Software Engineering")
    add_center(doc, "")
    add_center(doc, "By")
    add_center(doc, "[Student Name 1]")
    add_center(doc, "[Student Name 2]")
    add_center(doc, "")
    add_center(doc, "Supervisor")
    add_center(doc, "[Teacher Name]")
    add_center(doc, "_______________________")
    add_center(doc, "Designation")
    add_center(doc, "Department of Software Engineering")
    add_center(doc, "")
    add_center(doc, "Chairperson")
    add_center(doc, "Dr. Omer Irshad")
    add_center(doc, "_______________________")
    add_center(doc, "Head of Department")
    add_center(doc, "Department of Software Engineering")
    add_page_break(doc)

    # ── Copyrights ──
    add_center(doc, "COPYRIGHTS", bold=True, size=Pt(16))
    add_para(doc, 'This is to certify that the project titled "BioNAFNet: Biologically-Inspired Low-Light Image Enhancement with Knowledge Distillation and Desktop Application" is the genuine work carried out by [Student Names], student of BSSE of Software Engineering Department, Lahore Garrison University, Lahore. During the academic year [Year], in partial fulfilment of the requirements for the award of the degree of Bachelor of Science in Software Engineering and that the project has not formed the basis for the award previously of any other degree, diploma, fellowship or any other similar title.')
    add_center(doc, "")
    add_center(doc, "[Student Name 1] ____________")
    add_center(doc, "[Student Name 2] ____________")
    add_page_break(doc)

    # ── Declaration ──
    add_center(doc, "DECLARATION", bold=True, size=Pt(16))
    add_para(doc, 'This is to declare that the project entitled "BioNAFNet: Biologically-Inspired Low-Light Image Enhancement with Knowledge Distillation and Desktop Application" is an original work done by undersigned, in partial fulfilment of the requirements for the degree "Bachelor of Science in Software Engineering" at Software Engineering Department, Lahore Garrison University, Lahore.')
    add_para(doc, "All the analysis, design and system development have been accomplished by the undersigned. Moreover, this project has not been submitted to any other college or university.")
    add_center(doc, "")
    add_center(doc, "[Student Name 1] ________________")
    add_center(doc, "[Student Name 2] ________________")
    add_page_break(doc)

    # ── Acknowledgements ──
    add_center(doc, "ACKNOWLEDGEMENTS", bold=True, size=Pt(16))
    add_para(doc, "We would like to thank our supervisor [Teacher Name] for guiding us throughout this project. Their knowledge of deep learning and computer vision helped us design and build BioNAFNet and the NeonEnhancer Pro desktop application.")
    add_para(doc, "We also thank Dr. Omer Irshad, Head of Department of Software Engineering, Lahore Garrison University, for providing us the resources and academic environment to complete this work.")
    add_para(doc, "We thank the creators of LOL datasets (Wei et al., 2018; Yang et al., 2021) for making their data available for research. We also thank the NAFNet authors (Chen et al., 2022) for their backbone architecture and the CustomTkinter community for the modern UI framework.")
    add_para(doc, "Finally, we thank our families and friends for their patience and support during the long training hours and late nights of coding.")
    add_page_break(doc)

    # ── Dedication ──
    add_center(doc, "DEDICATION", bold=True, size=Pt(16))
    add_center(doc, "")
    add_center(doc, "Dedicated to our families,")
    add_center(doc, "who supported us throughout this journey,")
    add_center(doc, "and to making machines see in the dark")
    add_center(doc, "just like the human eye.")
    add_page_break(doc)

    # ── ToC / Lists (Word field codes — right-click → Update Field in Word) ──
    add_center(doc, "Table of Contents", bold=True, size=Pt(16))
    add_toc_field(doc)
    add_page_break(doc)

    add_center(doc, "List of Tables", bold=True, size=Pt(16))
    add_lot_field(doc)
    add_page_break(doc)

    add_center(doc, "List of Figures", bold=True, size=Pt(16))
    add_lof_field(doc)
    add_page_break(doc)

    # ── Abbreviations Table ──
    add_center(doc, "List of Abbreviations", bold=True, size=Pt(16))
    add_table_caption(doc, 1, "List of Abbreviations")
    abbrevs = [
        ("LLIE", "Low-Light Image Enhancement"),
        ("CNN", "Convolutional Neural Network"),
        ("GAN", "Generative Adversarial Network"),
        ("NAFNet", "Nonlinear Activation Free Network"),
        ("BioNAFNet", "Biologically-Inspired NAFNet"),
        ("RLIN", "Retinal Lateral Inhibition Network"),
        ("FAEB", "Frequency-Aware Enhancement Branch"),
        ("ARFP", "Adaptive Receptive Field Pooling"),
        ("PRCM", "Photoreceptor Response Curve Modeling"),
        ("SPDP", "Scotopic-Photopic Dual Pathway"),
        ("TAM", "Temporal Adaptation Memory"),
        ("WFPL", "Weber-Fechner Perceptual Loss"),
        ("PSNR", "Peak Signal-to-Noise Ratio"),
        ("SSIM", "Structural Similarity Index Measure"),
        ("EMA", "Exponential Moving Average"),
        ("AMP", "Automatic Mixed Precision"),
        ("GPU", "Graphics Processing Unit"),
        ("FPS", "Frames Per Second"),
        ("FFT", "Fast Fourier Transform"),
        ("GRU", "Gated Recurrent Unit"),
        ("SCA", "Simplified Channel Attention"),
        ("VGG", "Visual Geometry Group Network"),
        ("LOL", "Low-Light Dataset"),
        ("KD", "Knowledge Distillation"),
        ("LR", "Learning Rate"),
        ("UI", "User Interface"),
        ("CTk", "CustomTkinter"),
        ("RGB", "Red Green Blue Color Space"),
        ("YUV", "Luminance-Chrominance Color Space"),
        ("CLAHE", "Contrast Limited Adaptive Histogram Equalization"),
        ("UNet", "U-shaped Network Architecture"),
        ("DL", "Deep Learning"),
    ]
    make_table(doc, ["Abbreviation", "Full Form"], abbrevs)
    add_page_break(doc)

    # ── Abstract ──
    add_center(doc, "Abstract", bold=True, size=Pt(16))
    add_para(doc, "Low-light image enhancement is a real problem that affects security cameras, mobile photography, and many other areas where pictures are taken in dark conditions. Images captured in low light have noise, wrong colors, and missing details. Traditional methods like histogram equalization can brighten images but they also make the noise worse. Deep learning methods have shown good results but none of them use the biological mechanisms that allow the human eye to adapt to darkness.")
    add_para(doc, "In this project, we built two things: first, a deep learning model called BioNAFNet that enhances low-light images using ideas from how the human eye works; second, a desktop application called NeonEnhancer Pro built with CustomTkinter that lets users enhance their images through a simple and modern interface.")
    add_para(doc, "BioNAFNet integrates seven biologically-inspired modules into the NAFNet backbone: Retinal Lateral Inhibition Network (RLIN) for edge enhancement, Frequency-Aware Enhancement Branch (FAEB) for spectral recovery, Adaptive Receptive Field Pooling (ARFP) for luminance-dependent processing, Photoreceptor Response Curve Modeling (PRCM) for rod and cone simulation, Scotopic-Photopic Dual Pathway (SPDP) for separate luminance and color processing, Temporal Adaptation Memory (TAM) for iterative refinement, and Weber-Fechner Perceptual Loss (WFPL) for perception-weighted training.")
    add_para(doc, "We trained a big Teacher model (154 million parameters) and then compressed it into a small Student model (24 million parameters) through knowledge distillation. The Student is 6.4 times smaller but still gets great results. On the LOLv1 test set, the Student gets 25.23 dB PSNR which is actually higher than the Teacher (24.94 dB). When we combine both models together using ensemble fusion, we get the best result of 29.29 dB on the LOLv2 Real dataset. The Student model runs at 20+ frames per second which makes real-time enhancement possible.")
    add_para(doc, "The NeonEnhancer Pro desktop application has five main features: image enhancement with 12 different AI models, data augmentation, image cropping, image resizing, and live webcam preview. The application uses a futuristic dark theme and provides a complete tool for anyone working with low-light images.")
    add_para(doc, "Keywords: Low-light image enhancement, deep learning, biologically-inspired, NAFNet, knowledge distillation, ensemble fusion, desktop application, PSNR, SSIM", italic=True)
    add_page_break(doc)


def build_chapter1(doc):
    """Chapter 1: Introduction"""
    add_heading1(doc, "Chapter 1")
    add_heading2(doc, "Introduction")

    # 1.1 Background
    add_heading3(doc, "1.1 Background")
    add_para(doc, "Image enhancement is one of the oldest and most important tasks in computer vision. The idea is simple: take a bad image and make it look better. But when it comes to low-light images specifically, things get much more complicated than just making it brighter. Low-light images have multiple problems happening at the same time: they are dark, noisy, color-shifted, and lacking in detail. Fixing one problem often makes another worse.")
    add_para(doc, "Traditional methods like Histogram Equalization (1970s) and Gamma Correction can make images brighter, but they have a big limitation. They apply the same mathematical formula to every pixel without understanding what is actually in the image. So when they boost brightness, they also boost noise. When they fix contrast, they sometimes create ugly artifacts. These methods simply cannot handle the complexity of real low-light degradation.")
    add_para(doc, "Deep learning changed the game. Instead of writing rules by hand, we can now train neural networks on thousands of example pairs (dark image paired with its well-lit version) and the network learns how to do the enhancement automatically. Models like RetinexNet, MIRNet, and Retinexformer have achieved impressive results. But there is something interesting that nobody has tried: using the biological mechanisms of the human eye as inspiration for the neural network design.")
    add_para(doc, "Our eyes can see in conditions ranging from bright sunlight to near total darkness. This is possible because of specific biological mechanisms like photoreceptor cells (rods and cones), lateral inhibition between neurons, and temporal adaptation. In this project, we take these biological principles and implement them as neural network modules inside a model called BioNAFNet.")

    # 1.2 Motivation
    add_heading3(doc, "1.2 Motivation")
    add_para(doc, "The human visual system is remarkable. Our eyes can adapt to lighting conditions spanning over 10 orders of magnitude, from starlight to bright sunshine. This adaptation happens through specific biological mechanisms: rod and cone photoreceptors with different sensitivity curves, lateral inhibition between retinal neurons that enhances edges, separate processing pathways for brightness and color, and temporal adaptation that gradually adjusts sensitivity over time.")
    add_para(doc, "These mechanisms have been refined by millions of years of evolution. It makes sense to ask: can we put these biological principles into our deep learning models to make them better at low-light enhancement? That is exactly what BioNAFNet does. We take the NAFNet architecture, which is already a strong backbone for image restoration, and we add seven modules that are each inspired by a specific biological mechanism of the human visual system.")

    # 1.3 Problem Statement
    add_heading3(doc, "1.3 Problem Statement")
    add_para(doc, "Low-light images have four main problems happening at the same time: (1) noise from the camera sensor, (2) colors that look wrong, (3) loss of fine details like text and edges, and (4) very low contrast where everything looks flat. Existing deep learning methods can fix these problems to some extent, but they do not use the biological mechanisms that make the human eye so good at adapting to dark conditions. Also, most good models are too slow for real-time use and there is no existing desktop application that combines multiple enhancement models into one easy-to-use tool.")

    # 1.4 Research Objectives
    add_heading3(doc, "1.4 Research Objectives")
    objectives = [
        "Design a novel architecture called BioNAFNet with seven biologically-inspired modules (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL) integrated into the NAFNet backbone.",
        "Train the full Teacher model (154M parameters) on LOLv1 and LOLv2 datasets and achieve competitive results with state-of-the-art methods.",
        "Compress the Teacher into a lightweight Student model (24M parameters) using knowledge distillation for real-time deployment at 20+ FPS.",
        "Demonstrate ensemble fusion of Teacher and Student outputs for maximum enhancement quality.",
        "Build a modern desktop application (NeonEnhancer Pro) using CustomTkinter with image enhancement, augmentation, cropping, resizing, and live webcam preview.",
        "Evaluate all model variants on LOLv1, LOLv2 Real, and LOLv2 Synthetic test sets using PSNR and SSIM metrics.",
    ]
    for i, obj in enumerate(objectives, 1):
        add_list_numbered(doc, f"{i}. {obj}")

    # 1.5 Scope
    add_heading3(doc, "1.5 Scope of the Project")
    add_para(doc, "This project covers single-image low-light enhancement using supervised learning with paired datasets. We use three benchmark datasets: LOLv1 (485/15 train/test pairs), LOLv2 Real (689/100), and LOLv2 Synthetic (900/100). The desktop application supports 12 different enhancement models (3 BioNAFNet variants plus 9 other published methods), data augmentation, cropping, resizing, and live webcam enhancement. Training and testing are done on a standard desktop with an NVIDIA GPU. Everything runs on a local machine without needing the internet.")

    # 1.6 Novel Contributions
    add_heading3(doc, "1.6 Novel Contributions")
    contribs = [
        "RLIN (Retinal Lateral Inhibition Network): Center-surround edge enhancement inspired by retinal ganglion cell receptive fields.",
        "FAEB (Frequency-Aware Enhancement Branch): Fourier-domain amplitude and phase correction at the network bottleneck.",
        "ARFP (Adaptive Receptive Field Pooling): Multi-scale convolution (3x3, 5x5, 7x7) with luminance-dependent gating.",
        "PRCM (Photoreceptor Response Curve Modeling): Learned rod and cone gamma curves with adaptive scotopic-photopic threshold.",
        "SPDP (Scotopic-Photopic Dual Pathway): Separate luminance and chrominance processing inspired by magnocellular and parvocellular pathways.",
        "TAM (Temporal Adaptation Memory): GRU-based iterative refinement across multiple forward passes, modeling dark adaptation.",
        "WFPL (Weber-Fechner Perceptual Loss): Perception-weighted loss emphasizing dark region accuracy based on psychophysical principles.",
        "Knowledge distillation pipeline achieving 6.4x compression with the Student actually beating the Teacher on LOLv1.",
        "NeonEnhancer Pro: a full desktop application with 5 pages and 12 model options built using CustomTkinter.",
    ]
    for i, c in enumerate(contribs, 1):
        add_list_numbered(doc, f"{i}. {c}")

    # 1.7 Significance
    add_heading3(doc, "1.7 Significance")
    add_para(doc, "From a theoretical perspective, BioNAFNet is the first architecture to systematically integrate multiple biological visual processing mechanisms into a single deep learning model for low-light image enhancement. Each module has a clear biological analog which makes the architecture interpretable and scientifically grounded.")
    add_para(doc, "From a practical perspective, the Student model (BioNAFNet-Lite) at 24M parameters and 20+ FPS enables real-time low-light enhancement on standard desktop GPUs. The ensemble fusion strategy provides the highest quality for offline processing. The NeonEnhancer Pro application makes this technology accessible to regular users through a modern, intuitive interface.")

    # 1.8 Gantt Chart
    add_heading3(doc, "1.8 Project Timeline / Gantt Chart")
    add_table_caption(doc, 2, "Project Gantt Chart / Timeline")
    timeline = [
        ("1-2", "Literature review, topic selection", "Proposal draft"),
        ("3-4", "NAFNet study, dataset preparation", "Dataset ready"),
        ("5-6", "BioNAFNet design, RLIN, FAEB coding", "Architecture code"),
        ("7-8", "Teacher training (504 epochs)", "Trained Teacher model"),
        ("9-10", "Knowledge distillation (693 epochs)", "Trained Student model"),
        ("11-12", "Ensemble testing, benchmarking", "Results tables"),
        ("13-14", "NeonEnhancer Pro UI development", "Working application"),
        ("15-16", "Testing, documentation, final report", "This document"),
    ]
    make_table(doc, ["Week", "Activity", "Deliverable"], timeline)

    # 1.9 Report Organization
    add_heading3(doc, "1.9 Report Organization")
    chapters = [
        "Chapter 2 defines the problem of low-light image enhancement and explains the challenges.",
        "Chapter 3 covers the software requirements, literature survey, and research gaps.",
        "Chapter 4 describes our methodology including all seven biological modules, loss functions, and training strategy.",
        "Chapter 5 presents the system architecture, detailed design, and UML diagrams.",
        "Chapter 6 covers implementation details, application features, and testing procedures.",
        "Chapter 7 presents all experimental results, benchmark comparisons, and discussion.",
        "Chapter 8 provides conclusions and future work directions.",
    ]
    for ch in chapters:
        add_list_bullet(doc, ch)

    add_figure_placeholder(doc, 1, "NeonEnhancer Pro Main Window \u2014 Dark Futuristic Theme with Enhancement Page")
    add_page_break(doc)


def build_chapter2(doc):
    """Chapter 2: Problem Definition"""
    add_heading1(doc, "Chapter 2")
    add_heading2(doc, "Problem Definition")

    add_heading3(doc, "2.1 Problem Overview")
    add_para(doc, "Low-light image enhancement is the task of recovering a high-quality, well-lit image from a degraded input captured in poor lighting conditions. When a camera captures an image in low light, multiple things go wrong at once. The sensor receives very few photons, so the electronic noise becomes a big part of the signal. The auto white balance fails and creates unnatural color shifts. Fine textures and edges become invisible because pixel values are very close to zero. The overall contrast is compressed into a very narrow range.")
    add_para(doc, "The challenge is not just making the image brighter. Any simple brightening method also amplifies the noise. The real challenge is to increase brightness, fix colors, recover details, and remove noise all at the same time without introducing new artifacts.")

    add_heading3(doc, "2.2 Types of Low-Light Degradation")
    add_para(doc, "2.2.1 Noise Amplification", bold=True)
    add_para(doc, "When the camera sensor receives very few photons in dark conditions, the electronic noise from the sensor circuitry becomes significant relative to the actual signal. This noise appears as random grain throughout the image and is especially bad in the darkest regions. Any attempt to brighten the image also amplifies this noise.")

    add_para(doc, "2.2.2 Color Distortion", bold=True)
    add_para(doc, "Camera auto white balance algorithms are designed for normal lighting. In low light, they often fail completely, producing yellowish, greenish, or bluish tints that make the image look unnatural. Skin tones look wrong and environmental colors are shifted.")

    add_para(doc, "2.2.3 Loss of Fine Details", bold=True)
    add_para(doc, "When pixel intensity values are very close to zero, the difference between adjacent pixels becomes smaller than the noise level. This means fine textures, small text, and subtle edges are genuinely lost. They are not just hidden, they are gone from the captured data.")

    add_para(doc, "2.2.4 Low Dynamic Range", bold=True)
    add_para(doc, "In a well-lit scene, pixel values span from 0 to 255. In a low-light image, most pixels are between 0 and 30. Everything looks flat and lifeless because there is no contrast between different parts of the scene.")

    add_figure_placeholder(doc, 2, "Low-Light Input vs BioNAFNet Enhanced Output vs Ground Truth")

    add_heading3(doc, "2.3 Limitations of Existing Solutions")
    add_para(doc, "2.3.1 Traditional Methods", bold=True)
    add_para(doc, "Histogram Equalization (HE) redistributes pixel intensities across the full range. It improves contrast but amplifies noise and often produces over-saturated results. CLAHE applies HE locally but creates blocky artifacts. Gamma correction uses a power-law transformation but cannot separate signal from noise. Retinex methods decompose images into reflectance and illumination but produce halo artifacts around edges.")

    add_para(doc, "2.3.2 Deep Learning Methods", bold=True)
    add_para(doc, "Existing deep learning approaches like RetinexNet, KinD, MIRNet, and Retinexformer achieve much better results. However they share a common limitation: none of them incorporate the biological mechanisms that allow the human eye to handle extreme lighting variations. They treat low-light enhancement as a pure signal processing problem rather than drawing on the principles of biological vision.")

    add_para(doc, "2.3.3 The Quality-Speed Gap", bold=True)
    add_para(doc, "Large models with many parameters (50M+) achieve good quality but are too slow for real-time applications. Lightweight models are fast but sacrifice quality. There is a gap between what is achievable in terms of quality and what is practical for deployment. Knowledge distillation can help bridge this gap but has not been widely applied to LLIE methods. Also, there is no existing desktop application that combines multiple AI models with image processing tools in one package.")

    add_heading3(doc, "2.4 Formal Problem Statement")
    add_para(doc, '"How can we design a deep learning architecture for low-light image enhancement that (a) incorporates biological visual processing principles to improve enhancement quality, (b) achieves competitive performance with state-of-the-art methods, (c) can be compressed into a lightweight model suitable for real-time deployment, and (d) is integrated into a user-friendly desktop application?"')

    add_heading3(doc, "2.5 Research Questions")
    rqs = [
        "RQ1: Can biologically-inspired modules improve the performance of deep learning models for low-light image enhancement?",
        "RQ2: What is the individual contribution of each biological module to the overall enhancement quality?",
        "RQ3: Can knowledge distillation effectively compress a large Teacher model into a real-time capable Student model?",
        "RQ4: Does ensemble fusion of Teacher and Student produce results superior to either model alone?",
    ]
    for i, rq in enumerate(rqs, 1):
        add_list_numbered(doc, f"{i}. {rq}")

    add_figure_placeholder(doc, 3, "Side-by-Side Comparison: Input (with annotations for noise, color shift, detail loss) | BioNAFNet Enhanced | Ground Truth")
    add_page_break(doc)


if __name__ == "__main__":
    doc = Document()
    setup_styles(doc)
    build_front_matter(doc)
    build_chapter1(doc)
    build_chapter2(doc)
    doc.save("_test_p1.docx")
    print("Part 1 done.")
