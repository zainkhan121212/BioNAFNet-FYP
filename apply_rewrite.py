# -*- coding: utf-8 -*-
"""Apply humanized rewrites to BioNAFNet_Master_Report.docx"""
import sys
import copy
from docx import Document

doc = Document(r'F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Master_Report.docx')

# Build replacement dict: paragraph_index -> new_text
# "" means clear the paragraph (content absorbed elsewhere)
R = {}

# ============ ABSTRACT ============
R[251] = "Low-light image enhancement matters more than people think. Security cameras, phone photos taken at night, dashcams in tunnels \u2014 any time there is not enough light, the image quality tanks. You get noise everywhere, the colors look off, and fine details just vanish. Old-school techniques like histogram equalization can push the brightness up, sure, but they drag the noise up with it. Deep learning has made big strides here, no question. But here is what caught our attention: nobody had really tried borrowing from how the human eye actually handles darkness."
R[252] = "So we built two things. First, a deep learning model we call BioNAFNet. It sits on top of the NAFNet backbone and adds seven modules, each one modeled after a real biological mechanism in the human visual system \u2014 stuff like how retinal ganglion cells do edge detection through lateral inhibition, or how rods and cones have totally different sensitivity curves. Second, we made NeonEnhancer Pro, which is a desktop app built with CustomTkinter that wraps all of this into something anyone can actually use without touching a command line."
R[253] = "We trained a large Teacher model with 154 million parameters, then squeezed it down to a 24-million-parameter Student through knowledge distillation. The compression ratio is 6.4x. What surprised us is that the Student actually scores higher on LOLv1 \u2014 25.23 dB versus the Teacher\u2019s 24.94 dB. We think the smaller capacity acts like a regularizer. When we fuse both models together in an ensemble, the peak result hits 29.29 dB on LOLv2 Real. The Student runs above 20 FPS, so live webcam enhancement is smooth and practical."
R[254] = "NeonEnhancer Pro packs five pages: enhancement with a choice of 12 AI models, data augmentation, cropping, resizing, and a live preview mode. It has a dark neon-themed UI and handles batch processing too."
R[255] = ""

# ============ CH1 1.1 Background ============
R[261] = "Making images look better has been a goal in computer vision basically since the field existed. The pitch is straightforward \u2014 you have a bad image, you want a good one. Low-light images make that pitch a lot harder to deliver on, though. It is not just a brightness problem. A dark photo is simultaneously noisy, color-shifted, low-contrast, and missing fine detail. Crank the brightness and you amplify the noise. Fix the contrast and you might get weird artifacts instead. All four problems are tangled together."
R[262] = "The traditional toolkit \u2014 histogram equalization from the 1970s, gamma correction, that sort of thing \u2014 treats every pixel with the same blanket formula. No awareness of what the image actually contains. Deep learning flipped the approach: train on thousands of dark/light image pairs and let the network figure it out. RetinexNet, MIRNet, Retinexformer \u2014 they all showed strong numbers. But we noticed a gap. None of these networks incorporate the actual biological tricks that let the human eye work in near-total darkness."
R[263] = "Think about what your eyes can do. You walk from bright afternoon sunlight into a pitch-black movie theater and within minutes you can see the seats, the steps, the exit signs. That happens because of photoreceptor cells with different response curves, lateral inhibition that sharpens edges even when the signal is weak, and a slow temporal adaptation process that ramps your sensitivity up over time. Our idea was to take each of those mechanisms and turn it into a neural network module. That is BioNAFNet."
R[264] = ""

# ============ CH1 1.2 Motivation ============
R[268] = "The human visual system handles a lighting range of something like 10 orders of magnitude. Starlight to direct sun, and we manage both. The hardware behind this is fascinating \u2014 rod cells that fire in almost no light, cone cells for daylight color, inhibitory connections between retinal neurons that boost contrast at edges, parallel processing pathways for brightness versus color, and a gradual chemical regeneration process that slowly adjusts sensitivity after a sudden light change."
R[269] = "Evolution spent millions of years refining all that. So it felt like a reasonable question to ask: what if we wired those same principles into a neural network? NAFNet already provides a solid, clean backbone for image restoration. We took that and bolted on seven modules, each one tied to a specific piece of the biology. That is the core idea behind BioNAFNet."

# ============ CH1 1.3 Problem Statement ============
R[271] = "Low-light images suffer from four things at once: sensor noise (the camera circuitry adds random grain when photons are scarce), color distortion (auto white balance goes haywire in the dark), missing fine detail (pixel values near zero means tiny differences get buried), and crushed dynamic range (everything looks flat because all the values are packed between 0 and 30). Current deep learning methods handle some of these, but they treat the problem purely as signal processing. Nobody has brought in the biological mechanisms that make human night vision so effective. On top of that, the best models tend to be too heavy for real-time use, and there is no single desktop app out there that bundles multiple enhancement models with practical image-processing tools."

# ============ CH1 1.4 Research Objectives ============
R[273] = "1. Design BioNAFNet with seven bio-inspired modules (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL) built into the NAFNet backbone."
R[274] = "2. Train the full Teacher model (154M params) on LOLv1 and LOLv2, targeting competitive performance against published state-of-the-art."
R[275] = "3. Compress the Teacher into a Student (24M params) via knowledge distillation, targeting 20+ FPS for real-time deployment."
R[276] = "4. Show that ensemble fusion of Teacher and Student outputs produces better results than either one alone."
R[278] = "5. Build NeonEnhancer Pro using CustomTkinter with enhancement, augmentation, cropping, resizing, and live webcam preview features."
R[279] = "6. Evaluate everything on LOLv1, LOLv2 Real, and LOLv2 Synthetic using PSNR and SSIM."

# ============ CH1 1.5 Scope ============
R[281] = "We focus on single-image enhancement using supervised learning with paired data. Three benchmark datasets: LOLv1 (485 train / 15 test), LOLv2 Real (689 / 100), and LOLv2 Synthetic (900 / 100). The desktop app supports 12 models total \u2014 our three BioNAFNet variants plus nine published methods. It also does augmentation, cropping, resizing, and live webcam enhancement. All training and inference run locally on a desktop with an NVIDIA GPU. No cloud, no internet dependency."

