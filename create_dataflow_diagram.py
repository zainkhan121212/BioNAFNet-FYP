"""
create_dataflow_diagram.py
Generates a clean black-and-white Data Flow Diagram for BioNAFNet Teacher Model.
Shows how the image data transforms at each stage.
"""
import base64, zlib, urllib.request, os

PLANTUML_CODE = r"""
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontColor #000000
skinparam defaultFontName Arial
skinparam defaultFontSize 13
skinparam ArrowColor #000000
skinparam RectangleBorderColor #000000
skinparam RectangleBackgroundColor #FFFFFF
skinparam shadowing false
skinparam padding 8
skinparam ranksep 25
skinparam nodesep 30

title BioNAFNet Teacher Model - Data Flow Diagram

rectangle "**User Input**\nLow-light image file\n(JPG or PNG format)" as INPUT

rectangle "**Open and Convert**\nRead image file\nConvert to RGB format\nShape: (H, W, 3)" as OPEN

rectangle "**Normalize**\nDivide pixels by 255\nRange changes: [0-255] to [0.0-1.0]" as NORM

rectangle "**Reshape Tensor**\nReorder: (H, W, 3) to (3, H, W)\nAdd batch: (3, H, W) to (1, 3, H, W)" as RESHAPE

rectangle "**Move to Device**\nSend tensor to GPU\nor keep on CPU" as DEVICE

rectangle "**PRCM (Novelty 4)**\nInput: raw tensor\nProcess: adjust brightness curve\nOutput: brightness adjusted tensor" as PRCM

rectangle "**SPDP (Novelty 5)**\nInput: PRCM output\nProcess: split dark and color vision\nOutput: merged dual pathway tensor" as SPDP

rectangle "**Luminance Map**\nInput: original tensor\nProcess: calculate brightness per pixel\nOutput: (1, 1, H, W) brightness map" as LUM

rectangle "**Intro Conv**\nInput: SPDP tensor (1, 3, H, W)\nProcess: expand channels\nOutput: (1, 64, H, W) feature maps" as INTRO

rectangle "**Encoder Level 1** - RLIN fires\nInput: 64 channels\nProcess: 2 blocks + downsample\nOutput: 128 channels, H/2 x W/2\nSkip connection saved" as ENC1

rectangle "**Encoder Level 2** - RLIN fires\nInput: 128 channels\nProcess: 2 blocks + downsample\nOutput: 256 channels, H/4 x W/4\nSkip connection saved" as ENC2

rectangle "**Encoder Level 3** - RLIN fires\nInput: 256 channels\nProcess: 4 blocks + downsample\nOutput: 512 channels, H/8 x W/8\nSkip connection saved" as ENC3

rectangle "**Encoder Level 4** - RLIN fires\nInput: 512 channels\nProcess: 8 blocks + downsample\nOutput: 1024 channels, H/16 x W/16\nSkip connection saved" as ENC4

rectangle "**Bottleneck**\nInput: 1024 channels\nProcess: 12 deep blocks\nOutput: 1024 channels" as MID

rectangle "**FAEB (Novelty 2)**\nInput: bottleneck features\nProcess: FFT to frequency domain\nFix amplitude and phase\niFFT back to spatial domain\nOutput: cleaned deep features" as FAEB

rectangle "**Decoder Level 4**\nInput: 1024 channels\nProcess: upsample + skip from Encoder 4\nOutput: 512 channels, H/8 x W/8" as DEC4

rectangle "**Decoder Level 3**\nInput: 512 channels\nProcess: upsample + skip from Encoder 3\nOutput: 256 channels, H/4 x W/4" as DEC3

rectangle "**Decoder Level 2**\nInput: 256 channels\nProcess: upsample + skip from Encoder 2\nOutput: 128 channels, H/2 x W/2" as DEC2

rectangle "**Decoder Level 1**\nInput: 128 channels\nProcess: upsample + skip from Encoder 1\nOutput: 64 channels, H x W" as DEC1

rectangle "**ARFP (Novelty 3)**\nInput: decoded features + luminance map\nProcess: adapt focus per brightness area\nOutput: focused feature maps" as ARFP

rectangle "**Ending Conv**\nInput: 64 channel features\nProcess: compress channels\nOutput: (1, 3, H, W) RGB tensor" as ENDING

rectangle "**Add Residual**\nInput: ending output + original input\nProcess: element-wise addition\nOutput: corrected RGB tensor" as RESID

rectangle "**Pass 2 Repeat**\nInput: Pass 1 output tensor\nProcess: same Encoder-Bottleneck-Decoder\nOutput: refined Pass 2 tensor" as PASS2

rectangle "**TAM (Novelty 6)**\nInput: Pass 1 tensor + Pass 2 tensor\nProcess: GRU memory combines both\nOutput: final enhanced tensor" as TAM

rectangle "**Post Processing**\nClamp values to [0.0, 1.0]\nRemove batch dim: (1,3,H,W) to (3,H,W)\nReorder: (3,H,W) to (H,W,3)\nMultiply by 255 for pixel range" as POST

rectangle "**Convert to Image**\nInput: numpy array (H, W, 3)\nProcess: convert to PIL Image\nOutput: enhanced RGB image" as CONVERT

rectangle "**Save Output**\nSave enhanced image to disk\nDisplay in application gallery" as SAVE

INPUT --> OPEN
OPEN --> NORM
NORM --> RESHAPE
RESHAPE --> DEVICE
DEVICE --> PRCM
PRCM --> SPDP
SPDP --> INTRO
DEVICE --> LUM
LUM --> ARFP
INTRO --> ENC1
ENC1 --> ENC2
ENC2 --> ENC3
ENC3 --> ENC4
ENC4 --> MID
MID --> FAEB
FAEB --> DEC4
DEC4 --> DEC3
DEC3 --> DEC2
DEC2 --> DEC1
DEC1 --> ARFP
ARFP --> ENDING
ENDING --> RESID
RESID --> PASS2
PASS2 --> TAM
TAM --> POST
POST --> CONVERT
CONVERT --> SAVE

ENC4 ..> DEC4 : skip
ENC3 ..> DEC3 : skip
ENC2 ..> DEC2 : skip
ENC1 ..> DEC1 : skip

@enduml
"""

