"""
create_architecture_diagram.py
Generates a clean Architecture Diagram of the BioNAFNet Teacher Model.
Uses PlantUML for clean straight arrows and neat spacing.
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
skinparam RectangleBackgroundColor #F0F4FF
skinparam ComponentBorderColor #000000
skinparam ComponentBackgroundColor #F0F4FF
skinparam shadowing false
skinparam padding 10
skinparam ranksep 30
skinparam nodesep 40

title BioNAFNet Teacher Model - Architecture Diagram

rectangle "Dark Input Image\n(H x W x 3)" as INPUT #FFE0B2

rectangle "**PRCM (Novelty 4)**\nAdjust Brightness\nLike Pupil Dilation" as PRCM #E8F5E9

rectangle "**SPDP (Novelty 5)**\nSplit into Rod & Cone Vision\nThen Merge Both" as SPDP #E8F5E9

rectangle "Compute Brightness Map\n(Used Later by ARFP)" as LUM #FFF3E0

rectangle "**Intro Conv**\n3 channels to 64 channels" as INTRO #E3F2FD

rectangle "**Encoder Level 1** (2 blocks)\nRLIN (Novelty 1) - Edge Sharpen\nDownsample: halve size" as ENC1 #BBDEFB
rectangle "**Encoder Level 2** (2 blocks)\nRLIN (Novelty 1) - Edge Sharpen\nDownsample: halve size" as ENC2 #BBDEFB
rectangle "**Encoder Level 3** (4 blocks)\nRLIN (Novelty 1) - Edge Sharpen\nDownsample: halve size" as ENC3 #BBDEFB
rectangle "**Encoder Level 4** (8 blocks)\nRLIN (Novelty 1) - Edge Sharpen\nDownsample: halve size" as ENC4 #BBDEFB

rectangle "**Bottleneck** (12 blocks)\nDeepest Processing Point" as MID #D1C4E9

rectangle "**FAEB (Novelty 2)**\nClean Noise in Frequency Domain\nFFT -> Fix -> iFFT" as FAEB #E8F5E9

rectangle "**Decoder Level 4** (2 blocks)\nUpsample + Skip from Encoder 4" as DEC4 #C8E6C9
rectangle "**Decoder Level 3** (2 blocks)\nUpsample + Skip from Encoder 3" as DEC3 #C8E6C9
rectangle "**Decoder Level 2** (2 blocks)\nUpsample + Skip from Encoder 2" as DEC2 #C8E6C9
rectangle "**Decoder Level 1** (2 blocks)\nUpsample + Skip from Encoder 1" as DEC1 #C8E6C9

rectangle "**ARFP (Novelty 3)**\nAdapt Focus Using\nBrightness Map" as ARFP #E8F5E9

rectangle "**Ending Conv**\n64 channels back to 3 (RGB)" as ENDING #E3F2FD

rectangle "**Add Residual**\nOutput + Original Input" as RESID #FFF3E0

rectangle "**Pass 2**\nSame Encoder-Bottleneck-Decoder\nRuns Again on Pass 1 Output" as PASS2 #FFECB3

rectangle "**TAM (Novelty 6)**\nCombine Pass 1 & Pass 2\nUsing GRU Memory Cell" as TAM #E8F5E9

rectangle "Enhanced Output Image\n(H x W x 3)" as OUTPUT #A5D6A7

INPUT --> PRCM
PRCM --> SPDP
SPDP --> LUM
LUM --> INTRO
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
TAM --> OUTPUT

ENC1 -[hidden]right-> LUM
ENC4 ..> DEC4 : skip connection
ENC3 ..> DEC3 : skip connection
ENC2 ..> DEC2 : skip connection
ENC1 ..> DEC1 : skip connection

@enduml
"""

