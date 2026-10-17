"""
Generate all diagrams for the BioNAFNet Master FYP Report.
Creates 10 diagram subfolders, each with:
  - diagram.mmd  (Mermaid source code for future editing)
  - diagram.png  (Rendered black-and-white PNG image)

Usage: py -3 _generate_diagrams.py
Output: diagrams_only/ folder with 10 subfolders
"""

import base64, json, os, sys, urllib.request, zlib
from PIL import Image

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagrams_only")

# ---------- Black-and-white theme prefix for Mermaid ----------
BW_THEME = (
    "%%{init: {'theme': 'base', 'themeVariables': {"
    "'primaryColor': '#ffffff', "
    "'primaryBorderColor': '#000000', "
    "'primaryTextColor': '#000000', "
    "'lineColor': '#000000', "
    "'secondaryColor': '#f4f4f4', "
    "'tertiaryColor': '#ffffff', "
    "'noteBkgColor': '#ffffff', "
    "'noteTextColor': '#000000', "
    "'actorBkg': '#ffffff', "
    "'actorBorder': '#000000', "
    "'actorTextColor': '#000000', "
    "'signalColor': '#000000', "
    "'signalTextColor': '#000000', "
    "'activationBorderColor': '#000000', "
    "'activationBkgColor': '#f4f4f4', "
    "'classText': '#000000', "
    "'titleColor': '#000000'"
    "}}}%%\n"
)

# ================================================================
#  DIAGRAM DEFINITIONS
# ================================================================

DIAGRAMS = {}

# ------ Figure 4: RLIN Module Architecture ------
DIAGRAMS["Fig04_RLIN_Module_Architecture"] = {
    "caption": "Figure 4: RLIN Module Architecture - Center-Surround Pathways with Subtraction and Scaling",
    "code": """flowchart TB
    Input["Input Feature Map<br>(C channels)"] --> Center["Center Pathway<br>1x1 Convolution"]
    Input --> Surround["Surround Pathway<br>3x3 Convolution"]
    Center --> Sub["Subtraction<br>Center - Surround"]
    Surround --> Sub
    Sub --> Scale["Learnable Scaling<br>(alpha parameter)"]
    Scale --> Add(("Addition (+)"))
    Input --> Add
    Add --> Output["Output Feature Map<br>(C channels)"]
"""
}

# ------ Figure 5: FAEB Module ------
DIAGRAMS["Fig05_FAEB_Module"] = {
    "caption": "Figure 5: FAEB Module - FFT to Amplitude/Phase Processing to iFFT to Blend",
    "code": """flowchart LR
    Input["Input<br>Feature Map"] --> FFT["2D FFT"]
    FFT --> Amp["Amplitude Branch<br>Conv + ReLU + Conv"]
    FFT --> Phase["Phase Branch<br>Conv + ReLU + Conv"]
    Amp --> IFFT["Inverse<br>2D FFT"]
    Phase --> IFFT
    IFFT --> Blend["Blend<br>beta x freq +<br>(1-beta) x spatial"]
    Input --> Blend
    Blend --> Output["Output<br>Feature Map"]
"""
}

# ------ Figure 6: Knowledge Distillation Pipeline ------
DIAGRAMS["Fig06_Knowledge_Distillation_Pipeline"] = {
    "caption": "Figure 6: Knowledge Distillation Pipeline - Teacher (154M) to Student (24M)",
    "code": """flowchart TB
    IMG["Low-Light<br>Input Image"] --> Teacher
    IMG --> Student

    subgraph Teacher ["Teacher Model (154M Parameters)"]
        T1["Width: 64 | Middle Blocks: 12<br>Encoder: 2,2,4,8 | Passes: 2"]
    end

    subgraph Student ["Student Model (24M Parameters)"]
        S1["Width: 32 | Middle Blocks: 4<br>Encoder: 2,2,4,8 | Passes: 1"]
    end

    Teacher --> TO["Teacher<br>Output"]
    Teacher --> TF["Teacher<br>Features"]
    Student --> SO["Student<br>Output"]
    Student --> SF["Student<br>Features"]
    GT["Ground Truth<br>Image"] --> L1["L1 Loss<br>Student vs GT"]
    SO --> L1
    TO --> L2["KD Output Loss<br>Student vs Teacher"]
    SO --> L2
    TF --> L3["Feature Matching Loss<br>Intermediate Layers"]
    SF --> L3
    L1 --> TL["Total Loss =<br>alpha x L1 + beta x KD + gamma x Feature"]
    L2 --> TL
    L3 --> TL
    TL --> BP["Backpropagate<br>Update Student Weights Only"]
"""
}