MERMAID_CODE = """
flowchart TD
    INPUT["<b>User Input</b><br>Low-light image file<br>JPG or PNG format"]
    OPEN["<b>Open and Convert</b><br>Read image file<br>Convert to RGB format<br>Shape: H x W x 3"]
    NORM["<b>Normalize</b><br>Divide pixels by 255<br>Range: 0-255 to 0.0-1.0"]
    RESHAPE["<b>Reshape Tensor</b><br>Reorder: H,W,3 to 3,H,W<br>Add batch: 3,H,W to 1,3,H,W"]
    DEVICE["<b>Move to Device</b><br>Send tensor to GPU or CPU"]
    PRCM["<b>PRCM - Novelty 4</b><br>Input: raw tensor<br>Process: adjust brightness curve<br>Output: brightness adjusted tensor"]
    SPDP["<b>SPDP - Novelty 5</b><br>Input: PRCM output<br>Process: split dark and color vision<br>Output: merged dual pathway tensor"]
    LUM["<b>Luminance Map</b><br>Input: original tensor<br>Process: brightness per pixel<br>Output: 1,1,H,W brightness map"]
    INTRO["<b>Intro Conv</b><br>Input: 1,3,H,W SPDP tensor<br>Process: expand channels<br>Output: 1,64,H,W feature maps"]
    ENC1["<b>Encoder Level 1 - RLIN fires</b><br>Input: 64 channels<br>2 blocks then downsample<br>Output: 128 ch, H/2 x W/2<br>Skip connection saved"]
    ENC2["<b>Encoder Level 2 - RLIN fires</b><br>Input: 128 channels<br>2 blocks then downsample<br>Output: 256 ch, H/4 x W/4<br>Skip connection saved"]
    ENC3["<b>Encoder Level 3 - RLIN fires</b><br>Input: 256 channels<br>4 blocks then downsample<br>Output: 512 ch, H/8 x W/8<br>Skip connection saved"]
    ENC4["<b>Encoder Level 4 - RLIN fires</b><br>Input: 512 channels<br>8 blocks then downsample<br>Output: 1024 ch, H/16 x W/16<br>Skip connection saved"]
    MID["<b>Bottleneck</b><br>Input: 1024 channels<br>12 deep blocks<br>Output: 1024 channels"]
    FAEB["<b>FAEB - Novelty 2</b><br>Input: bottleneck features<br>FFT to frequency domain<br>Fix amplitude and phase<br>iFFT back to spatial<br>Output: cleaned deep features"]
    DEC4["<b>Decoder Level 4</b><br>Input: 1024 channels<br>Upsample plus skip from Encoder 4<br>Output: 512 ch, H/8 x W/8"]
    DEC3["<b>Decoder Level 3</b><br>Input: 512 channels<br>Upsample plus skip from Encoder 3<br>Output: 256 ch, H/4 x W/4"]
    DEC2["<b>Decoder Level 2</b><br>Input: 256 channels<br>Upsample plus skip from Encoder 2<br>Output: 128 ch, H/2 x W/2"]
    DEC1["<b>Decoder Level 1</b><br>Input: 128 channels<br>Upsample plus skip from Encoder 1<br>Output: 64 ch, H x W"]
    ARFP["<b>ARFP - Novelty 3</b><br>Input: decoded features plus luminance map<br>Process: adapt focus per brightness<br>Output: focused feature maps"]
    ENDING["<b>Ending Conv</b><br>Input: 64 channel features<br>Compress channels<br>Output: 1,3,H,W RGB tensor"]
    RESID["<b>Add Residual</b><br>Input: ending output plus original input<br>Element-wise addition<br>Output: corrected RGB tensor"]
    PASS2["<b>Pass 2 Repeat</b><br>Input: Pass 1 output tensor<br>Same Encoder-Bottleneck-Decoder<br>Output: refined Pass 2 tensor"]
    TAM["<b>TAM - Novelty 6</b><br>Input: Pass 1 plus Pass 2 tensors<br>GRU memory combines both<br>Output: final enhanced tensor"]
    POST["<b>Post Processing</b><br>Clamp to 0.0-1.0<br>Remove batch dim<br>Reorder to H,W,3<br>Multiply by 255"]
    CONVERT["<b>Convert to Image</b><br>Input: numpy array H,W,3<br>Convert to PIL Image<br>Output: enhanced RGB image"]
    SAVE["<b>Save Output</b><br>Save enhanced image to disk<br>Display in application gallery"]

    INPUT --> OPEN --> NORM --> RESHAPE --> DEVICE
    DEVICE --> PRCM --> SPDP --> INTRO
    DEVICE --> LUM
    LUM --> ARFP
    INTRO --> ENC1 --> ENC2 --> ENC3 --> ENC4
    ENC4 --> MID --> FAEB
    FAEB --> DEC4 --> DEC3 --> DEC2 --> DEC1
    DEC1 --> ARFP --> ENDING --> RESID
    RESID --> PASS2 --> TAM
    TAM --> POST --> CONVERT --> SAVE

    ENC4 -.->|skip| DEC4
    ENC3 -.->|skip| DEC3
    ENC2 -.->|skip| DEC2
    ENC1 -.->|skip| DEC1

    style INPUT fill:#fff,stroke:#000,color:#000
    style OPEN fill:#fff,stroke:#000,color:#000
    style NORM fill:#fff,stroke:#000,color:#000
    style RESHAPE fill:#fff,stroke:#000,color:#000
    style DEVICE fill:#fff,stroke:#000,color:#000
    style PRCM fill:#fff,stroke:#000,color:#000
    style SPDP fill:#fff,stroke:#000,color:#000
    style LUM fill:#fff,stroke:#000,color:#000
    style INTRO fill:#fff,stroke:#000,color:#000
    style ENC1 fill:#fff,stroke:#000,color:#000
    style ENC2 fill:#fff,stroke:#000,color:#000
    style ENC3 fill:#fff,stroke:#000,color:#000
    style ENC4 fill:#fff,stroke:#000,color:#000
    style MID fill:#fff,stroke:#000,color:#000
    style FAEB fill:#fff,stroke:#000,color:#000
    style DEC4 fill:#fff,stroke:#000,color:#000
    style DEC3 fill:#fff,stroke:#000,color:#000
    style DEC2 fill:#fff,stroke:#000,color:#000
    style DEC1 fill:#fff,stroke:#000,color:#000
    style ARFP fill:#fff,stroke:#000,color:#000
    style ENDING fill:#fff,stroke:#000,color:#000
    style RESID fill:#fff,stroke:#000,color:#000
    style PASS2 fill:#fff,stroke:#000,color:#000
    style TAM fill:#fff,stroke:#000,color:#000
    style POST fill:#fff,stroke:#000,color:#000
    style CONVERT fill:#fff,stroke:#000,color:#000
    style SAVE fill:#fff,stroke:#000,color:#000
"""


def render_via_kroki(diagram_type, code, output_path):
    compressed = zlib.compress(code.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode()
    url = f"https://kroki.io/{diagram_type}/png/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()
            with open(output_path, "wb") as f:
                f.write(data)
        print(f"Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False


out_dir = r"F:\low_light_enhancement\eye adaption\BioNAFNet\thesis_figures"
os.makedirs(out_dir, exist_ok=True)

plantuml_path = os.path.join(out_dir, "dataflow_diagram_plantuml.png")
render_via_kroki("plantuml", PLANTUML_CODE, plantuml_path)

mermaid_path = os.path.join(out_dir, "dataflow_diagram_mermaid.png")
render_via_kroki("mermaid", MERMAID_CODE, mermaid_path)
