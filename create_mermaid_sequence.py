import base64, zlib, urllib.request, os

MERMAID_CODE = """
sequenceDiagram
    participant Caller as Inference Caller
    participant Main as Teacher Model
    participant PRCM as Pupil Dilation
    participant SPDP as Rod & Cone Merging
    participant UNet as U-Net Processor
    participant RLIN as Edge Filter
    participant FAEB as Frequency Filter
    participant ARFP as Adaptive Focus
    participant TAM as Darkness Memory

    Caller->>+Main: Send dark image tensor
    
    Note over Main,SPDP: STAGE 1: PRE-PROCESSING
    
    Main->>+PRCM: Adjust overall brightness
    PRCM-->>-Main: Brightness adjusted tensor
    
    Main->>+SPDP: Split Dark Vision & Color Vision
    SPDP-->>-Main: Merged vision tensor
    
    Note over Main,ARFP: STAGE 2: PASS 1 (FIRST ATTEMPT)
    
    Main->>+UNet: Start first pass
    
    UNet->>+RLIN: Downsample & Sharpen edges (Encoder)
    RLIN-->>-UNet: Deep target features
    
    UNet->>+FAEB: Clean noise frequencies (Bottleneck)
    FAEB-->>-UNet: Clean deep features
    
    UNet->>+UNet: Upsample & Add skip connections (Decoder)
    UNet-->>-UNet: Reconstructed features
    
    UNet->>+ARFP: Focus using brightness map
    ARFP-->>-UNet: Focused features
    
    UNet-->>-Main: Tensor from Pass 1
    
    Note over Main,ARFP: STAGE 3: PASS 2 (REFINEMENT)
    
    Main->>+UNet: Send Pass 1 tensor for second pass
    
    UNet->>+RLIN: Downsample & Sharpen again (Encoder)
    RLIN-->>-UNet: Deep target features
    
    UNet->>+FAEB: Clean frequency noise again (Bottleneck)
    FAEB-->>-UNet: Cleaner deep features
    
    UNet->>+UNet: Upsample & Add skip connections (Decoder)
    UNet-->>-UNet: Reconstructed features
    
    UNet->>+ARFP: Adjust focus again
    ARFP-->>-UNet: Better focused features
    
    UNet-->>-Main: Tensor from Pass 2
    
    Note over Main,TAM: STAGE 4: FINAL OUTPUT
    
    Main->>+TAM: Intelligently combine Pass 1 and Pass 2
    TAM-->>-Main: Final smooth enhanced tensor
    
    Main-->>-Caller: Return final enhanced tensor
"""

def render_via_kroki_mermaid(mermaid_code, output_path):
    compressed = zlib.compress(mermaid_code.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode()
    url = f"https://kroki.io/mermaid/png/{encoded}"
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
out_path = os.path.join(out_dir, "sequence_diagram_teacher_mermaid.png")

render_via_kroki_mermaid(MERMAID_CODE, out_path)