# ============ CH1 1.6 Novel Contributions ============
R[283] = "1. RLIN \u2014 Center-surround edge enhancement drawn from how retinal ganglion cells form their receptive fields."
R[284] = "2. FAEB \u2014 Fourier-domain correction of amplitude and phase at the network bottleneck."
R[285] = "3. ARFP \u2014 Multi-scale convolutions (3x3, 5x5, 7x7) gated by luminance. Darker areas get bigger receptive fields, mimicking the rod/cone tradeoff."
R[286] = "4. PRCM \u2014 Learned gamma curves for rod-like and cone-like response, with a trainable blending threshold."
R[287] = "5. SPDP \u2014 Parallel luminance and chrominance pathways, inspired by the magnocellular and parvocellular streams in the brain."
R[288] = "6. TAM \u2014 GRU-based iterative refinement across multiple forward passes, modeling the gradual process of dark adaptation."
R[289] = "7. WFPL \u2014 A loss function that penalizes errors in dark regions more heavily, grounded in the Weber-Fechner law from psychophysics."
R[290] = "8. Knowledge distillation achieving 6.4x compression where the Student actually outscores the Teacher on LOLv1."
R[291] = "9. NeonEnhancer Pro \u2014 a five-page desktop application with 12 model choices, built on CustomTkinter."

# ============ CH1 1.7 Significance ============
R[293] = "On the theory side, BioNAFNet is (to our knowledge) the first architecture that takes multiple biological visual processing mechanisms and weaves them into one model for low-light enhancement. Every module has a clear biological counterpart, which gives the architecture a level of interpretability that pure engineering designs lack."
R[294] = "On the practical side, the Student model at 24M parameters and 20+ FPS means you can run real-time enhancement on a normal desktop GPU. The ensemble strategy gets you the highest quality when speed does not matter. And NeonEnhancer Pro puts all of it behind a modern interface so non-technical users can benefit too."

# ============ CH1 1.9 Report Organization ============
R[298] = "\u2022  Chapter 2 lays out the low-light enhancement problem and what makes it hard."
R[299] = "\u2022  Chapter 3 goes through the literature, identifies research gaps, and states the requirements."
R[300] = "\u2022  Chapter 4 is the methodology \u2014 all seven bio modules, the loss functions, training setup."
R[301] = "\u2022  Chapter 5 covers system architecture, the app design, and UML diagrams."
R[302] = "\u2022  Chapter 6 handles implementation specifics, the app\u2019s features, and testing."
R[303] = "\u2022  Chapter 7 is where we present results, benchmarks, ablation, and discussion."
R[304] = "\u2022  Chapter 8 wraps up with conclusions and where we think this work could go next."

# ============ CH2 2.1 Problem Overview ============
R[311] = "Low-light image enhancement boils down to this: take an image captured in bad lighting and make it look like it was shot in good lighting. Sounds simple. It is not. When a camera shoots in the dark, the sensor barely gets any photons. Electronic noise, which is always there, now makes up a huge chunk of the recorded signal. The auto white balance algorithm \u2014 designed for daylight \u2014 picks the wrong correction and throws the colors off. Textures and edges that would be obvious in a bright photo now live in a narrow band of pixel values right near zero, effectively invisible. And the overall contrast gets squished into a tiny range, making everything look washed out and flat."
R[312] = "The naive fix \u2014 just multiply all pixel values by some constant \u2014 fails immediately because the noise scales right along with the signal. Proper enhancement needs to lift brightness, restore color, recover texture, and suppress noise, all at once, without introducing new problems."

# ============ CH2 2.2 Types of Degradation ============
R[315] = "Camera sensors always produce some electronic noise. In good light you never notice it because the actual signal drowns it out. In the dark, the signal is so weak that the noise becomes a major component of what the camera records. It shows up as random grainy speckles, worst in the darkest parts of the image. Brighten the image and you brighten the grain too."
R[317] = "Auto white balance is calibrated for normal conditions. Throw it a scene lit only by a distant streetlamp or the glow of a phone screen and it has no idea what to do. The result is images with strong yellow, green, or blue casts. Skin tones look sickly, and environmental colors are completely wrong."
R[319] = "When pixel intensities hover near zero, the differences between neighboring pixels shrink below the noise floor. Textures, small text, thin edges \u2014 they are not just hidden by the darkness, they are gone from the data. No amount of post-processing can hallucinate them back with certainty."
R[321] = "A well-exposed image uses the full 0-to-255 range. A low-light image might cram everything between 0 and 30. There is no separation between a dark wall and the slightly-less-dark door next to it. Everything looks flat."

# ============ CH2 2.3 Limitations ============
R[326] = "Histogram equalization stretches pixel values across the full range. Contrast goes up, but so does noise, and you often get over-saturated blobs. CLAHE does the same thing locally, tile by tile, which helps but leaves blocking artifacts at tile edges. Gamma correction applies a power curve that cannot tell signal from noise. Retinex-based methods decompose the image into reflectance and illumination, which is elegant in theory but produces halos around strong edges in practice."
R[328] = "RetinexNet, KinD, MIRNet, Retinexformer \u2014 these are all real improvements over the traditional approaches. They learn complex mappings from data and produce noticeably better results. But they all share one blind spot: none of them draw on biology. They approach low-light enhancement as a pure computational problem without asking how nature solved the same problem in the human eye."
R[330] = "Big models with 50+ million parameters get good numbers but run too slowly for anything interactive. Small models are fast but sacrifice quality. Knowledge distillation could help bridge that gap, but it has barely been applied to low-light enhancement. And when it comes to end-user tools, there is no desktop application that bundles multiple AI models with image processing features in one place."

# ============ CH2 2.4 Formal Problem Statement ============
R[332] = "\u201cHow can we design a deep learning architecture for low-light image enhancement that (a) incorporates biological visual processing principles to improve quality, (b) performs competitively against state-of-the-art methods, (c) can be compressed for real-time deployment, and (d) is wrapped in a desktop application that is actually usable?\u201d"

# ============ CH2 2.5 Research Questions ============
R[334] = "1. RQ1: Can biologically-inspired modules genuinely improve deep learning performance for low-light enhancement?"
R[335] = "2. RQ2: How much does each individual bio module contribute to the overall quality?"
R[336] = "3. RQ3: Can knowledge distillation compress a large teacher model into a student that runs in real time without losing too much quality?"
R[337] = "4. RQ4: Does fusing teacher and student outputs via ensemble averaging beat either model on its own?"