# ------ Figure 7: BioNAFNet System Architecture Block Diagram ------
DIAGRAMS["Fig07_BioNAFNet_System_Architecture"] = {
    "caption": "Figure 7: BioNAFNet System Architecture Block Diagram",
    "code": """flowchart TB
    IN["Input Image<br>H x W x 3"] --> PRCM["PRCM<br>Pupil Response<br>Calibration Module"]
    PRCM --> SPDP["SPDP<br>Spatial-Dependent<br>Processing"]

    SPDP --> E1["Encoder Level 1<br>2 Blocks + RLIN"]
    E1 --> E2["Encoder Level 2<br>2 Blocks + RLIN"]
    E2 --> E3["Encoder Level 3<br>4 Blocks + RLIN"]
    E3 --> E4["Encoder Level 4<br>8 Blocks + RLIN"]

    E4 --> MID["Middle Blocks<br>12 Blocks + FAEB<br>Frequency Processing"]

    MID --> D4["Decoder Level 4<br>2 Blocks"]
    D4 --> D3["Decoder Level 3<br>2 Blocks"]
    D3 --> D2["Decoder Level 2<br>2 Blocks"]
    D2 --> D1["Decoder Level 1<br>2 Blocks"]

    E4 -. "Skip Connection" .-> D4
    E3 -. "Skip Connection" .-> D3
    E2 -. "Skip Connection" .-> D2
    E1 -. "Skip Connection" .-> D1

    D1 --> ARFP["ARFP<br>Adaptive Residual<br>Feature Processing"]
    ARFP --> OUT["Enhanced Image<br>H x W x 3"]
"""
}

# ------ Figure 9: Use Case Diagram ------
DIAGRAMS["Fig09_Use_Case_Diagram"] = {
    "caption": "Figure 9: Use Case Diagram - User Interactions with NeonEnhancer Pro",
    "code": """flowchart LR
    User(("User"))

    subgraph NeonEnhancer_Pro ["NeonEnhancer Pro System"]
        UC1["Upload Image"]
        UC2["Select AI Model"]
        UC3["Enhance Image"]
        UC4["View Gallery"]
        UC5["Batch Process<br>Multiple Images"]
        UC6["Augment Image"]
        UC7["Crop Image"]
        UC8["Resize Image"]
        UC9["Live Preview<br>Webcam Feed"]
    end

    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    User --> UC8
    User --> UC9

    UC3 --> UC10["Load Model<br>Weights"]
    UC5 --> UC3
"""
}

# ------ Figure 10: Class Diagram ------
DIAGRAMS["Fig10_Class_Diagram"] = {
    "caption": "Figure 10: Class Diagram - NeonEnhancerPro and BioNAFNet Components",
    "code": """classDiagram
    class NeonEnhancerPro {
        +CTk root
        +String current_page
        +show_page(page_name)
        +run()
    }

    class EnhancePage {
        +Dropdown model_dropdown
        +Button enhance_button
        +Frame gallery_frame
        +load_image()
        +run_enhancement()
        +batch_process()
    }

    class AugmentationPage {
        +Slider variations_slider
        +generate_augmentations()
    }

    class CroppingPage {
        +Rectangle crop_region
        +apply_crop()
    }

    class ResizingPage {
        +Slider width_slider
        +Slider height_slider
        +apply_resize()
    }

    class LivePreviewPage {
        +VideoCapture webcam_feed
        +start_preview()
        +stop_preview()
    }

    class BioNAFNet {
        +int width
        +int middle_blk_num
        +list enc_blks
        +list dec_blks
        +int n_passes
        +forward(input) Tensor
    }

    class LateralInhibition {
        +Conv2d center_conv
        +Conv2d surround_conv
        +Parameter alpha
        +forward(x) Tensor
    }

    class FrequencyBranch {
        +Conv2d amp_conv
        +Conv2d phase_conv
        +forward(x) Tensor
    }

    class ARFP {
        +Conv2d conv
        +forward(x) Tensor
    }

    class PRCM {
        +calibrate(x) Tensor
    }

    class SPDP {
        +process(x) Tensor
    }

    class TAM {
        +adapt(x) Tensor
    }

    NeonEnhancerPro --> EnhancePage
    NeonEnhancerPro --> AugmentationPage
    NeonEnhancerPro --> CroppingPage
    NeonEnhancerPro --> ResizingPage
    NeonEnhancerPro --> LivePreviewPage
    EnhancePage ..> BioNAFNet : uses
    BioNAFNet *-- LateralInhibition
    BioNAFNet *-- FrequencyBranch
    BioNAFNet *-- ARFP
    BioNAFNet *-- PRCM
    BioNAFNet *-- SPDP
    BioNAFNet *-- TAM
"""
}

