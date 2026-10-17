import base64, json, os, urllib.request, zlib
from PIL import Image

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

CODE = """flowchart TB
    IN["Input Image<br>H x W x 3"] --> PRCM["PRCM (Novelty 4)<br>Pupil Response Calibration"]
    
    subgraph Architecture ["BioNAFNet Forward Pass"]
        PRCM --> SPDP["SPDP (Novelty 5)<br>Spatial-Dependent Processing"]
        
        SPDP --> E1["Encoder Level 1<br>(2 Blocks + RLIN: Novelty 1)"]
        E1 --> E2["Encoder Level 2<br>(2 Blocks + RLIN)"]
        E2 --> E3["Encoder Level 3<br>(4 Blocks + RLIN)"]
        E3 --> E4["Encoder Level 4<br>(8 Blocks + RLIN)"]
        
        E4 --> MID["Middle Blocks<br>(12 Blocks + FAEB: Novelty 2)"]
        
        MID --> D4["Decoder Level 4"]
        D4 --> D3["Decoder Level 3"]
        D3 --> D2["Decoder Level 2"]
        D2 --> D1["Decoder Level 1"]
        
        E4 -. "Skip" .-> D4
        E3 -. "Skip" .-> D3
        E2 -. "Skip" .-> D2
        E1 -. "Skip" .-> D1
        
        D1 --> ARFP["ARFP (Novelty 3)<br>Adaptive Residual Feature Processing"]
    end
    
    ARFP --> TAM["TAM (Novelty 6)<br>Temporal Adaptation Memory<br>(Iterative Loop)"]
    
    TAM --> OUT["Enhanced Output"]

    subgraph Training ["Biological Training Strategy"]
        BL["WFLL (Novelty 7)<br>Weber-Fechner Luminance Loss"]
        KD["Knowledge Distillation<br>(Teacher compressed to Student)"]
        
        OUT -. "Applies" .-> BL
        OUT -. "Guides" .-> KD
    end

    BL --> Final["Final Optimized<br>BioNAFNet Models"]
    KD --> Final
"""

def render_via_mermaid_ink(mermaid_code, output_path):
    full_code = BW_THEME + mermaid_code
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
        print(f"mermaid.ink failed: {e}")
        return False

def render_via_kroki(mermaid_code, output_path):
    full_code = BW_THEME + mermaid_code
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
        print(f"kroki.io failed: {e}")
        return False

def ensure_bw(png_path):
    try:
        img = Image.open(png_path)
        gray = img.convert("L")
        bw = gray.convert("RGB")
        bw.save(png_path, "PNG")
    except Exception as e:
        pass

out_dir = r"f:/low_light_enhancement/eye adaption/BioNAFNet/thesis_figures"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "fig_BioNAFNet_Complete_Architecture.png")

if not render_via_mermaid_ink(CODE, out_path):
    render_via_kroki(CODE, out_path)

if os.path.exists(out_path):
    ensure_bw(out_path)
    print(f"Chart successfully saved to {out_path}")
else:
    print("Failed to save chart.")
