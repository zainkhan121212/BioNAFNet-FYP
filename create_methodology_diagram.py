"""
create_methodology_diagram.py
Generates a clean black-and-white Methodology Diagram for BioNAFNet.
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

title BioNAFNet - Research Methodology Diagram

rectangle "**Step 1: Problem Definition**\nLow-light images have poor\nvisibility, noise, and lost colors" as PROB

rectangle "**Step 2: Dataset Collection**\nLOLv1 (485 pairs)\nLOLv2 Real (689 pairs)\nLOLv2 Synthetic (900 pairs)" as DATA

rectangle "**Step 3: Data Preprocessing**\nRandom crop to 256 x 256\nRandom rotation and flip\nNormalize pixels to 0-1 range" as PREPROC

rectangle "**Step 4: Design Bio-Inspired Model**\nBuild NAFNet backbone enhanced\nwith 7 Biological Novelties" as DESIGN

rectangle "**Novelty 1: RLIN**\nEdge sharpening filter\ninspired by retinal cells" as N1
rectangle "**Novelty 2: FAEB**\nClean noise using\nfrequency domain (FFT)" as N2
rectangle "**Novelty 3: ARFP**\nAdapt focus based on\nbrightness of each area" as N3
rectangle "**Novelty 4: PRCM**\nAdjust brightness curve\nlike pupil dilation" as N4
rectangle "**Novelty 5: SPDP**\nSplit dark vision and\ncolor vision then merge" as N5
rectangle "**Novelty 6: TAM**\nTwo-pass refinement\nusing GRU memory cell" as N6
rectangle "**Novelty 7: Weber-Fechner Loss**\nBiological loss function\nfor human-like perception" as N7

rectangle "**Step 5: Train Teacher Model**\n154M parameters\n2 passes through U-Net\nTrained on paired images" as TRAIN_T

rectangle "**Step 6: Train Student Model**\nSmaller and faster model\nLearns from Teacher output\n(Knowledge Distillation)" as TRAIN_S

rectangle "**Step 7: Evaluation Metrics**\nPSNR (pixel accuracy)\nSSIM (structure similarity)\nLPIPS (visual quality)" as EVAL

rectangle "**Step 8: Compare With Others**\nRetinexNet\nRetinexformer\nNAFNet baseline\nOther state-of-the-art methods" as COMPARE

rectangle "**Step 9: Desktop Application**\nBuild UI for users to\nenhance images easily\nSupport batch processing" as APP

rectangle "**Step 10: Results & Conclusion**\nReport scores and visual results\nShow improvement over baselines\nSubmit thesis" as RESULTS

PROB --> DATA
DATA --> PREPROC
PREPROC --> DESIGN

DESIGN --> N1
DESIGN --> N2
DESIGN --> N3
DESIGN --> N4
DESIGN --> N5
DESIGN --> N6
DESIGN --> N7

N1 --> TRAIN_T
N2 --> TRAIN_T
N3 --> TRAIN_T
N4 --> TRAIN_T
N5 --> TRAIN_T
N6 --> TRAIN_T
N7 --> TRAIN_T

TRAIN_T --> TRAIN_S
TRAIN_S --> EVAL
EVAL --> COMPARE
COMPARE --> APP
APP --> RESULTS

@enduml
"""

MERMAID_CODE = """
flowchart TD
    PROB["<b>Step 1: Problem Definition</b><br>Low-light images have poor<br>visibility, noise, and lost colors"]
    DATA["<b>Step 2: Dataset Collection</b><br>LOLv1 - 485 pairs<br>LOLv2 Real - 689 pairs<br>LOLv2 Synthetic - 900 pairs"]
    PREPROC["<b>Step 3: Data Preprocessing</b><br>Random crop to 256 x 256<br>Random rotation and flip<br>Normalize pixels to 0-1 range"]
    DESIGN["<b>Step 4: Design Bio-Inspired Model</b><br>Build NAFNet backbone enhanced<br>with 7 Biological Novelties"]

    N1["<b>Novelty 1: RLIN</b><br>Edge sharpening filter<br>inspired by retinal cells"]
    N2["<b>Novelty 2: FAEB</b><br>Clean noise using<br>frequency domain FFT"]
    N3["<b>Novelty 3: ARFP</b><br>Adapt focus based on<br>brightness of each area"]
    N4["<b>Novelty 4: PRCM</b><br>Adjust brightness curve<br>like pupil dilation"]
    N5["<b>Novelty 5: SPDP</b><br>Split dark vision and<br>color vision then merge"]
    N6["<b>Novelty 6: TAM</b><br>Two-pass refinement<br>using GRU memory cell"]
    N7["<b>Novelty 7: Weber-Fechner Loss</b><br>Biological loss function<br>for human-like perception"]

    TRAIN_T["<b>Step 5: Train Teacher Model</b><br>154M parameters<br>2 passes through U-Net<br>Trained on paired images"]
    TRAIN_S["<b>Step 6: Train Student Model</b><br>Smaller and faster model<br>Learns from Teacher output<br>Knowledge Distillation"]
    EVAL["<b>Step 7: Evaluation Metrics</b><br>PSNR - pixel accuracy<br>SSIM - structure similarity<br>LPIPS - visual quality"]
    COMPARE["<b>Step 8: Compare With Others</b><br>RetinexNet<br>Retinexformer<br>NAFNet baseline<br>Other methods"]
    APP["<b>Step 9: Desktop Application</b><br>Build UI for users to<br>enhance images easily<br>Support batch processing"]
    RESULTS["<b>Step 10: Results and Conclusion</b><br>Report scores and visual results<br>Show improvement over baselines<br>Submit thesis"]

    PROB --> DATA --> PREPROC --> DESIGN

    DESIGN --> N1
    DESIGN --> N2
    DESIGN --> N3
    DESIGN --> N4
    DESIGN --> N5
    DESIGN --> N6
    DESIGN --> N7

    N1 --> TRAIN_T
    N2 --> TRAIN_T
    N3 --> TRAIN_T
    N4 --> TRAIN_T
    N5 --> TRAIN_T
    N6 --> TRAIN_T
    N7 --> TRAIN_T

    TRAIN_T --> TRAIN_S --> EVAL --> COMPARE --> APP --> RESULTS

    style PROB fill:#fff,stroke:#000,color:#000
    style DATA fill:#fff,stroke:#000,color:#000
    style PREPROC fill:#fff,stroke:#000,color:#000
    style DESIGN fill:#fff,stroke:#000,color:#000
    style N1 fill:#fff,stroke:#000,color:#000
    style N2 fill:#fff,stroke:#000,color:#000
    style N3 fill:#fff,stroke:#000,color:#000
    style N4 fill:#fff,stroke:#000,color:#000
    style N5 fill:#fff,stroke:#000,color:#000
    style N6 fill:#fff,stroke:#000,color:#000
    style N7 fill:#fff,stroke:#000,color:#000
    style TRAIN_T fill:#fff,stroke:#000,color:#000
    style TRAIN_S fill:#fff,stroke:#000,color:#000
    style EVAL fill:#fff,stroke:#000,color:#000
    style COMPARE fill:#fff,stroke:#000,color:#000
    style APP fill:#fff,stroke:#000,color:#000
    style RESULTS fill:#fff,stroke:#000,color:#000
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

plantuml_path = os.path.join(out_dir, "methodology_diagram_plantuml.png")
render_via_kroki("plantuml", PLANTUML_CODE, plantuml_path)

mermaid_path = os.path.join(out_dir, "methodology_diagram_mermaid.png")
render_via_kroki("mermaid", MERMAID_CODE, mermaid_path)