# ------ Figure 11: Activity Diagram ------
DIAGRAMS["Fig11_Activity_Diagram"] = {
    "caption": "Figure 11: Activity Diagram - BioNAFNet Image Enhancement Process",
    "code": """flowchart TB
    Start(["Start"]) --> Load["Load Input Image"]
    Load --> Norm["Normalize Pixel Values<br>to 0-1 Range"]
    Norm --> Pad["Pad Image to Multiple<br>of 2^n for Encoder"]
    Pad --> PRCM["Apply PRCM<br>Pupil Response Calibration"]
    PRCM --> SPDP["Apply SPDP<br>Spatial-Dependent Processing"]
    SPDP --> Enc["Encoder Blocks<br>with RLIN at Each Level"]
    Enc --> FAEB["Apply FAEB<br>Frequency Processing<br>in Middle Blocks"]
    FAEB --> Dec["Decoder Blocks<br>with Skip Connections"]
    Dec --> ARFP["Apply ARFP<br>Adaptive Residual Processing"]
    ARFP --> Res["Add Residual Connection<br>Output = Model Output + Input"]
    Res --> Crop["Crop to Original<br>Image Dimensions"]
    Crop --> Clamp["Clamp Values<br>to 0-1 Range"]
    Clamp --> Save["Save Enhanced<br>Image to Disk"]
    Save --> End(["End"])
"""
}

# ------ Figure 12: Sequence Diagram ------
DIAGRAMS["Fig12_Sequence_Diagram"] = {
    "caption": "Figure 12: Sequence Diagram - Enhancement Process Flow",
    "code": """sequenceDiagram
    actor User
    participant App as NeonEnhancerPro
    participant Thread as Worker Thread
    participant Model as BioNAFNet

    User->>App: Click Enhance Button
    App->>App: Get Selected Model Path
    App->>App: Disable UI Controls
    App->>Thread: Start Enhancement Thread
    Thread->>Model: Load Checkpoint from Disk
    Model-->>Thread: Model Ready
    Thread->>Model: forward(input_tensor)
    Note over Model: PRCM -> SPDP -> Encoder
    Note over Model: FAEB -> Decoder -> ARFP
    Model-->>Thread: Enhanced Tensor
    Thread->>Thread: Convert Tensor to PIL Image
    Thread->>Thread: Save Image to Output Folder
    Thread-->>App: Signal Completion
    App->>App: Enable UI Controls
    App->>App: Update Gallery Display
    App-->>User: Show Enhanced Result
"""
}

# ------ Figure 13: Data Flow Diagram (Level 0) ------
DIAGRAMS["Fig13_Data_Flow_Diagram"] = {
    "caption": "Figure 13: Data Flow Diagram (Level 0) - NeonEnhancer Pro System",
    "code": """flowchart LR
    User(("User")) -->|"Input Images"| System["NeonEnhancer Pro<br>System"]
    User -->|"Model Selection"| System
    User -->|"Enhancement<br>Settings"| System
    System -->|"Enhanced<br>Images"| Output[("Enhanced Images<br>Directory")]
    System -->|"Gallery<br>Display"| User
    System -->|"Metrics<br>and Logs"| Logs[("Log Files")]
    Weights[("Pre-trained Model<br>Checkpoints")] -->|"Model Weights"| System
"""
}

# ------ Figure 41: NeonEnhancer Pro Enhancement Workflow ------
DIAGRAMS["Fig41_Enhancement_Workflow"] = {
    "caption": "Figure 41: NeonEnhancer Pro Complete Enhancement Workflow",
    "code": """flowchart TB
    A["Open<br>NeonEnhancer Pro"] --> B["Navigate to<br>Enhancement Page"]
    B --> C["Upload Image<br>or Select Folder"]
    C --> D["Select AI Model<br>from 12 Options"]
    D --> E{"Single Image<br>or Batch?"}
    E -->|"Single"| F["Click Enhance<br>Button"]
    E -->|"Batch"| G["Click Batch<br>Process Button"]
    F --> H["View Result<br>in Before/After Gallery"]
    G --> H
    H --> I{"Satisfied with<br>Result?"}
    I -->|"Yes"| J["Save Enhanced<br>Image"]
    I -->|"No"| K["Try Different<br>AI Model"]
    K --> D
    J --> L{"Need Post-<br>Processing?"}
    L -->|"Yes"| M["Go to Augmentation<br>or Crop or Resize Page"]
    L -->|"No"| N["Done"]
    M --> N
"""
}


