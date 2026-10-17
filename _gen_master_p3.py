"""
Master FYP Report Generator — Part 3: Chapters 5-6
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from _merge_helpers import *

DIAGRAMS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams_only")


def build_chapter5(doc):
    """Chapter 5: System Architecture / Initial Design"""
    add_heading1(doc, "Chapter 5")
    add_heading2(doc, "System Architecture / Initial Design")

    # 5.1 System Architecture
    add_heading3(doc, "5.1 System Architecture")
    add_para(doc, "5.1.1 Architecture Design Approach", bold=True)
    add_para(doc, "The system has two main parts: the BioNAFNet deep learning model (backend) and the NeonEnhancer Pro desktop application (frontend). Both are built with Python. The model is implemented in PyTorch and the UI uses CustomTkinter. We follow a modular architecture where each biological component is implemented as an independent PyTorch nn.Module. This allows easy addition, removal, or modification of any module without affecting the rest of the system.")

    add_para(doc, "5.1.2 Architecture Design", bold=True)
    add_para(doc, "The system has four layers:")
    layers = [
        "Input Layer: Handles image loading (PIL), format conversion (to tensor), normalization to [0,1] range, and padding to multiples of 16.",
        "Preprocessing Layer: PRCM (photoreceptor curves) followed by SPDP (dual pathway) applied to the normalized input.",
        "Enhancement Core: NAFNet encoder-decoder with RLIN in encoder blocks and FAEB at the bottleneck. For the Teacher model: 2-pass processing with TAM memory.",
        "Output Layer: ARFP (adaptive receptive field) followed by global residual connection, crop padding, clamp to [0,1], and save to disk.",
    ]
    for i, l in enumerate(layers, 1):
        add_list_numbered(doc, f"{i}. {l}")

    add_figure_placeholder(doc, 7, "BioNAFNet System Architecture Block Diagram \u2014 Input \u2192 PRCM \u2192 SPDP \u2192 Encoder+RLIN \u2192 FAEB \u2192 Decoder \u2192 ARFP \u2192 Output",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig07_BioNAFNet_System_Architecture", "diagram.png"))

    add_table_caption(doc, 13, "BioNAFNet Layer-by-Layer Architecture")
    arch_layers = [
        ("Input Conv", "3\u219264", "3\u219232", "H\u00d7W", "\u2014"),
        ("Encoder 1", "2 BioNAFBlocks", "2 BioNAFBlocks", "H\u00d7W", "RLIN"),
        ("Encoder 2", "2 BioNAFBlocks", "2 BioNAFBlocks", "H/2\u00d7W/2", "RLIN"),
        ("Encoder 3", "4 BioNAFBlocks", "4 BioNAFBlocks", "H/4\u00d7W/4", "RLIN"),
        ("Encoder 4", "8 BioNAFBlocks", "8 BioNAFBlocks", "H/8\u00d7W/8", "\u2014"),
        ("Bottleneck", "12 BioNAFBlocks", "4 BioNAFBlocks", "H/16\u00d7W/16", "FAEB"),
        ("Decoder 1-4", "2 blocks each", "2 blocks each", "H/8\u2192H", "\u2014"),
        ("Output", "ARFP+Conv 64\u21923", "ARFP+Conv 32\u21923", "H\u00d7W", "ARFP"),
    ]
    make_table(doc, ["Stage", "Teacher Config", "Student Config", "Resolution", "Key Module"], arch_layers)

    add_para(doc, "5.1.3 Subsystem Architecture", bold=True)
    add_para(doc, "The system consists of the following subsystems:")
    subsystems = [
        "Training Subsystem: Handles data loading, augmentation, forward/backward pass, loss computation, EMA update, validation, and checkpoint saving.",
        "Distillation Subsystem: Extends training with frozen Teacher inference and mimic loss computation.",
        "Inference Subsystem: Loads trained checkpoint, processes single images or batches, computes metrics.",
        "Ensemble Subsystem: Loads both Teacher and Student, computes weighted average of outputs.",
        "Application Subsystem: NeonEnhancer Pro UI with webcam capture, real-time enhancement, display, and user controls.",
    ]
    for s in subsystems:
        add_list_bullet(doc, s)

    # 5.2 NeonEnhancer Pro Application Architecture (from Doc1)
    add_heading3(doc, "5.2 NeonEnhancer Pro Application Architecture")
    add_para(doc, "5.2.1 Application Overview", bold=True)
    add_para(doc, "NeonEnhancer Pro is a desktop application built with Python and CustomTkinter. It has a futuristic dark theme with neon cyan, purple, pink, blue, and green accent colors. The window starts at 1600\u00d71000 pixels with a minimum size of 1400\u00d7900. The application uses particle animations in the background for visual appeal.")

    add_para(doc, "5.2.2 Application Pages", bold=True)
    add_table_caption(doc, 14, "NeonEnhancer Pro Application Pages")
    app_pages = [
        ("Enhance", "Star", "AI-powered image enhancement", "12 model options, CPU/GPU toggle, batch processing, gallery preview"),
        ("Augmentation", "Rotate", "Generate image variations", "Upload multiple images, slider for 1-4 variations, random transforms"),
        ("Cropping", "Scissors", "Crop images with presets", "Square, 16:9, center crop presets, custom coordinates, live preview"),
        ("Resizing", "Ruler", "Resize with aspect ratio", "Width/height sliders, aspect ratio lock, batch resize, quality preview"),
        ("Live Preview", "Camera", "Real-time webcam enhancement", "Webcam capture, model selection, live side-by-side comparison"),
    ]
    make_table(doc, ["Page", "Icon", "Purpose", "Key Features"], app_pages)

    add_para(doc, "5.2.3 Supported AI Models (12 Total)", bold=True)
    add_table_caption(doc, 15, "All 12 Supported Enhancement Models")
    models = [
        ("BioNAFNet Teacher", "Supervised", "154M", "Our model", "Optional"),
        ("BioNAFNet Student", "Supervised", "24M", "Our model (distilled)", "Optional"),
        ("BioNAFNet Ensemble", "Supervised", "178M (both)", "Our fusion model", "Optional"),
        ("Zero-DCE", "Unsupervised", "0.08M", "Guo et al., 2020", "Not needed"),
        ("EnlightenGAN", "Unsupervised", "8.6M", "Jiang et al., 2021", "Not needed"),
        ("SCI", "Unsupervised", "~0.5M", "Ma et al., 2022", "Not needed"),
        ("RUAS", "Unsupervised", "~0.3M", "Liu et al., 2021", "Not needed"),
        ("Retinexformer", "Supervised", "1.6M", "Cai et al., 2023", "Optional"),
        ("MIRNet", "Supervised", "31.8M", "Zamir et al., 2020", "Optional"),
        ("RetinexNet", "Supervised", "0.8M", "Wei et al., 2018", "Optional"),
        ("KinD", "Supervised", "8.2M", "Zhang et al., 2019", "Optional"),
        ("LLFlow", "Supervised", "~38M", "Wang et al., 2022", "Optional"),
    ]
    make_table(doc, ["Model", "Type", "Parameters", "Source", "Ground Truth"], models)
    add_figure_placeholder(doc, 8, "NeonEnhancer Pro Enhance Page \u2014 Model Selection Dropdown with 12 Options")

    # 5.3 Detailed System Design
    add_heading3(doc, "5.3 Detailed System Design")
    add_para(doc, "5.3.1 System Component Hierarchy", bold=True)
    add_table_caption(doc, 16, "System Component Hierarchy")
    components = [
        ("BioNAFNet", "nn.Module", "154M / 24M", "Main enhancement model"),
        ("BioNAFBlock", "nn.Module", "~1.5M / ~0.4M each", "Core processing block with SimpleGate+RLIN"),
        ("LateralInhibition", "nn.Module", "~2K per block", "RLIN center-surround edge enhancement"),
        ("FrequencyBranch", "nn.Module", "~500K", "FAEB FFT-based spectral processing"),
        ("AdaptiveReceptiveField", "nn.Module", "~100K", "ARFP luminance-adaptive output"),
        ("PhotoreceptorCurve", "nn.Module", "3 params", "PRCM input gamma preprocessing"),
        ("DualPathway", "nn.Module", "~50K", "SPDP Y/UV dual processing"),
        ("TemporalAdaptation", "nn.Module", "~200K", "TAM GRU multi-pass memory"),
        ("TotalLoss", "nn.Module", "VGG16 features", "Composite loss function"),
        ("LOLDataset", "Dataset", "\u2014", "Data loading and augmentation"),
        ("EMA", "Helper", "\u2014", "Exponential moving average"),
        ("NeonEnhancerPro", "ctk.CTk", "2708 lines", "Main application window class"),
        ("model_hooks", "Python module", "430 lines", "Model loader and inference functions"),
    ]
    make_table(doc, ["Component", "Type", "Size", "Purpose"], components)

    add_para(doc, "5.3.2 Data Flow", bold=True)
    add_para(doc, "When a user clicks \"Enhance Image\" in NeonEnhancer Pro, the following happens:")
    data_flow = [
        "The selected image file path is passed to the model wrapper function.",
        "The wrapper loads the model if not already cached, loads the image as a PIL Image, converts to a PyTorch tensor.",
        "The tensor is normalized to [0,1], padded to multiples of 16, and moved to the selected device (CPU or GPU).",
        "The model forward pass runs with torch.no_grad() for inference efficiency.",
        "The output tensor is clamped to [0,1], cropped to original size, converted back to PIL Image.",
        "The enhanced image is displayed in the gallery preview and saved to the selected output directory.",
        "If ground truth is available, PSNR and SSIM are computed and displayed.",
    ]
    for i, step in enumerate(data_flow, 1):
        add_list_numbered(doc, f"{i}. {step}")

    add_para(doc, "5.3.3 UML Diagrams", bold=True)
    add_figure_placeholder(doc, 9, "Use Case Diagram \u2014 User interactions: Upload Image, Select Model, Enhance, View Gallery, Batch Process, Augment, Crop, Resize, Live Preview",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig09_Use_Case_Diagram", "diagram.png"))
    add_figure_placeholder(doc, 10, "Class Diagram \u2014 NeonEnhancerPro contains 5 pages; BioNAFNet contains BioNAFBlock, LateralInhibition, FrequencyBranch, ARFP, PRCM, SPDP, TAM",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig10_Class_Diagram", "diagram.png"))
    add_figure_placeholder(doc, 11, "Activity Diagram \u2014 Start \u2192 Load Image \u2192 Normalize \u2192 Pad \u2192 PRCM \u2192 SPDP \u2192 Encoder \u2192 FAEB \u2192 Decoder \u2192 ARFP \u2192 Residual \u2192 Crop \u2192 Clamp \u2192 Save \u2192 End",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig11_Activity_Diagram", "diagram.png"))
    add_figure_placeholder(doc, 12, "Sequence Diagram \u2014 User \u2192 NeonEnhancerPro: click Enhance \u2192 Thread: run model \u2192 BioNAFNet: forward() \u2192 return PIL Image \u2192 update gallery",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig12_Sequence_Diagram", "diagram.png"))
    add_figure_placeholder(doc, 13, "Data Flow Diagram (Level 0) \u2014 User sends images to NeonEnhancer Pro, outputs to Enhanced Images directory",
                          image_path=os.path.join(DIAGRAMS_DIR, "Fig13_Data_Flow_Diagram", "diagram.png"))

    add_para(doc, "5.3.4 Pseudocode: Training Algorithm", bold=True)
    add_para(doc, "Algorithm 1: Teacher Model Training", bold=True)
    algo1 = """INPUT: Dataset D, BioNAFNet model M, epochs N=504
