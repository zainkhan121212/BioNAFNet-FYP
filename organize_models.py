"""
Organize BioNAFNet models into separate folders.
COPIES files (does NOT move/delete originals) for safety.
"""
import os, shutil

ROOT = r"F:\low_light_enhancement\eye adaption\BioNAFNet"

# Folder structure to create
TEACHER = os.path.join(ROOT, "Teacher_Model")
STUDENT = os.path.join(ROOT, "Student_Model")
ENSEMBLE = os.path.join(ROOT, "Ensemble_Model")

def copy_file(src, dst_dir, new_name=None):
    os.makedirs(dst_dir, exist_ok=True)
    name = new_name or os.path.basename(src)
    dst = os.path.join(dst_dir, name)
    if os.path.exists(src):
        if not os.path.exists(dst):
            shutil.copy2(src, dst)
            print(f"  COPIED: {os.path.basename(src)} -> {os.path.relpath(dst, ROOT)}")
        else:
            print(f"  EXISTS: {os.path.relpath(dst, ROOT)}")
    else:
        print(f"  SKIP (not found): {src}")

def copy_dir(src, dst):
    if os.path.exists(src):
        if not os.path.exists(dst):
            shutil.copytree(src, dst)
            count = sum(len(files) for _, _, files in os.walk(dst))
            print(f"  COPIED DIR: {os.path.relpath(src, ROOT)} -> {os.path.relpath(dst, ROOT)} ({count} files)")
        else:
            print(f"  EXISTS DIR: {os.path.relpath(dst, ROOT)}")
    else:
        print(f"  SKIP DIR (not found): {src}")

print("=" * 60)
print("ORGANIZING BIONAFNET INTO SEPARATE MODEL FOLDERS")
print("=" * 60)

# ═══════════════════════════════════════════════════════════════
# TEACHER MODEL
# ═══════════════════════════════════════════════════════════════
print("\n[1] TEACHER MODEL")
print("-" * 40)

# Code files
copy_file(os.path.join(ROOT, "train_bionafnet.py"), os.path.join(TEACHER, "code"))
copy_file(os.path.join(ROOT, "train_bionafnet_fast.py"), os.path.join(TEACHER, "code"))
copy_file(os.path.join(ROOT, "train_bionafnet_colab.py"), os.path.join(TEACHER, "code"))
copy_file(os.path.join(ROOT, "train_bionafnet_5090.py"), os.path.join(TEACHER, "code"))
copy_file(os.path.join(ROOT, "eval_lol_datasets.py"), os.path.join(TEACHER, "code"))
copy_file(os.path.join(ROOT, "infer_bionafnet.py"), os.path.join(TEACHER, "code"))
copy_file(os.path.join(ROOT, "niqe_calculator.py"), os.path.join(TEACHER, "code"))

# Training log
copy_file(os.path.join(ROOT, "training_log.txt"), os.path.join(TEACHER, "logs"))

# Checkpoints (only best and latest to save space)
copy_file(os.path.join(ROOT, "checkpoints", "best.pth"), os.path.join(TEACHER, "checkpoints"))
copy_file(os.path.join(ROOT, "checkpoints", "latest.pth"), os.path.join(TEACHER, "checkpoints"))

# Results
copy_dir(os.path.join(ROOT, "results"), os.path.join(TEACHER, "results", "lolv1"))
copy_dir(os.path.join(ROOT, "results_lolv2_real"), os.path.join(TEACHER, "results", "lolv2_real"))
copy_dir(os.path.join(ROOT, "results_lolv2_synthetic"), os.path.join(TEACHER, "results", "lolv2_synthetic"))

# Non-GT enhanced images
copy_dir(os.path.join(ROOT, "enhanced_non_gt_my_data"), os.path.join(TEACHER, "results", "enhanced_non_gt_my_data"))
copy_dir(os.path.join(ROOT, "enhanced_non_gt_v2"), os.path.join(TEACHER, "results", "enhanced_non_gt_v2"))
copy_dir(os.path.join(ROOT, "enhanced_non_gt_v2_raw"), os.path.join(TEACHER, "results", "enhanced_non_gt_v2_raw"))
copy_dir(os.path.join(ROOT, "enhanced_real_test"), os.path.join(TEACHER, "results", "enhanced_real_test"))

# README
readme = """# Teacher Model (BioNAFNet Full)

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
"""
with open(os.path.join(TEACHER, "README.md"), 'w', encoding='utf-8') as f:
    f.write(readme)
print("  CREATED: Teacher_Model/README.md")

