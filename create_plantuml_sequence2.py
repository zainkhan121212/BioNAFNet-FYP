import base64, zlib, urllib.request, os

PLANTUML_CODE = """
@startuml
skinparam backgroundColor #FFFFFF
skinparam defaultFontColor #000000
skinparam sequenceArrowColor #000000
skinparam sequenceLifeLineBorderColor #000000
skinparam sequenceParticipantBorderColor #000000
skinparam sequenceParticipantBackgroundColor #FFFFFF
skinparam actorBorderColor #000000
skinparam actorBackgroundColor #FFFFFF
skinparam maxMessageSize 150
hide footbox

actor "Inference Caller" as Caller
participant "Teacher Model" as Main
participant "PRCM (Novelty 4)" as PRCM
participant "SPDP (Novelty 5)" as SPDP
participant "U-Net Processor" as UNet
participant "RLIN (Novelty 1)" as RLIN
participant "FAEB (Novelty 2)" as FAEB
participant "ARFP (Novelty 3)" as ARFP
participant "TAM (Novelty 6)" as TAM

Caller -> Main : Send dark tensor
activate Main

Main -> PRCM : Adjust overall brightness
activate PRCM
PRCM --> Main : Brightness adjusted tensor
deactivate PRCM

Main -> SPDP : Split Dark & Color Vision
activate SPDP
SPDP --> Main : Merged vision tensor
deactivate SPDP

Main -> UNet : Start Pass 1
activate UNet

UNet -> RLIN : Encoder Level 1 (2 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Features
deactivate RLIN

UNet -> RLIN : Encoder Level 2 (2 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Features
deactivate RLIN

UNet -> RLIN : Encoder Level 3 (4 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Features
deactivate RLIN

UNet -> RLIN : Encoder Level 4 (8 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Deep features
deactivate RLIN

UNet -> FAEB : BOTTLENECK (12 blocks)\\nClean noise frequencies
activate FAEB
FAEB --> UNet : Clean deep features
deactivate FAEB

UNet -> UNet : Decoder Level 4 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> UNet : Decoder Level 3 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> UNet : Decoder Level 2 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> UNet : Decoder Level 1 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> ARFP : Focus using brightness map
activate ARFP
ARFP --> UNet : Focused features
deactivate ARFP

UNet --> Main : Tensor from Pass 1
deactivate UNet

Main -> UNet : Send Pass 1 tensor for Pass 2
activate UNet

UNet -> RLIN : Encoder Level 1 (2 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Features
deactivate RLIN

UNet -> RLIN : Encoder Level 2 (2 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Features
deactivate RLIN

UNet -> RLIN : Encoder Level 3 (4 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Features
deactivate RLIN

UNet -> RLIN : Encoder Level 4 (8 blocks)\\nSharpen & Downsample
activate RLIN
RLIN --> UNet : Deep features
deactivate RLIN

UNet -> FAEB : BOTTLENECK (12 blocks)\\nClean noise frequencies again
activate FAEB
FAEB --> UNet : Cleaner deep features
deactivate FAEB

UNet -> UNet : Decoder Level 4 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> UNet : Decoder Level 3 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> UNet : Decoder Level 2 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> UNet : Decoder Level 1 (2 blocks)\\nUpsample & Skip add
activate UNet
UNet --> UNet : Reconstructed features
deactivate UNet

UNet -> ARFP : Adjust focus again
activate ARFP
ARFP --> UNet : Better focused features
deactivate ARFP

UNet --> Main : Tensor from Pass 2
deactivate UNet

Main -> TAM : Combine Pass 1 and Pass 2
activate TAM
TAM --> Main : Final smooth enhanced tensor
deactivate TAM

Main --> Caller : Return final enhanced tensor
deactivate Main

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
out_path = os.path.join(out_dir, "sequence_diagram_teacher_plantuml.png")

render_via_kroki_plantuml(PLANTUML_CODE, out_path)
