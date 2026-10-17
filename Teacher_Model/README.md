# Teacher Model (BioNAFNet Full)

## Architecture
- Parameters: 154,380,888 (154M)
- Width: 64 channels
- Middle blocks: 12
- N passes (TAM): 2
- Model size: ~589 MB

## Training
- Dataset: LOLv1 + LOLv2 Real + LOLv2 Synthetic (2074 pairs)
- Epochs: 504
- Best validation PSNR: 25.05 dB (epoch 476)
- Training time: ~34 hours

## Test Results
| Dataset | PSNR | SSIM | FPS |
|---------|------|------|-----|
| LOLv1 | 24.94 dB | 0.8661 | 5.3 |
| LOLv2 Real | 28.67 dB | 0.9101 | 5.3 |
| LOLv2 Synth | 26.22 dB | 0.9457 | 5.3 |

## Files
- `code/` — Training and inference scripts
- `checkpoints/` — best.pth and latest.pth
- `logs/` — Training log (504 epochs)
- `results/` — Enhanced test images (LOLv1 + LOLv2)
