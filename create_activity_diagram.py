"""
create_activity_diagram.py
Generates a standard UML Activity Diagram of the BioNAFNet Teacher Model
using PlantUML syntax, rendered via kroki.io.
"""
import base64, zlib, urllib.request, os

PLANTUML_CODE = """
@startuml
skinparam backgroundColor #FFFFFF
skinparam activityBackgroundColor #F0F4FF
skinparam activityBorderColor #222255
skinparam activityFontSize 12
skinparam activityFontName Arial
skinparam arrowColor #222255
skinparam diamondBackgroundColor #FFF8CC
skinparam diamondBorderColor #555500
skinparam partitionBackgroundColor #F0FAF0
skinparam partitionBorderColor #225522

title BioNAFNet Teacher Model - UML Activity Diagram

(*) --> "User uploads low-light image\\nand selects Teacher Model in app"

--> "Click ENHANCE Button"

if "Image uploaded?" then
  -->[Yes] "Check save folder selected?"
else
  -->[No] "Show Warning: No Image"
  --> (*)
endif

if "Save folder selected?" then
  -->[Yes] "Start Background Processing Thread"
else
  -->[No] "Show Warning: No Folder"
  --> (*)
endif

partition "bionafnet_teacher.py" {
  --> "Look up Teacher model fn()\\nfrom model registry"

  if "Model already in memory cache?" then
    -->[Yes] "Get model from cache\\n(instant - no reload needed)"
  else
    -->[No] "Build BioNAFNet architecture\\nwidth=64, passes=2\\nenc=[2,2,4,8], mid=12"
    --> "Load 2.47 GB weights\\nfrom best.pth checkpoint"
    --> "Fill model with weights\\nload_state_dict(strict=False)"
    --> "Switch to eval() mode\\nFreeze dropout and batchnorm"
    --> "Save model in cache\\nfor fast future calls"
  endif

  --> "Open image: PIL.Image.open()\\nConvert to RGB"
  --> "Normalize pixels: 0-255 to 0.0-1.0"
  --> "Reshape: (H,W,C) to (1,C,H,W)"
  --> "Move tensor to GPU or CPU"
}

partition "model.py - forward()" {
  --> "NOVELTY 4: PRCM\\nPupil Response Calibration Module\\nAdjust brightness like pupil dilation"

  --> "NOVELTY 5: SPDP\\nSpatial Dual Pathway\\nRod pathway + Cone pathway merged"

  --> "Compute luminance map\\nBrightness estimate per pixel"

  --> "Set current = SPDP output\\nBegin multi-pass loop (2 passes)"

  --> "--- PASS 1 ---"

  --> "Pad image to divisible-by-16"
  --> "Intro Conv: expand RGB (3ch) to 64 feature channels"

  --> "ENCODER LEVEL 1: 2 blocks\\nNOVELTY 1 RLIN fires\\nSave skip connection then Downsample"
  --> "ENCODER LEVEL 2: 2 blocks\\nNOVELTY 1 RLIN fires\\nSave skip connection then Downsample"
  --> "ENCODER LEVEL 3: 4 blocks\\nNOVELTY 1 RLIN fires\\nSave skip connection then Downsample"
  --> "ENCODER LEVEL 4: 8 blocks\\nNOVELTY 1 RLIN fires\\nSave skip connection then Downsample"

  --> "BOTTLENECK: 12 Middle Blocks\\nDeepest feature processing point"

  --> "NOVELTY 2: FAEB\\nFrequency-Aware Enhancement Branch\\nFFT splits Amplitude and Phase\\nConv layers fix both spectra\\niFFT reconstructs enhanced features"

  --> "DECODER LEVEL 4: 2 blocks\\nUpsample + Add skip from Encoder 4"
  --> "DECODER LEVEL 3: 2 blocks\\nUpsample + Add skip from Encoder 3"
  --> "DECODER LEVEL 2: 2 blocks\\nUpsample + Add skip from Encoder 2"
  --> "DECODER LEVEL 1: 2 blocks\\nUpsample + Add skip from Encoder 1"

  --> "NOVELTY 3: ARFP\\nAdaptive Receptive Field Processing\\nGuided by luminance brightness map"

  --> "Ending Conv: 64 channels back to 3 RGB"
  --> "Add residual: output + original padded input"
  --> "Crop padding - return Pass 1 output"

  --> "--- PASS 2 ---\\nFeed Pass 1 output as new input"
  --> "Run full encoder-bottleneck-decoder again\\nAll RLIN + FAEB + ARFP fire again"
  --> "Append Pass 2 result to pass_outputs"

  --> "NOVELTY 6: TAM\\nTemporal Adaptation Memory\\nGRU cell combines Pass 1 and Pass 2\\nLike eyes progressively adapting to dark"

  --> "Clamp final output to range 0.0-1.0"
}

partition "bionafnet_teacher.py - post inference" {
  --> "Squeeze batch dim: (1,C,H,W) to (C,H,W)"
  --> "Permute: (C,H,W) to (H,W,C)"
  --> "Scale pixels: multiply by 255"
  --> "Convert to uint8 numpy array"
  --> "Convert numpy to PIL Image"
  --> "Return enhanced PIL Image to thread"
}

partition "neon_enhancer_pro.py - thread" {
  --> "Save enhanced image to output folder"
  --> "Update progress bar in UI"

  if "More images in batch?" then
    -->[Yes] "Process next image"
  else
    -->[No] "Signal UI to update gallery"
  endif

  --> "Display before vs after gallery"
  --> "Re-enable Enhance button"
}

--> "DONE: Enhanced image shown to user"
--> (*)

@enduml
"""


def render_via_kroki_plantuml(plantuml_code, output_path):
    compressed = zlib.compress(plantuml_code.encode("utf-8"), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode()
    url = f"https://kroki.io/plantuml/png/{encoded}"
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
out_path = os.path.join(out_dir, "activity_diagram_teacher_model.png")

render_via_kroki_plantuml(PLANTUML_CODE, out_path)