# ============ CH3 3.1.1 Traditional Methods ============
R[345] = "Histogram equalization dates back to the 1970s. The idea is to remap pixel intensities so they spread evenly across 0\u2013255 (Gonzalez and Woods, 2002). It does boost contrast, but it treats noise the same as signal, so dark images come out grainy and sometimes over-saturated."
R[346] = "CLAHE (Zuiderveld, 1994) was a smart refinement \u2014 split the image into tiles, equalize each one locally, and clip the histogram to prevent runaway amplification. It works well enough for medical imaging, but the tile boundaries still create visible blocks, and extremely dark scenes remain problematic."
R[347] = "Gamma correction raises pixel values to a power (I_out = I_in^gamma, where gamma < 1 brightens). Some adaptive versions estimate gamma locally (Huang et al., 2013), but the fundamental issue stays: a power curve does not know whether it is boosting real detail or random noise."
R[348] = "The Retinex theory from Edwin Land (1977) is interesting from a perceptual standpoint. It models an image as reflectance times illumination (I = R \u00d7 L) and tries to separate the two. Single-Scale Retinex and Multi-Scale Retinex (Jobson et al., 1997) estimate illumination with Gaussian filters. The theory is sound, but in practice you get halos around edges and the noise problem is still there."

# ============ CH3 3.1.2 CNN-Based ============
R[351] = "LLNet (Lore et al., 2017) was an early attempt \u2014 stacked sparse denoising autoencoders applied to low-light images. It proved the concept that neural networks could learn enhancement, but the architecture was too simple to produce strong results."
R[352] = "MBLLEN (Lv et al., 2018) went with a multi-branch design to capture features at different scales. More flexibility, but also more compute."
R[353] = "RetinexNet (Wei et al., 2018) brought deep learning and Retinex theory together. KinD (Zhang et al., 2019) built on that idea with a two-branch setup and hit 20.87 dB on LOLv1."
R[354] = "MIRNet (Zamir et al., 2020) pushed the numbers further with multi-scale residual blocks and selective kernel features, reaching 24.14 dB. Then NAFNet (Chen et al., 2022) came along and simplified things dramatically by getting rid of activation functions entirely, using a SimpleGate mechanism instead. We chose NAFNet as our backbone specifically because of that clean, efficient design."

# ============ CH3 3.1.3 Transformer-Based ============
R[356] = "Restormer (Zamir et al., 2022) brought efficient transformers into image restoration, using multi-DConv head transposed attention. It set new benchmarks across several restoration tasks."
R[357] = "SNR-Aware Transformer (Xu et al., 2022) added signal-to-noise ratio awareness, so the attention adapts based on local noise levels. It reached 24.61 dB on LOLv1."
R[358] = "Retinexformer (Cai et al., 2023) merged Retinex decomposition with a transformer backbone and achieved 25.16 dB on LOLv1 \u2014 one of the best published results on that benchmark."

# ============ CH3 3.1.4 GAN-Based ============
R[360] = "EnlightenGAN (Jiang et al., 2021) stood out because it does not need paired training data. Adversarial learning lets it train on unpaired images. The tradeoff is lower scores \u2014 17.48 dB is well below supervised methods."

# ============ CH3 3.1.5 Knowledge Distillation ============
R[362] = "Knowledge distillation (Hinton et al., 2015) trains a small Student network to mimic the outputs of a larger Teacher. It has been used extensively in classification and detection, but hardly anyone has applied it to low-light enhancement. We found that distillation compresses our model by 6.4x, and the surprising part is the Student actually beats the Teacher on LOLv1. That result alone seemed worth reporting."

# ============ CH3 3.2 Research Gaps ============
R[365] = "After going through the literature, six gaps stood out:"
R[366] = "1. No biological integration. Nobody has taken photoreceptor modeling, lateral inhibition, temporal adaptation, or any other biological vision mechanism and put it inside an LLIE model."
R[367] = "2. Limited frequency processing. Nearly all methods stay in the spatial domain. FFT-based processing for low-light enhancement is essentially unexplored."
R[368] = "3. Fixed receptive fields. Every method uses the same kernel size everywhere. The human eye does not \u2014 rod cells pool over larger areas in the dark while cones keep things sharp in bright light."
R[369] = "4. Perception-unaware losses. Standard loss functions weigh all pixel errors equally. But the Weber-Fechner law tells us humans are far more sensitive to changes in dark regions than bright ones."
R[370] = "5. The speed-quality gap. Knowledge distillation has not been seriously applied to LLIE to bridge the gap between heavy high-quality models and lightweight real-time ones."
R[371] = "6. No all-in-one desktop tool. There is no existing application that puts multiple AI enhancement models together with augmentation, cropping, resizing, and live preview in a single package."

# ============ CH3 3.3 Benchmark extra ============
R[374] = "We use LOLv1, LOLv2 Real, and LOLv2 Synthetic. Combined that gives us 2074 training pairs and 215 test images. The mix of real captured pairs and synthetically degraded pairs gives a more rounded evaluation than any single dataset would."

# ============ CH3 3.7 Evaluation Metrics ============
R[382] = "We rely on two standard metrics."
R[383] = "PSNR (Peak Signal-to-Noise Ratio) is measured in decibels. The formula is PSNR = 10 \u00d7 log10(MAX\u00b2 / MSE), with MAX = 1.0 for normalized images. Higher is better. Decent LLIE scores usually land between 20 and 30 dB. Our best is 29.29 dB."
R[384] = "SSIM (Structural Similarity Index) outputs a value between 0 and 1. It compares structure, luminance, and contrast between the enhanced image and the ground truth. It correlates better with human perception than PSNR does. Anything above 0.85 is generally considered good."

