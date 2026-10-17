# RTX 5090 Deployment Guide — BioNAFNet "Beast Mode"

Use this guide to deploy the High-Performance version of BioNAFNet on your RTX 5090 machine.

## 1. Prerequisites
- **OS:** Windows or Linux
- **GPU:** NVIDIA RTX 5090 (24GB+ VRAM)
- **Python:** 3.10 or newer

## 2. Setup Environment
Open a terminal (PowerShell or Bash) and run:

```bash
# 1. Install PyTorch (ensure CUDA support)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 2. Install dependencies
pip install scikit-image tqdm pillow numpy
```

## 3. Data Setup
Create a folder named `data` in the same directory as the script, and organize your datasets like this:

```
BioNAFNet/
├── train_bionafnet_5090.py
└── data/
    ├── LOLv1/
    │   ├── Train/
    │   │   ├── input/     # Low-light images
    │   │   └── target/    # Normal-light images
    │   └── Test/ ...
    └── LOLv2/             # (Optional)
        ├── Real_captured/ ...
        └── Synthetic/ ...
```

## 4. Run Training
This script is configured for **maximum quality** ("Beast Mode"):
- **Resolution:** Progressive up to **512x512** patches (vs 128 on your current PC)
- **Batch Size:** 32 (Effective)
- **Precision:** Float32 FFT enabled for best quality

Run command:
```bash
python train_bionafnet_5090.py
```

## 5. What to Expect
- **Speed:** Blazing fast. The 5090 should crush 512x512 patches effortlessly.
- **Quality:** significantly better than the standard version due to seeing larger image contexts (512px).
- **Checkpoints:** Saved to `checkpoints_5090/`.
