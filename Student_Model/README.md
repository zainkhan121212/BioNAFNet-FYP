# Student Model (BioNAFNet-Lite)

## Architecture
- Parameters: 23,969,016 (24M)
- Width: 32 channels
- Middle blocks: 4
- N passes (TAM): 1
- Model size: ~91 MB

## Training (Knowledge Distillation)
- Teacher: BioNAFNet Full (154M, frozen)
- Dataset: LOLv1 + LOLv2 Real + LOLv2 Synthetic (2074 pairs)
- Epochs: 693
- Best validation PSNR: 25.09 dB (epoch 693)
- Training time: ~40 hours
- Loss: 0.5*L1(student,gt) + 0.1*SSIM(student,gt) + 0.4*L2(student,teacher_out)

## Test Results (Student-693)
| Dataset | PSNR | SSIM | FPS |
|---------|------|------|-----|
| LOLv1 | 25.23 dB | 0.8528 | 20.5 |
| LOLv2 Real | 28.48 dB | 0.8942 | 20.5 |
| LOLv2 Synth | 25.75 dB | 0.9375 | 20.5 |

## Compression vs Teacher
- 6.4x fewer parameters (154M → 24M)
- 6.5x smaller file (589 MB → 91 MB)
- 3.9x faster (188.7 ms → 48.9 ms)
- Student BEATS Teacher on LOLv1! (25.23 vs 24.94 dB)

## Files
- `code/` — Distillation training + standalone testing scripts
- `checkpoints/` — Student checkpoint files
- `logs/` — Distillation training log (693 epochs)
- `results/` — Enhanced test images (LOLv1 + LOLv2)