# ============ CH4 4.1 Research Approach ============
R[389] = "We followed an experimental, quantitative approach. Design the architecture, implement it in PyTorch, train on benchmarks, measure with objective metrics. Four phases:"
R[390] = "1. Architecture Design \u2014 build seven bio-inspired modules, integrate them into NAFNet."
R[391] = "2. Teacher Training \u2014 train the full 154M-parameter BioNAFNet on LOLv1 + LOLv2 combined, 504 epochs."
R[392] = "3. Knowledge Distillation \u2014 train a 24M-parameter Student for 693 epochs, using the frozen Teacher\u2019s outputs as guidance."
R[393] = "4. Application Development \u2014 build NeonEnhancer Pro with CustomTkinter and run all evaluations including ensemble fusion."

# ============ CH4 4.2 NAFNet Backbone ============
R[395] = "NAFNet (Chen et al., 2022) has one big idea: throw out activation functions. No ReLU, no GELU, nothing. Instead, it uses something called SimpleGate \u2014 split the feature tensor into two halves along the channel dimension and multiply them element-wise. Where ReLU zeros out all negative values (losing information), SimpleGate keeps everything."
R[396] = "A NAFNet block goes: LayerNorm, 1\u00d71 conv to expand channels, 3\u00d73 depthwise conv for spatial features, SimpleGate for nonlinearity, Simplified Channel Attention (SCA) to reweight channels, and a final 1\u00d71 conv to bring channels back down. We modified this into what we call a BioNAFBlock by inserting our RLIN module right after the channel attention step."

# ============ CH4 4.3 RLIN ============
R[398] = "The biology. Retinal ganglion cells have center-surround receptive fields. The center region gets excited by light; the surrounding area is inhibited. When there is an edge \u2014 bright on one side, dark on the other \u2014 the difference between center excitation and surround inhibition produces a strong signal. That is how we pick up on edges even in very dim conditions."
R[399] = "Our implementation. RLIN has two parallel pathways. A center pathway (1\u00d71 conv) captures the response at each pixel directly. A surround pathway (5\u00d75 average pooling followed by a 1\u00d71 conv) captures the average of the neighborhood. We subtract surround from center, scale by a learnable parameter alpha (initialized to 0.3), and add back as a residual: Output = x + alpha * (Center(x) - Surround(x)). RLIN goes into every BioNAFBlock in the first three encoder stages."

# ============ CH4 4.4 FAEB ============
R[403] = "The biology. Visual cortex neurons respond to specific spatial frequencies. Some are tuned to fine detail (high frequency), others to broad patterns (low frequency). In dark images, the high-frequency components get destroyed by noise first."
R[404] = "Our implementation. FAEB sits at the network bottleneck \u2014 the deepest, lowest-resolution point. It takes the feature maps, converts them to the frequency domain with a 2D FFT, then processes the amplitude (how much of each frequency is present) and phase (where things are spatially located) through separate small conv networks. After processing, inverse FFT brings things back to the spatial domain. The result blends with the original features through a learnable factor (initialized to 0.15). We force float32 precision for all FFT operations because half-precision causes numerical blowups in the frequency domain."

# ============ CH4 4.5 ARFP ============
R[408] = "The biology. In bright light, cones give sharp, detailed vision through small receptive fields. In the dark, rods pool signals over larger areas to gather enough photons to produce any signal at all. That is why you cannot read small print in dim light but you can still navigate a dark room."
R[409] = "Our implementation. Three parallel depthwise convolutions with kernel sizes 3\u00d73, 5\u00d75, and 7\u00d77. A gating network reads the luminance map and outputs three softmax-normalized weights. Dark patches push more weight onto the larger kernels (acting like rods). Bright patches favor the 3\u00d73 kernel (acting like cones). ARFP sits at the decoder output, right before final reconstruction."

# ============ CH4 4.6 PRCM ============
R[411] = "The biology. Rod cells have a response curve with an effective gamma around 0.45 \u2014 extremely sensitive to small brightness changes. Cones have gamma near 0.95, closer to linear. The brain blends between the two depending on ambient brightness."
R[412] = "Our implementation. Two learned gamma curves. Rod response: x^gamma_rod (initialized to 0.45). Cone response: x^gamma_cone (initialized to 0.95). A sigmoid blends between them based on luminance, with a learnable threshold starting at 0.25. All three values are trainable. PRCM is the very first thing applied to the input image, before anything else."

# ============ CH4 4.7 SPDP ============
R[414] = "The biology. The brain keeps brightness and color processing separate. The magnocellular pathway handles luminance and motion; the parvocellular pathway handles color and fine spatial detail. Each pathway is optimized for its own job."
R[415] = "Our implementation. Convert RGB to YUV. The scotopic pathway processes Y (luminance) through its own conv network. The photopic pathway processes U and V (chrominance) through a different network. The results fuse and get added as a residual with 0.2 scaling. SPDP runs right after PRCM, as the second preprocessing step."

# ============ CH4 4.8 TAM ============
R[417] = "The biology. Dark adaptation is not instant. Walk into a dark room and your vision improves gradually over several minutes as photoreceptor chemicals regenerate. No existing LLIE method models this time-dependent process."
R[418] = "Our implementation. A GRU cell that carries a memory state across multiple forward passes. The Teacher runs two passes (n_passes=2), refining the output each time \u2014 mimicking the progressive nature of dark adaptation. The GRU accumulates information between passes. The Student model uses n_passes=1 to keep things fast, effectively skipping the iterative refinement."

# ============ CH4 4.9 WFPL ============
R[420] = "The biology. The Weber-Fechner law (1830s\u20131860s) is one of the oldest findings in psychophysics. Perceived change in a stimulus is proportional to the log of the stimulus intensity. Translation: a brightness change from 0 to 5 is very obvious to you, but the same 5-unit change from 200 to 205 is barely noticeable."
R[421] = "Our implementation. We build a weight map: weight = 1 / (luminance(target) + epsilon), with epsilon = 0.02 to avoid division by zero. After normalization, this map makes the loss function penalize errors in dark regions much more than errors in bright regions. It is a direct application of the psychophysical principle \u2014 focus the network\u2019s training effort where human eyes are most sensitive."