# ================================================================
#  RENDERING FUNCTIONS
# ================================================================

def render_via_mermaid_ink(mermaid_code, output_path, use_bw_theme=True):
    """Download rendered PNG from mermaid.ink API."""
    if use_bw_theme:
        full_code = BW_THEME + mermaid_code
    else:
        full_code = mermaid_code

    payload = json.dumps({"code": full_code, "mermaid": {"theme": "base"}})
    encoded = base64.urlsafe_b64encode(payload.encode()).decode()
    url = f"https://mermaid.ink/img/{encoded}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(output_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"    WARNING: mermaid.ink failed: {e}")
        return False


def render_via_kroki(mermaid_code, output_path, use_bw_theme=True):
    """Fallback: download rendered PNG from kroki.io."""
    if use_bw_theme:
        full_code = BW_THEME + mermaid_code
    else:
        full_code = mermaid_code

    compressed = zlib.compress(full_code.encode(), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode()
    url = f"https://kroki.io/mermaid/png/{encoded}"

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(output_path, "wb") as f:
                f.write(data)
            return True
    except Exception as e:
        print(f"    WARNING: kroki.io failed: {e}")
        return False


def ensure_bw(png_path):
    """Convert PNG to pure black and white (grayscale)."""
    try:
        img = Image.open(png_path)
        gray = img.convert("L")
        # Threshold: anything not white becomes black-ish, keep gradients for readability
        bw = gray.convert("RGB")
        bw.save(png_path, "PNG")
        return True
    except Exception as e:
        print(f"    WARNING: B&W conversion failed: {e}")
        return False


# ================================================================
#  MAIN
# ================================================================

def main():
    print("=" * 60)
    print("  BioNAFNet Diagram Generator")
    print("  Creating 10 diagrams in black and white")
    print("=" * 60)

    # Set temp dir to F: drive (C: is full)
    os.environ["TEMP"] = "F:\\temp_py"
    os.environ["TMP"] = "F:\\temp_py"
    os.makedirs("F:\\temp_py", exist_ok=True)

    os.makedirs(BASE_DIR, exist_ok=True)

    total = len(DIAGRAMS)
    success = 0

    for i, (folder_name, info) in enumerate(DIAGRAMS.items(), 1):
        caption = info["caption"]
        code = info["code"].strip()

        print(f"\n[{i}/{total}] {caption}")

        # Create subfolder
        folder_path = os.path.join(BASE_DIR, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        # Write .mmd file (Mermaid source code)
        mmd_path = os.path.join(folder_path, "diagram.mmd")
        with open(mmd_path, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        print(f"    Saved: diagram.mmd")

        # Render PNG
        png_path = os.path.join(folder_path, "diagram.png")
        rendered = render_via_mermaid_ink(code, png_path)
        if not rendered:
            print("    Trying fallback (kroki.io)...")
            rendered = render_via_kroki(code, png_path)

        if rendered and os.path.exists(png_path):
            size_kb = os.path.getsize(png_path) / 1024
            print(f"    Saved: diagram.png ({size_kb:.1f} KB)")

            # Convert to black and white
            ensure_bw(png_path)
            print(f"    Converted to black and white")
            success += 1
        else:
            print(f"    ERROR: Could not render PNG. Use diagram.mmd on mermaid.live")

    print(f"\n{'=' * 60}")
    print(f"  Results: {success}/{total} diagrams rendered successfully")
    print(f"  Output folder: {BASE_DIR}")
    print(f"{'=' * 60}")

    # Print folder structure
    print(f"\nFolder structure:")
    for folder_name in DIAGRAMS:
        folder_path = os.path.join(BASE_DIR, folder_name)
        files = os.listdir(folder_path)
        print(f"  {folder_name}/")
        for f in sorted(files):
            fpath = os.path.join(folder_path, f)
            sz = os.path.getsize(fpath)
            print(f"    {f} ({sz/1024:.1f} KB)")


if __name__ == "__main__":
    main()