INIT: AdamW optimizer, EMA (decay=0.9995), LR scheduler
FOR epoch = 1 TO N:
    FOR each batch (low, high) IN D:
        enhanced = M.forward(low)
        loss = TotalLoss(enhanced, high)
        loss.backward()
        IF step % 2 == 0: optimizer.step()  // gradient accumulation
        EMA.update(M)
    END FOR
    val_psnr = validate(EMA_model, val_set)
    IF val_psnr > best: save_checkpoint("best.pth")
    scheduler.step()
END FOR"""
    add_para(doc, algo1)

    add_para(doc, "Algorithm 2: Knowledge Distillation", bold=True)
    algo2 = """INPUT: Frozen Teacher T, Student S, Dataset D, epochs N=693
FOR epoch = 1 TO N:
    FOR each batch (low, high) IN D:
        WITH no_grad: teacher_out = T(low)
        student_out = S(low)
        loss = 0.5*L1(student,high) + 0.1*SSIM(student,high) + 0.4*L2(student, teacher_out)
        loss.backward(); optimizer.step(); EMA.update(S)
    END FOR
END FOR"""
    add_para(doc, algo2)

    add_para(doc, "Algorithm 3: Ensemble Inference", bold=True)
    algo3 = """INPUT: Teacher T, Student S, image I, alpha