# ============ CH4 4.12 Knowledge Distillation ============
R[429] = "The Student has the same architectural family as the Teacher but scaled down: 32 channels instead of 64, 4 middle blocks instead of 12, and single-pass inference (n_passes=1). During distillation, the Teacher is frozen. For each training batch, the Teacher generates its output, and the Student trains against both the ground truth (L1 + SSIM) and the Teacher\u2019s output (L2 mimic loss, weight 0.4)."
R[430] = "The numbers are striking. 6.4x fewer parameters. 6.5x smaller on disk (91 MB vs 589 MB). 3.9x faster inference (48.9 ms vs 188.7 ms per image). And the Student-693 actually posts a higher PSNR than the Teacher on LOLv1 (25.23 vs 24.94 dB). Our best explanation is that the reduced capacity acts as implicit regularization, helping the Student generalize better to full-resolution test images when training was done on 128\u00d7128 patches."

# ============ CH4 4.13 Ensemble ============
R[434] = "We tried combining Teacher and Student outputs via weighted averaging: enhanced = alpha \u00d7 teacher_out + (1-alpha) \u00d7 student_out, clamped to [0,1]. Three configurations tested (see table)."
R[436] = "The ensemble needs both models loaded, so it is 3\u20134x slower than running either alone. Good for offline processing, not for real-time."

# ============ CH5 5.1.1 ============
R[442] = "Two main parts: BioNAFNet (the deep learning model, the backend) and NeonEnhancer Pro (the desktop app, the frontend). Both written in Python. The model uses PyTorch, the UI uses CustomTkinter. Each biological component is its own independent nn.Module, so swapping one out or tweaking it does not break anything else."

# ============ CH5 5.1.2 Architecture Layers ============
R[444] = "Four layers:"
R[445] = "1. Input Layer \u2014 loads the image with PIL, converts to tensor, normalizes to [0,1], pads to multiples of 16."
R[446] = "2. Preprocessing Layer \u2014 PRCM runs first (photoreceptor curves), then SPDP (dual pathway)."
R[447] = "3. Enhancement Core \u2014 NAFNet encoder-decoder backbone. RLIN injected into encoder blocks. FAEB at the bottleneck. The Teacher model makes 2 passes through this with TAM memory."
R[448] = "4. Output Layer \u2014 ARFP (adaptive receptive field), then global residual, crop the padding off, clamp to [0,1], save."

# ============ CH5 5.1.3 Subsystems ============
R[453] = "Five subsystems:"
R[454] = "\u2022  Training Subsystem: data loading, augmentation, forward/backward passes, loss computation, EMA updates, validation, checkpoint saving."
R[455] = "\u2022  Distillation Subsystem: everything from training plus frozen Teacher inference and mimic loss."
R[456] = "\u2022  Inference Subsystem: load checkpoint, process images (single or batch), compute metrics against ground truth."
R[457] = "\u2022  Ensemble Subsystem: load both Teacher and Student, average their outputs with learned weights."
R[458] = "\u2022  Application Subsystem: NeonEnhancer Pro UI, webcam capture, real-time processing, display."

# ============ CH5 5.2.1 App Overview ============
R[461] = "NeonEnhancer Pro is a Python + CustomTkinter desktop app. Dark theme with neon accent colors \u2014 cyan, purple, pink, blue, green. Window starts at 1600\u00d71000, minimum 1400\u00d7900. There are even particle animations in the background because we figured if we are building a tool for visual processing, it should look good too."

# ============ CH5 5.3.2 Data Flow ============
R[472] = "When someone clicks \u201cEnhance Image\u201d in the app, here is what happens under the hood:"
R[473] = "1. The selected image path gets passed to the model wrapper."
R[474] = "2. The wrapper checks if the model is already loaded in the cache. If not, it loads it (this takes 8\u201310 seconds for the Teacher). The image loads as PIL, then converts to a PyTorch tensor."
R[475] = "3. Normalize to [0,1], pad to the nearest multiple of 16, move to the right device (CPU or GPU)."
R[476] = "4. Forward pass runs inside torch.no_grad() since we are just inferring."
R[477] = "5. Clamp the output to [0,1], crop back to the original size, convert to PIL."
R[478] = "6. Display in the gallery, save to the output folder."
R[479] = "7. If ground truth is available, compute and show PSNR and SSIM."

# ============ CH6 6.1 Implementation Overview ============
R[505] = "Everything is Python. PyTorch for the model, CustomTkinter 5.2 for the app. About 5,500 lines of code spread across 12 files. Trained on an NVIDIA RTX GPU with CUDA 12. We went with a single-file-per-model philosophy \u2014 each script contains the model definition, loss functions, dataset class, and training/testing loop. Makes it easy to run anything by just executing one file, no dependency chains to worry about."

# ============ CH6 6.3 Implementation Details ============
R[510] = "The heart of NAFNet. Take the input tensor, split it into two halves along the channel dimension, multiply element-wise: x1, x2 = x.chunk(2, dim=1); out = x1 * x2. ReLU clips negatives to zero and throws away information. SimpleGate does not clip anything."
R[512] = "We keep an exponential moving average of the model weights with a decay of 0.9995. After each step: ema_weight = 0.9995 \u00d7 ema_weight + 0.0005 \u00d7 current_weight. At test time we use the EMA weights \u2014 they produce smoother, more stable results. All our benchmark numbers use EMA."
R[514] = "Training runs in float16 to save memory and speed things up, except for the FFT operations in FAEB. Half-precision causes numerical overflow in the frequency domain, so those stay in float32. PyTorch\u2019s autocast handles the switching. A gradient scaler prevents underflow during the backward pass."
R[516] = "The 4-level encoder-decoder downsamples 4 times by 2x each, so inputs need dimensions divisible by 16. We use reflection padding to extend the image, run the model, then crop the output back to the original size. Reflection padding avoids the black border artifacts that zero padding would create."
R[518] = "The Teacher weighs 2.47 GB on disk. Loading it takes 8\u201310 seconds. Our wrapper caches the loaded model in a dictionary keyed by device, so only the first call is slow. Every subsequent call is instant. This matters a lot for batch processing."
R[520] = "Two files saved during training: best.pth (highest validation PSNR) and latest.pth (most recent epoch). Each contains model state, EMA state, optimizer state, and the best PSNR value. For inference we always load EMA weights from the best checkpoint."

