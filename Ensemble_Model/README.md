# Ensemble Model (Teacher + Student Fusion)

## Strategy
Combines Teacher and Student model outputs via weighted averaging:
  ensemble_output = alpha * teacher_out + (1-alpha) * student_out

## Variants
| Strategy | Teacher Weight | Student Weight |
|----------|---------------|----------------|
| Ensemble 50/50 | 50% | 50% |
| Ensemble T60/S40 | 60% | 40% |
| Ensemble T40/S60 | 40% | 60% |
| Synergy T70/S30 | 70% | 30% |

## Test Results
| Strategy | LOLv1 | LOLv2 Real | LOLv2 Synth | FPS |
|----------|-------|------------|-------------|-----|
| Ensemble 50/50 | 25.27 dB | 29.26 dB | 26.47 dB | ~4 |
| Ensemble T60/S40 | 25.23 dB | **29.29 dB** | 26.46 dB | ~4 |
| Ensemble T40/S60 | 25.29 dB | 29.19 dB | 26.43 dB | ~4 |
| Synergy T70/S30 | 24.96 dB | 28.90 dB | 26.33 dB | ~3 |

## Key Finding  
Ensemble T60/S40 achieves **29.29 dB on LOLv2 Real**, the highest result
across ALL model configurations (+0.62 dB over Teacher alone).

## Requirements
Requires both Teacher and Student checkpoints loaded simultaneously.
- Teacher: `../Teacher_Model/checkpoints/best.pth`
- Student: `../Student_Model/checkpoints/best.pth`

## Files
- `code/` — Ensemble and synergy testing scripts
- `results/` — Enhanced images for all fusion strategies
- `results_synergy/` — Original synergy test results
