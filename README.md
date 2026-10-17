# BioNAFNet: biologically inspired low-light image enhancement

Final-year project combining a NAFNet-based teacher, a distilled student, ensemble experiments, and the NeonEnhancer Pro desktop application. The architecture models retinal lateral inhibition (RLIN), frequency processing (FAEB), adaptive receptive fields (ARFP), photoreceptor curves (PRCM), luminance/chrominance pathways (SPDP), and iterative adaptation (TAM). The teacher training objective includes Weber-Fechner perceptual loss. The one-pass student bypasses TAM aggregation and uses L1, SSIM, and teacher-output distillation losses.

**Start here:** [installation and usage](docs/INSTALL.md) · [results and comparison](docs/RESULTS.md) · [Master Report](docs/BioNAFNet_Master_Report.pdf) · [trained weights](https://github.com/zainkhan121212/BioNAFNet-FYP/releases/tag/v1.0.0)

## Quick start (Windows PowerShell)

Use 64-bit Python 3.12 and Git. This repository is private: the owner must grant your GitHub account access before cloning or downloading releases.

```powershell
git clone https://github.com/zainkhan121212/BioNAFNet-FYP.git
cd BioNAFNet-FYP
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Download `student_ema.pth` from the release to `Student_Model/checkpoints/best.pth` (create the folder), then run:

```powershell
.\.venv\Scripts\python.exe enhance.py --model student --weights Student_Model/checkpoints/best.pth --input path/to/dark.png --output outputs/enhanced.png
```

For NVIDIA GPU installation, use the command generated for your hardware by the [official PyTorch installer](https://pytorch.org/get-started/locally/), then pass `--device cuda`. CPU inference is supported but slower. Training and full-resolution teacher inference require substantially more memory than the small validation smoke test.

## Model comparison

| Property | Teacher | Student |
|---|---:|---:|
| Parameters | 154,380,888 | 23,969,016 |
| Base width | 64 | 32 |
| Bottleneck blocks | 12 | 4 |
| Refinement passes | 2 | 1 |
| Reported LOLv1 PSNR / SSIM | 24.94 / 0.8661 | 25.23 / 0.8528 |
| Reported LOLv2 Real PSNR / SSIM | 28.67 / 0.9101 | 28.48 / 0.8942 |
| Reported LOLv2 Synthetic PSNR / SSIM | 26.22 / 0.9457 | 25.75 / 0.9375 |

These are report values, not measurements reproduced during repository preparation. The saved evaluation CSV differs, and checkpoint filenames may not match their embedded epochs. Read [RESULTS.md](docs/RESULTS.md) and the release manifest before comparing results. The report's ablations are estimates, not completed controlled experiments.

## Repository layout

- `Teacher_Model/code/code/`: modular teacher model, training, evaluation, and existing tests.
- `Student_Model/code/code/`: modular student model and distillation pipeline.
- `Teacher_Model/code/`, `Student_Model/code/`: original standalone scripts.
- `Ensemble_Model/`: ensemble experiment code.
- `Kimi_Agent_CustomTkinter Futuristic UI/`: NeonEnhancer Pro and integrations.
- `enhance.py`: portable single-image inference wrapper; original architecture files are unchanged.
- `docs/`: installation, results, original report, evaluation CSV, and source inventory.
- Other app prototypes, benchmark scripts, and report-generation source are retained as research material. The documented supported entry points are the modular model folders, `enhance.py`, and NeonEnhancer Pro.

Datasets, caches, generated experiment images, duplicate portable bundles, and original training-state checkpoints are excluded. Inference-only checkpoints are separate release assets. No model was retrained for this publication.

## Attribution and reuse

The project builds on NAFNet concepts and includes third-party integration code, including Retinexformer and Zero-DCE. Retained third-party license notices apply to their respective files. No new blanket license is assigned to the original project code; contact the owner for reuse permission. Third-party models require their own weights and may have additional installation requirements.