# ============ CH6 6.4 App Features ============
R[523] = "This is the main event. Left side has the controls: upload buttons for individual images or folders, save directory selector, model dropdown (12 options), CPU/GPU toggle, and the big \u201cENHANCE IMAGE\u201d button. Right side is a split-screen gallery showing original versus enhanced side by side. Previous/Next buttons for navigating batch results."
R[527] = "Upload images, pick a save folder, slide a control from 1 to 4 variations per image. Augmentations include random rotation, horizontal and vertical flips, brightness and contrast jitter, and noise injection. Every variation gets a unique filename. Useful for padding out small training sets."
R[531] = "Three preset aspect ratios (1:1 square, 16:9 wide, center crop) plus manual coordinate entry. Live preview shows the crop rectangle overlaid on the image. Works on single images or entire folders."
R[535] = "Width and height sliders with an aspect ratio lock toggle. When locked, moving one slider auto-adjusts the other. Single or batch mode."
R[539] = "Hooks into the system webcam. Pick any of the 12 models and see the enhanced feed next to the raw feed in real time. The Student model runs above 20 FPS so the preview is smooth enough to feel responsive."

# ============ CH6 6.5 Training Process ============
R[544] = "504 epochs on the combined dataset (2074 image pairs from LOLv1 + LOLv2 Real + LOLv2 Synthetic). Random 128\u00d7128 crops from each image. Augmentation: random horizontal/vertical flips, 90-degree rotations, MixUp with alpha=0.2. Learning rate followed a CosineAnnealingWarmRestarts schedule cycling between 2e-4 and 1e-6, with restart periods at 50, 100, 200, and 400 epochs."
R[545] = "Loss went from 0.6061 at epoch 1 down to 0.2341 at epoch 504. Validation PSNR climbed from around 18 dB to 25.05 dB at epoch 476 (the best). Training was stable throughout \u2014 no blowups, thanks to gradient clipping at 0.5 and accumulation over 2 steps."
R[551] = "693 epochs with the frozen Teacher generating reference outputs. The Student\u2019s loss values are much lower (0.03\u20130.11 range versus the Teacher\u2019s 0.23\u20130.61) because the loss function is simpler \u2014 L1, SSIM, and mimic loss instead of the Teacher\u2019s full composite. Validation PSNR reached 25.09 dB at epoch 693 and was still climbing, which suggests more training would have helped."

# ============ CH6 6.6 Testing ============
R[563] = "All models tested on full-resolution images (not patches) using EMA weights. For each image: load, normalize to [0,1], pad to multiples of 16, run forward with torch.no_grad(), crop output, compute PSNR and SSIM against ground truth. Enhanced images saved to separate directories for manual inspection."

# ============ CH6 6.8 Integration Testing ============
R[568] = "Integration testing ran the full pipeline end-to-end on a small data subset (10 pairs, 5 epochs). We verified that loss decreases, validation PSNR increases, checkpoints save correctly, EMA updates work, and the LR scheduler follows the expected curve."

# ============ CH6 6.9 Software Quality ============
R[571] = "We kept things clean with consistent naming (snake_case for functions, CamelCase for classes), inline comments for the biological modules, modular design (each component is its own nn.Module), seed=42 for reproducibility, model caching, error handling for missing files, reflection padding for any image size, and threaded inference so the UI does not freeze during batch jobs. The single-file-per-model approach means anyone can clone the repo and run a script without chasing down imports."

# ============ CH7 7.1 Overview ============
R[576] = "We ran all six BioNAFNet configurations on three test sets at full resolution. The numbers tell a clear story: the biological modules work, knowledge distillation works, and ensemble fusion works."

# ============ CH7 7.4 SOTA Comparison ============
R[588] = "Our Student-693 hits 25.23 dB PSNR on LOLv1. That edges out Retinexformer (25.16 dB), which is a very different architecture \u2014 a transformer rather than our CNN-based approach. The ensemble variants push further: 25.27\u201325.29 dB on LOLv1 and a peak of 29.29 dB on LOLv2 Real."

# ============ CH7 7.5 Knowledge Distillation Results ============
R[593] = "Here is where it gets interesting. The Student model, with 6.4x fewer parameters, actually outperforms the Teacher on LOLv1 by 0.29 dB (25.23 vs 24.94). That is not supposed to happen \u2014 normally compression costs you quality. We think the smaller model acts as a regularizer. The Teacher has 154M parameters and may be slightly overfitting to the 128\u00d7128 training patches. The Student with only 24M parameters does not have that luxury, so it learns more generalizable features that transfer better to full-resolution test images."

# ============ CH7 7.6 Ensemble Fusion ============
R[598] = "The ensemble consistently beats both individual models. T60/S40 (60% Teacher, 40% Student) hits the single highest PSNR of 29.29 dB on LOLv2 Real \u2014 that is +0.62 dB over the Teacher alone and +0.81 dB over the Student alone. What this suggests is that the two models learn somewhat different things. The Teacher, with its larger capacity and two-pass processing, captures certain kinds of detail. The Student, being simpler, captures cleaner overall structure. Combine them and you get the best of both."

# ============ CH7 7.7 Ablation ============
R[603] = "We looked at how much each module contributes by estimating the drop from removing each one:"
R[605] = "RLIN makes the biggest difference. Makes sense \u2014 edge and contrast enhancement is probably the single most valuable thing you can do to a dark image. FAEB is second; working in the frequency domain lets you target noise patterns that are hard to catch in spatial-domain-only processing. WFPL ranks third because focusing training effort on dark regions (where human perception is most sensitive) naturally pushes the model toward perceptually better outputs."
R[608] = "We also looked at the impact of removing individual modules from the full model:"

# ============ CH7 7.9 Training Convergence ============
R[619] = "The Teacher peaked at 25.05 dB validation PSNR around epoch 476 out of 504. Training loss dropped from around 0.25 to 0.02. The PSNR curve shows a steady climb with periodic dips where the cosine annealing scheduler restarts the learning rate."
R[620] = "The Student hit 25.09 dB at epoch 693 \u2014 the very last epoch \u2014 and the curve was still going up. Unlike the Teacher which plateaued, the Student had not converged yet. More epochs would likely have pushed it higher."
R[621] = "The train-validation gap for the Teacher stayed between 0.3 and 0.5 dB, which is healthy. The Student\u2019s gap grows to 0.5\u20130.9 dB later in training, hinting at some overfitting to the 128\u00d7128 patches. But this did not noticeably hurt performance on full-resolution test images, given the strong benchmark numbers."