# ═══════════════════════════════════════════════════════════════
# STUDENT MODEL
# ═══════════════════════════════════════════════════════════════
print("\n[2] STUDENT MODEL")
print("-" * 40)

# Code files
copy_file(os.path.join(ROOT, "train_distillation.py"), os.path.join(STUDENT, "code"))
copy_file(os.path.join(ROOT, "BioNAFNet_Distilled_Test", "test_distilled.py"), os.path.join(STUDENT, "code"))
copy_file(os.path.join(ROOT, "benchmark_all_models.py"), os.path.join(STUDENT, "code"))

# Training log
copy_file(os.path.join(ROOT, "distillation_log.txt"), os.path.join(STUDENT, "logs"))

# Checkpoints
copy_file(os.path.join(ROOT, "checkpoints_student", "best.pth"), os.path.join(STUDENT, "checkpoints"))
copy_file(os.path.join(ROOT, "checkpoints_student", "latest.pth"), os.path.join(STUDENT, "checkpoints"))

# Student-693 checkpoint from distilled test folder
wt_path = os.path.join(ROOT, "BioNAFNet_Distilled_Test", "weights")
if os.path.exists(wt_path):
    for f in os.listdir(wt_path):
        copy_file(os.path.join(wt_path, f), os.path.join(STUDENT, "checkpoints"), f"student_693_{f}")
new_folder = os.path.join(ROOT, "BioNAFNet_Distilled_Test", "New folder")
if os.path.exists(new_folder):
    for f in os.listdir(new_folder):
        if f.endswith('.pth'):
            copy_file(os.path.join(new_folder, f), os.path.join(STUDENT, "checkpoints"), f"student_new_{f}")

# Results
copy_dir(os.path.join(ROOT, "results_student"), os.path.join(STUDENT, "results"))

# Distilled test results
copy_dir(os.path.join(ROOT, "BioNAFNet_Distilled_Test", "results"), os.path.join(STUDENT, "results_distilled_test"))
copy_dir(os.path.join(ROOT, "BioNAFNet_Distilled_Test", "resultsneww"), os.path.join(STUDENT, "results_student_693"))

# README
readme = """# Student Model (BioNAFNet-Lite)

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
"""
with open(os.path.join(STUDENT, "README.md"), 'w', encoding='utf-8') as f:
    f.write(readme)
print("  CREATED: Student_Model/README.md")

# ═══════════════════════════════════════════════════════════════
# ENSEMBLE MODEL
# ═══════════════════════════════════════════════════════════════
print("\n[3] ENSEMBLE MODEL")
print("-" * 40)

# Code files
copy_file(os.path.join(ROOT, "ensemble_test.py"), os.path.join(ENSEMBLE, "code"))
copy_file(os.path.join(ROOT, "BioNAFNet_Distilled_Test", "synergy_test.py"), os.path.join(ENSEMBLE, "code"))
copy_file(os.path.join(ROOT, "benchmark_all_models.py"), os.path.join(ENSEMBLE, "code"))

# Results
copy_dir(os.path.join(ROOT, "results_ensemble"), os.path.join(ENSEMBLE, "results"))
copy_dir(os.path.join(ROOT, "BioNAFNet_Distilled_Test", "results_synergy"), os.path.join(ENSEMBLE, "results_synergy"))

# Non-GT ensemble results
copy_dir(os.path.join(ROOT, "enhanced_non_gt_v3_ensemble"), os.path.join(ENSEMBLE, "results_non_gt_ensemble"))

# README
readme = """# Ensemble Model (Teacher + Student Fusion)

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
"""
with open(os.path.join(ENSEMBLE, "README.md"), 'w', encoding='utf-8') as f:
    f.write(readme)
print("  CREATED: Ensemble_Model/README.md")

# ═══════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ORGANIZATION COMPLETE!")
print("=" * 60)
for folder_name in ["Teacher_Model", "Student_Model", "Ensemble_Model"]:
    folder_path = os.path.join(ROOT, folder_name)
    total_files = sum(len(files) for _, _, files in os.walk(folder_path))
    total_size = sum(os.path.getsize(os.path.join(dp, f))
                     for dp, dn, files in os.walk(folder_path)
                     for f in files)
    print(f"\n  {folder_name}/")
    for item in sorted(os.listdir(folder_path)):
        item_path = os.path.join(folder_path, item)
        if os.path.isdir(item_path):
            sub_count = sum(len(files) for _, _, files in os.walk(item_path))
            print(f"    {item}/ ({sub_count} files)")
        else:
            print(f"    {item}")
    print(f"    TOTAL: {total_files} files, {total_size/1024/1024:.1f} MB")