teacher_out = T(I)
student_out = S(I)
ensemble_out = alpha * teacher_out + (1-alpha) * student_out
RETURN clamp(ensemble_out, 0, 1)"""
    add_para(doc, algo3)
    add_page_break(doc)


def build_chapter6(doc):
    """Chapter 6: Implementation and Testing"""
    add_heading1(doc, "Chapter 6")
    add_heading2(doc, "Implementation and Testing")

    # 6.1 Implementation Overview
    add_heading3(doc, "6.1 Implementation Overview")
    add_para(doc, "The BioNAFNet system was implemented entirely in Python using the PyTorch deep learning framework. The desktop application uses CustomTkinter 5.2 for the modern dark-themed UI. The total codebase is about 5,500 lines of Python code across 12 files. Training was done on an NVIDIA RTX GPU with CUDA 12. We followed a single-file-per-model approach where each script contains the complete model definition, loss functions, dataset class, and training/testing logic. This self-contained approach means each script can run independently without dependency issues.")

    # 6.2 Code Structure
    add_heading3(doc, "6.2 Code Structure")
    add_table_caption(doc, 17, "Project Code File Structure")
    code_files = [
        ("train_bionafnet.py", "~1100 lines", "Teacher model training with all losses"),
        ("train_distillation.py", "~1100 lines", "Student knowledge distillation training"),
        ("neon_enhancer_pro.py", "2708 lines", "Main NeonEnhancer Pro application"),
        ("model_hooks.py", "430 lines", "Model loading and inference wrappers for all 12 models"),
        ("bionafnet_teacher.py", "97 lines", "Teacher model wrapper (154M, cached loading)"),
        ("bionafnet_student.py", "96 lines", "Student model wrapper (24M, cached loading)"),
        ("bionafnet_ensemble.py", "46 lines", "Ensemble fusion wrapper (Teacher + Student blending)"),
        ("eval_lol_datasets.py", "~800 lines", "Full evaluation script for PSNR/SSIM benchmarking"),
        ("ensemble_test.py", "~450 lines", "Ensemble testing across all fusion strategies"),
        ("benchmark_all_models.py", "~450 lines", "Speed benchmarking for all 6 model variants"),
        ("infer_bionafnet.py", "~700 lines", "Single-image inference and enhancement"),
        ("test_distilled.py", "~14 KB", "Standalone Student testing on LOL datasets"),
    ]
    make_table(doc, ["File", "Size", "Purpose"], code_files)

    # 6.3 Key Implementation Details
    add_heading3(doc, "6.3 Key Implementation Details")
    add_para(doc, "6.3.1 SimpleGate Mechanism", bold=True)
    add_para(doc, "The core of NAFNet is the SimpleGate that replaces activation functions. The input tensor is split along the channel dimension into two equal halves, which are then multiplied element-wise: x1, x2 = x.chunk(2, dim=1); output = x1 * x2. Unlike ReLU which clips negative values to zero (losing information), SimpleGate preserves all information through multiplicative gating.")

    add_para(doc, "6.3.2 Exponential Moving Average (EMA)", bold=True)
    add_para(doc, "We use EMA to keep a shadow copy of the model weights with a decay of 0.9995. After each training step, the shadow weights are updated as: ema_weight = 0.9995 * ema_weight + 0.0005 * current_weight. During testing, we use the EMA weights because they give smoother and better results than the raw training weights. All our benchmark results use EMA weights.")

    add_para(doc, "6.3.3 Automatic Mixed Precision (AMP)", bold=True)
    add_para(doc, "Training uses float16 for most operations to save GPU memory and speed up training. But we keep float32 for the FFT operations in FAEB because half-precision causes numerical overflow in frequency domain computations. PyTorch autocast handles this switching automatically. Loss scaling prevents underflow in float16 gradient computation.")

    add_para(doc, "6.3.4 Padding Strategy", bold=True)
    add_para(doc, "The 4-level encoder-decoder reduces spatial resolution by 16x (4 downsamplings of 2x each). So input images must have dimensions divisible by 16. We use reflection padding to extend images to the nearest multiple of 16, then crop the output back to original size. Reflection padding avoids black border artifacts that zero padding would create.")

    add_para(doc, "6.3.5 Model Caching", bold=True)
    add_para(doc, "The Teacher model is 2.47 GB. Loading it from disk takes about 8-10 seconds. Our model wrappers cache the loaded model in a Python dictionary keyed by device. So the first enhancement call is slow but all subsequent calls are instant. This is important for batch processing where the user may enhance 100+ images.")

    add_para(doc, "6.3.6 Checkpoint Management", bold=True)
    add_para(doc, "We save two checkpoint files during training: best.pth (highest validation PSNR) and latest.pth (most recent epoch). Each checkpoint contains: model state dict, EMA state dict, optimizer state dict, and best_psnr value. For inference, we always load the EMA weights from the best checkpoint.")

    # 6.4 NeonEnhancer Pro Application Features (from Doc1)
    add_heading3(doc, "6.4 NeonEnhancer Pro Application Features")

    add_para(doc, "6.4.1 Enhancement Page", bold=True)
    add_para(doc, "The Enhancement page is the main feature. On the left is a control panel with: upload buttons for images and folders, save directory selection, model dropdown with 12 options, CPU/GPU toggle switch, and the main \"ENHANCE IMAGE\" button. On the right is a split-screen gallery showing Original vs Enhanced side by side. Users can navigate through batch results with Previous/Next buttons. The page counter shows the current image number.")
    add_figure_placeholder(doc, 14, "Enhancement Page \u2014 After processing a batch with BioNAFNet Student, showing before/after gallery (1 / 15)")

    add_para(doc, "6.4.2 Augmentation Page", bold=True)
    add_para(doc, "The Augmentation page lets users generate multiple random variations of their images. Users upload images, select a save folder, and use a slider to choose 1 to 4 variations per image. The augmentations include random rotation, horizontal/vertical flipping, brightness adjustment, contrast adjustment, and noise addition. Each variation is saved with a unique filename. This is useful for expanding small datasets for training.")
    add_figure_placeholder(doc, 15, "Augmentation Page \u2014 Slider set to 3 variations with augmented image preview")

    add_para(doc, "6.4.3 Cropping Page", bold=True)
    add_para(doc, "The Cropping page provides three preset aspect ratios (square 1:1, wide 16:9, center crop) plus custom coordinates. Users can see a live preview of the crop region overlaid on the original image. The crop can be applied to single or multiple images at once.")
    add_figure_placeholder(doc, 16, "Cropping Page \u2014 Image with crop region highlighted and preset buttons visible")

    add_para(doc, "6.4.4 Resizing Page", bold=True)
    add_para(doc, "The Resizing page has width and height sliders with an aspect ratio lock toggle. When locked, changing the width automatically adjusts the height to maintain proportions and vice versa. Users can resize individual images or batch process entire folders.")
    add_figure_placeholder(doc, 17, "Resizing Page \u2014 Width/height sliders with aspect ratio lock toggle")

    add_para(doc, "6.4.5 Live Preview Page", bold=True)
    add_para(doc, "The Live Preview page connects to the system\u2019s webcam and shows a real-time enhancement preview. Users can select any of the 12 models and see the enhanced feed alongside the raw webcam feed. The Student model runs at 20+ FPS which makes the live preview smooth and responsive.")
    add_figure_placeholder(doc, 18, "Live Preview Page \u2014 Webcam feed (left) vs Enhanced version (right) with FPS counter")

    # 6.5 Training Process
    add_heading3(doc, "6.5 Training Process")
    add_para(doc, "6.5.1 Teacher Model Training", bold=True)
    add_para(doc, "The Teacher model was trained for 504 epochs on the combined dataset of 2074 image pairs (LOLv1 + LOLv2 Real + LOLv2 Synthetic). Training patches of 128\u00d7128 pixels were randomly cropped from the images. Data augmentation included random horizontal and vertical flips, 90-degree rotations, and MixUp with alpha=0.2. The CosineAnnealingWarmRestarts scheduler cycled the learning rate between 2e-4 and 1e-6 with restart periods of 50, 100, 200, and 400 epochs.")
    add_para(doc, "The training loss decreased from 0.6061 (epoch 1) to 0.2341 (epoch 504). Validation PSNR progressed from about 18 dB to a best of 25.05 dB at epoch 476. Training was stable throughout with no divergence events, thanks to gradient clipping at 0.5 and gradient accumulation over 2 steps.")
    add_figure_placeholder(doc, 19, "Teacher Model Training Curves \u2014 PSNR and Loss Over 504 Epochs")
    add_figure_placeholder(doc, 20, "Teacher Model \u2014 Early vs Late Training Convergence")

    add_para(doc, "6.5.2 Student Model Training (Distillation)", bold=True)
    add_para(doc, "The Student model was trained for 693 epochs with the frozen Teacher providing reference outputs for mimic loss. The Student loss is much lower (0.03-0.11 range) compared to the Teacher loss (0.23-0.61) because it combines lightweight L1 and SSIM losses with mimic loss rather than the Teacher\u2019s full composite loss. Validation PSNR reached 25.09 dB at epoch 693, showing the model was still improving and could benefit from more training.")
    add_figure_placeholder(doc, 21, "Student Model Distillation Training Curves \u2014 PSNR and Loss Over 693 Epochs")
    add_figure_placeholder(doc, 22, "Training Loss Comparison: Teacher vs Student")
    add_figure_placeholder(doc, 23, "Teacher vs Student \u2014 Validation PSNR Convergence")
    add_figure_placeholder(doc, 24, "Teacher vs Student \u2014 Validation SSIM Over Training")
    add_figure_placeholder(doc, 25, "Learning Rate Schedule for Both Models (CosineAnnealingWarmRestarts)")

    # 6.6 Testing Methodology
    add_heading3(doc, "6.6 Testing Methodology")
    add_para(doc, "All models are evaluated on full-resolution test images (not patches) using the EMA weights. The testing process loads each image, normalizes to [0,1], pads to multiples of 16, runs the forward pass with torch.no_grad(), crops the output, and computes PSNR and SSIM against the ground truth. Enhanced images are saved to separate output directories for visual inspection.")
    add_table_caption(doc, 18, "Test Set Details")
    test_sets = [
        ("LOLv1 Test", "15", "400\u00d7600", "Wei et al., 2018"),
        ("LOLv2 Real Test", "100", "Various", "Yang et al., 2021"),
        ("LOLv2 Synthetic Test", "100", "Various", "Yang et al., 2021"),
        ("Total", "215", "\u2014", "\u2014"),
    ]
    make_table(doc, ["Test Set", "Images", "Resolution", "Source"], test_sets)

    # 6.7 Unit Testing
    add_heading3(doc, "6.7 Unit Testing")
    add_table_caption(doc, 19, "Unit Test Results")
    unit_tests = [
        ("PRCM", "Output values in [0,1] for input [0,1]", "Pass"),
        ("SPDP", "YUV conversion and dual pathway produce valid output", "Pass"),
        ("RLIN", "Center-surround difference produces bounded output", "Pass"),
        ("FAEB", "FFT\u2192iFFT roundtrip preserves input (identity test)", "Pass"),
        ("ARFP", "Softmax weights sum to 1.0", "Pass"),
        ("TAM", "GRU hidden state dimensions correct across passes", "Pass"),
        ("WFPL", "Loss value is non-negative and finite", "Pass"),
        ("BioNAFNet", "Forward pass produces correct output dimensions", "Pass"),
        ("TotalLoss", "All 6 loss components compute without errors", "Pass"),
        ("LOLDataset", "Correct number of pairs loaded per dataset", "Pass"),
        ("Model loads", "Teacher and Student load from checkpoints", "Pass"),
        ("Output range", "Enhanced pixels in [0, 255] after conversion", "Pass"),
        ("Batch processing", "10 images in \u2192 10 output files saved", "Pass"),
        ("GPU matches CPU", "Same input \u2192 similar outputs on both devices", "Pass"),
        ("Model caching", "Second inference call loads in < 1ms", "Pass"),
        ("Ensemble blend", "T50/S50 = mean of both outputs", "Pass"),
    ]
    make_table(doc, ["Module / Test Case", "Expected Result", "Status"], unit_tests)

    # 6.8 Integration Testing
    add_heading3(doc, "6.8 Integration Testing")
    add_para(doc, "Integration testing verified the complete training and application pipeline works end-to-end. A small subset of training data (10 pairs) was used to train for 5 epochs, verifying that: (a) loss decreases, (b) validation PSNR increases, (c) checkpoints are saved correctly, (d) EMA weights are updated, and (e) the learning rate scheduler follows the expected pattern.")
    add_table_caption(doc, 20, "Integration Test Results")
    int_tests = [
        ("UI loads all 12 models", "UI + model_hooks", "Dropdown shows 12 options", "Pass"),
        ("CPU/GPU toggle works", "UI + PyTorch", "Model moves to correct device", "Pass"),
        ("Batch enhancement E2E", "UI + model + filesystem", "All images enhanced and saved", "Pass"),
        ("Gallery navigation", "UI + batch results", "Previous/Next buttons work", "Pass"),
        ("Ground truth metrics", "UI + PSNR/SSIM calc", "Metrics displayed when GT provided", "Pass"),
        ("Augmentation pipeline", "UI + PIL transforms", "Correct number of variations", "Pass"),
        ("Crop presets", "UI + image processing", "Square crop produces 1:1 image", "Pass"),
        ("Resize aspect ratio", "UI + PIL resize", "Locked ratio preserved", "Pass"),
        ("Webcam live feed", "UI + cv2.VideoCapture", "Real-time feed displayed", "Pass"),
    ]
    make_table(doc, ["Test Case", "Components", "Expected", "Result"], int_tests)

    # 6.9 Software Quality
    add_heading3(doc, "6.9 Software Quality")
    add_para(doc, "Code quality was maintained through: consistent naming conventions (snake_case for functions, CamelCase for classes), comprehensive inline comments explaining each biological module, modular design with each component as an independent nn.Module, deterministic initialization with seed=42 for reproducibility, model weight caching for performance, error handling for missing checkpoints, reflection padding for arbitrary image sizes, and thread-based inference to keep the UI responsive during batch processing. The self-contained single-file approach means anyone can run training or testing by simply executing a single Python script.")
    add_page_break(doc)


if __name__ == "__main__":
    from docx import Document
    doc = Document()
    setup_styles(doc)
    build_chapter5(doc)
    build_chapter6(doc)
    doc.save("_test_p3.docx")
    print("Part 3 done.")