MERMAID_CODE = """
---
config:
  theme: base
  themeVariables:
    primaryColor: "#F0F4FF"
    primaryBorderColor: "#000000"
    lineColor: "#000000"
    textColor: "#000000"
    fontSize: "14px"
---
flowchart TD
    INPUT["Dark Input Image<br>(H x W x 3)"]
    PRCM["<b>PRCM - Novelty 4</b><br>Adjust Brightness<br>Like Pupil Dilation"]
    SPDP["<b>SPDP - Novelty 5</b><br>Split Rod and Cone Vision<br>Then Merge Both"]
    LUM["Compute Brightness Map<br>Used Later by ARFP"]
    INTRO["<b>Intro Conv</b><br>3 channels to 64 channels"]
    ENC1["<b>Encoder Level 1</b> - 2 blocks<br>RLIN Novelty 1: Edge Sharpen<br>Downsample: halve size"]
    ENC2["<b>Encoder Level 2</b> - 2 blocks<br>RLIN Novelty 1: Edge Sharpen<br>Downsample: halve size"]
    ENC3["<b>Encoder Level 3</b> - 4 blocks<br>RLIN Novelty 1: Edge Sharpen<br>Downsample: halve size"]
    ENC4["<b>Encoder Level 4</b> - 8 blocks<br>RLIN Novelty 1: Edge Sharpen<br>Downsample: halve size"]
    MID["<b>Bottleneck</b> - 12 blocks<br>Deepest Processing Point"]
    FAEB["<b>FAEB - Novelty 2</b><br>Clean Noise in Frequency Domain<br>FFT then Fix then iFFT"]
    DEC4["<b>Decoder Level 4</b> - 2 blocks<br>Upsample and Add Skip from Encoder 4"]
    DEC3["<b>Decoder Level 3</b> - 2 blocks<br>Upsample and Add Skip from Encoder 3"]
    DEC2["<b>Decoder Level 2</b> - 2 blocks<br>Upsample and Add Skip from Encoder 2"]
    DEC1["<b>Decoder Level 1</b> - 2 blocks<br>Upsample and Add Skip from Encoder 1"]
    ARFP["<b>ARFP - Novelty 3</b><br>Adapt Focus Using<br>Brightness Map"]
    ENDING["<b>Ending Conv</b><br>64 channels back to 3 RGB"]
    RESID["<b>Add Residual</b><br>Output plus Original Input"]
    PASS2["<b>Pass 2</b><br>Same Encoder-Bottleneck-Decoder<br>Runs Again on Pass 1 Output"]
    TAM["<b>TAM - Novelty 6</b><br>Combine Pass 1 and Pass 2<br>Using GRU Memory Cell"]
    OUTPUT["Enhanced Output Image<br>(H x W x 3)"]

    INPUT --> PRCM --> SPDP --> LUM --> INTRO
    INTRO --> ENC1 --> ENC2 --> ENC3 --> ENC4
    ENC4 --> MID --> FAEB
    FAEB --> DEC4 --> DEC3 --> DEC2 --> DEC1
    DEC1 --> ARFP --> ENDING --> RESID
    RESID --> PASS2 --> TAM --> OUTPUT

    ENC4 -.->|skip| DEC4
    ENC3 -.->|skip| DEC3
    ENC2 -.->|skip| DEC2
    ENC1 -.->|skip| DEC1

    style INPUT fill:#FFE0B2,stroke:#000,color:#000
    style PRCM fill:#E8F5E9,stroke:#000,color:#000
    style SPDP fill:#E8F5E9,stroke:#000,color:#000
    style LUM fill:#FFF3E0,stroke:#000,color:#000
    style INTRO fill:#E3F2FD,stroke:#000,color:#000
    style ENC1 fill:#BBDEFB,stroke:#000,color:#000
    style ENC2 fill:#BBDEFB,stroke:#000,color:#000
    style ENC3 fill:#BBDEFB,stroke:#000,color:#000
    style ENC4 fill:#BBDEFB,stroke:#000,color:#000
    style MID fill:#D1C4E9,stroke:#000,color:#000
    style FAEB fill:#E8F5E9,stroke:#000,color:#000
    style DEC4 fill:#C8E6C9,stroke:#000,color:#000
    style DEC3 fill:#C8E6C9,stroke:#000,color:#000
    style DEC2 fill:#C8E6C9,stroke:#000,color:#000
    style DEC1 fill:#C8E6C9,stroke:#000,color:#000
    style ARFP fill:#E8F5E9,stroke:#000,color:#000
    style ENDING fill:#E3F2FD,stroke:#000,color:#000
    style RESID fill:#FFF3E0,stroke:#000,color:#000
    style PASS2 fill:#FFECB3,stroke:#000,color:#000
    style TAM fill:#E8F5E9,stroke:#000,color:#000
    style OUTPUT fill:#A5D6A7,stroke:#000,color:#000
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

# Render PlantUML version
plantuml_path = os.path.join(out_dir, "architecture_diagram_teacher_plantuml.png")
render_via_kroki("plantuml", PLANTUML_CODE, plantuml_path)

# Render Mermaid version
mermaid_path = os.path.join(out_dir, "architecture_diagram_teacher_mermaid.png")
render_via_kroki("mermaid", MERMAID_CODE, mermaid_path)