# ============ CH7 7.10 Qualitative Results ============
R[627] = "Looking at the enhanced images directly:"
R[628] = "\u2022  Brightness recovery looks natural. Dark areas come up without blowing out bright areas. PRCM\u2019s rod/cone simulation seems to be doing its job."
R[629] = "\u2022  Noise suppression is solid. RLIN and FAEB working together handle noise well while keeping legitimate texture."
R[630] = "\u2022  Colors look right. The SPDP dual pathway keeps chrominance processing separate from luminance, and the result is natural skin tones and accurate environmental colors."
R[631] = "\u2022  Edges stay sharp. RLIN\u2019s center-surround mechanism runs throughout the encoder, and you can see the payoff in the output \u2014 boundaries are clean, not smeared."
R[639] = "The app works as intended. Load images, pick a model, hit enhance, scroll through the before/after gallery. The live preview page demonstrates the Student model\u2019s 20+ FPS capability pretty convincingly \u2014 the enhanced webcam feed updates smoothly."

# ============ CH7 7.11.1 Key Findings ============
R[646] = "Four main takeaways from our experiments:"
R[647] = "1. The biological modules provide real, measurable improvement. Adding all seven to NAFNet improved LOLv1 PSNR by an estimated +2.94 dB. That validates the basic hypothesis \u2014 biological visual principles can make deep learning models for low-light enhancement noticeably better."
R[648] = "2. Knowledge distillation works remarkably well here. 6.4x compression with the Student actually outscoring the Teacher on LOLv1 (25.23 vs 24.94 dB). The distillation seems to provide regularization that helps generalization to full-resolution images."
R[649] = "3. Ensemble fusion creates genuine synergy. The Teacher captures fine detail through two-pass refinement and larger capacity. The Student produces cleaner structure through its simpler architecture. Combining them gives you something better than either alone."
R[650] = "4. Real-time deployment is achievable. Student-693 at 20.5 FPS is smooth enough for live webcam enhancement, making the research results practically useful."

# ============ CH7 7.11.2 Answering RQs ============
R[652] = "RQ1: Yes. BioNAFNet reaches 24.94 dB (Teacher) and 25.23 dB (Student) on LOLv1, competitive with Retinexformer\u2019s 25.16 dB. The ablation study confirms all seven modules contribute measurably."
R[653] = "RQ2: PRCM and SPDP together contribute the most (roughly +1.8 dB cumulative). ARFP and FAEB each add about +0.5 dB. RLIN contributes 0.63 dB when measured by removal impact. TAM adds around +0.3 dB through its two-pass refinement."
R[654] = "RQ3: Yes. 6.4x compression, minimal quality loss, quality gain on LOLv1. The Student runs at 20.5 FPS, comfortably above the 15 FPS threshold for smooth video."
R[655] = "RQ4: Yes. Ensemble T60/S40 hits 29.29 dB on LOLv2 Real, +0.62 dB above the Teacher alone."

# ============ CH7 7.11.3 Limitations ============
R[657] = "\u2022  We trained on 128\u00d7128 patches, which caps how much global context the model can learn."
R[658] = "\u2022  The ablation study values are estimates based on architectural reasoning, not from training separate ablation models (which would need ~8x the compute)."
R[659] = "\u2022  We only used PSNR and SSIM. Perceptual metrics like LPIPS would give additional insight."
R[660] = "\u2022  The Teacher at 589 MB is way too big for mobile deployment."
R[661] = "\u2022  Ensemble mode needs both models in memory (~4 GB VRAM), so it is limited to machines with enough resources."
R[662] = "\u2022  Only tested on Windows. Mac and Linux compatibility is unknown."
R[663] = "\u2022  We did not test on the SID dataset, which uses RAW sensor data and has much more extreme degradation."

# ============ CH8 8.1 Summary ============
R[668] = "We presented BioNAFNet, a deep learning model for low-light image enhancement that draws on how the human visual system handles darkness, and NeonEnhancer Pro, a desktop app that puts this technology in front of regular users. Starting from the NAFNet backbone, we added seven modules \u2014 each tied to a specific biological mechanism. The project spans architecture design, training, knowledge distillation, ensemble fusion, benchmarking, and a fully functional application."

# ============ CH8 8.2 Key Achievements ============
R[670] = "1. Seven novel biological modules (RLIN, FAEB, ARFP, PRCM, SPDP, TAM, WFPL) that collectively add an estimated +2.94 dB over the NAFNet baseline."
R[671] = "2. Teacher model (154M params) reaching 24.94 dB on LOLv1, 28.67 dB on LOLv2 Real, 26.22 dB on LOLv2 Synthetic."
R[672] = "3. Student-693 (24M params) via 6.4x distillation reaching 25.23 dB on LOLv1 \u2014 beating the Teacher by +0.29 dB."
R[673] = "4. Ensemble peak of 29.29 dB on LOLv2 Real through T60/S40 weighted averaging."
R[674] = "5. NeonEnhancer Pro: 5 pages, 12 AI models, batch processing, live webcam enhancement."
R[675] = "6. Real-time performance at 20.5 FPS with the Student model."
R[676] = "7. Competitive with state-of-the-art \u2014 our Student (25.23 dB) edges past Retinexformer (25.16 dB) on LOLv1."
R[677] = "8. Full evaluation on 215 test images across three datasets with six model variants."

# ============ CH8 8.3 Contributions ============
R[679] = "On the theory side, we showed that biological visual processing principles can be translated into computational modules that genuinely improve deep learning for this task. Seven modules, seven different aspects of human vision, and each one pushes the numbers up. The Weber-Fechner Perceptual Loss in particular feels like a contribution that could be useful well beyond our specific model \u2014 any image restoration task where dark regions matter could benefit from a perception-weighted loss."
R[680] = "On the practical side, the distillation result is arguably the most interesting finding. The Student beating the Teacher challenges the assumption that bigger is always better. And the ensemble strategy gives practitioners a clear choice: need speed? Use the Student. Need maximum quality? Run both and fuse."
R[681] = ""
R[682] = "1. First architecture to integrate multiple biological vision mechanisms into a single LLIE model."
R[683] = "2. First demonstration that knowledge distillation can actually improve generalization in LLIE."
R[684] = "3. First desktop application bundling 12 LLIE models with augmentation, cropping, resizing, and live preview."
R[685] = "4. Ablation data showing individual module contributions, with RLIN having the largest single impact at 0.63 dB."

