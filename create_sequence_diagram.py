"""
create_sequence_diagram.py
Generates a detailed UML Sequence Diagram of the BioNAFNet Teacher Model internals.
Shows message passing between all 7 biological novelty components.
"""
import base64, zlib, urllib.request, os

PLANTUML_CODE = """
@startuml
skinparam backgroundColor #FFFFFF
skinparam sequenceArrowThickness 1.5
skinparam roundcorner 8
skinparam sequenceParticipantBorderColor #222266
skinparam sequenceParticipantBackgroundColor #EEF0FF
skinparam sequenceLifeLineBorderColor #888888
skinparam sequenceMessageAlign center
skinparam sequenceGroupBackgroundColor #FFFFF0
skinparam sequenceGroupBorderColor #AAAAAA
skinparam noteBorderColor #996600
skinparam noteBackgroundColor #FFF8CC
skinparam sequenceActorBorderColor #222266
skinparam sequenceActorBackgroundColor #D0D8FF

title BioNAFNet Teacher Model - Detailed UML Sequence Diagram

participant "Inference\\nCaller" as CALLER
participant "BioNAFNet\\nforward()" as FWD
participant "PRCM\\nNovelty 4" as PRCM
participant "SPDP\\nNovelty 5" as SPDP
participant "forward_single()" as FS
participant "RLIN\\nNovelty 1" as RLIN
participant "FAEB\\nNovelty 2" as FAEB
participant "ARFP\\nNovelty 3" as ARFP
participant "TAM\\nNovelty 6" as TAM

== Inference Entry ==

CALLER -> FWD : forward(inp_tensor)\\nshape: (1, 3, H, W)

== PRCM: Photoreceptor Calibration ==

FWD -> PRCM : prcm(x)\\nRaw dark image tensor
note right of PRCM
  Applies biological brightness curve\\n
  Simulates pupil dilation in dark\\n
  Uses learned gamma-like correction\\n
  Output: brightness-adjusted tensor
end note
PRCM --> FWD : x_prcm\\nTensor with adjusted brightness

== SPDP: Spatial Dual Pathway ==

FWD -> SPDP : spdp(x_prcm)\\nAdjusted tensor input
note right of SPDP
  Splits into two pathways:\\n
  Rod pathway: dark/peripheral vision\\n
  Cone pathway: colour/central vision\\n
  Merges both streams via 1x1 conv\\n
  Output: dual-pathway merged tensor
end note
SPDP --> FWD : x_spdp\\nMerged dual-pathway tensor

FWD -> FWD : lum_map = luminance(x)\\nCompute per-pixel brightness map

== Multi-Pass Loop: Pass 1 ==

group Pass 1 of 2 [n_passes = 2 for Teacher]
  FWD -> FS : forward_single(x_spdp, lum_map)

  FS -> FS : check_image_size(inp)\\nPad to divisible by 16

  FS -> FS : intro_conv(x)\\n3 channels -> 64 channels

  == Encoder Path (RLIN fires at each level) ==

  loop 4 Encoder Levels [enc_blk_nums = 2, 2, 4, 8]
    FS -> RLIN : encoder_block(x)\\nRLIN inside each BioNAFBlock
    note right of RLIN
      Center pathway: 1x1 Conv (fine detail)\\n
      Surround: AvgPool5x5 + 1x1 (context)\\n
      Compute: center - surround\\n
      Output: x + alpha * (center - surround)\\n
      Enhances local contrast and edges
    end note
    RLIN --> FS : x_encoded\\nContrast-enhanced features
    FS -> FS : save enc_skip for decoder
    FS -> FS : down_conv(x)\\nHalve H and W, double channels
  end

  == Bottleneck (12 Blocks) ==

  FS -> FS : middle_blks(x)\\n12 BioNAFBlocks at deepest level\\nNo RLIN here, pure NAFNet blocks

  == FAEB: Frequency Enhancement ==

  FS -> FAEB : faeb(x)\\nBottleneck features tensor
  note right of FAEB
    1. rfft2: convert to frequency domain\\n
    2. Extract amplitude and phase\\n
    3. Conv+PReLU+Conv on amplitude\\n
    4. Conv+PReLU+Conv on phase\\n
    5. Reconstruct: amp*cos(phase) + j*amp*sin(phase)\\n
    6. irfft2: convert back to spatial domain\\n
    7. Output: x + blend * freq_enhanced
  end note
  FAEB --> FS : x_freq_enhanced\\nFrequency-corrected bottleneck features

  == Decoder Path (Skip Connections) ==

  loop 4 Decoder Levels [dec_blk_nums = 2, 2, 2, 2]
    FS -> FS : up_conv(x)\\nPixelShuffle: double H and W
    FS -> FS : x = x + enc_skip\\nAdd matching encoder skip connection
    FS -> FS : decoder_block(x)\\nRefine reconstructed features
  end

  == ARFP: Adaptive Receptive Field ==

  FS -> ARFP : arfp(x, lum_map)\\nDecoded features + luminance map
  note right of ARFP
    Uses luminance map to guide\\n
    multi-scale receptive field selection\\n
    Bright regions: small receptive field\\n
    Dark regions: large receptive field\\n
    Output: spatially adaptive features
  end note
  ARFP --> FS : x_adaptive\\nLuminance-guided adaptive features

  FS -> FS : ending_conv(x)\\n64 channels back to 3 RGB channels
  FS -> FS : x = x + inp_padded\\nResidual: model learns the correction delta
  FS -> FS : crop padding to original H x W

  FS --> FWD : pass1_out\\nshape: (1, 3, H, W) - first enhanced image
  FWD -> FWD : clamp(0, 1)\\ncurrent = pass1_out
  FWD -> FWD : pass_outputs.append(pass1_out)
end

== Multi-Pass Loop: Pass 2 ==

group Pass 2 of 2 [Input is now Pass 1 enhanced output]
  note over FWD
    Pass 2 receives the already-enhanced image\\n
    from Pass 1 as its input.\\n
    Like eyes refining their vision the second\\n
    time they look at a dark scene.
  end note

  FWD -> FS : forward_single(current=pass1_out, lum_map)

  note over FS, ARFP
    Exact same sequence as Pass 1:\\n
    Encoder (RLIN x4) -> Bottleneck -> FAEB -> Decoder x4 -> ARFP\\n
    But operating on already-enhanced features
  end note

  FS -> RLIN : encoder_blocks(x) x4 levels
  RLIN --> FS : x_encoded
  FS -> FAEB : faeb(x_bottleneck)
  FAEB --> FS : x_freq_enhanced
  FS -> ARFP : arfp(x_decoded, lum_map)
  ARFP --> FS : x_adaptive
  FS --> FWD : pass2_out\\nFurther refined output

  FWD -> FWD : clamp(0, 1)\\npass_outputs.append(pass2_out)
end

== TAM: Temporal Adaptation Memory ==

FWD -> TAM : tam(pass_outputs)\\nList: [pass1_out, pass2_out]
note right of TAM
  GRU cell processes each pass output\\n
  sequentially as temporal frames:\\n
  hidden = GRU(pass1_features, hidden=0)\\n
  hidden = GRU(pass2_features, hidden)\\n
  Project hidden state back to image space\\n
  Output: pass2_out + 0.15 * gru_residual\\n
  Intelligent combination of both passes
end note
TAM --> FWD : final_enhanced\\nGRU-aggregated best of both passes

FWD -> FWD : clamp(0, 1)
FWD --> CALLER : final_output\\nshape: (1, 3, H, W)\\nFully enhanced image tensor

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
out_path = os.path.join(out_dir, "sequence_diagram_teacher_model.png")

render_via_kroki_plantuml(PLANTUML_CODE, out_path)