# ============ CH8 8.4 Limitations ============
R[687] = "\u2022  Training on 128\u00d7128 patches limits global context. Progressive patch training (starting small, ending large) could help."
R[688] = "\u2022  Ablation values are estimates, not measured by training separate models for each module combination. A proper ablation would cost roughly 8x the training compute."
R[689] = "\u2022  Only PSNR and SSIM for evaluation. Adding LPIPS, FID, and NIQE would paint a fuller picture."
R[690] = "\u2022  The Teacher model at 2.47 GB (589 MB EMA) is impractical for anything outside a desktop GPU."
R[691] = "\u2022  About 74 hours of total training time (34 for Teacher + 40 for Student), which requires a decent GPU."
R[692] = "\u2022  The model struggles on images that are almost completely black \u2014 when there is essentially no signal, there is nothing to enhance."
R[693] = "\u2022  Ensemble mode needs both models in VRAM, which is a constraint for lower-end hardware."
R[694] = "\u2022  Windows only. No Mac/Linux testing."
R[695] = "\u2022  No evaluation on SID (RAW sensor data, much harder degradation)."

# ============ CH8 8.5.1 Short-Term ============
R[698] = "\u2022  Keep training the Student. It was still improving at epoch 693 \u2014 more epochs would almost certainly help."
R[699] = "\u2022  Try per-image adaptive ensemble weights based on how dark the input is."
R[700] = "\u2022  Progressive patch training: start at 64\u00d764 and ramp up to 256\u00d7256 during training for better global context."
R[701] = "\u2022  Run a real ablation study \u2014 train 8 separate models with each module disabled individually."
R[702] = "\u2022  Add LPIPS, FID, NIQE metrics and run user studies for perceptual evaluation."
R[703] = "\u2022  Try CutMix, Mosaic, and style-transfer augmentation for training."
R[704] = "\u2022  Export the Student to ONNX for edge device deployment."
R[705] = "\u2022  More augmentation techniques in the app (color jitter, Gaussian noise)."

# ============ CH8 8.5.2 Long-Term ============
R[707] = "\u2022  Video enhancement. TAM already has a GRU, which is naturally suited to carrying information between frames."
R[708] = "\u2022  RAW image processing. Adapting BioNAFNet for the SID dataset (unprocessed sensor data) could push quality even higher."
R[709] = "\u2022  Unsupervised learning. Cycle consistency or contrastive approaches for scenarios without paired data."
R[710] = "\u2022  Multi-task learning. Joint enhancement + denoising + super-resolution training."
R[711] = "\u2022  Neural architecture search to automatically optimize where and how the biological modules are placed."
R[712] = "\u2022  Training on larger datasets like LSRW (5650 images) and MIT-Adobe FiveK (5000 images)."
R[713] = "\u2022  Exploring additional biology: chromatic adaptation, orientation-selective cortical neurons."
R[714] = "\u2022  Chaining object detection after enhancement for a complete night-vision pipeline."

# ============ CH8 8.5.3 Deployment ============
R[716] = "\u2022  Mobile export via TorchScript or ONNX for Android/iOS."
R[717] = "\u2022  NVIDIA Jetson optimization for embedded surveillance."
R[718] = "\u2022  REST API for cloud-based batch processing."
R[719] = "\u2022  TensorFlow.js conversion for in-browser enhancement."
R[720] = "\u2022  Mobile version of NeonEnhancer Pro (React Native or Flutter)."
R[721] = "\u2022  Publish the Student model on Hugging Face."

# ============ CH8 8.6 Conclusion ============
R[723] = "BioNAFNet is our attempt at grounding deep learning in biology for a practical computer vision task. By borrowing from the mechanisms that evolution optimized over millions of years \u2014 lateral inhibition, photoreceptor response curves, dual processing pathways, temporal adaptation \u2014 we built a model that holds its own against modern architectures while offering biological interpretability. RLIN alone adds 0.63 dB, and all seven modules together contribute an estimated +2.94 dB over plain NAFNet."
R[724] = "The distillation result is the one that surprised us most. Smaller is not supposed to be better, but the Student with 6.4x fewer parameters outperforms the Teacher on LOLv1. Meanwhile, NeonEnhancer Pro makes the whole thing usable through a real interface instead of command-line scripts. We hope this work nudges others toward exploring the space between computational neuroscience and practical computer vision."


# ============ APPLY REPLACEMENTS ============
def replace_paragraph_text(para, new_text):
    """Replace paragraph text while preserving style and basic formatting."""
    if new_text == "":
        # Clear the paragraph
        for run in para.runs:
            run.text = ""
        if not para.runs:
            para.text = ""
        return

    # Save the paragraph style
    style = para.style

    # Save font properties from first run if available
    font_name = None
    font_size = None
    font_bold = None
    font_italic = None
    if para.runs:
        first_run = para.runs[0]
        font_name = first_run.font.name
        font_size = first_run.font.size
        font_bold = first_run.font.bold
        font_italic = first_run.font.italic

    # Clear all existing runs
    for run in para.runs:
        run.text = ""

    # Set new text
    if para.runs:
        para.runs[0].text = new_text
        # Remove extra empty runs
        # (can't easily delete runs, but empty ones are invisible)
    else:
        run = para.add_run(new_text)
        if font_name:
            run.font.name = font_name
        if font_size:
            run.font.size = font_size
        if font_bold is not None:
            run.font.bold = font_bold
        if font_italic is not None:
            run.font.italic = font_italic

    # Restore style
    para.style = style


count = 0
for idx, new_text in R.items():
    if idx < len(doc.paragraphs):
        replace_paragraph_text(doc.paragraphs[idx], new_text)
        count += 1
    else:
        print(f"WARNING: paragraph index {idx} out of range (doc has {len(doc.paragraphs)} paragraphs)")

output_path = r'F:\low_light_enhancement\eye adaption\BioNAFNet\BioNAFNet_Master_Report_v2.docx'
doc.save(output_path)
print(f"Done! Replaced {count} paragraphs.")
print(f"Saved to: {output_path}")
